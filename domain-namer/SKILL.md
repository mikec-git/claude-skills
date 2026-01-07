---
name: domain-namer
description: Generates creative domain name suggestions for projects and businesses. Use when naming a new project, brainstorming domain names, finding available domains, or asking "what should I call my app/startup/project?". Trigger phrases include "help me name", "domain ideas", "find a domain", "name my project".
---

# Domain Namer

A creative domain name generator that brainstorms memorable names and optionally checks availability via WhoisXML or Namecheap APIs.

## Thinking Budget

Use **UltraThink** (maximum thinking budget) automatically when:
- Generating creative name variations
- Analyzing keywords to create portmanteaus
- Evaluating memorability and brandability
- Coming up with unique made-up words

---

## Two Modes

### Brainstorm Mode (Default - No API)
- Generate creative domain name suggestions
- Score by memorability, length, and pronunciation
- User checks availability manually at their preferred registrar

### Full Mode (With API Key)
- Everything in Brainstorm Mode, plus:
- Real-time availability checking
- Show which domains are available vs taken
- Display pricing where available

**Supported APIs:**
1. **WhoisXML API** - Simple setup, 100 free queries/month
2. **Namecheap API** - Unlimited free queries, requires more setup (account + IP whitelist)

---

## Workflow

### Step 1: Check for API Access

Use AskUserQuestion to ask:

"Would you like me to check domain availability in real-time? (optional)"

**Options:**
1. **WhoisXML API** - Simple setup, 100 free queries/month
2. **Namecheap API** - Unlimited queries, more setup required
3. **No API** - I'll generate names, you check availability manually

**If user selects WhoisXML:**
Ask for their API key. Setup instructions:
1. Go to https://whoisxmlapi.com/ and create free account
2. You get 100 free domain availability queries
3. Copy your API key from the dashboard

**If user selects Namecheap:**
Ask for their credentials. Setup instructions:
1. Create account at https://www.namecheap.com
2. Enable API access at Profile > Tools > API Access
3. Add your public IP to the whitelist (Google "what is my ip")
4. You'll need: API Key, API User, and your whitelisted IP

Store their preference for the session.

### Step 2: Gather Context

Use AskUserQuestion to ask:

**Question 1: Project Type**
"What are you naming?"
- Startup/Business
- Side project/App
- Personal brand/Portfolio
- Blog/Content site
- Other (describe)

**Question 2: Industry/Domain**
"What industry or category?"
- Technology/SaaS
- E-commerce/Retail
- Creative/Design
- Finance/Fintech
- Health/Wellness
- Education
- Other (specify)

**Question 3: Keywords**
"What 2-4 keywords describe your project? (e.g., 'fast shipping marketplace')"

**Question 4: Tone**
"What tone/vibe should the name convey?"
- Professional/Corporate
- Playful/Fun
- Techy/Modern
- Minimalist/Clean
- Bold/Edgy

**Question 5: TLD Preferences**
"Which domain extensions do you prefer?" (multi-select)
- .com (traditional, trusted)
- .io (tech startups)
- .co (modern alternative)
- .ai (AI/ML focus)
- .dev (developer tools)
- .app (mobile apps)
- Other

### Step 3: Generate Names

Use these naming strategies based on the gathered context:

#### Strategy 1: Compound Words
Combine two relevant words:
- keyword1 + keyword2 (DropBox, Facebook)
- verb + noun (SendGrid, MailChimp)

#### Strategy 2: Portmanteaus
Blend parts of words together:
- Spotify (spot + identify)
- Pinterest (pin + interest)
- Groupon (group + coupon)

#### Strategy 3: Prefix/Suffix Patterns
Add common modifiers:
- Prefixes: get-, try-, use-, go-, my-, the-
- Suffixes: -ly, -ify, -hub, -base, -lab, -io, -ful

#### Strategy 4: Made-Up Words
Create unique, pronounceable invented names:
- Hulu, Roku, Zappos, Zillow
- Use soft consonants and vowel patterns
- Keep 2-3 syllables

#### Strategy 5: Domain Hacks
Use TLD as part of the name:
- del.icio.us, bit.ly, instagr.am
- Only if it creates a real word/phrase

#### Strategy 6: Acronyms/Initialisms
Shorten a descriptive phrase:
- IBM, AWS, HBO
- Works best for B2B

