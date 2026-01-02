
This is a minimalist, professional Markdown structure designed for **GitHub Pages** (or a standard GitHub `README.md`). It uses clear hierarchy, tables for readability, and clean code blocks.

---

# Condition-Action Engine Bot

A powerful Discord automation bot driven by a **Condition-Action Engine**. Intercept events, evaluate custom logic, and execute complex command sequences in real-time.

## 🚀 Quick Start

Rules follow a strict syntax to ensure predictable execution:

```bash
vrule add if <condition> then <action1>; <action2> priority <int> tags [tag1, tag2]

```

* **Condition:** Logic statement that must return `True`.
* **Actions:** Multiple commands separated by `;`.
* **Priority:** Higher integers execute first.
* **Tags:** Metadata for filtering and exporting via `vmodule`.

---

## ⚖️ Logical Operators

Use these within your `if` statements to define trigger logic.

| Operator | Type | Description |
| --- | --- | --- |
| `==` / `!=` | Comparison | Equal to / Not equal to |
| `>` / `<` | Math | Greater than / Less than |
| `startswith` | String | Matches beginning of text |
| `matches` | Regex | Matches a Regular Expression pattern |
| `in` | Collection | Checks if value exists in list/string |
| `and` / `or` | Logic | Combine multiple conditions |
| `not` | Logic | Inverts the boolean result |

---

## 🛠 Action Commands

### Guild & Member Management

* `guild.setname "Name"`: Update server name.
* `role.create "Name"`: Create a new role.
* `member.timeout <mins>`: Timeout a user.
* `member.addrole "Name"`: Assign a role to the user.
* `member.ban`: Permanently ban the user.

### Messaging & Channels

* `channel.purge <int>`: Bulk delete messages.
* `channel.send "text"`: Message the current channel.
* `message.reply "text"`: Reply to the triggering user.
* `message.delete`: Remove the triggering message.
* `reaction.add "emoji"`: React to the message.

### Variable System

| Command | Scope | Description |
| --- | --- | --- |
| `var.set <k> <v>` | Global | Persistent server-wide variable |
| `uvar.set <k> <v>` | User | Persistent user-specific variable |
| `temp.set <k> <v>` | Local | Exists only for current execution |

---

## 🔄 Dynamic Resolvers

Inject real-time data using `{placeholder}` syntax.

* **User:** `{member.mention}`, `{member.id}`, `{member.name}`
* **Server:** `{guild.name}`, `{guild.member_count}`, `{channel.name}`
* **Content:** `{message.content}`, `{event_type}`
* **Logic:** `{var.key}`, `{uvar.key}`, `{random.1-100}`
* **Time:** `{time.hour}`, `{time.date}`, `{time.timestamp}`

---

## 📅 Event Types

Monitor these events by checking `if event_type == 'type'`:
`message` • `message_delete` • `message_edit` • `member_join` • `member_leave` • `reaction_add` • `channel_create` • `voice_update`

---

## 💎 Advanced: Embeds

Pass a dictionary to create rich Discord embeds:

```python
channel.send_embed {
    'title': 'Alert',
    'description': 'Action logged',
    'color': 'FF0000',
    'footer': 'System Engine'
}

```

---

## ⌨️ User Commands

| Command | Description |
| --- | --- |
| `vruledex` | List all active rules. |
| `vrule toggle <id>` | Enable or disable a specific rule. |
| `vmodule export <tag>` | Export rules as a shareable module. |
| `vmodule import` | Install a module from a file attachment. |
| `vvardex` | View all global server variables. |

---

**Would you like me to create a sample "Standard Moderation" module file based on this syntax?**
