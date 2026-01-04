# vrk
**vrk** is a high-performance Discord-Native DSL & IDE that lets you code your own server directly within your server. Its architecture is built with a fully integrated interpreter, allowing for the definition, compilation, and execution of arbitrary logic pipelines at runtime, granting you granular control over the Discord data model via deep object introspection.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Script Structure](#script-structure)
3. [Creating Scripts](#creating-scripts)
4. [Conditions](#conditions)
5. [Actions](#actions)
6. [Variables](#variables)
7. [Dynamic Properties](#dynamic-properties)
8. [Events](#events)
9. [Script Editor](#script-editor)
10. [Commands](#commands)
11. [Import/Export](#importexport)
12. [Examples](#examples)

---

## Getting Started

### What is vrk?

vrk is a scripting engine that lets you automate Discord server actions using conditional logic. Scripts follow an if-then structure where conditions trigger specific actions.

### Your First Script

```lua
vscript create pingpong
if message.content == "ping" then
    message.reply "pong!";
endif priority 10
```

You can also do it in one line:
```
vscript create ping if message.content == "ping" then message.reply "pong!" priority 10
```

**What this does:**
- Listens for messages containing "ping"
- Automatically replies with "pong!"

### Multiple Actions

Chain actions with semicolons (`;`):

```lua
if member.name == "spammer" then
    message.delete;
    member.timeout 60;
endif
```

---

## Script Structure

### Basic Anatomy

Every script has this structure:

```lua
// Optional initialization (runs before condition check)
var count = 0;

if <condition> then
    <action>;
    <action>;
endif
```

**Key Components:**

| Part | Required? | Description |
|------|-----------|-------------|
| Initialization | No | Variable setup before condition evaluation |
| if | Yes | Starts the condition block |
| condition | Yes | Logic that determines when to trigger |
| then | Yes | Separates condition from actions |
| actions | Yes | What the bot should do (semicolon-separated) |
| endif | Yes | Closes the if block |
| priority | No | Execution order (higher = first, default: 0) |

### Hidden Wrapper

When your condition is simply `True`, vrk automatically hides the `if/then/endif` wrapper in the editor view:

```lua
// Instead of showing:
if True then
    channel.send "Always runs!";
endif

// The editor shows just:
channel.send "Always runs!";
```

This makes scripts that should always execute (like scheduled tasks) cleaner to read.

### Priority System

Scripts with higher priority execute first:
- Priority 100 runs before Priority 10
- Same priority = execution by ID order (alphabetical)

### Nested Logic

Scripts support nested if/else blocks:

```lua
if time.hour >= 9 and time.hour < 17 then
    if member.is_admin then
        channel.send "Admin working hours!";
    else
        channel.send "Regular working hours!";
    endif
endif
```

### Comments

Use `//` for single-line comments:

```lua
// This is a comment
var count = 0; // Initialize counter
```

---

## Creating Scripts

### Method 1: Command-Line Creation
```
vscript create <name> if <condition> then <actions> priority <number>
```
**Example Inline:**
```
vscript create welcome if event_type == "member_join" then channel.send "Welcome {member.mention}!" priority 50
```
**Example Codeblock:**
```lua
if event_type == "member_join"
    then channel.send "Welcome {member.mention}!"
endif priority 50
```
Endifs are required in code blocks!

### Method 2: Interactive Editor

```
vscript edit <name>
```

Opens a line-by-line editor where you can:
- Add lines by typing text
- Edit lines: `3 new content` (replace line 3)
- Insert above: `3^ new line` (insert before line 3)
- Insert below: `3. new line` (insert after line 3)
- Delete lines: `3-` (delete line 3)
- Save changes: `save`
- Cancel editing: `exit`

---

## Conditions

### Comparison Operators

| Operator | Example | Description |
|----------|---------|-------------|
| == | message.content == "hello" | Exact match |
| != | channel.name != "general" | Not equal |
| > | guild.member_count > 100 | Greater than |
| < | time.hour < 12 | Less than |
| >= | uvar.level >= 10 | Greater or equal |
| <= | var.warnings <= 3 | Less or equal |

### String Operators

| Operator | Example | Description |
|----------|---------|-------------|
| startswith | message.content startswith "!" | Starts with text |
| endswith | member.name endswith "_bot" | Ends with text |
| in | "Admin" in member.role_names | Contains item |
| not in | "Banned" not in member.role_names | Doesn't contain |
| matches | message.content matches https?:\/\/ | Regex pattern |

> **Note:** When using `matches`, you don't need to wrap the pattern in `/` delimiters. Just use the raw regex pattern.

### Logical Operators

| Operator | Example | Description |
|----------|---------|---------|
| and | time.hour > 9 and time.hour < 17 | Both true |
| or | message.content == "hi" or message.content == "hello" | Either true |
| not | not member.bot | Reverse result |
| ( ) | (A and B) or C | Group conditions |

### Math in Conditions

```lua
if var.points + 10 > 100 then
    channel.send "Milestone!";
endif

if uvar.health - 50 <= 0 then
    member.dm "You died!";
endif
```

---

## Actions

### Message Actions

| Action | Syntax | Example |
|--------|--------|---------|
| channel.send | channel.send "text" | channel.send "Hello!" |
| channel.send_to | channel.send_to "id:text" | channel.send_to "123456:Alert!" |
| channel.send_embed_to | channel.send_embed_to id:{...} | channel.send_embed_to 123:{title: Alert, desc: Important!}" |
| message.reply | message.reply "text" | message.reply "Got it!" |
| message.delete | message.delete | message.delete |
| message.edit | message.edit "text" | message.edit "Updated!" |
| message.pin | message.pin | message.pin |
| message.unpin | message.unpin | message.unpin |

### Webhook Actions

| Action | Syntax | Example |
|--------|--------|---------|
| webhook.send | webhook.send url "text" | webhook.send https://... "Log message" |
| webhook.send_embed | webhook.send_embed url {...} | webhook.send_embed https://... title: Alert |

### Embed Format 

vrk uses this format for embeds, separate properties by commas:

```lua
vscript create voice_log
if voice.joined == True then
    channel.send_embed_to 123456:"{
        title: Voice Entry Detected,
        desc: {member.name} joined {voice.name},
        color: {member.color},
        thumb: {member.avatar_url},
        field1: User ID | {member.id} | true,
        footer: Voice logging
    }"
endif
```

**Supported fields:**
- `title:` - Main heading
- `desc:` or `description:` - Body text
- `color:` - Hex color (0xFF0000 or #FF0000)
- `thumb:` or `thumbnail:` - Small image URL
- `image:` - Large image URL
- `footer:` - Footer text
- `url:` - Title link
- `field1:`, `field2:`, etc. - Fields (format: `name|value|inline`)

**Multi-field example:**
```lua
title: Stats, field1: Level|10|true, field2: XP|1500|true
```

> **Important:** Use `field1:`, `field2:`, `field3:` etc. for multiple fields, not just `field:`.

### Member Actions

| Action | Syntax | Example |
|--------|--------|---------|
| member.timeout | member.timeout minutes | member.timeout 60 |
| member.nickname | member.nickname "name" | member.nickname "NewNick" |
| member.addrole | member.addrole "role" | member.addrole "Member" |
| member.removerole | member.removerole "role" | member.removerole "Trial" |
| member.kick | member.kick | member.kick |
| member.ban | member.ban | member.ban |
| member.unban | member.unban userid | member.unban 123456 |
| member.dm | member.dm "text" | member.dm "Warning!" |

### Channel Actions

| Action | Syntax | Example |
|--------|--------|---------|
| channel.setname | channel.setname "name" | channel.setname "new-name" |
| channel.settopic | channel.settopic "topic" | channel.settopic "Discussion here" |
| channel.settopic_to | channel.settopic_to "id:topic" | channel.settopic_to "123:New topic" |
| channel.setslowmode | channel.setslowmode seconds | channel.setslowmode 10 |
| channel.setnsfw | channel.setnsfw true/false | channel.setnsfw true |
| channel.purge | channel.purge count | channel.purge 10 |
| channel.delete | channel.delete | channel.delete |
| channel.create | channel.create "name" | channel.create "new-chat" |
| channel.create_voice | channel.create_voice "name" | channel.create_voice "Voice 1" |

### Thread Actions

| Action | Syntax | Example |
|--------|--------|---------|
| thread.create | thread.create "name" | thread.create "Discussion" |
| thread.archive | thread.archive | thread.archive |

### Reaction Actions

| Action | Syntax | Example |
|--------|--------|---------|
| reaction.add | reaction.add "emoji" | reaction.add "✅" |
| reaction.remove | reaction.remove "emoji" | reaction.remove "👎" |

### Role Actions

| Action | Syntax | Example |
|--------|--------|---------|
| role.create | role.create "name" | role.create "VIP" |
| role.delete | role.delete "name" | role.delete "Temp" |

### Guild Actions

| Action | Syntax | Example |
|--------|--------|---------|
| guild.setname | guild.setname "name" | guild.setname "New Server" |
| guild.seticon | guild.seticon "url" | guild.seticon "https://..." |

### System Actions

| Action | Syntax | Example |
|--------|--------|---------|
| system.wait | system.wait seconds | system.wait 2 |

---

## Variables

### Variable Types

| Type | Scope | Persistence | Access Syntax |
|------|-------|-------------|---------------|
| var | Server-wide | Permanent | var.name |
| uvar | Per-user | Permanent | uvar.name |
| temp | Script-only | Temporary | temp.name |

### Variable Operations

**Assignment:**
```lua
var count = 0;
uvar xp = 100;
temp roll = {random.1,6};
var enabled = true;  // Boolean support
```

**Supported Data Types:**
- **Integers:** `var count = 10`
- **Floats:** `var ratio = 3.14`
- **Strings:** `var name = "Player"`
- **Booleans:** `var active = true` or `var active = false`

**Math operations:**
```lua
var count += 1;         // Add
uvar health -= 10;      // Subtract
var bonus *= 2;         // Multiply
var average /= 2;       // Divide
var remainder %= 3;     // Modulo
```

**Smart Integer Conversion:**
When doing math, vrk automatically converts `1.0` to `1` to keep integers clean:
```lua
var score = 0;
var score += 1;  // Result: 1 (not 1.0)
```

**Actions (legacy syntax):**
```lua
var.set "count" 0
var.set "count" {var.count} + 1
uvar.set "xp" {uvar.xp} + 10
temp.set "dice" {random.1,6}
```

### Deletion

```lua
var.del "count"
uvar.del "warnings"
uvar.clear  // Wipes ALL user variables
```

### Using Variables in Text

```lua
channel.send "You have {uvar.coins} coins!";
message.reply "Welcome member #{var.total_joins}!";
channel.send "Rolled: {temp.dice}";
```

---

## Dynamic Properties

### Message Properties

| Property | Returns | Description |
|----------|---------|-------------|
| message.content | String | Message text |
| message.author | Member | Message author |
| message.channel | Channel | Where message was sent |
| message.guild | Guild | Server object |
| message.id | Integer | Message ID |
| message.created_at | Datetime | When message was created |
| message.length | Integer | Character count |
| message.word_count | Integer | Number of words |
| message.has_image | Boolean | Has attachments |
| message.has_link | Boolean | Contains "http" |
| message.has_embed | Boolean | Has embeds |
| message.is_reply | Boolean | Is a reply to another message |
| message.is_pinned | Boolean | Message is pinned |
| message.mentions_everyone | Boolean | Has @everyone |
| message.mention_count | Integer | Number of user mentions |

**Example:**
```lua
if message.length > 500 then
    channel.send "That's a long message!";
endif

if message.has_image and not member.is_admin then
    message.delete;
endif
```

### Member Properties

| Property | Returns | Description |
|----------|---------|-------------|
| member.name | String | Username |
| member.display_name | String | Nickname or username |
| member.id | Integer | User ID |
| member.mention | String | Mention tag |
| member.discriminator | String | Tag (e.g., "0001") |
| member.created_at | Datetime | Account creation date |
| member.joined_at | Datetime | Server join date |
| member.bot | Boolean | Is a bot |
| member.role_names | List | All role names |
| member.top_role | String | Highest role name |
| member.color | String | Role color (hex) |
| member.avatar_url | String | Profile picture URL |
| member.is_admin | Boolean | Has administrator permission |
| member.is_mod | Boolean | Has moderation permissions |
| member.is_booster | Boolean | Boosting the server |
| member.boost_months | Integer | Months boosted |
| member.premium_since | Datetime | When they started boosting |
| member.status | String | online/offline/idle/dnd |
| member.activity | String | Current activity name |
| member.is_on_mobile | Boolean | Using mobile app |
| member.age_days | Integer | Days since account creation |
| member.joined_days | Integer | Days since joining server |

**Voice-Specific Properties:**
| Property | Returns | Description |
|----------|---------|-------------|
| member.is_self_muted | Boolean | User muted themselves |
| member.is_server_muted | Boolean | Server muted them |
| member.is_streaming | Boolean | Streaming to voice |
| member.is_video_on | Boolean | Camera is on |

**Examples:**
```lua
if member.is_booster and member.boost_months >= 3 then
    member.addrole "Veteran Booster";
endif

if member.status == "online" and member.is_on_mobile then
    channel.send "{member.name} is on mobile!";
endif
```

### Channel Properties

| Property | Returns | Description |
|----------|---------|-------------|
| channel.name | String | Channel name |
| channel.id | Integer | Channel ID |
| channel.mention | String | Channel mention |
| channel.topic | String | Channel topic |
| channel.created_at | Datetime | When channel was created |
| channel.category_name | String | Parent category name |
| channel.is_nsfw | Boolean | NSFW channel |
| channel.is_news | Boolean | Announcement channel |
| channel.slowmode | Integer | Slowmode delay (seconds) |
| channel.user_limit | Integer | Voice channel user limit |
| channel.bitrate | Integer | Voice channel bitrate |

**Example:**
```lua
if channel.slowmode > 0 then
    channel.send "Slowmode is active ({channel.slowmode}s)";
endif
```

### Guild Properties

| Property | Returns | Description |
|----------|---------|-------------|
| guild.name | String | Server name |
| guild.id | Integer | Server ID |
| guild.owner | Member | Server owner |
| guild.owner_name | String | Owner username |
| guild.owner_id | Integer | Owner user ID |
| guild.member_count | Integer | Total members |
| guild.human_count | Integer | Non-bot members |
| guild.bot_count | Integer | Bot members |
| guild.created_at | Datetime | When server was created |
| guild.created_age | Integer | Days since creation |
| guild.icon | String | Server icon URL |
| guild.boost_count | Integer | Number of boosts |
| guild.boost_tier | Integer | Boost tier (0-3) |
| guild.role_count | Integer | Number of roles |
| guild.channel_count | Integer | Number of channels |
| guild.premium_tier | Integer | Nitro boost level |

**Example:**
```lua
if guild.member_count >= 1000 then
    channel.send "🎉 We hit 1000 members!";
endif
```

### Voice Properties

| Property | Returns | Description |
|----------|---------|-------------|
| voice.name | String | Voice channel name |
| voice.id | Integer | Channel ID |
| voice.user_count | Integer | Total users in channel |
| voice.human_count | Integer | Non-bot users in channel |
| voice.is_full | Boolean | At user limit |
| voice.category_name | String | Parent category name |

**Example:**
```lua
if voice.user_count >= 10 then
    channel.send "Voice channel is getting crowded!";
endif
```

### Time Properties

| Property | Returns | Description |
|----------|---------|-------------|
| time.hour | Integer | Current hour (0-23) |
| time.minute | Integer | Current minute (0-59) |
| time.second | Integer | Current second (0-59) |
| time.day | String | Day name (e.g., "Monday") |
| time.month | String | Month name (e.g., "January") |
| time.year | Integer | Current year |
| time.iso | String | ISO format timestamp |
| time.timestamp | Float | Unix timestamp |

**Example:**
```lua
if time.hour == 9 and time.minute == 0 then
    channel.send "Good morning! ☀️";
endif
```

### Random Values

| Property | Returns | Description |
|----------|---------|-------------|
| random.min,max | Integer | Random number between min and max |

**Example:**
```lua
temp dice = {random.1,6};
channel.send "You rolled: {temp.dice}";
```

---

## Events

### Message Events

| Event | Trigger | Context |
|-------|---------|---------|
| message | User sends message | message, member, channel |
| message_delete | Message deleted | message, member, channel |
| message_edit | Message edited | message, member, channel |

### Member Events

| Event | Trigger | Context |
|-------|---------|---------|
| member_join | User joins server | member, guild |
| member_leave | User leaves server | member, guild |
| member_ban | User banned | member, guild |
| member_unban | User unbanned | member, guild |

### Voice Events

| Event | Trigger | Context |
|-------|---------|---------|
| voice_update | Voice state changes | member, voice, event.joined/left/moved |

**Voice booleans:**
- `event.joined` - True when joining voice
- `event.left` - True when leaving voice
- `event.moved` - True when switching channels
- `event.afk` - True in AFK channel
- `event.muted` - True when muted
- `event.deafened` - True when deafened

### Reaction Events

| Event | Trigger | Context |
|-------|---------|---------|
| reaction_add | Reaction added | emoji, message, member |
| reaction_remove | Reaction removed | emoji, message, member |

### Channel Events

| Event | Trigger | Context |
|-------|---------|---------|
| channel_create | Channel created | channel, guild |
| channel_delete | Channel deleted | channel, guild |

### Guild Events

| Event | Trigger | Context |
|-------|---------|---------|
| guild_update | Server settings changed | guild, old_name, new_name |

---

## Script Editor

### Opening the Editor

```
vscript edit <script_name>
```

### Editor Commands

The editor uses a line-based system:

| Command | Action | Example |
|---------|--------|---------|
| `<text>` | Append new line | `channel.send "Hello";` |
| `3 <text>` | Replace line 3 | `3 channel.send "Updated";` |
| `3^ <text>` | Insert before line 3 | `3^ var count = 0;` |
| `3. <text>` | Insert after line 3 | `3. system.wait 1;` |
| `3-` | Delete line 3 | `3-` |
| `save` | Save and compile | `save` |
| `exit` | Cancel editing | `exit` |

### Editor Example

```
**Editing welcome.vrk** (Buffered Mode)
Type `save` to apply, `exit` to cancel.

 1 if event_type == "member_join" then
 2     var count += 1;
 3     channel.send "Welcome!";
 4 endif
```

**Add a line:**
```
member.addrole "Member";
```

**Result:**
```
 1 if event_type == "member_join" then
 2     var count += 1;
 3     channel.send "Welcome!";
 4     member.addrole "Member";
 5 endif
```

---

## Commands

### Script Commands

| Command | Description |
|---------|-------------|
| `vscript create <name> if ... then ...` | Create new script |
| `vscript edit <name>` | Open interactive editor |
| `vscript del <name>` | Delete script |
| `vscript toggle <name>` | Enable/disable script |
| `vscript clear` | Delete ALL scripts |
| `vcodex [page]` | List all scripts |

### Variable Commands

| Command | Description |
|---------|-------------|
| `vvar set <key> <value>` | Set server variable |
| `vvar get <key>` | Get variable value |
| `vvar del <key>` | Delete variable |
| `vvar clear` | Delete ALL variables |
| `vvardex [page]` | List all server variables |
| `vuvardex [@user] [page]` | View user variables |
| `vuvar set @user <key> <value>` | Set user variable |
| `vuvar get @user <key>` | Get user variable |
| `vuvar del @user <key>` | Delete user variable |

### Debug Commands

| Command | Description |
|---------|-------------|
| `vprint (expression)` | Evaluate and print value |

**Examples:**
```
vprint (member.name)
vprint (var.count + 10)
vprint ({uvar.xp})
```

### Import/Export Commands

| Command | Description |
|---------|-------------|
| `vimport` | Import script from JSON file |
| `vexport <name>` | Export script to JSON file |
| `vbackup` | Backup all scripts |
| `vrestore` | Restore from backup |

---

## Import/Export

### Exporting a Script

```
vexport welcome
```

Creates a JSON file containing:
- Script structure (condition, actions, initialization)
- Metadata (name, version, author, timestamp)
- Optional variables

### Importing a Script

```
vimport
```

Then attach a `.json` file. The bot will:
- Validate the schema
- Add variables (if they don't exist)
- Import scripts with new unique IDs
- Preserve original metadata

### Backup & Restore

**Full backup:**
```
vbackup
```

Downloads ALL scripts as JSON.

**Restore:**
```
vrestore
```

Attach backup file to restore all scripts.

---

## Examples

### Welcome System

```lua
if event_type == "member_join" then
    var total_joins += 1;
    channel.send_to "123456:Welcome {member.mention}! Member #{var.total_joins}";
    member.addrole "Member";
endif
```

### Auto-Moderation

**Spam filter:**
```lua
if message.content matches (.)\1{10,} then
    message.delete;
    member.timeout 5;
endif
```

**Link blocker:**
```lua
if message.content matches https?:\/\/ and "Admin" not in member.role_names then
    message.delete;
    message.reply "No links allowed!";
endif
```

**Long message filter:**
```lua
if message.length > 1000 and not member.is_mod then
    message.delete;
    member.dm "Messages must be under 1000 characters!";
endif
```

### Leveling System

**Gain XP:**
```lua
if event_type == "message" and not member.bot then
    uvar xp += 5;
endif
```

**Level up:**
```lua
if uvar.xp >= 1000 and "Level 10" not in member.role_names then
    member.addrole "Level 10";
    channel.send "🎉 {member.mention} reached Level 10!";
endif
```

**Check rank:**
```lua
if message.content == "!rank" then
    message.reply "You have {uvar.xp} XP!";
endif
```

### Economy System

**Work command:**
```lua
if message.content == "!work" then
    temp earned = {random.10,50};
    uvar coins += {temp.earned};
    message.reply "Earned {temp.earned} coins! Total: {uvar.coins}";
endif
```

**Shop:**
```lua
if message.content == "!buy vip" and uvar.coins >= 1000 then
    uvar coins -= 1000;
    member.addrole "VIP";
    message.reply "Bought VIP for 1000 coins!";
endif
```

### Custom Commands

**Dice roll:**
```lua
if message.content == "!roll" then
    temp dice = {random.1,6};
    message.reply "🎲 You rolled: {temp.dice}";
endif
```

**Server stats:**
```lua
if message.content == "!stats" then
    channel.send "**Server Stats**\nMembers: {guild.member_count}\nHumans: {guild.human_count}\nBots: {guild.bot_count}\nBoosts: {guild.boost_count}";
endif
```

### Reaction Roles

```lua
if event_type == "reaction_add" and emoji == "✅" then
    member.addrole "Verified";
endif

if event_type == "reaction_remove" and emoji == "✅" then
    member.removerole "Verified";
endif
```

### Scheduled Messages

**Morning announcement:**
```lua
if time.hour == 9 and time.minute == 0 then
    channel.send "☀️ Good morning everyone!";
endif
```

**Weekend message:**
```lua
if (time.day == "Saturday" or time.day == "Sunday") and time.hour == 12 then
    channel.send "🎉 Happy weekend!";
endif
```

### Warnings System

**Track warnings:**
```lua
if message.content matches badword then
    message.delete;
    uvar warnings += 1;
    member.dm "⚠️ Warning {uvar.warnings}/3";
endif
```

**Auto-timeout:**
```lua
if uvar.warnings >= 3 then
    member.timeout 60;
    channel.send "🚫 {member.name} timed out for violations.";
endif
```

### Voice Channel Management

**Alert when channel is full:**
```lua
if voice.is_full then
    channel.send "🔊 Voice channel {voice.name} is at capacity!";
endif
```

**Track voice activity:**
```lua
if event.joined then
    var voice_joins += 1;
    channel.send_embed_to 123456:{
        title: Voice Join,
        desc: {member.name} joined {voice.name},
        color: 0x00FF00,
        field1: Total Joins Today | {var.voice_joins} | true
    }
endif
```

### Status-Based Actions

**Welcome active members:**
```lua
if event_type == "member_join" and member.status == "online" then
    channel.send "Welcome {member.mention}! Glad to see you're active! 🟢";
endif
```

**Track mobile users:**
```lua
if event_type == "message" and member.is_on_mobile then
    temp mobile_msg_count += 1;
endif
```
