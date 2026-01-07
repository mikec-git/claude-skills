---
name: tweet-writer
description: Helps write engaging Twitter/X posts and threads. Use when asking to "write a tweet", "create an X post", "draft a thread", "help me post on Twitter", or "make this tweetable". (user)
---

# Tweet Writer

A skill for crafting engaging Twitter/X content - from single tweets to multi-part threads.

## Thinking Budget

Use **UltraThink** (maximum thinking budget) automatically for all tweet writing tasks - crafting hooks and engaging content benefits from deep creative thinking.

## Your Preferred Style

Based on examples you like, follow these formatting rules:

**Formatting Rules:**

- Short sentences, often one per line
- Frequent line breaks between thoughts (creates breathing room)
- No hashtags - keep it clean
- Sentence fragments for emphasis are good
- Parenthetical asides add personality (like this lol)

**Voice:**

- First-person ("I", "my")
- Conversational, not formal
- Casual language is fine ("kinda", "lol", asides in parentheses)
- Vulnerable/honest tone when appropriate

**Avoid AI-sounding language:**

- No "In today's [X]..." or "Let's dive into..."
- No "Here's the thing:" or "The truth is:"
- No excessive enthusiasm ("Amazing!", "Incredible!", "Game-changer!")
- No corporate buzzwords ("leverage", "optimize", "synergy")
- No overly structured "First... Second... Third..." unless it's a numbered thread
- No wrapping up with "In conclusion" or "To sum up"
- Write like you're texting a smart friend, not writing a LinkedIn post

**Structure varies by tweet type:**

- Reflective tweets: Stream-of-consciousness, emotional buildup
- Threads: Clear intro, numbered points (1/, 2/), engagement question at end
- Tip tweets: Direct instruction, explain the benefit

## Workflow

### 1. Understand the Content

Ask the user (if not already clear):

- What topic or message do you want to share?
- Is this a single tweet or a thread?

### 2. Choose the Tone

Present tone options using AskUserQuestion:

- **Reflective** - Vulnerable, honest, stream-of-consciousness
- **Casual** - Conversational, friendly, relatable
- **Witty** - Clever, humorous, attention-grabbing
- **Informative** - Educational, clear, value-focused
- **Provocative** - Bold, contrarian, debate-sparking

### 3. Craft the Hook

The first line is everything. Apply these hook techniques:

**Hook Formulas:**

- **Vulnerable opener**: "I am not sure if [others] feel like this."
- **Intro + context**: "I'm [name] and I [credential]. [What you're sharing]."
- **Direct instruction**: "[Do X]. [Do Y]. Now, [result]."
- **Contrarian**: "Unpopular opinion: [challenge common belief]"
- **Curiosity gap**: "Most people don't know this about [topic]..."
- **Bold claim**: "[Strong statement] - here's why"

**Hook Rules:**

- Front-load the value - the first 5 words matter most
- Create tension or curiosity
- Avoid weak openers like "Just wanted to share..."
- No hashtags or @mentions in the hook

### 4. Write the Content

**For Single Tweets:**

- One thought per line
- Line breaks create rhythm and breathing room
- Use periods to create pauses, even with fragments
- No hashtags
- Can exceed 280 chars - it's okay to write longer posts now

**Tweet Types:**

_Reflective/Emotional:_

```
I am not sure if other developers feel like this.

But I feel kinda depressed.

[Build the emotional arc]

The thing I spent most of my life getting good at.

Is becoming a full commodity extremely quickly.

[Resolution or open question]
```

_Tip/Hack:_

```
Give Claude Code as much of your idea as you can

End it with this: "[specific instruction]"

Now, it will [explain what happens]

[Optional: include image]
```

**For Threads:**

- Tweet 1: Clear intro with context (who you are, what you're sharing)
- Tweet 2-N: Numbered (1/, 2/), one idea per tweet
- Include links where helpful
- Final tweet: Engagement question ("What are your tips?", "What do you want to hear about next?")

_Thread Structure:_

```
[Intro tweet]
I'm [name] and I [context]. Lots of people have asked [topic], so I wanted to [share/show/explain].

[Setup expectations]
My [approach] might be surprisingly [adjective]! [Brief philosophy].

So, here goes.

1/ [First point with detail]

2/ [Second point with detail]

...

[Final tweet]
I hope this was helpful! What are your tips for [topic]? What do you want to hear about next?
```

### 5. Polish and Format

- Keep sentences short
- Add line breaks generously
- Parenthetical asides add personality
- No hashtags
- Sentence fragments are good for emphasis
- Check that it reads conversationally (read it out loud)
- **Remove anything that sounds AI-generated** - if it sounds like a LinkedIn post or marketing copy, rewrite it

## Output Format

Present the final tweet(s) in a code block for easy copying:

```
[Tweet content here]
```

For threads, separate each tweet clearly:

```
[Intro]

1/
[First tweet]

2/
[Second tweet]

...

[Final engagement tweet]
```

## Example Triggers

- "Write a tweet about..."
- "Help me post on Twitter"
- "Create an X post for..."
- "Draft a thread on..."
- "Make this into a tweet"
- "Turn this into a Twitter thread"
- "I need a tweet for..."
