#!/usr/bin/env python3
"""
Claude Code JSONL Parser

Parses Claude Code's JSONL output files to extract:
- Full conversation history
- Token usage and costs
- Tool call analysis

Usage:
    python claude_jsonl_parser.py <jsonl_file_or_directory> [options]

Examples:
    python claude_jsonl_parser.py ~/.claude/projects/my-project/agent-abc123.jsonl
    python claude_jsonl_parser.py ~/.claude/projects/ --summary
    python claude_jsonl_parser.py session.jsonl --format json --output report.json
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from typing import Optional


# Pricing per 1M tokens (as of Jan 2025)
MODEL_PRICING = {
    "claude-opus-4-5-20251101": {"input": 15.00, "output": 75.00},
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    "claude-3-5-sonnet-20240620": {"input": 3.00, "output": 15.00},
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.00},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
}


@dataclass
class Message:
    uuid: str
    parent_uuid: Optional[str]
    timestamp: str
    role: str
    content: str
    model: Optional[str] = None
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0
    tool_calls: list = field(default_factory=list)
    session_id: Optional[str] = None
    agent_id: Optional[str] = None
    cwd: Optional[str] = None
    git_branch: Optional[str] = None


@dataclass
class ToolCall:
    name: str
    input_preview: str
    success: bool = True


@dataclass
class SessionStats:
    session_id: str
    agent_id: Optional[str]
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    message_count: int = 0
    user_messages: int = 0
    assistant_messages: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cache_read_tokens: int = 0
    total_cache_creation_tokens: int = 0
    tool_usage: dict = field(default_factory=dict)
    models_used: set = field(default_factory=set)
    estimated_cost: float = 0.0


def parse_content(content) -> tuple[str, list[ToolCall]]:
    """Parse message content, extracting text and tool calls."""
    if isinstance(content, str):
        return content, []

    if not isinstance(content, list):
        return str(content), []

    text_parts = []
    tool_calls = []

    for block in content:
        if isinstance(block, str):
            text_parts.append(block)
        elif isinstance(block, dict):
            block_type = block.get("type", "")

            if block_type == "text":
                text_parts.append(block.get("text", ""))
            elif block_type == "tool_use":
                tool_name = block.get("name", "unknown")
                tool_input = block.get("input", {})
                # Create a preview of the input
                input_preview = json.dumps(tool_input)[:100]
                if len(json.dumps(tool_input)) > 100:
                    input_preview += "..."
                tool_calls.append(ToolCall(name=tool_name, input_preview=input_preview))
            elif block_type == "tool_result":
                # Tool results indicate previous tool call completed
                is_error = block.get("is_error", False)
                tool_use_id = block.get("tool_use_id", "")
                if is_error:
                    text_parts.append(f"[Tool Error: {block.get('content', 'Unknown error')[:50]}]")

    return "\n".join(text_parts), tool_calls


def parse_jsonl_file(file_path: Path) -> list[Message]:
    """Parse a single JSONL file into a list of Messages."""
    messages = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Warning: Skipping invalid JSON at {file_path}:{line_num}: {e}", file=sys.stderr)
                continue

            # Skip non-message entries (like file-history-snapshot)
            msg_type = data.get("type", "")
            if msg_type not in ("user", "assistant"):
                continue

            msg_data = data.get("message", {})
            role = msg_data.get("role", data.get("type", "unknown"))

            content_raw = msg_data.get("content", "")
            content_text, tool_calls = parse_content(content_raw)

            usage = msg_data.get("usage", {})

            message = Message(
                uuid=data.get("uuid", ""),
                parent_uuid=data.get("parentUuid"),
                timestamp=data.get("timestamp", ""),
                role=role,
                content=content_text,
                model=msg_data.get("model"),
                input_tokens=usage.get("input_tokens", 0),
                output_tokens=usage.get("output_tokens", 0),
                cache_read_tokens=usage.get("cache_read_input_tokens", 0),
                cache_creation_tokens=usage.get("cache_creation_input_tokens", 0),
                tool_calls=tool_calls,
                session_id=data.get("sessionId"),
                agent_id=data.get("agentId"),
                cwd=data.get("cwd"),
                git_branch=data.get("gitBranch"),
            )
            messages.append(message)

    return messages


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate estimated cost based on model and token counts."""
    pricing = MODEL_PRICING.get(model, {"input": 3.00, "output": 15.00})  # Default to Sonnet pricing
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost


