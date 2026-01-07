---
name: tweet-writer
description: Helps write engaging Twitter/X posts and threads. Use when asking to "write a tweet", "create an X post", "draft a thread", "help me post on Twitter", or "make this tweetable". (user)
---

# Tweet Writer

A skill for crafting engaging Twitter/X content - from single tweets to multi-part threads.

## Thinking Budget

Use **UltraThink** (maximum thinking budget) automatically for all tweet writing tasks - crafting hooks and engaging content benefits from deep creative thinking.

## Workflow

### 1. Understand the Content

Ask the user (if not already clear):

- What topic or message do you want to share?
- Is this a single tweet or a thread?

### 2. Choose the Tone

Present tone options using AskUserQuestion:

- **Professional** - Polished, authoritative, suitable for industry insights
- **Casual** - Conversational, friendly, relatable
- **Witty** - Clever, humorous, attention-grabbing
- **Informative** - Educational, clear, value-focused
- **Provocative** - Bold, contrarian, debate-sparking

### 3. Craft the Hook

The first line is everything. Apply these hook techniques:

**Hook Formulas:**

- **Contrarian**: "Unpopular opinion: [challenge common belief]"
- **Curiosity gap**: "Most people don't know this about [topic]..."
- **Bold claim**: "[Strong statement] - here's why"
- **Story opener**: "Last week, something happened that changed how I think about [topic]"
- **Direct value**: "How to [achieve result] in [timeframe]"
- **Question**: "Why do [people/companies] keep making this mistake?"

**Hook Rules:**

- Front-load the value - the first 5 words matter most
- Create tension or curiosity
- Avoid weak openers like "I think..." or "Just wanted to share..."
- No hashtags or @mentions in the hook

### 4. Write the Content

**For Single Tweets (max 280 characters):**

- One clear idea per tweet
- Use line breaks for readability
- End with a call to action or thought-provoking question when appropriate
- Save hashtags for the end (max 2-3) or omit entirely

**For Threads:**

- Tweet 1: The hook - must stand alone and compel clicks
- Tweet 2-N: One idea per tweet, numbered (e.g., "1/", "2/")
- Build momentum - each tweet should make them want the next
- Final tweet: Summary + call to action (follow, reply, repost)
- Keep threads to 5-10 tweets for best engagement

**Thread Structure Templates:**

_Listicle:_

```
Hook: "X things I learned about [topic]:"
1/ First insight
2/ Second insight
...
Final: "That's it. [CTA]"
```

_Story:_

```
Hook: "A story about [topic]..."
1/ Setting the scene
2/ The challenge
3/ The turning point
4/ The lesson
Final: Summary + CTA
```

_How-to:_

```
Hook: "How to [achieve X] - a thread:"
1/ Step one
2/ Step two
...
Final: "Now you know how to [X]. [CTA]"
```

### 5. Polish and Format

- Remove filler words ("just", "really", "very")
- Use em dashes and line breaks for rhythm
- Ensure it reads well on mobile (short paragraphs)
- Check character count (280 max per tweet)
- Add 1-2 relevant emojis if appropriate for tone (optional)

## Output Format

Present the final tweet(s) in a code block for easy copying:

```
[Tweet content here]
```

For threads, separate each tweet clearly:

```
1/
[First tweet]

2/
[Second tweet]

...
```

## Example Triggers

- "Write a tweet about..."
- "Help me post on Twitter"
- "Create an X post for..."
- "Draft a thread on..."
- "Make this into a tweet"
- "Turn this into a Twitter thread"
- "I need a tweet for..."
