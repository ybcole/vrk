# vrk Bot

**Automate your Discord server with powerful condition-action rules.**

---

## 📋 Table of Contents

1. [Getting Started](#-getting-started)
2. [Creating Rules](#-creating-rules)
3. [Conditions](#-conditions)
4. [Actions](#-actions)
5. [Variables](#-variables)
6. [Modules](#-modules)
7. [Commands](#-commands)
8. [Examples](#-examples)

---

## 🚀 Getting Started

### What is VRK Automation?

VRK is a Discord bot that lets you create **custom automation rules** using simple if-then logic:

```
if <something happens> then <do something>
```

### Your First Rule

```
vrule add if message.content == "ping" then message.reply "pong!" priority 10 tags []
```

**What this does:**
- When someone types "ping"
- The bot replies "pong!"

---

## 📐 Creating Rules

### Basic Syntax

```
vrule add if <condition> then <action> priority <number> tags [tag1, tag2]
```

| Part | Required? | What it does |
|------|-----------|--------------|
| `if` | Yes | Starts the condition |
| `<condition>` | Yes | When to trigger |
| `then` | Yes | Separates condition from actions |
| `<action>` | Yes | What to do |
| `priority` | No | Higher = runs first (default: 0) |
| `tags` | No | Labels for organizing |

### Multiple Actions

Separate actions with semicolons (`;`):

```
vrule add if member.name == "spammer" then message.delete; member.timeout 60 priority 100 tags [moderation]
```

---

## ⚖️ Conditions

### Comparison Operators

| Operator | Example | Explanation |
|----------|---------|-------------|
| `==` | `message.content == "hello"` | Exact match |
| `!=` | `channel.name != "general"` | Not equal |
| `>` | `guild.member_count > 100` | Greater than |
| `<` | `time.hour < 12` | Less than |
| `>=` | `uvar.level >= 10` | Greater or equal |
| `<=` | `var.warnings <= 3` | Less or equal |

### String Checks

| Operator | Example | Explanation |
|----------|---------|-------------|
| `startswith` | `message.content startswith "!"` | Begins with |
| `endswith` | `member.name endswith "_bot"` | Ends with |
| `in` | `"Moderator" in member.role_names` | Contains |
| `matches` | `message.content matches /https?:\/\//` | Regex pattern |

### Combining Conditions

| Operator | Example | Explanation |
|----------|---------|-------------|
| `and` | `time.hour > 9 and time.hour < 17` | Both must be true |
| `or` | `message.content == "hi" or message.content == "hello"` | Either can be true |
| `not` | `not member.bot` | Reverses the result |
| `( )` | `(A and B) or C` | Group conditions |

### What You Can Check

#### User Info
- `member.name` - Username (e.g., "JohnDoe")
- `member.id` - User ID number
- `member.bot` - Is this a bot? (true/false)
- `member.role_names` - List of roles they have

#### Message Info
- `message.content` - What they typed
- `message.length` - How many characters

#### Server Info
- `guild.name` - Server name
- `guild.member_count` - Total members
- `channel.name` - Channel name

#### Time Info
- `time.hour` - Current hour (0-23)
- `time.minute` - Current minute (0-59)
- `time.dayofweek` - Day name (Monday, Tuesday, etc.)

#### Event Info
- `event_type` - What happened (message, member_join, etc.)

#### Variables
- `var.name` - Server variable
- `uvar.name` - User variable
- `temp.name` - Temporary variable (only in current rule)

---

## 🛠 Actions

### Messaging

| Action | Example | What it does |
|--------|---------|--------------|
| `channel.send` | `channel.send "Hello everyone!"` | Send message in current channel |
| `channel.send_to` | `channel.send_to 123456:"Alert!"` | Send to specific channel ID |
| `message.reply` | `message.reply "Got it!"` | Reply to the user |
| `message.delete` | `message.delete` | Delete the message |

### Member Actions

| Action | Example | What it does |
|--------|---------|--------------|
| `member.timeout` | `member.timeout 60` | Timeout for X minutes |
| `member.nickname` | `member.nickname "NewName"` | Change their nickname |
| `member.addrole` | `member.addrole "Member"` | Give them a role |
| `member.removerole` | `member.removerole "Trial"` | Take away a role |
| `member.kick` | `member.kick` | Kick from server |
| `member.ban` | `member.ban` | Ban from server |
| `member.dm` | `member.dm "Warning: Stop spamming"` | Send private message |

### Reactions

| Action | Example | What it does |
|--------|---------|--------------|
| `reaction.add` | `reaction.add "✅"` | React with emoji |
| `reaction.remove` | `reaction.remove "❌"` | Remove all of that emoji |

### Channel Management

| Action | Example | What it does |
|--------|---------|--------------|
| `channel.setname` | `channel.setname "new-name"` | Rename channel |
| `channel.settopic` | `channel.settopic "Chat here"` | Change description |
| `channel.setslowmode` | `channel.setslowmode 5` | Set slowmode (seconds) |
| `channel.purge` | `channel.purge 10` | Delete last X messages |
| `channel.create` | `channel.create "new-channel"` | Create text channel |
| `channel.delete` | `channel.delete` | Delete current channel |

### Variables

| Action | Example | What it does |
|--------|---------|--------------|
| `var.set` | `var.set counter 0` | Set server variable |
| `var.add` | `var.add points 10` | Increase by amount |
| `var.del` | `var.del temp` | Delete variable |
| `uvar.set` | `uvar.set xp 100` | Set user variable |
| `uvar.add` | `uvar.add coins 50` | Increase user variable |
| `uvar.sub` | `uvar.sub health 10` | Decrease user variable |
| `temp.set` | `temp.set result 42` | Set temporary variable |

### Other

| Action | Example | What it does |
|--------|---------|--------------|
| `system.wait` | `system.wait 2` | Wait X seconds before next action |
| `message.pin` | `message.pin` | Pin the message |

---

## 📊 Variables

### Server Variables (var)

**Available to:** Everyone in the server  
**Saved:** Forever (until deleted)

```
vvar set welcome_count 0
vvar set server_motto "Be nice!"
vvar get welcome_count
vvar del welcome_count
```

Use in rules:
```
vrule add if event_type == "member_join" then var.add welcome_count 1; channel.send "Welcome! You're member #{var.welcome_count}!" priority 10 tags []
```

### User Variables (uvar)

**Available to:** Specific user  
**Saved:** Per-user, per-server

```
vrule add if message.content startswith "!work" then uvar.add coins 10; message.reply "You earned 10 coins! Total: {uvar.coins}" priority 10 tags [economy]
```

Each user has their own `uvar.coins`, `uvar.xp`, etc.

### Temporary Variables (temp)

**Available to:** Only during the current rule execution  
**Saved:** Deleted after rule finishes

```
vrule add if message.content == "!roll" then temp.set dice {random.1-6}; message.reply "You rolled: {temp.dice}" priority 10 tags [fun]
```

### Using Variables in Text

Put variable names in `{curly braces}`:

```
channel.send "Welcome {member.name}! We now have {guild.member_count} members."
```

Special variables:
- `{member.mention}` - @mentions the user
- `{channel.mention}` - #mentions the channel
- `{random.1-100}` - Random number between 1-100
- `{time.hour}` - Current hour
- `{var.name}` - Your custom variable

---

## 📦 Modules

### What are Modules?

Modules let you **export and import** groups of rules to share with others or move between servers.

### Exporting a Module

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

### Importing a Module

1. Get a module file (from someone else or your export)
2. Run:
```
vmodule import
```
3. Attach the JSON file
4. Rules are installed with new IDs (won't conflict with existing rules)

### Backup & Restore

**Backup everything:**
```
vmodule backup
```
Downloads ALL your server's rules.

**Restore from backup:**
```
vmodule restore
```
Attach the backup file. All rules are re-imported.

---

## ⌨️ Commands

### Rule Commands

| Command | What it does | Permission |
|---------|--------------|------------|
| `vrule add if ... then ...` | Create a new rule | Admin |
| `vrule <id>` | View a rule's details | Anyone |
| `vrule del <id>` | Delete a rule | Admin |
| `vrule toggle <id>` | Enable/disable a rule | Admin |
| `vrule clear` | Delete ALL rules | Admin |
| `vruledex` | List all rules (10 per page) | Anyone |
| `vruledex 2` | Show page 2 of rules | Anyone |

### Variable Commands

| Command | What it does | Permission |
|---------|--------------|------------|
| `vvar set <name> <value>` | Create/update variable | Admin |
| `vvar get <name>` | See variable value | Admin |
| `vvar del <name>` | Delete variable | Admin |
| `vvar clear` | Delete ALL variables | Admin |
| `vvardex` | List all variables | Admin |

### Module Commands

| Command | What it does | Permission |
|---------|--------------|------------|
| `vmodule import` | Install module (attach file) | Admin |
| `vmodule export <tag>` | Create module from tag | Admin |
| `vmodule backup` | Backup all rules | Admin |
| `vmodule restore` | Restore from backup | Admin |

### Help

| Command | What it does |
|---------|--------------|
| `vhelp` | Interactive help menu |

---

## 💡 Examples

### Auto-Moderation

**Delete spam:**
```
vrule add if message.content matches /(.)\1{10,}/ then message.delete; member.timeout 5 priority 100 tags [automod]
```

**Block links (except for admins):**
```
vrule add if message.content matches /https?:\/\// and "Admin" not in member.role_names then message.delete; message.reply "No links allowed!" priority 90 tags [automod]
```

**Auto-ban on bad words:**
```
vrule add if message.content matches /(badword1|badword2)/ then message.delete; member.ban priority 100 tags [automod]
```

### Welcome System

**Welcome new members:**
```
vrule add if event_type == "member_join" then channel.send_to 123456:"Welcome {member.mention} to the server!"; member.addrole "Member" priority 50 tags [welcome]
```

**Track total joins:**
```
vrule add if event_type == "member_join" then var.add total_joins 1; channel.send "You're member #{var.total_joins}!" priority 50 tags [welcome]
```

**Goodbye message:**
```
vrule add if event_type == "member_leave" then channel.send_to 123456:"{member.name} has left the server." priority 50 tags [welcome]
```

### Leveling System

**Gain XP on every message:**
```
vrule add if event_type == "message" and not member.bot then uvar.add xp 5 priority 5 tags [leveling]
```

**Level 10 role reward:**
```
vrule add if uvar.xp >= 1000 and "Level 10" not in member.role_names then member.addrole "Level 10"; channel.send "🎉 {member.mention} reached Level 10!" priority 20 tags [leveling]
```

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

**Auto-ban at 3 warnings:**
```
vrule add if uvar.warnings >= 3 then member.ban; channel.send "{member.name} was banned for repeated violations" priority 100 tags [moderation]
```

---

## ❓ FAQ

**Q: Can I have multiple conditions?**  
A: Yes! Use `and`, `or`, and parentheses:
```
if (A and B) or (C and D) then ...
```

**Q: How do I mention a user in a message?**  
A: Use `{member.mention}`:
```
channel.send "Hello {member.mention}!"
```

**Q: Can rules trigger other rules?**  
A: Yes, if one rule's action creates an event that matches another rule's condition.

**Q: How do I find a channel ID?**  
A: Enable Developer Mode in Discord → Right-click channel → Copy ID

**Q: Why isn't my rule working?**  
A: Check these:
- Is it enabled? (`vrule toggle <id>`)
- Check spelling: `vrule <id>`
- Wait 1 second between tests (cooldown)
- Check `vruledex` to see if it's listed

**Q: Can I undo `vrule clear`?**  
A: Only if you ran `vmodule backup` first. Always backup before clearing!

**Q: How many rules can I have?**  
A: Maximum 100 rules per server.

---

## 🆘 Need Help?

- Run `vhelp` for the interactive help menu
- Check your rule with `vrule <id>`
- List all rules with `vruledex`
- Test conditions one at a time
- Make backups with `vmodule backup`

---

**Happy Automating! 🚀**
