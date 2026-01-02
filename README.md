# About

vrk is Discord bot with a programmable automation engine that lets you create complex logic rules with conditions, multiple actions, and persistent variables to automate your server. It can reference all objects including members, channels, messages, roles, and guild properties to create sophisticated automation workflows.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Creating Rules](#creating-rules)
3. [Conditions](#conditions)
4. [Placeholders](#placeholders)
5. [Events](#events)
6. [Actions](#actions)
7. [Variables](#variables)
8. [Modules](#modules)
9. [Commands](#commands)
10. [Examples](#examples)

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

### Variables

Reference stored data.

| Variable | Scope | Description |
| --- | --- | --- |
| var.name | Global | Server-wide variable (accessible to everyone) |
| uvar.name | User | User-specific variable (unique per user) |
| temp.name | Local | Temporary variable (exists only during rule execution) |


---

## Events

Events are discrete actions or changes that occur within a Discord server. They represent specific triggers that the bot can respond to. Each event provides contextual information about the objects involved. Use the `event_type` variable in your conditions to target specific triggers.

### Message Events

Triggered by activity in text channels. Provides the message content, author info, and channel details so rules can respond to messages or edits, or track deletions.

| Event          | Trigger                     | Context Variables                                                                     |
| -------------- | --------------------------- | ------------------------------------------------------------------------------------- |
| message        | When a user sends a message | {message.content}, {message.id}, {message.author.bot}, {member.name}, {channel.topic} |
| message_delete | When a message is deleted   | {message.content} (if cached), {message.id}, {message.created_at}, {channel.name}     |
| message_edit   | When a message is edited    | {message.content} (new text), {message.id}, {message.jump_url}, {member.name}         |

### Member Events

Covers users joining, leaving, or having their roles and nicknames updated. Provides access to member details, roles changed, and server membership info.

| Event         | Trigger                        | Context Variables                                                                       |
| ------------- | ------------------------------ | --------------------------------------------------------------------------------------- |
| member_join   | When someone joins the server  | {member.name}, {member.id}, {member.created_at}, {guild.member_count}, {guild.owner_id} |
| member_leave  | When someone leaves the server | {member.name}, {member.id}, {member.joined_at}, {guild.member_count}                    |
| member_update | When roles or nickname change  | {nick_changed}, {old_nick}, {new_nick}, {added_roles}, {removed_roles}, {member.roles}  |
| member_ban    | When a user is banned          | {member.name}, {member.id}, {member.discriminator}                                      |
| member_unban  | When a user is unbanned        | {member.name}, {member.id}                                                              |

### Voice Events

Tracks user activity in voice channels, including joining, leaving, or moving. Context includes the user, channel, and mute status.

| Event        | Trigger                           | Context Variables                                                                           |
| ------------ | --------------------------------- | ------------------------------------------------------------------------------------------- |
| voice_update | When a user’s voice state changes | {voice.joined}, {voice.left}, {voice.moved}, {voice.channel_name}, {member.voice.self_mute} |

### Reaction Events

Triggered when members add or remove reactions. Provides the emoji, the message reacted to, and relevant member information.

| Event           | Trigger                    | Context Variables                                                         |
| --------------- | -------------------------- | ------------------------------------------------------------------------- |
| reaction_add    | When a reaction is added   | {emoji}, {message.id}, {message.content}, {member.name}, {reaction.count} |
| reaction_remove | When a reaction is removed | {emoji}, {message.id}, {message.channel.id}, {member.name}                |

### Server/Guild Events

Covers changes to channels or server settings. Context includes channel or server details so rules can respond to structural updates.

| Event          | Trigger                          | Context Variables                                                                                               |
| -------------- | -------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| channel_create | When a new channel is created    | {channel.name}, {channel.id}, {channel.category.name}, {guild.name}                                             |
| channel_delete | When a channel is deleted        | {channel.name}, {channel.id}, {channel.position}                                                                |
| guild_update   | When server settings are changed | {name_changed}, {icon_changed}, {old_name}, {new_name}, {guild.description}, {guild.premium_subscription_count} |

**Note**: For advanced and sophisticated rules, `vrk` supports accessing properties defined in the Discord library. Use these links to find available attributes for your rules: [message](https://www.google.com/search?q=https://discordpy.readthedocs.io/en/stable/api.html%23discord.Message), [member](https://www.google.com/search?q=https://discordpy.readthedocs.io/en/stable/api.html%23discord.Member), [guild](https://www.google.com/search?q=https://discordpy.readthedocs.io/en/stable/api.html%23discord.Guild), [channel](https://www.google.com/search?q=https://discordpy.readthedocs.io/en/stable/api.html%23discord.TextChannel), [reaction](https://www.google.com/search?q=https://discordpy.readthedocs.io/en/stable/api.html%23discord.Reaction), [role](https://www.google.com/search?q=https://discordpy.readthedocs.io/en/stable/api.html%23discord.Role)
  
---


## Actions

Actions are what the bot does when a rule triggers. You can send messages, modify users, manage channels, and more.

### Messaging

Control how and where the bot sends messages:

| Action | Example | What it does |
|--------|---------|--------------|
| channel.send | channel.send "Hello everyone!" | Send message to current channel |
| channel.send_to | channel.send_to "123456:Alert!" | Send message to specific channel by ID |
| channel.send_embed | channel.send_embed "{'title': 'Alert', 'description': 'Something happened!', 'color': 0xFF0000}" | Send embed to current channel |
| channel.send_embed_to | channel.send_embed_to "12345:{'title': 'Alert', 'description': 'Something happened!', 'color': 0xFF0000}" | Send message to specific channel by ID |
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
| member.ban | member.ban 123456789 | Permanently ban user from server |
| member.ban | member.ban 123456789 | Unbans the user from server |
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

### Variables & Math

Store data and perform calculations. **Note:** To do math, use `{}` to retrieve the current value.

| Action | Example | What it does |
|--------|---------|--------------|
| var.set | `var.set "counter" 0` | Set a global variable |
| var.del | `var.del "counter"` | Delete a global variable |
| uvar.set | `uvar.set "xp" 100` | Set a user variable |
| uvar.del | `uvar.del "xp"` | Delete a specific user variable |
| uvar.clear | `uvar.clear` | **Hard Reset:** Wipes ALL data for that user |
| temp.set | `temp.set "roll" {random.1-6}` | Set temporary variable |

**Math Examples:**
* **Add:** `uvar.set "coins" {uvar.coins} + 10`
* **Subtract:** `uvar.set "hp" {uvar.hp} - 5`
* **Multiply:** `uvar.set "bonus" {uvar.points} * 1.5`

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

* **Available to:** Everyone in the server  
* **Saved:** Permanently in database  
* **Use case:** Server-wide counters, settings, shared data  

**Managing via commands:**  

```
vvar set "welcome_count" 0
vvar set "server_motto" "Be nice!"
vvar get "welcome_count"
vvar del "welcome_count"
```

**Using in rules:**
To add to a counter, use `.set` with `{}` to get the current value first.

```
vrule add if event_type == "member_join" then var.set "welcome_count" {var.welcome_count} + 1; channel.send "Welcome! You're member #{var.welcome_count}!" priority 10 tags []
```

### User Variables (uvar)

User variables are unique to each user. Every user has their own separate copy of each uvar, making them perfect for tracking individual stats.

* **Available to:** Specific user only   
* **Saved:** Per-user, per-server   
* **Use case:** XP systems, currency, personal stats, achievements  

**Managing via commands:**
vuvardex (View your own variables) vuvardex @User (View another user's variables) vvar clearusers (Admin only: Delete ALL user data)

**Example:**
```
vrule add if message.content startswith "!work" then uvar.add coins 10; message.reply "You earned 10 coins! Total: {uvar.coins}" priority 10 tags [economy]
```

Each user has their own `uvar.coins`, `uvar.xp`, etc. User A's coins don't affect User B's coins.

### Temporary Variables (temp)

Temporary variables only exist while a rule is executing. They're perfect for storing intermediate calculations or random values.

* **Available to:** Current rule execution only  
* **Saved:** Deleted after rule finishes  
* **Use case:** Random rolls, calculations, temporary storage  

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

Modules are packages of rules that can be exported and imported. They let you share automation setups with others or move rules between servers. They allow you ti share automation templates with other servers, backup specific rule sets, and istribute pre-made automation packages.

### What are Modules?

A module is a JSON file containing:
- Multiple rules grouped by a tag
- Metadata (name, version, author)
- Optional variables

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

3. The bot sends you a `module_welcome.json` file

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

---

Yes, you absolutely should update the "Examples" section. The current examples use `.add` commands which you deleted from the code, so if a user copies them, **they will fail silently.**

Here is the corrected **Examples** section. It uses the new `.set` syntax with math expressions and includes the quotes around variable names to match your latest code fix.

## Examples

Here are some automation examples you can use and modify.

### Auto-Moderation

**Delete spam (repeated characters):**

```bash
vrule add if message.content matches /(.)\1{10,}/ then message.delete; member.timeout 5 priority 100 tags [automod]

```

Detects when someone types the same character 10+ times in a row.

**Block links (except for admins):**

```bash
vrule add if message.content matches /https?:\/\// and "Admin" not in member.role_names then message.delete; message.reply "No links allowed!" priority 90 tags [automod]

```

Prevents non-admins from posting URLs.

**Auto-ban on bad words:**

```bash
vrule add if message.content matches /(badword1|badword2)/ then message.delete; member.ban priority 100 tags [automod]

```

Replace `badword1|badword2` with your actual filtered words.

### Welcome System

**Welcome new members:**

```bash
vrule add if event_type == "member_join" then channel.send_to "123456:Welcome {member.mention} to the server!"; member.addrole "Member" priority 50 tags [welcome]

```

Replace `123456` with your welcome channel ID.

**Track total joins (Server Variable):**

```bash
vrule add if event_type == "member_join" then var.set "total_joins" {var.total_joins} + 1; channel.send "You're member #{var.total_joins}!" priority 50 tags [welcome]

```

Counts and announces each new member using a global variable.

**Goodbye message:**

```bash
vrule add if event_type == "member_leave" then channel.send_to 123456:"{member.name} has left the server." priority 50 tags [welcome]

```

### Leveling System

**Gain XP on every message:**

```bash
vrule add if event_type == "message" and not member.bot then uvar.set "xp" {uvar.xp} + 5 priority 5 tags [leveling]

```

Award 5 XP for each message (excludes bots). Note the math syntax.

**Level 10 role reward:**

```bash
vrule add if uvar.xp >= 1000 and "Level 10" not in member.role_names then member.addrole "Level 10"; channel.send "🎉 {member.mention} reached Level 10!" priority 20 tags [leveling]

```

Automatically gives role when user hits 1000 XP.

**Check rank command:**

```bash
vrule add if message.content == "!rank" then message.reply "You have {uvar.xp} XP!" priority 10 tags [leveling]

```

### Custom Commands

**Dice roll:**

```bash
vrule add if message.content == "!roll" then temp.set "dice" {random.1-6}; message.reply "🎲 You rolled a {temp.dice}!" priority 10 tags [fun]

```

**Coin flip:**

```bash
vrule add if message.content == "!flip" then temp.set "coin" {random.0-1}; message.reply "{temp.coin} == 0 ? Heads : Tails" priority 10 tags [fun]

```

**Server stats:**

```bash
vrule add if message.content == "!stats" then channel.send "📊 Server: {guild.name}\n👥 Members: {guild.member_count}" priority 10 tags [info]

```

### Reaction Roles

**Give role when reacting with ✅:**

```bash
vrule add if event_type == "reaction_add" and emoji == "✅" then member.addrole "Verified" priority 30 tags [roles]

```

User gets "Verified" role when they react with ✅.

**Remove role when unreacting:**

```bash
vrule add if event_type == "reaction_remove" and emoji == "✅" then member.removerole "Verified" priority 30 tags [roles]

```

### Scheduled Messages

**Morning announcement at 9 AM:**

```bash
vrule add if time.hour == 9 and time.minute == 0 then channel.send "☀️ Good morning everyone!" priority 1 tags [scheduled]

```

**Only on weekends:**

```bash
vrule add if (time.dayofweek == "Saturday" or time.dayofweek == "Sunday") and time.hour == 12 then channel.send "Happy weekend!" priority 1 tags [scheduled]

```

### Advanced: Warnings System

**Track warnings:**

```bash
vrule add if message.content matches /badword/ then message.delete; uvar.set "warnings" {uvar.warnings} + 1; member.dm "Warning {uvar.warnings}/3" priority 100 tags [moderation]

```

Each violation increases user's warning count.

**Auto-ban at 3 warnings:**

```bash
vrule add if uvar.warnings >= 3 then member.ban; channel.send "{member.name} was banned for repeated violations" priority 100 tags [moderation]

```

**Reset User (Unban):**

```bash
vrule add if event_type == "member_unban" then uvar.del "warnings" priority 10 tags [moderation]

```

Clears the warning history when a user is unbanned.

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

vrk