def compute_session_stats(messages: list[Message]) -> dict[str, SessionStats]:
    """Compute statistics grouped by session."""
    sessions: dict[str, SessionStats] = {}

    for msg in messages:
        session_id = msg.session_id or "unknown"

        if session_id not in sessions:
            sessions[session_id] = SessionStats(
                session_id=session_id,
                agent_id=msg.agent_id,
                tool_usage=defaultdict(int),
                models_used=set(),
            )

        stats = sessions[session_id]
        stats.message_count += 1

        if msg.role == "user":
            stats.user_messages += 1
        else:
            stats.assistant_messages += 1

        stats.total_input_tokens += msg.input_tokens
        stats.total_output_tokens += msg.output_tokens
        stats.total_cache_read_tokens += msg.cache_read_tokens
        stats.total_cache_creation_tokens += msg.cache_creation_tokens

        if msg.model:
            stats.models_used.add(msg.model)
            stats.estimated_cost += calculate_cost(msg.model, msg.input_tokens, msg.output_tokens)

        for tool in msg.tool_calls:
            stats.tool_usage[tool.name] += 1

        # Track time range
        if msg.timestamp:
            if not stats.start_time or msg.timestamp < stats.start_time:
                stats.start_time = msg.timestamp
            if not stats.end_time or msg.timestamp > stats.end_time:
                stats.end_time = msg.timestamp

    return sessions


def format_conversation(messages: list[Message], verbose: bool = False) -> str:
    """Format messages as readable conversation."""
    lines = []

    for msg in sorted(messages, key=lambda m: m.timestamp or ""):
        timestamp = ""
        if msg.timestamp:
            try:
                dt = datetime.fromisoformat(msg.timestamp.replace("Z", "+00:00"))
                timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                timestamp = msg.timestamp

        role_display = "USER" if msg.role == "user" else "ASSISTANT"
        header = f"[{timestamp}] {role_display}"

        if verbose and msg.model:
            header += f" ({msg.model})"

        lines.append(header)
        lines.append("-" * len(header))

        # Content preview (truncate very long messages)
        content = msg.content.strip()
        if len(content) > 2000 and not verbose:
            content = content[:2000] + "\n... [truncated]"
        lines.append(content)

        # Show tool calls
        if msg.tool_calls:
            lines.append("")
            lines.append("Tool calls:")
            for tool in msg.tool_calls:
                lines.append(f"  - {tool.name}: {tool.input_preview}")

        # Token usage
        if verbose and (msg.input_tokens or msg.output_tokens):
            lines.append("")
            lines.append(f"Tokens: in={msg.input_tokens:,}, out={msg.output_tokens:,}")
            if msg.cache_read_tokens:
                lines.append(f"Cache read: {msg.cache_read_tokens:,}")

        lines.append("")
        lines.append("")

    return "\n".join(lines)


def format_summary(sessions: dict[str, SessionStats]) -> str:
    """Format session statistics as a summary report."""
    lines = []
    lines.append("=" * 60)
    lines.append("CLAUDE CODE USAGE SUMMARY")
    lines.append("=" * 60)
    lines.append("")

    total_input = 0
    total_output = 0
    total_cost = 0.0
    all_tools = defaultdict(int)
    all_models = set()
    total_messages = 0

    for session_id, stats in sessions.items():
        total_input += stats.total_input_tokens
        total_output += stats.total_output_tokens
        total_cost += stats.estimated_cost
        total_messages += stats.message_count
        all_models.update(stats.models_used)
        for tool, count in stats.tool_usage.items():
            all_tools[tool] += count

    # Overall stats
    lines.append("OVERALL STATISTICS")
    lines.append("-" * 40)
    lines.append(f"Total sessions:        {len(sessions)}")
    lines.append(f"Total messages:        {total_messages:,}")
    lines.append(f"Total input tokens:    {total_input:,}")
    lines.append(f"Total output tokens:   {total_output:,}")
    lines.append(f"Estimated total cost:  ${total_cost:.4f}")
    lines.append("")

    # Models used
    if all_models:
        lines.append("MODELS USED")
        lines.append("-" * 40)
        for model in sorted(all_models):
            lines.append(f"  - {model}")
        lines.append("")

    # Tool usage
    if all_tools:
        lines.append("TOOL USAGE (sorted by frequency)")
        lines.append("-" * 40)
        sorted_tools = sorted(all_tools.items(), key=lambda x: -x[1])
        for tool, count in sorted_tools:
            lines.append(f"  {tool:30} {count:>6} calls")
        lines.append("")

    # Per-session breakdown (if multiple sessions)
    if len(sessions) > 1:
        lines.append("PER-SESSION BREAKDOWN")
        lines.append("-" * 40)
        for session_id, stats in sessions.items():
            agent_info = f" (agent: {stats.agent_id})" if stats.agent_id else ""
            lines.append(f"\nSession: {session_id[:36]}...{agent_info}")
            lines.append(f"  Messages: {stats.message_count} ({stats.user_messages} user, {stats.assistant_messages} assistant)")
            lines.append(f"  Tokens: {stats.total_input_tokens:,} in / {stats.total_output_tokens:,} out")
            lines.append(f"  Cost: ${stats.estimated_cost:.4f}")
            if stats.start_time and stats.end_time:
                lines.append(f"  Time: {stats.start_time} to {stats.end_time}")

    return "\n".join(lines)