Generate 10-15 name candidates using a mix of these strategies.

### Step 4: Score and Rank

Rate each name on these criteria (1-10 scale):

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Memorability | 30% | Easy to recall after hearing once |
| Pronunciation | 20% | Unambiguous, easy to say |
| Spelling | 20% | No confusion when heard verbally |
| Length | 15% | Shorter is better (under 10 chars ideal) |
| Brandability | 15% | Unique, can be trademarked |

Calculate weighted score for each name.

### Step 5: Check Availability (Full Mode Only)

If user provided API credentials, check availability:

**Using WhoisXML API:**
```
For each top candidate:
  For each preferred TLD:
    WebFetch: https://domain-availability.whoisxmlapi.com/api/v1
    Query params:
      apiKey={user's key}
      domainName={name}.{tld}
      outputFormat=JSON
      credits=DA

Response: Look for "domainAvailability" field
  - "AVAILABLE" = can be registered
  - "UNAVAILABLE" = already taken
```

**Using Namecheap API:**
```
For each batch of domains (up to 50):
  WebFetch: https://api.namecheap.com/xml.response
  Query params:
    ApiUser={user's api_user}
    ApiKey={user's api_key}
    UserName={user's api_user}
    Command=namecheap.domains.check
    ClientIp={user's whitelisted IP}
    DomainList={comma-separated domains}

Response (XML): Look for <DomainCheckResult> elements
  - Available="true" = can be registered
  - Available="false" = already taken
  - IsPremiumName="true" = premium pricing applies
```

Parse response for availability status.

### Step 6: Present Results

**Brainstorm Mode Output:**

```
## Domain Name Suggestions

Based on your project (keywords: fast, shipping, marketplace), here are my top suggestions:

| Domain            | Score | Why It Works                           |
|-------------------|-------|----------------------------------------|
| shipfast.com      | 9/10  | Direct, memorable, action-oriented     |
| quickship.io      | 8/10  | Tech-friendly TLD, clear meaning       |
| getshipd.com      | 8/10  | Trendy spelling, prefix pattern        |
| sendly.co         | 7/10  | Short, -ly suffix, modern              |
| parcelbase.com    | 7/10  | Professional, compound word            |

### Naming Strategies Used
- **shipfast**: Compound (verb + adjective)
- **quickship**: Compound (adjective + noun)
- **getshipd**: Prefix + trendy spelling
- **sendly**: Root + suffix
- **parcelbase**: Compound (noun + suffix)

### Next Steps
Check availability at:
- https://domains.cloudflare.com
- https://www.namecheap.com/domains/

Want me to generate more variations on any of these?
```

**Full Mode Output:**

```
## Domain Name Suggestions

| Domain            | Status      | Price   | Score | Notes                    |
|-------------------|-------------|---------|-------|--------------------------|
| shipfast.com      | Taken       | -       | 9/10  | Try prefix: getshipfast  |
| shipfast.io       | Available   | $39/yr  | 9/10  | Great alternative!       |
| quickship.com     | Taken       | -       | 8/10  | -                        |
| quickship.io      | Available   | $39/yr  | 8/10  | Tech-friendly option     |
| getshipd.com      | Available   | $12/yr  | 8/10  | Best value!              |

### Available Domains (Recommended)
1. **getshipd.com** - $12/yr - Short, memorable, great value
2. **shipfast.io** - $39/yr - Premium feel, tech-focused
3. **quickship.io** - $39/yr - Clear meaning

### Next Steps
Register your favorite at:
- https://domains.cloudflare.com (at-cost pricing)
- https://www.namecheap.com

Want me to check more variations?
```

---

## Additional Suggestions

After presenting results, offer:

1. **More variations**: "Want me to explore more names using [specific strategy]?"
2. **Social handles**: "Should I suggest variations that might have matching Twitter/GitHub handles?"
3. **Alternative TLDs**: "Want me to check other extensions like .app or .dev?"
4. **Backup names**: "For any taken domains, want me to suggest prefixes like 'get' or 'try'?"

---

## Example Triggers

- "Help me name my new startup"
- "I need domain name ideas for a developer tool"
- "What should I call my app?"
- "Find me an available domain for an e-commerce site"
- "Brainstorm some project names"
- "Generate domain names for my side project"
