# vrk User Guide

vrk is Discord bot with a programmable automation engine that lets you create complex logic rules with conditions, multiple actions, and persistent variables to automate your server. It can reference all objects including members, channels, messages, roles, and guild properties to create sophisticated automation workflows.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Creating Rules](#creating-rules)
3. [Conditions](#conditions)
4. [Placeholders](#placeholders)
5. [Actions](#actions)
6. [Variables](#variables)
7. [Modules](#modules)
8. [Commands](#commands)
9. [Examples](#examples)

---

## Getting Started

### What is vrk?

vrk is a rule engine that lets you create custom automation rules using conditional logic. Rules follow an if-then structure where you define conditions that trigger specific actions.

```
if <something happens> then <do something>
```

### Your First Rule

```
vrule add if message.content == "ping" then message.reply "pong!" priority 10 tags []
```

**What this does:**
- When someone types "ping" in any channel
- The bot automatically replies "pong!"

### Multiple Actions

You can chain multiple actions together by separating them with semicolons (`;`). This lets you create powerful automation sequences:

```
vrule add if member.name == "spammer" then message.delete; member.timeout 60 priority 100 tags [moderation]
```

This rule deletes the message AND times out the user for 60 minutes.

---

## Creating Rules

### Basic Syntax

Every rule follows this structure:

```
vrule add if <condition> then <action> priority <number> tags [tag1, tag2]
```

| Part | Required? | What it does |
|------|-----------|--------------|
| if | Yes | Starts the condition block |
| condition | Yes | Logic that determines when to trigger |
| then | Yes | Separates condition from actions |
| action | Yes | What the bot should do |
| priority | No | Execution order - higher runs first (default: 0) |
| tags | No | Labels for organizing and exporting rules |

**Priority Example:** A rule with priority 100 will run before a rule with priority 10.

**Tags Example:** Use tags like [moderation], [welcome], [leveling] to group related rules for export.

---

## Conditions

Conditions determine when your rule should trigger. You can check user properties, message content, time, events, and more.

### Comparison Operators

These operators let you compare values:

| Operator | Example | Explanation |
|----------|---------|-------------|
| == | message.content == "hello" | Exact match (case-sensitive) |
| != | channel.name != "general" | Not equal to |
| > | guild.member_count > 100 | Greater than (numbers only) |
| < | time.hour < 12 | Less than (numbers only) |
| >= | uvar.level >= 10 | Greater than or equal to |
| <= | var.warnings <= 3 | Less than or equal to |

### String Checks

Special operators for working with text:

| Operator | Example | Explanation |
|----------|---------|-------------|
| startswith | message.content startswith "!" | Text begins with specific characters |
| endswith | member.name endswith "_bot" | Text ends with specific characters |
| in | "Moderator" in member.role_names | Check if item exists in a list |
| matches | message.content matches /https?:\/\// | Regex pattern matching |

**Regex Example:** The pattern `/https?:\/\//` matches URLs starting with http:// or https://

### Combining Conditions

Create complex logic by combining multiple conditions:

| Operator | Example | Explanation |
|----------|---------|-------------|
| and | time.hour > 9 and time.hour < 17 | Both conditions must be true |
| or | message.content == "hi" or message.content == "hello" | At least one condition must be true |
| not | not member.bot | Reverses the result (true becomes false) |
| ( ) | (A and B) or C | Groups conditions for order of operations |

**Logic Example:**
```
if (time.hour >= 9 and time.hour < 17) and not member.bot then channel.send "Office hours!"
```

---

## Placeholders

Placeholders are dynamic variables that represent the event. These keywords let you access the context of the data.

### User Info

Access information about the user who triggered the event.

| Variable | Description |
| --- | --- |
| member.name | Username (e.g., "Cole") |
| member.id | Unique user ID number |
| member.bot | Returns `true` if user is a bot, `false` if user |
| member.role_names | List of all role names the user has |


### Message Info

Access properties of the message that triggered the rule.

| Variable | Description |
| --- | --- |
| message.content | The full text of the message |
| message.length | Number of characters in the message |


### Server Info

Check properties of your server.

| Variable | Description |
| --- | --- |
| guild.name | Server name |
| guild.member_count | Total number of members |
| channel.name | Name of the current channel |

### Time Info

Schedule rules based on current time.

| Variable | Description |
| --- | --- |
| time.hour | Current hour in 24-hour format (0-23) |
| time.minute | Current minute (0-59) |
| time.dayofweek | Day name (Monday, Tuesday, etc.) |

### Event Info

Determine what type of event triggered the rule.

| Variable | Description |
| --- | --- |
| event_type | Event name (`message`, `member_join`, `reaction_add`, etc.) |

### Variables

Reference stored data.

| Variable | Scope | Description |
| --- | --- | --- |
| var.name | Global | Server-wide variable (accessible to everyone) |
| uvar.name | User | User-specific variable (unique per user) |
| temp.name | Local | Temporary variable (exists only during rule execution) |


---

## Actions

Actions are what your bot does when a rule triggers. You can send messages, modify users, manage channels, and more.

### Messaging

Control how and where the bot sends messages:

| Action | Example | What it does |
|--------|---------|--------------|
| channel.send | channel.send "Hello everyone!" | Send message to current channel |
| channel.send_to | channel.send_to "123456:Alert!" | Send message to specific channel by ID |
| message.reply | message.reply "Got it!" | Reply directly to the user's message |
| message.delete | message.delete | Delete the message that triggered the rule |

**Note:** To get a channel ID, enable Developer Mode in Discord, right-click a channel, and select "Copy ID"

### Member Actions

Moderate and manage server members:

| Action | Example | What it does |
|--------|---------|--------------|
| member.timeout | member.timeout 60 | Timeout user for X minutes (mutes them) |
| member.nickname | member.nickname "Cole" | Change user's server nickname |
| member.addrole | member.addrole "Member" | Give user a role by name |
| member.removerole | member.removerole "Trial" | Remove a role from user |
| member.kick | member.kick | Remove user from server temporarily |
| member.ban | member.ban | Permanently ban user from server |
| member.dm | member.dm "Warning: Stop spamming" | Send private message to user |


### Reactions

Add or remove emoji reactions:

| Action | Example | What it does |
|--------|---------|--------------|
| reaction.add | reaction.add "👀" | Add emoji reaction to message |
| reaction.remove | reaction.remove "👎🏼" | Remove all instances of emoji from message |

### Channel Management

Modify channel settings and structure:

| Action | Example | What it does |
|--------|---------|--------------|
| channel.setname | channel.setname "new-name" | Rename the current channel |
| channel.settopic | channel.settopic "Chat here" | Change channel description/topic |
| channel.setslowmode | channel.setslowmode 5 | Set slowmode delay in seconds |
| channel.purge | channel.purge 10 | Bulk delete last X messages |
| channel.create | channel.create "new-channel" | Create new text channel |
| channel.delete | channel.delete | Delete the current channel |

### Variables

Store and manipulate persistent data:

| Action | Example | What it does |
|--------|---------|--------------|
| var.set | var.set counter 0 | Create or update server variable |
| var.add | var.add points 10 | Increase variable by amount |
| var.del | var.del temp | Delete server variable |
| uvar.set | uvar.set xp 100 | Create or update user-specific variable |
| uvar.add | uvar.add coins 50 | Increase user variable by amount |
| uvar.sub | uvar.sub health 10 | Decrease user variable by amount |
| temp.set | temp.set result 42 | Set temporary variable (cleared after rule) |

**Variables can store:** String, numbers, lists, and JSON objects

### Other

Additional utility actions:

| Action | Example | What it does |
|--------|---------|--------------|
| system.wait | system.wait 2 | Pause for X seconds before next action |
| message.pin | message.pin | Pin message to channel |

---

## Variables

Variables let you store persistent data that your rules can read and modify. There are three types of variables, each with different scopes and lifespans.

### Server Variables (var)

Server variables are shared across your entire Discord server. Anyone can trigger rules that use them, and they persist forever unless deleted.

**Available to:** Everyone in the server  
**Saved:** Permanently in database  
**Use case:** Server-wide counters, settings, shared data

**Managing via commands:**
```
vvar set welcome_count 0
vvar set server_motto "Be nice!"
vvar get welcome_count
vvar del welcome_count
```

**Using in rules:**
```
vrule add if event_type == "member_join" then var.add welcome_count 1; channel.send "Welcome! You're member #{var.welcome_count}!" priority 10 tags []
```

### User Variables (uvar)

User variables are unique to each user. Every user has their own separate copy of each uvar, making them perfect for tracking individual stats.

**Available to:** Specific user only  
**Saved:** Per-user, per-server  
**Use case:** XP systems, currency, personal stats, achievements

**Example:**
```
vrule add if message.content startswith "!work" then uvar.add coins 10; message.reply "You earned 10 coins! Total: {uvar.coins}" priority 10 tags [economy]
```

Each user has their own `uvar.coins`, `uvar.xp`, etc. User A's coins don't affect User B's coins.

### Temporary Variables (temp)

Temporary variables only exist while a rule is executing. They're perfect for storing intermediate calculations or random values.

**Available to:** Current rule execution only  
**Saved:** Deleted after rule finishes  
**Use case:** Random rolls, calculations, temporary storage

**Example:**
```
vrule add if message.content == "!roll" then temp.set dice {random.1-6}; message.reply "You rolled: {temp.dice}" priority 10 tags [fun]
```

### Using Variables in Text

You can insert variable values into messages using curly braces `{variable}`:

```
channel.send "Welcome {member.name}! We now have {guild.member_count} members."
```

**Special dynamic variables:**
- `{member.mention}` - Creates @mention for the user
- `{channel.mention}` - Creates #mention for the channel
- `{random.1-100}` - Generates random number between 1-100
- `{time.hour}` - Current hour
- `{var.name}` - Your custom server variable
- `{uvar.name}` - User's variable value

---

## Modules

Modules are packages of rules that can be exported and imported. They let you share automation setups with others or move rules between servers.

### What are Modules?

A module is a JSON file containing:
- Multiple rules grouped by a tag
- Metadata (name, version, author)
- Optional variables

**Benefits:**
- Share automation templates with other servers
- Backup specific rule sets
- Distribute pre-made automation packages

### Exporting a Module

Export creates a portable file containing all rules with a specific tag.

**Steps:**

1. Add tags to your rules:
```
vrule add if ... then ... tags [welcome]
vrule add if ... then ... tags [welcome]
```

2. Export all rules with that tag:
```
vmodule export welcome
```

3. Bot sends you a `module_welcome.json` file

**What gets exported:** All rules tagged with the specified tag, metadata, and structure.

### Importing a Module

Import installs rules from a module file into your server.

**Steps:**

1. Get a module file (from someone else or your own export)
2. Run the import command:
```
vmodule import
```
3. Attach the JSON file to your message
4. Rules are installed with new IDs (won't conflict with existing rules)

**Safety:** The bot validates all imports to prevent malicious code.

### Backup & Restore

Create full backups of ALL your server's rules, not just tagged ones.

**Backup everything:**
```
vmodule backup
```
Downloads a complete snapshot of ALL rules in your server.

**Restore from backup:**
```
vmodule restore
```
Attach the backup file. All rules are re-imported with new IDs.

**Important:** Always backup before using `vrule clear` or making major changes!

---

## Commands

All commands that modify rules or variables require Administrator permission.

### Rule Commands

Manage your automation rules:

| Command | What it does | 
|---------|--------------|
| vrule add if ... then ... | Create a new automation rule |
| vrule &lt;id&gt; | View full details of a specific rule |
| vrule del &lt;id&gt; | Delete a rule permanently |
| vrule toggle &lt;id&gt; | Enable or disable a rule without deleting |
| vrule clear | Delete ALL rules in the server |
| vruledex | List all rules with pagination (10 per page) |
| vruledex 2 | Show page 2 of rules |

**Note:** Rule IDs are assigned automatically and shown in `vruledex`.

### Variable Commands

Manage server-wide variables directly:

| Command | What it does | 
|---------|--------------|
| vvar set &lt;name&gt; &lt;value&gt; | Create or update a server variable |
| vvar get &lt;name&gt; | Retrieve variable value (or download as JSON if large) |
| vvar del &lt;name&gt; | Delete a server variable |
| vvar clear | Delete ALL server variables |
| vvardex | List all variables with pagination |

**Note:** Variables can store numbers, text, lists, or JSON objects.

### Module Commands

Import, export, and backup rule collections:

| Command | What it does | 
|---------|--------------|
| vmodule import | Install module from attached JSON file | 
| vmodule export &lt;tag&gt; | Create module containing all rules with tag |
| vmodule backup | Create full backup of all server rules |
| vmodule restore | Restore rules from backup file |

### Help

Get interactive help within Discord:

| Command | What it does |
|---------|--------------|
| vhelp | Shows interactive dropdown menu with categorized help |

---

## Examples

Real-world automation examples you can use and modify.

### Auto-Moderation

**Delete spam (repeated characters):**
```
vrule add if message.content matches /(.)\1{10,}/ then message.delete; member.timeout 5 priority 100 tags [automod]
```
Detects when someone types the same character 10+ times in a row.

**Block links (except for admins):**
```
vrule add if message.content matches /https?:\/\// and "Admin" not in member.role_names then message.delete; message.reply "No links allowed!" priority 90 tags [automod]
```
Prevents non-admins from posting URLs.

**Auto-ban on bad words:**
```
vrule add if message.content matches /(badword1|badword2)/ then message.delete; member.ban priority 100 tags [automod]
```
Replace `badword1|badword2` with your actual filtered words.

### Welcome System

**Welcome new members:**
```
vrule add if event_type == "member_join" then channel.send_to 123456:"Welcome {member.mention} to the server!"; member.addrole "Member" priority 50 tags [welcome]
```
Replace `123456` with your welcome channel ID.

**Track total joins:**
```
vrule add if event_type == "member_join" then var.add total_joins 1; channel.send "You're member #{var.total_joins}!" priority 50 tags [welcome]
```
Counts and announces each new member.

**Goodbye message:**
```
vrule add if event_type == "member_leave" then channel.send_to 123456:"{member.name} has left the server." priority 50 tags [welcome]
```

### Leveling System

**Gain XP on every message:**
```
vrule add if event_type == "message" and not member.bot then uvar.add xp 5 priority 5 tags [leveling]
```
Award 5 XP for each message (excludes bots).

**Level 10 role reward:**
```
vrule add if uvar.xp >= 1000 and "Level 10" not in member.role_names then member.addrole "Level 10"; channel.send "🎉 {member.mention} reached Level 10!" priority 20 tags [leveling]
```
Automatically gives role when user hits 1000 XP.

**Check rank command:**
```
vrule add if message.content == "!rank" then message.reply "You have {uvar.xp} XP!" priority 10 tags [leveling]
```

### Custom Commands

**Dice roll:**
```
vrule add if message.content == "!roll" then temp.set dice {random.1-6}; message.reply "🎲 You rolled a {temp.dice}!" priority 10 tags [fun]
```

**Coin flip:**
```
vrule add if message.content == "!flip" then temp.set coin {random.0-1}; message.reply "{temp.coin} == 0 ? Heads : Tails" priority 10 tags [fun]
```

**Server stats:**
```
vrule add if message.content == "!stats" then channel.send "📊 Server: {guild.name}\n👥 Members: {guild.member_count}" priority 10 tags [info]
```

### Reaction Roles

**Give role when reacting with ✅:**
```
vrule add if event_type == "reaction_add" and emoji == "✅" then member.addrole "Verified" priority 30 tags [roles]
```
User gets "Verified" role when they react with ✅.

**Remove role when unreacting:**
```
vrule add if event_type == "reaction_remove" and emoji == "✅" then member.removerole "Verified" priority 30 tags [roles]
```

### Scheduled Messages

**Morning announcement at 9 AM:**
```
vrule add if time.hour == 9 and time.minute == 0 then channel.send "☀️ Good morning everyone!" priority 1 tags [scheduled]
```

**Only on weekends:**
```
vrule add if (time.dayofweek == "Saturday" or time.dayofweek == "Sunday") and time.hour == 12 then channel.send "Happy weekend!" priority 1 tags [scheduled]
```

### Advanced: Warnings System

**Track warnings:**
```
vrule add if message.content matches /badword/ then message.delete; uvar.add warnings 1; member.dm "Warning {uvar.warnings}/3" priority 100 tags [moderation]
```
Each violation increases user's warning count.

**Auto-ban at 3 warnings:**
```
vrule add if uvar.warnings >= 3 then member.ban; channel.send "{member.name} was banned for repeated violations" priority 100 tags [moderation]
```

---

## FAQ

**Q: Can I have multiple conditions?**  
A: Yes! Use `and`, `or`, and parentheses to create complex logic:
```
if (A and B) or (C and D) then ...
```

**Q: How do I mention a user in a message?**  
A: Use `{member.mention}` in your text:
```
channel.send "Hello {member.mention}!"
```

**Q: Can rules trigger other rules?**  
A: Yes, if one rule's action creates an event that matches another rule's condition, the second rule will trigger.

**Q: How do I find a channel ID?**  
A: Enable Developer Mode in Discord (Settings → Advanced → Developer Mode), then right-click any channel and select "Copy ID".

**Q: Why isn't my rule working?**  
A: Check these common issues:
- Is it enabled? Use `vrule toggle <id>` to check
- Verify syntax with `vrule <id>`
- Wait 1 second between tests (rules have cooldowns)
- Check `vruledex` to confirm rule exists

**Q: Can I undo vrule clear?**  
A: Only if you ran `vmodule backup` first. Always backup before clearing!

**Q: How many rules can I have?**  
A: Maximum 100 rules per server.

**Q: Do variables persist after bot restart?**  
A: Yes! Server variables (var) and user variables (uvar) are saved to the database and persist permanently. Only temp variables are cleared.

**Q: Can I use math in conditions?**  
A: Yes! Example: `if var.points + 10 > 100 then ...`

---

## Need Help?

- Run `vhelp` for the interactive help menu
- Check your rule with `vrule <id>` to see exact syntax
- List all rules with `vruledex` to find IDs
- Test conditions one at a time to isolate issues
- Always make backups with `vmodule backup` before major changes

---

**Happy Automating! 🚀**
