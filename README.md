# VRK Automation Engine - Complete Documentation

**vrk** is a Discord bot with a programmable automation engine that lets you create complex logic rules with conditions, multiple actions, and persistent variables to automate your server. It can reference all Discord objects including members, channels, messages, roles, and guild properties to create sophisticated automation workflows.

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
11. [FAQ](#faq)

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

**Priority:** A rule with priority 100 will run before a rule with priority 10. Rules with the same priority execute in order of their ID.

**Tags:** Use tags like `[moderation]`, `[welcome]`, `[leveling]` to group related rules for organization and export.

### Rule Limits

- **Maximum rules per server:** 100
- **Maximum condition length:** 2000 characters
- **Maximum action length:** 2000 characters per action
- **Maximum actions per rule:** 10
- **Rule cooldown:** 1 second between triggers of the same rule
- **Burst limit:** 5 rules can fire per second per server

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

**Note:** The `in` operator checks if a string is contained within another string or if an item exists in a list.

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

### Math in Conditions

You can perform mathematical operations in conditions:

```
if var.points + 10 > 100 then channel.send "Milestone reached!"
if uvar.health - 50 <= 0 then member.dm "You died!"
```

**Supported operators:** `+`, `-`, `*`, `/`

---

## Placeholders

Placeholders are dynamic variables that represent data from the event context. Use these keywords to access information about the trigger.

### User Info

Access information about the user who triggered the event.

| Variable | Description | Example Value |
|----------|-------------|---------------|
| member.name | Username | "Cole" |
| member.id | Unique user ID number | 123456789012345678 |
| member.bot | Returns true if user is a bot | true/false |
| member.role_names | List of all role names | ["Admin", "Member"] |
| member.mention | Creates @mention for the user | <@123456789012345678> |
| member.display_name | Server nickname or username | "CoolNick" |
| member.created_at | Account creation timestamp | Discord timestamp object |
| member.joined_at | When member joined server | Discord timestamp object |

### Message Info

Access properties of the message that triggered the rule.

| Variable | Description | Example Value |
|----------|-------------|---------------|
| message.content | The full text of the message | "Hello world!" |
| message.length | Number of characters | 12 |
| message.id | Unique message ID | 987654321098765432 |
| message.jump_url | Direct link to message | https://discord.com/channels/... |
| message.created_at | Message timestamp | Discord timestamp object |

### Channel Info

Information about the current channel.

| Variable | Description | Example Value |
|----------|-------------|---------------|
| channel.name | Name of the channel | "general" |
| channel.id | Unique channel ID | 111222333444555666 |
| channel.mention | Creates #mention for channel | <#111222333444555666> |
| channel.topic | Channel description/topic | "Main chat" |
| channel.category.name | Parent category name | "Text Channels" |

### Server/Guild Info

Check properties of your server.

| Variable | Description | Example Value |
|----------|-------------|---------------|
| guild.name | Server name | "My Server" |
| guild.id | Unique server ID | 777888999000111222 |
| guild.member_count | Total number of members | 150 |
| guild.owner_id | Server owner's user ID | 123456789012345678 |
| guild.description | Server description | "Welcome to our community!" |

### Time Info

Schedule rules based on current time.

| Variable | Description | Example Value |
|----------|-------------|---------------|
| time.hour | Current hour in 24-hour format (0-23) | 14 |
| time.minute | Current minute (0-59) | 30 |
| time.dayofweek | Day name | "Monday" |
| time.date | Current date (YYYY-MM-DD) | "2024-01-15" |
| time.timestamp | Unix timestamp | 1705334400.0 |

### Random Values

Generate random numbers for games and variety.

| Variable | Description | Example |
|----------|-------------|---------|
| {random.1-6} | Random number in range | Generates 1-6 |
| {random.1-100} | Random number 1 to 100 | Generates 1-100 |
| {random.-10-10} | Can use negative ranges | Generates -10 to 10 |

### Variables

Reference stored data (see [Variables](#variables) section for details).

| Variable | Scope | Description |
|----------|-------|-------------|
| var.name | Global | Server-wide variable (accessible to everyone) |
| uvar.name | User | User-specific variable (unique per user) |
| temp.name | Local | Temporary variable (exists only during rule execution) |

### Advanced Properties

vrk supports accessing properties directly from the Discord.py library. For complete lists of available attributes:

- [Message Properties](https://discordpy.readthedocs.io/en/stable/api.html#discord.Message)
- [Member Properties](https://discordpy.readthedocs.io/en/stable/api.html#discord.Member)
- [Guild Properties](https://discordpy.readthedocs.io/en/stable/api.html#discord.Guild)
- [Channel Properties](https://discordpy.readthedocs.io/en/stable/api.html#discord.TextChannel)
- [Reaction Properties](https://discordpy.readthedocs.io/en/stable/api.html#discord.Reaction)
- [Role Properties](https://discordpy.readthedocs.io/en/stable/api.html#discord.Role)

**Examples:**
- `member.premium_since` - When user started boosting
- `channel.slowmode_delay` - Current slowmode seconds
- `guild.premium_tier` - Server boost level

---

## Events

Events are discrete actions or changes that occur within a Discord server. They represent specific triggers that the bot can respond to. Use the `event_type` variable in your conditions to target specific triggers.

### Message Events

Triggered by activity in text channels.

| Event | Trigger | Context Variables |
|-------|---------|-------------------|
| message | When a user sends a message | message.content, message.id, message.author.bot, member.name, channel.name, channel.topic |
| message_delete | When a message is deleted | message.content (if cached), message.id, message.created_at, channel.name |
| message_edit | When a message is edited | message.content (new text), message.id, message.jump_url, member.name |

**Example:**
```
vrule add if event_type == "message" and message.content startswith "!" then channel.send "Command detected!" priority 10 tags []
```

### Member Events

Covers users joining, leaving, or having their roles and nicknames updated.

| Event | Trigger | Context Variables |
|-------|---------|-------------------|
| member_join | When someone joins the server | member.name, member.id, member.created_at, guild.member_count, guild.owner_id |
| member_leave | When someone leaves the server | member.name, member.id, member.joined_at, guild.member_count |
| member_update | When roles or nickname change | nick_changed, old_nick, new_nick, added_roles, removed_roles, member.roles |
| member_ban | When a user is banned | member.name, member.id, member.discriminator |
| member_unban | When a user is unbanned | member.name, member.id |

**Example:**
```
vrule add if event_type == "member_join" then channel.send "Welcome {member.mention}!" priority 50 tags [welcome]
```

### Voice Events

Tracks user activity in voice channels.

| Event | Trigger | Context Variables |
|-------|---------|-------------------|
| voice_update | When a user's voice state changes | voice.joined, voice.left, voice.moved, voice.channel_name, member.voice.self_mute |

**Special voice booleans:**
- `voice.joined` - True when user joins a voice channel
- `voice.left` - True when user leaves a voice channel
- `voice.moved` - True when user switches voice channels

**Example:**
```
vrule add if event_type == "voice_update" and voice.joined then channel.send "{member.name} joined {voice.channel_name}" priority 10 tags []
```

### Reaction Events

Triggered when members add or remove reactions.

| Event | Trigger | Context Variables |
|-------|---------|-------------------|
| reaction_add | When a reaction is added | emoji, message.id, message.content, member.name, reaction.count |
| reaction_remove | When a reaction is removed | emoji, message.id, message.channel.id, member.name |

**Example:**
```
vrule add if event_type == "reaction_add" and emoji == "✅" then member.addrole "Verified" priority 30 tags [roles]
```

### Server/Guild Events

Covers changes to channels or server settings.

| Event | Trigger | Context Variables |
|-------|---------|-------------------|
| channel_create | When a new channel is created | channel.name, channel.id, channel.category.name, guild.name |
| channel_delete | When a channel is deleted | channel.name, channel.id, channel.position |
| guild_update | When server settings are changed | name_changed, icon_changed, old_name, new_name, guild.description, guild.premium_subscription_count |

**Example:**
```
vrule add if event_type == "channel_create" then channel.send_to "123456:New channel created: {channel.name}" priority 10 tags []
```

---

## Actions

Actions are what the bot does when a rule triggers. You can send messages, modify users, manage channels, and more.

### Messaging Actions

Control how and where the bot sends messages.

| Action | Syntax | Example | What it does |
|--------|--------|---------|--------------|
| channel.send | channel.send "text" | channel.send "Hello everyone!" | Send message to current channel |
| channel.send_to | channel.send_to "id:text" | channel.send_to "123456:Alert!" | Send message to specific channel by ID |
| channel.send_embed | channel.send_embed "dict" | channel.send_embed "{'title': 'Alert', 'description': 'Important!', 'color': 0xFF0000}" | Send rich embed to current channel |
| channel.send_embed_to | channel.send_embed_to "id:dict" | channel.send_embed_to "123456:{'title': 'Alert', 'color': 0x00FF00}" | Send embed to specific channel by ID |
| message.reply | message.reply "text" | message.reply "Got it!" | Reply directly to the user's message |
| message.delete | message.delete | message.delete | Delete the message that triggered the rule |

**Getting Channel IDs:**
1. Enable Developer Mode in Discord (Settings → Advanced → Developer Mode)
2. Right-click any channel
3. Select "Copy ID"

**Embed Format:**
Embeds use Python dictionary syntax with these fields:
- `title` - Main heading (string)
- `description` - Body text (string)
- `color` - Hex color code (e.g., 0xFF0000 for red)
- `image` - Image URL (string)
- `thumbnail` - Small image URL (string)
- `footer` - Footer text (string)

**Embed Example:**
```
channel.send_embed "{'title': 'Server Rules', 'description': '1. Be respectful\n2. No spam', 'color': 0x0099FF, 'footer': 'Updated 2024'}"
```

### Member Actions

Moderate and manage server members.

| Action | Syntax | Example | What it does |
|--------|--------|---------|--------------|
| member.timeout | member.timeout minutes | member.timeout 60 | Timeout user for X minutes (mutes them) |
| member.nickname | member.nickname "name" | member.nickname "NewNick" | Change user's server nickname |
| member.addrole | member.addrole "role" | member.addrole "Member" | Give user a role by name |
| member.removerole | member.removerole "role" | member.removerole "Trial" | Remove a role from user |
| member.kick | member.kick | member.kick | Remove user from server (can rejoin) |
| member.ban | member.ban | member.ban | Permanently ban user from server |
| member.unban | member.unban userid | member.unban 123456789 | Unban user by their ID |
| member.dm | member.dm "text" | member.dm "Warning: Stop spamming" | Send private message to user |

**Note:** Timeout duration is in minutes. The bot must have appropriate permissions to perform moderation actions.

### Reaction Actions

Add or remove emoji reactions.

| Action | Syntax | Example | What it does |
|--------|--------|---------|--------------|
| reaction.add | reaction.add "emoji" | reaction.add "👀" | Add emoji reaction to message |
| reaction.remove | reaction.remove "emoji" | reaction.remove "👎" | Remove all instances of emoji from message |

**Note:** Use standard Unicode emojis. Custom server emojis may require special formatting.

### Channel Management

Modify channel settings and structure.

| Action | Syntax | Example | What it does |
|--------|--------|---------|--------------|
| channel.setname | channel.setname "name" | channel.setname "new-chat" | Rename the current channel |
| channel.settopic | channel.settopic "text" | channel.settopic "Chat here" | Change channel description/topic |
| channel.setslowmode | channel.setslowmode seconds | channel.setslowmode 5 | Set slowmode delay in seconds |
| channel.setnsfw | channel.setnsfw bool | channel.setnsfw true | Mark channel as NSFW (true/false) |
| channel.purge | channel.purge count | channel.purge 10 | Bulk delete last X messages |
| channel.create | channel.create "name" | channel.create "new-channel" | Create new text channel |
| channel.delete | channel.delete | channel.delete | Delete the current channel |

**Warning:** `channel.delete` is permanent! The bot cannot delete the server's system channel.

### Role Management

Create and delete roles.

| Action | Syntax | Example | What it does |
|--------|--------|---------|--------------|
| role.create | role.create "name" | role.create "VIP" | Create a new role with the given name |
| role.delete | role.delete "name" | role.delete "Temporary" | Delete a role by name |

### Guild Management

Modify server-level settings.

| Action | Syntax | Example | What it does |
|--------|--------|---------|--------------|
| guild.setname | guild.setname "name" | guild.setname "New Server Name" | Rename the server |
| guild.seticon | guild.seticon "url" | guild.seticon "https://example.com/icon.png" | Change server icon (provide image URL) |

### Message Management

Pin and unpin messages.

| Action | Syntax | Example | What it does |
|--------|--------|---------|--------------|
| message.pin | message.pin | message.pin | Pin message to channel |
| message.unpin | message.unpin | message.unpin | Unpin message from channel |

### System Actions

Control rule execution flow.

| Action | Syntax | Example | What it does |
|--------|--------|---------|--------------|
| system.wait | system.wait seconds | system.wait 2 | Pause for X seconds before next action |

**Note:** Use `system.wait` to create delays between actions, useful for timed sequences.

### Variable Actions

Store and manipulate persistent data. **Important:** To perform math operations, use `{}` to retrieve the current value first.

| Action | Syntax | Example | What it does |
|--------|--------|---------|--------------|
| var.set | var.set "key" value | var.set "counter" 0 | Set a global server variable |
| var.del | var.del "key" | var.del "counter" | Delete a global server variable |
| uvar.set | uvar.set "key" value | uvar.set "xp" 100 | Set a user-specific variable |
| uvar.del | uvar.del "key" | uvar.del "warnings" | Delete a specific user variable |
| uvar.clear | uvar.clear | uvar.clear | **Hard Reset:** Wipes ALL variables for that user |
| temp.set | temp.set "key" value | temp.set "roll" {random.1-6} | Set temporary variable (rule-scoped only) |

**Math Operations:**

To modify existing numeric variables, use `{}` to get the current value:

```
uvar.set "coins" {uvar.coins} + 10        (Add 10 coins)
uvar.set "hp" {uvar.hp} - 5               (Subtract 5 HP)
uvar.set "bonus" {uvar.points} * 1.5      (Multiply by 1.5)
var.set "total" {var.count} / 2           (Divide by 2)
```

**Supported Data Types:**
- **Numbers:** Integers and floats (`0`, `100`, `3.14`)
- **Strings:** Text in quotes (`"hello"`, `"user_data"`)
- **Lists:** Arrays in brackets (`[1, 2, 3]`, `["a", "b"]`)
- **Dictionaries:** JSON objects (`{"key": "value", "count": 5}`)

**Setting Complex Data:**
```
var.set "config" {"enabled": true, "limit": 100}
var.set "items" ["sword", "shield", "potion"]
```

---

## Variables

Variables let you store persistent data that your rules can read and modify. There are three types of variables, each with different scopes and lifespans.

### Server Variables (var)

Server variables are shared across your entire Discord server. Anyone can trigger rules that use them, and they persist forever unless deleted.

**Properties:**
- **Scope:** Everyone in the server
- **Persistence:** Permanent (saved to database)
- **Use case:** Server-wide counters, settings, shared data

**Managing via Commands:**

```
vvar set "welcome_count" 0
vvar set "server_motto" "Be nice!"
vvar get "welcome_count"
vvar del "welcome_count"
vvar clear  (Admin only - deletes all server variables)
vvardex [page]  (List all server variables)
```

**Using in Rules:**

```
vrule add if event_type == "member_join" then var.set "welcome_count" {var.welcome_count} + 1; channel.send "Welcome! You're member #{var.welcome_count}!" priority 10 tags []
```

**Accessing in Conditions:**
```
if var.max_warnings >= 3 then member.ban
if var.event_mode == "true" then channel.send "Event is active!"
```

### User Variables (uvar)

User variables are unique to each user. Every user has their own separate copy of each uvar, making them perfect for tracking individual stats.

**Properties:**
- **Scope:** Specific user only
- **Persistence:** Per-user, per-server (saved to database)
- **Use case:** XP systems, currency, personal stats, achievements

**Managing via Commands:**

```
vuvardex              (View your own variables)
vuvardex @Username    (View another user's variables)
```

**Note:** Server administrators can use `vvar clear` to delete ALL user data if needed.

**Using in Rules:**

```
vrule add if message.content startswith "!work" then uvar.set "coins" {uvar.coins} + 10; message.reply "You earned 10 coins! Total: {uvar.coins}" priority 10 tags [economy]
```

**Key Concept:** Each user has their own `uvar.coins`, `uvar.xp`, etc. User A's coins don't affect User B's coins. The data is automatically isolated per user.

**Example XP System:**
```
# Gain XP
vrule add if event_type == "message" and not member.bot then uvar.set "xp" {uvar.xp} + 5 priority 5 tags [leveling]

# Level up at 1000 XP
vrule add if uvar.xp >= 1000 and "Level 10" not in member.role_names then member.addrole "Level 10"; channel.send "🎉 {member.mention} reached Level 10!" priority 20 tags [leveling]

# Check rank
vrule add if message.content == "!rank" then message.reply "You have {uvar.xp} XP!" priority 10 tags [leveling]
```

**Deleting User Data:**
```
# Delete specific variable
vrule add if message.content == "!resetwarnings" then uvar.del "warnings"; message.reply "Warnings cleared!" priority 10 tags []

# Wipe all user data (nuclear option)
vrule add if message.content == "!resetme" then uvar.clear; message.reply "All your data has been wiped!" priority 10 tags []
```

### Temporary Variables (temp)

Temporary variables only exist while a rule is executing. They're perfect for storing intermediate calculations or random values.

**Properties:**
- **Scope:** Current rule execution only
- **Persistence:** Deleted immediately after rule finishes
- **Use case:** Random rolls, calculations, temporary storage

**Example:**

```
vrule add if message.content == "!roll" then temp.set "dice" {random.1-6}; message.reply "You rolled: {temp.dice}" priority 10 tags [fun]
```

**Use Cases:**
- Storing random values for use in multiple actions
- Intermediate calculations
- Temporary flags within a rule

**Note:** `temp` variables cannot be accessed by other rules, even if they trigger immediately after. Each rule execution has its own isolated temp scope.

### Using Variables in Text

You can insert variable values into messages using curly braces `{variable}`:

```
channel.send "Welcome {member.name}! We now have {guild.member_count} members."
message.reply "You have {uvar.coins} coins and {uvar.xp} XP!"
channel.send "Server record: {var.highest_score} points"
```

**Dynamic Variables:**
- `{member.mention}` - Creates @mention for the user
- `{channel.mention}` - Creates #mention for the channel
- `{random.1-100}` - Generates random number between 1-100
- `{time.hour}` - Current hour
- `{var.name}` - Your custom server variable
- `{uvar.name}` - User's variable value
- `{temp.name}` - Temporary variable (within same rule)

### Variable Storage Details

**Database Storage:**
- All `var` and `uvar` data is stored in MySQL database
- Data persists through bot restarts
- Automatic backup every 5 minutes
- Data saved on bot shutdown

**Data Structure:**
```json
{
  "guild_id": "123456789",
  "welcome_count": 50,
  "max_warnings": 3,
  "users": {
    "user_id_1": {
      "xp": 1500,
      "coins": 250,
      "warnings": 1
    },
    "user_id_2": {
      "xp": 3000,
      "coins": 500
    }
  }
}
```

---

## Modules

Modules are packages of rules that can be exported and imported. They let you share automation templates with other servers, backup specific rule sets, and distribute pre-made automation packages.

### What are Modules?

A module is a JSON file containing:
- Multiple rules grouped by a tag
- Metadata (name, version, author)
- Optional variables

**Module Structure:**
```json
{
  "meta": {
    "name": "welcome",
    "version": "1.0",
    "author": "ServerAdmin",
    "exported_at": "2024-01-15 10:30:00"
  },
  "variables": {},
  "rules": [
    {
      "condition": "event_type == 'member_join'",
      "actions": ["channel.send 'Welcome!'"],
      "priority": 50,
      "tags": ["welcome"]
    }
  ]
}
```

### Exporting a Module

Export creates a portable file containing all rules with a specific tag.

**Steps:**

1. Add tags to your rules when creating them:
```
vrule add if event_type == "member_join" then channel.send "Welcome!" priority 50 tags [welcome]
vrule add if event_type == "member_leave" then channel.send "Goodbye!" priority 50 tags [welcome]
```

2. Export all rules with that tag:
```
vmodule export welcome
```

3. The bot sends you a `module_welcome.json` file

**What gets exported:**
- All rules tagged with the specified tag
- Rule conditions, actions, priorities
- Metadata (module name, version, author, timestamp)
- Structure ready for import

**Example Use Cases:**
- Share your leveling system with other servers
- Create template packs for common automation tasks
- Backup specific features separately

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

**Import Process:**
- Module file is validated for security
- Variables are added (only if they don't already exist)
- Rules are given new unique IDs
- Original tags are preserved, plus a `module:name` tag is added
- All rules are enabled by default

**Safety Features:**
- Schema validation prevents malicious code
- Invalid rules are rejected
- Existing variables are not overwritten
- Import report shows what was added

**Example Import Output:**
```
Module Installed: welcome v1.0
Added 3 Rules and 2 Variables.
```

### Backup & Restore

Create full backups of ALL your server's rules, not just tagged ones.

**Backup Everything:**
```
vmodule backup
```
Downloads a complete snapshot of ALL rules in your server.

**Restore from Backup:**
```
vmodule restore
```
Attach the backup file. All rules are re-imported with new IDs.

**Important:**
- Always backup before using `vrule clear` or making major changes!
- Backups include ALL rules, regardless of tags
- Restore creates new rule IDs (doesn't overwrite existing rules)
- Backup files are timestamped for version control

**Backup Filename Format:**
```
backup_<guild_id>_<timestamp>.json
```

Example: `backup_123456789012345678_1705334400.json`

**Use Cases:**
- Before making experimental changes
- Migrating to a new server
- Creating save points during development
- Disaster recovery

---

## Commands

All commands that modify rules or variables require **Administrator permission**.

### Rule Commands

Manage your automation rules.

| Command | What it does | 
|---------|--------------|
| vrule add if ... then ... | Create a new automation rule |
| vrule <id> | View full details of a specific rule |
| vrule del <id> | Delete a rule permanently |
| vrule toggle <id> | Enable or disable a rule without deleting |
| vrule clear | Delete ALL rules in the server |
| vruledex [page] | List all rules with pagination (10 per page) |

**Examples:**
```
vrule 5                    (View rule #5)
vrule del 5                (Delete rule #5)
vrule toggle 5             (Disable/enable rule #5)
vruledex                   (Show page 1)
vruledex 2                 (Show page 2)
```

**Note:** Rule IDs are assigned automatically and shown in `vruledex`. IDs are unique and permanent within a server.

### Variable Commands

Manage server-wide variables directly.

| Command | What it does |  
|---------|--------------|
| vvar set <name> <value> | Create or update a server variable |
| vvar get <name> | Retrieve variable value (or download as JSON if large) |
| vvar del <name> | Delete a server variable |
| vvar clear | Delete ALL server variables |
| vvardex [page] | List all variables with pagination |
| vuvardex | View your own user variables |
| vuvardex @User | View another user's variables |

**Examples:**
```
vvar set "counter" 0
vvar set "motd" "Welcome to the server!"
vvar set "config" {"enabled": true, "limit": 100}
vvar get "counter"
vvardex
vvardex 2
vuvardex
vuvardex @JohnDoe
```

**Note:** Large variables (>1900 characters) are automatically sent as downloadable JSON files.

### Module Commands

Import, export, and backup rule collections.

| Command | What it does | 
|---------|--------------|
| vmodule import | Install module from attached JSON file | 
| vmodule export <tag> | Create module containing all rules with tag |
| vmodule backup | Create full backup of all server rules |
| vmodule restore | Restore rules from backup file |

**Examples:**
```
vmodule export welcome
vmodule import        (attach file in same message)
vmodule backup
vmodule restore       (attach file in same message)
```

---

## Examples

Here are automation examples you can copy and modify for your server.

### Auto-Moderation

**Delete spam (repeated characters):**
```
vrule add if message.content matches /(.)\1{10,}/ then message.delete; member.timeout 5 priority 100 tags [automod]
```
Detects when someone types the same character 10+ times in a row, deletes the message, and times them out for 5 minutes.

**Block links (except for admins):**
```
vrule add if message.content matches /https?:\/\// and "Admin" not in member.role_names then message.delete; message.reply "No links allowed!" priority 90 tags [automod]
```
Prevents non-admins from posting URLs.

**Auto-ban on bad words:**
```
vrule add if message.content matches /(badword1|badword2)/i then message.delete; member.ban priority 100 tags [automod]
```
Replace `badword1|badword2` with your actual filtered words. The `/i` flag makes it case-insensitive.

**Mention spam protection:**
```
vrule add if message.content matches /@everyone|@here/ and "Moderator" not in member.role_names then message.delete; uvar.set "warnings" {uvar.warnings} + 1; member.dm "Warning: Don't spam mentions!" priority 100 tags [automod]
```

### Welcome System

**Welcome new members:**
```
vrule add if event_type == "member_join" then channel.send_to "123456:Welcome {member.mention} to the server! 🎉"; member.addrole "Member" priority 50 tags [welcome]
```
Replace `123456` with your welcome channel ID.

**Track total joins:**
```
vrule add if event_type == "member_join" then var.set "total_joins" {var.total_joins} + 1; channel.send "You're member #{var.total_joins}!" priority 50 tags [welcome]
```
Counts and announces each new member using a global variable.

**Goodbye message:**
```
vrule add if event_type == "member_leave" then channel.send_to "123456:{member.name} has left the server. We now have {guild.member_count} members." priority 50 tags [welcome]
```

**Rich welcome embed:**
```
vrule add if event_type == "member_join" then channel.send_embed "{'title': 'Welcome!', 'description': '{member.mention} just joined!', 'color': 0x00FF00, 'footer': 'Member #{guild.member_count}'}" priority 50 tags [welcome]
```

### Leveling System

**Gain XP on every message:**
```
vrule add if event_type == "message" and not member.bot then uvar.set "xp" {uvar.xp} + 5 priority 5 tags [leveling]
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

**Multiple level tiers:**
```
vrule add if uvar.xp >= 5000 and "Level 50" not in member.role_names then member.addrole "Level 50"; channel.send "🏆 {member.mention} is now Level 50!" priority 20 tags [leveling]

vrule add if uvar.xp >= 10000 and "Level 100" not in member.role_names then member.addrole "Level 100"; channel.send "⭐ {member.mention} reached Level 100! Legendary!" priority 20 tags [leveling]
```

### Custom Commands

**Dice roll:**
```
vrule add if message.content == "!roll" then temp.set "dice" {random.1-6}; message.reply "🎲 You rolled a {temp.dice}!" priority 10 tags [fun]
```

**Coin flip:**
```
vrule add if message.content == "!flip" then temp.set "coin" {random.0-1}; message.reply "🪙 Result: heads" priority 10 tags [fun]

vrule add if message.content == "!flip" then temp.set "coin" {random.0-1}; message.reply "🪙 Result: tails" priority 9 tags [fun]
```
Note: Use two rules with different priorities to simulate 50/50 chance.

**Server stats:**
```
vrule add if message.content == "!stats" then channel.send "📊 **Server Stats**\nName: {guild.name}\n👥 Members: {guild.member_count}" priority 10 tags [info]
```

**User info:**
```
vrule add if message.content startswith "!userinfo" then message.reply "**User Info**\nName: {member.name}\nID: {member.id}\nJoined: {member.joined_at}" priority 10 tags [info]
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

**Multiple reaction roles:**
```
vrule add if event_type == "reaction_add" and emoji == "🎮" then member.addrole "Gamer" priority 30 tags [roles]

vrule add if event_type == "reaction_add" and emoji == "🎨" then member.addrole "Artist" priority 30 tags [roles]

vrule add if event_type == "reaction_add" and emoji == "📚" then member.addrole "Reader" priority 30 tags [roles]
```

### Scheduled Messages

**Morning announcement at 9 AM:**
```
vrule add if time.hour == 9 and time.minute == 0 then channel.send "☀️ Good morning everyone!" priority 1 tags [scheduled]
```

**Only on weekends:**
```
vrule add if (time.dayofweek == "Saturday" or time.dayofweek == "Sunday") and time.hour == 12 then channel.send "🎉 Happy weekend!" priority 1 tags [scheduled]
```

**Daily reminder:**
```
vrule add if time.hour == 18 and time.minute == 0 then channel.send_to "123456:📢 Daily reminder: Check the announcements!" priority 1 tags [scheduled]
```

### Advanced: Warnings System

**Track warnings:**
```
vrule add if message.content matches /badword/ then message.delete; uvar.set "warnings" {uvar.warnings} + 1; member.dm "⚠️ Warning {uvar.warnings}/3: Please follow server rules!" priority 100 tags [moderation]
```
Each violation increases user's warning count and sends them a DM.

**Auto-timeout at 3 warnings:**
```
vrule add if uvar.warnings >= 3 then member.timeout 60; channel.send "🚫 {member.name} has been timed out for repeated violations." priority 100 tags [moderation]
```

**Reset warnings on unban:**
```
vrule add if event_type == "member_unban" then uvar.del "warnings" priority 10 tags [moderation]
```
Clears the warning history when a user is unbanned.

**Manual warning command:**
```
vrule add if message.content startswith "!warn" and "Moderator" in member.role_names then uvar.set "warnings" {uvar.warnings} + 1 priority 50 tags [moderation]
```

### Economy System

**Work command:**
```
vrule add if message.content == "!work" then temp.set "earned" {random.10-50}; uvar.set "coins" {uvar.coins} + {temp.earned}; message.reply "💼 You worked and earned {temp.earned} coins! Total: {uvar.coins}" priority 10 tags [economy]
```

**Balance check:**
```
vrule add if message.content == "!balance" then message.reply "💰 You have {uvar.coins} coins!" priority 10 tags [economy]
```

**Shop system:**
```
vrule add if message.content == "!buy vip" and uvar.coins >= 1000 then uvar.set "coins" {uvar.coins} - 1000; member.addrole "VIP"; message.reply "✅ You bought VIP for 1000 coins!" priority 10 tags [economy]
```

### Voice Activity Tracking

**Announce voice joins:**
```
vrule add if event_type == "voice_update" and voice.joined then channel.send_to "123456:🎤 {member.name} joined {voice.channel_name}" priority 10 tags [voice]
```

**Track voice time:**
```
vrule add if event_type == "voice_update" and voice.joined then uvar.set "voice_sessions" {uvar.voice_sessions} + 1 priority 10 tags [voice]
```

### Anti-Raid Protection

**Kick new accounts (less than 7 days old):**
```
vrule add if event_type == "member_join" and member.created_at > time.timestamp - 604800 then member.kick; channel.send "🛡️ Blocked new account: {member.name}" priority 100 tags [security]
```

**Auto-ban raid bots:**
```
vrule add if event_type == "member_join" and member.bot and "Admin" not in member.role_names then member.ban priority 100 tags [security]
```

---

## FAQ

**Q: Can I have multiple conditions?**  
A: Yes! Use `and`, `or`, and parentheses to create complex logic:
```
if (A and B) or (C and D) then ...
if time.hour >= 9 and time.hour < 17 and not member.bot then ...
```

**Q: How do I mention a user in a message?**  
A: Use `{member.mention}` in your text:
```
channel.send "Hello {member.mention}!"
message.reply "{member.mention}, you have {uvar.coins} coins!"
```

**Q: Can rules trigger other rules?**  
A: Yes, if one rule's action creates an event that matches another rule's condition, the second rule will trigger. For example:
- Rule A sends a message
- Rule B triggers on any message
- Rule B will see Rule A's message

**Q: How do I find a channel ID?**  
A: 
1. Enable Developer Mode in Discord (Settings → Advanced → Developer Mode)
2. Right-click any channel
3. Select "Copy ID"
4. Use this ID in commands like `channel.send_to "ID:message"`

**Q: Why isn't my rule working?**  
A: Check these common issues:
- Is it enabled? Use `vrule toggle <id>` to check
- Verify syntax with `vrule <id>` to see if it was parsed correctly
- Wait 1 second between tests (rules have cooldowns)
- Check `vruledex` to confirm rule exists and priority is correct
- Look at bot logs for error messages
- Test conditions individually to isolate the problem
- Make sure you have the required permissions

**Q: Can I undo vrule clear?**  
A: Only if you ran `vmodule backup` first. **Always backup before clearing!** There is no undo function.

**Q: How many rules can I have?**  
A: Maximum 100 rules per server. This limit prevents performance issues.

**Q: Do variables persist after bot restart?**  
A: Yes! Server variables (`var`) and user variables (`uvar`) are saved to the database and persist permanently. The bot auto-saves every 5 minutes and on shutdown. Only `temp` variables are cleared after each rule execution.

**Q: Can I use math in conditions?**  
A: Yes! Example:
```
if var.points + 10 > 100 then ...
if uvar.health - 50 <= 0 then ...
if guild.member_count * 2 > 1000 then ...
```

**Q: What happens if two rules have the same priority?**  
A: They execute in order of their rule ID (lower IDs first). Use different priorities to control execution order explicitly.

**Q: How do rate limits work?**  
A: 
- Each rule has a 1-second cooldown before it can trigger again
- Maximum 5 rules can fire per second per server (burst limit)
- This prevents infinite loops and performance issues

**Q: Can I export rules to use in another bot?**  
A: Modules are specific to vrk's format. You can share modules with other servers using vrk, but not with different bots.

**Q: How do I debug a complex rule?**  
A: 
1. Break it into smaller rules first
2. Use `channel.send` actions to print variable values
3. Test conditions one at a time
4. Check the bot logs for parsing errors
5. Use `vrule <id>` to verify how the rule was interpreted

**Q: What's the difference between `==` and `in`?**  
A: 
- `==` checks exact equality: `message.content == "hello"`
- `in` checks if something is contained: `"Mod" in member.role_names`

**Q: Can I use regex in conditions?**  
A: Yes! Use the `matches` operator:
```
if message.content matches /https?:\/\// then ...
if member.name matches /^[A-Z]/ then ...
```

**Q: How do I reset all user data?**  
A: Individual users can use `uvar.clear` in a rule. Admins can use `vvar clear` to wipe everything including all user data.

**Q: Do user variables transfer to other servers?**  
A: No. User variables are per-server. The same user will have different `uvar` data in different servers.

**Q: Can I create custom commands with arguments?**  
A: Not directly, but you can use `startswith` to detect command prefixes:
```
if message.content startswith "!say " then channel.send "{message.content}"
```

**Q: What permissions does the bot need?**  
A: The bot needs permissions for the actions it performs:
- **Moderate Members** for timeouts/bans
- **Manage Channels** for channel edits
- **Manage Roles** for role assignments
- **Send Messages** for messaging actions
- **Manage Messages** for deleting/pinning messages

**Q: Can I see who created a rule?**  
A: No, rules don't track creators. Use module metadata or external documentation to track authorship.

**Q: How do I prevent infinite loops?**  
A: 
- Avoid rules that trigger themselves
- Use the 1-second cooldown to your advantage
- Add conditions like `not member.bot` to exclude bot messages
- Use specific event types instead of general conditions

**Q: What's the maximum message length for actions?**  
A: Discord limits messages to 2000 characters. The bot will not send messages longer than this.

**Q: Can I use variables in embed fields?**  
A: Yes! Variables are substituted before the embed is created:
```
channel.send_embed "{'title': 'Stats', 'description': '{member.name} has {uvar.xp} XP'}"
```

---

## Technical Details

### Performance & Limits

- **Message cache:** 1000 most recent messages cached for deleted message events
- **Rule execution:** Asynchronous, non-blocking
- **Database:** MySQL with connection pooling
- **Auto-save interval:** Every 5 minutes
- **Rate limiting:** Per-guild token bucket system

### Security Features

- **Input sanitization:** All user inputs are sanitized
- **Command validation:** Only whitelisted commands are allowed
- **Module validation:** Strict schema validation on imports
- **Permission checks:** Admin-only for destructive operations
- **Execution depth limit:** Maximum 20 levels of nested condition parsing

### Database Schema

**guild_data table:**
- `guild_id` (VARCHAR PRIMARY KEY)
- `data` (JSON) - Contains all server and user variables

**guild_rules table:**
- `guild_id` (VARCHAR PRIMARY KEY)
- `rules` (JSON) - Contains all automation rules

### Logging

All significant events are logged to `bot.log`:
- Rule triggers and executions
- Database operations
- Errors and exceptions
- Rate limit hits

---

**vrk Automation Engine** - Built for powerful, flexible Discord server automation.