def format_json_output(messages: list[Message], sessions: dict[str, SessionStats]) -> str:
    """Format output as JSON."""
    output = {
        "messages": [],
        "sessions": [],
        "summary": {
            "total_messages": len(messages),
            "total_sessions": len(sessions),
            "total_input_tokens": sum(s.total_input_tokens for s in sessions.values()),
            "total_output_tokens": sum(s.total_output_tokens for s in sessions.values()),
            "estimated_total_cost": sum(s.estimated_cost for s in sessions.values()),
        },
    }

    for msg in messages:
        msg_dict = {
            "uuid": msg.uuid,
            "parent_uuid": msg.parent_uuid,
            "timestamp": msg.timestamp,
            "role": msg.role,
            "content": msg.content,
            "model": msg.model,
            "input_tokens": msg.input_tokens,
            "output_tokens": msg.output_tokens,
            "tool_calls": [{"name": t.name, "input_preview": t.input_preview} for t in msg.tool_calls],
            "session_id": msg.session_id,
        }
        output["messages"].append(msg_dict)

    for session_id, stats in sessions.items():
        session_dict = {
            "session_id": stats.session_id,
            "agent_id": stats.agent_id,
            "start_time": stats.start_time,
            "end_time": stats.end_time,
            "message_count": stats.message_count,
            "user_messages": stats.user_messages,
            "assistant_messages": stats.assistant_messages,
            "total_input_tokens": stats.total_input_tokens,
            "total_output_tokens": stats.total_output_tokens,
            "cache_read_tokens": stats.total_cache_read_tokens,
            "cache_creation_tokens": stats.total_cache_creation_tokens,
            "tool_usage": dict(stats.tool_usage),
            "models_used": list(stats.models_used),
            "estimated_cost": stats.estimated_cost,
        }
        output["sessions"].append(session_dict)

    return json.dumps(output, indent=2)


def find_jsonl_files(path: Path) -> list[Path]:
    """Find all JSONL files in a path (file or directory)."""
    if path.is_file():
        return [path]
    elif path.is_dir():
        return sorted(path.rglob("*.jsonl"))
    else:
        return []


def main():
    parser = argparse.ArgumentParser(
        description="Parse Claude Code JSONL output files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("path", type=Path, help="JSONL file or directory to parse")
    parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json", "summary"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument("--output", "-o", type=Path, help="Output file (default: stdout)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Include full message content and details")
    parser.add_argument("--summary", "-s", action="store_true", help="Show summary statistics only")
    parser.add_argument(
        "--filter-session",
        type=str,
        help="Filter to a specific session ID (partial match)",
    )
    parser.add_argument(
        "--filter-agent",
        type=str,
        help="Filter to a specific agent ID (partial match)",
    )

    args = parser.parse_args()

    # Handle --summary as shorthand for --format=summary
    if args.summary:
        args.format = "summary"

    # Find files
    files = find_jsonl_files(args.path)
    if not files:
        print(f"Error: No JSONL files found at {args.path}", file=sys.stderr)
        sys.exit(1)

    print(f"Parsing {len(files)} file(s)...", file=sys.stderr)

    # Parse all files
    all_messages = []
    for file_path in files:
        messages = parse_jsonl_file(file_path)
        all_messages.extend(messages)

    print(f"Found {len(all_messages)} messages", file=sys.stderr)

    # Apply filters
    if args.filter_session:
        all_messages = [m for m in all_messages if m.session_id and args.filter_session in m.session_id]
    if args.filter_agent:
        all_messages = [m for m in all_messages if m.agent_id and args.filter_agent in m.agent_id]

    if not all_messages:
        print("No messages found after applying filters", file=sys.stderr)
        sys.exit(0)

    # Compute statistics
    sessions = compute_session_stats(all_messages)

    # Format output
    if args.format == "json":
        output = format_json_output(all_messages, sessions)
    elif args.format == "summary":
        output = format_summary(sessions)
    else:  # text
        output = format_conversation(all_messages, verbose=args.verbose)
        output += "\n" + "=" * 60 + "\n"
        output += format_summary(sessions)

    # Write output
    if args.output:
        args.output.write_text(output)
        print(f"Output written to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
