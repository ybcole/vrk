import discord
from discord.ext import commands, tasks
import json

# IMPORTS

import re
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
import logging
from dotenv import load_dotenv
from asyncio import Lock
import io
import aiomysql
import random
import ast
import operator

# LOGIC ENGINE

class SafeLogicEngine(ast.NodeVisitor):
    def __init__(self, context_resolver, context_data):
        self.resolver = context_resolver 
        self.context = context_data      
        self.safe_operators = {
            # MATH
            ast.Add: operator.add, ast.Sub: operator.sub,
            ast.Mult: operator.mul, ast.Div: operator.truediv, 
            ast.Mod: operator.mod, ast.Pow: operator.pow,
            
            # COMPARISON
            ast.Eq: operator.eq, ast.NotEq: operator.ne,
            ast.Lt: operator.lt, ast.LtE: operator.le,
            ast.Gt: operator.gt, ast.GtE: operator.ge,
            # LOGIC
            ast.In: lambda x, y: x in y,
            ast.NotIn: lambda x, y: x not in y,
            ast.Not: operator.not_, ast.USub: operator.neg,
        }

    def evaluate(self, expression: str):
        """Entry point: Parses string -> AST -> Result"""
        if not expression or not expression.strip():
            return False
        try:
            node = ast.parse(str(expression), mode='eval')
            return self.visit(node.body)
        except Exception as e:
            return False

    def visit_Constant(self, node):
        return node.value

    def visit_Name(self, node):
        return self._resolve(node.id)

    def visit_Attribute(self, node):
        full_path = self._get_full_attr_name(node)
        return self._resolve(full_path)

    def _get_full_attr_name(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_full_attr_name(node.value)}.{node.attr}"
        return ""

    def _resolve(self, path):
        val = self.resolver(path, self.context)
        if isinstance(val, str):
            if val.lower() == "true": return True
            if val.lower() == "false": return False
            try:
                if '.' in val: return float(val)
                return int(val)
            except ValueError:
                return val
        return val

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_type = type(node.op)
        
        if op_type in self.safe_operators:
            return self.safe_operators[op_type](left, right)
        raise ValueError(f"Unsafe operation: {op_type}")

    def visit_Compare(self, node):
        left = self.visit(node.left)
        
        for op, comparator in zip(node.ops, node.comparators):
            right = self.visit(comparator)
            op_type = type(op)
            
            if op_type in self.safe_operators:
                if not self.safe_operators[op_type](left, right):
                    return False
            else:
                raise ValueError(f"Unknown comparison: {op_type}")
        return True

    def visit_BoolOp(self, node):
        if isinstance(node.op, ast.And):
            return all(self.visit(v) for v in node.values)
        elif isinstance(node.op, ast.Or):
            return any(self.visit(v) for v in node.values)
        return False

    def visit_UnaryOp(self, node):
        val = self.visit(node.operand)
        op_type = type(node.op)
        if op_type in self.safe_operators:
            return self.safe_operators[op_type](val)
        raise ValueError(f"Unsafe unary op: {op_type}")
        

class ScriptParser:
    def parse(self, raw_text: str) -> List[Any]:
        # Use raw_text directly to preserve comments
        clean_text = raw_text
        
        tokens = []
        current_token = []
        in_quotes = False
        brace_level = 0 

        # Tokenizer
        for char in clean_text:
            if char == '"':
                in_quotes = not in_quotes
            elif char == '{' and not in_quotes:
                brace_level += 1
            elif char == '}' and not in_quotes:
                brace_level -= 1
            
            # Split on semicolons or newlines
            if (char == ';' or char == '\n') and not in_quotes and brace_level <= 0:
                t = "".join(current_token).strip()
                if t: tokens.append(t)
                current_token = []
            else:
                current_token.append(char)
        
        # Catch the last token
        last_t = "".join(current_token).strip()
        if last_t: tokens.append(last_t)

        # Logic Construction
        root = []
        stack = [(root, None)]
        
        for token in tokens:
            current_list = stack[-1][0]
            low_token = token.lower().strip()
            
            if low_token.startswith("if "):
                # Extract condition
                cond_part = token[3:].strip()
                if ' then' in cond_part.lower():
                    cond = re.split(r'(?i)\s+then', cond_part)[0].strip()
                else:
                    cond = cond_part
                
                if_node = {"type": "if", "condition": cond, "then": [], "else": []}
                current_list.append(if_node)
                stack.append((if_node['then'], if_node))
            
            elif low_token == "else":
                if len(stack) > 1:
                    parent = stack[-1][1]
                    stack.pop()
                    stack.append((parent['else'], parent))

            elif low_token == "endif":
                if len(stack) > 1: 
                    stack.pop()
                else:
                    current_list.append("endif")
            
            else:
                # Includes comments
                current_list.append(token)
                
        return root


class LineEditor:
    @staticmethod
    def apply_edit(current_source: str, edit_cmd: str) -> str:
        lines = current_source.split('\n')
        
        # Preserve indentation by eating max 1 space/tab
        match = re.match(r'^(\d+)([\^\.\-]?)[ \t]?(.*)$', edit_cmd.strip(), re.DOTALL)
        
        if not match:
            return None

        line_num = int(match.group(1))
        operator = match.group(2)
        content = match.group(3)
        idx = line_num - 1
        
        # Validation
        if idx < 0: return current_source
        if idx >= len(lines) and operator != '.': return current_source

        if operator == '^':
            lines.insert(idx, content)
        elif operator == '.':
            lines.insert(idx + 1, content)
        elif operator == '-':
            if 0 <= idx < len(lines): del lines[idx]
        else:
            lines[idx] = content

        return "\n".join(lines)

    @staticmethod
    def render_with_numbers(source: str) -> str:
        lines = source.split('\n')
        pad = len(str(len(lines))) 
        return "\n".join(f"{str(i).rjust(pad)} {line}" for i, line in enumerate(lines, 1))
    

load_dotenv()

REGEX_VAR_SUB = re.compile(r'\{([a-zA-Z0-9_.\-,\s]+)\}')
REGEX_RANDOM = re.compile(r'-?\d+')


# DATABASE

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

pool = None
server_variables = {}
automation_scripts = {} 
guild_locks: Dict[str, Lock] = {}
dirty_guilds = set()
editing_sessions: Dict[int, Dict[str, Any]] = {}  


async def init_db():
    global pool
    try:
        pool = await aiomysql.create_pool(
            host=DB_HOST, port=DB_PORT,
            user=DB_USER, password=DB_PASS,
            db=DB_NAME, autocommit=True
        )
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS guild_data (
                        guild_id VARCHAR(30) PRIMARY KEY,
                        data JSON
                    )
                """)
                await cur.execute("""
                    CREATE TABLE IF NOT EXISTS guild_scripts (
                        guild_id VARCHAR(30) PRIMARY KEY,
                        scripts JSON
                    )
                """)
        logger.info("Connected to Cloud Database (MySQL)!")
    except Exception as e:
        logger.error(f"Database Connection Failed: {e}")

        
# SECURITY AND LOGGING

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AutomationBot')


# VALIDATION

VALID_OPERATORS = [
    '==', '!=', '>', '<', '>=', '<=', 'matches', 'startswith', 'endswith', 'in', 'not in'
]
VALID_COMMANDS = [
    'channel.setname', 'channel.settopic', 'channel.settopic_to', 'channel.setslowmode', 'channel.setnsfw', 
    'channel.send', 'channel.send_to', 'channel.send_embed', 'channel.send_embed_to', 'channel.purge', 'channel.delete', 'channel.create', 'channel.create_voice',
    'webhook.send', 'webhook.send_embed',
    'message.delete', 'message.reply', 'message.pin', 'message.unpin', 'message.edit',
    'thread.create', 'thread.archive', 'thread.join',
    'reaction.add', 'reaction.remove',
    'member.timeout', 'member.nickname', 'member.addrole', 'member.removerole', 
    'member.kick', 'member.ban', 'member.unban', 'member.dm',
    'role.create', 'role.delete', 
    'guild.setname', 'guild.seticon',
    'system.wait',
    'var.set', 'var.del', 'var.push', 'var.remove',
    'uvar.set', 'uvar.del', 'temp.set',
    'print'
]


# BOT CONFIG

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='v', intents=intents, help_command=None)


# CONFIG

MAX_CACHE_SIZE = 1000
message_cache: Dict[int, discord.Message] = {}
script_cooldowns: Dict[tuple, datetime] = {} 
guild_rate_limits: Dict[str, Dict[str, float]] = {}
COOLDOWN_SECONDS = 0.5 
BURST_LIMIT = 20 
MAX_SCRIPTS = 100
MAX_CONDITION_LENGTH = 4000
MAX_ACTION_LENGTH = 4000
MAX_ACTIONS_PER_SCRIPT = 50


# HELPER FUNCTIONS

def detect_type(value: str) -> Any:
    """Convert string to appropriate Python type"""
    v = value.strip().strip('"\'')
    if v.lower() == "true": return True
    if v.lower() == "false": return False
    try:
        if '.' in v: return float(v)
        return int(v)
    except ValueError:
        return v


# DATABASE LOGIC

async def load_variables(guild_id: str):
    if not pool: return
    
    if guild_id not in guild_locks:
        guild_locks[guild_id] = Lock()     
        
    async with guild_locks[guild_id]:
        try:
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT data FROM guild_data WHERE guild_id = %s", (guild_id,))
                    result = await cur.fetchone()
                    if result:
                        data = result[0]
                        if isinstance(data, str):
                            server_variables[guild_id] = json.loads(data)
                        else:
                            server_variables[guild_id] = data
                    else:
                        server_variables[guild_id] = {}
        except Exception as e:
            logger.error(f"Failed to load variables for {guild_id}: {e}")
            server_variables[guild_id] = {}


async def save_variables(guild_id: str):
    if not pool: return

    if guild_id not in guild_locks:
        guild_locks[guild_id] = Lock()

    async with guild_locks[guild_id]: 
        try:
            data_json = json.dumps(server_variables.get(guild_id, {}))
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("""
                        INSERT INTO guild_data (guild_id, data) 
                        VALUES (%s, %s) 
                        ON DUPLICATE KEY UPDATE data = %s
                    """, (guild_id, data_json, data_json))
        except Exception as e:
            logger.error(f"Failed to save {guild_id}: {e}")


async def load_scripts(guild_id: str, force_reload: bool = False):
    if not pool: return
    
    if not force_reload and guild_id in automation_scripts and automation_scripts[guild_id]:
        return
    
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT scripts FROM guild_scripts WHERE guild_id = %s", (guild_id,))
                result = await cur.fetchone()
                
                if result:
                    data = result[0]
                    raw_scripts = json.loads(data) if isinstance(data, str) else data
                    if isinstance(raw_scripts, list):
                        valid_scripts = [r for r in raw_scripts if validate_script_structure(r)]
                        valid_scripts.sort(key=lambda r: (-r.get('priority', 0), r['id']))
                        automation_scripts[guild_id] = valid_scripts
                    else:
                        automation_scripts[guild_id] = []
                else:
                    automation_scripts[guild_id] = []
                    
    except Exception as e:
        logger.error(f"DB Load Rules Error: {e}")
        automation_scripts[guild_id] = []

        
def validate_script_structure(script: Dict[str, Any]) -> bool:
    try:
        if not isinstance(script, dict): return False
        required_fields = ['id', 'condition', 'actions', 'enabled']
        if not all(field in script for field in required_fields): return False
        
        if not isinstance(script['actions'], list): return False

        for action in script['actions']:
            if not isinstance(action, (str, dict)): return False
            
        return True
    except Exception:
        return False


async def save_scripts(guild_id: str):
    if not pool: return
    try:
        scripts_data = json.dumps(automation_scripts.get(guild_id, []))
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("""
                    INSERT INTO guild_scripts (guild_id, scripts) 
                    VALUES (%s, %s) 
                    ON DUPLICATE KEY UPDATE scripts = %s
                """, (guild_id, scripts_data, scripts_data))
        logger.info(f"Saved scripts to DB for {guild_id}")
    except Exception as e:
        logger.error(f"DB Save Rules Error: {e}")


def sanitize_input(text: str, max_length: int = 500) -> str:
    if not isinstance(text, str): return ""
    text = text[:max_length]
    text = ''.join(ch for ch in text if ch.isprintable() or ch in '\n\r\t')
    return text.strip()


def prettify_ast_numbered(condition: str, actions: List[Any], initialization: List[Any] = None) -> List[str]:
    lines = []
    if initialization:
        for item in initialization:
            if isinstance(item, str):
                if item.strip().startswith('//'):
                    lines.append(item)
                else:
                    clean = re.sub(r'^(var|uvar|temp)\s+(\w+)\s+(=|\+=|-=|\*=|/=|%=)\s*(.*)$', r'\1 \2 \3 \4', item)
                    lines.append(f"{clean};")
    
    if condition != "True":
        lines.append(f"if {condition} then")
    
    def format_actions(action_list: List[Any], indent: int = 1):
        result = []
        for item in action_list:
            spacing = "    " * indent
            if isinstance(item, str):
                if item.strip().startswith('//'):
                    result.append(f"{spacing}{item}")
                else:
                    clean = re.sub(r'^(var|uvar|temp)\.set\s+"?(\w+)"?\s+(.*)$', r'\1 \2 = \3', item)
                    result.append(f"{spacing}{clean};")
            elif isinstance(item, dict) and item.get('type') == 'if':
                result.append(f"{spacing}if {item['condition']} then")
                result.extend(format_actions(item['then'], indent + 1))
                if item['else']:
                    result.append(f"{spacing}else")
                    result.extend(format_actions(item['else'], indent + 1))
                result.append(f"{spacing}endif")
        return result
    
    start_indent = 1 if condition != "True" else 0
    lines.extend(format_actions(actions, indent=start_indent))
    
    if condition != "True":
        lines.append("endif")
    
    return lines


def check_rate_limit(guild_id: str, script_id: int) -> bool:
    now = datetime.now().timestamp()
    key = (guild_id, script_id)
    
    if key in script_cooldowns:
        last_run = script_cooldowns[key].timestamp()
        if now - last_run < COOLDOWN_SECONDS:
            return False

    if guild_id not in guild_rate_limits:
        guild_rate_limits[guild_id] = {"tokens": BURST_LIMIT, "last_update": now}
    
    bucket = guild_rate_limits[guild_id]
    time_passed = now - bucket["last_update"]
    bucket["tokens"] = min(float(BURST_LIMIT), bucket["tokens"] + time_passed)
    bucket["last_update"] = now
    
    if bucket["tokens"] >= 1.0:
        bucket["tokens"] -= 1.0 
        return True
    else:
        logger.warning(f"Rate limit hit for guild {guild_id}. Tokens: {bucket['tokens']:.2f}")
        return False
    

def confirm_execution(guild_id: str, script_id: int):
    script_cooldowns[(guild_id, script_id)] = datetime.now()
    if guild_id in guild_rate_limits:
        bucket = guild_rate_limits[guild_id]
        bucket["tokens"] = max(0.0, bucket["tokens"] - 1.0)
        

def set_cooldown(guild_id: str, script_id: int):
    script_cooldowns[(guild_id, script_id)] = datetime.now()
    

def validate_module_schema(data: Dict[str, Any]) -> bool:
    required_keys = {'meta', 'scripts', 'variables'}
    if not all(key in data for key in required_keys): 
        return False
    if not isinstance(data['meta'], dict): return False
    if 'name' not in data['meta'] or 'version' not in data['meta']: return False
    if not isinstance(data['variables'], dict): return False
    if not isinstance(data['scripts'], list): return False
    
    for r in data['scripts']:
        test_script = {
            'id': 0, 
            'condition': r.get('condition', ''),
            'actions': r.get('actions', []),
            'enabled': True
        }
        if not validate_script_structure(test_script):
            return False
            
    return True


# DYNAMIC RESOLVER

def resolve_dynamic_value(path: str, context: Dict[str, Any]) -> Any:
    now = context.get('now') or discord.utils.utcnow()
    guild = context.get('guild')
    member = context.get('member') 
    message = context.get('message')
    channel = context.get('channel')
    voice_obj = context.get('voice') 

    # MESSAGES
    if path == 'message.length': 
        return len(message.content) if message else 0
    if path == 'message.word_count': 
        return len(message.content.split()) if message else 0
    if path == 'message.has_image': 
        return bool(message.attachments) if message else False
    if path == 'message.has_link': 
        return "http" in message.content if message else False
    if path == 'message.has_embed': 
        return bool(message.embeds) if message else False
    if path == 'message.is_reply': 
        return bool(message.reference) if message else False
    if path == 'message.is_pinned': 
        return message.pinned if message else False
    if path == 'message.mentions_everyone': 
        return message.mention_everyone if message else False
    if path == 'message.mention_count': 
        return len(message.mentions) if message else 0

    # MEMBERS
    if path == 'member.role_names': 
        return [r.name for r in member.roles] if member and hasattr(member, 'roles') else []
    if path == 'member.top_role': 
        return member.top_role.name if member and hasattr(member, 'top_role') else "None"
    if path == 'member.color': 
        return str(member.color) if member else "#000000"
    if path == 'member.is_admin': 
        return member.guild_permissions.administrator if member else False
    if path == 'member.is_mod': 
        p = member.guild_permissions
        return (p.ban_members or p.kick_members or p.manage_messages) if member else False
    if path == 'member.is_booster': 
        return bool(member.premium_since) if member else False
    if path == 'member.boost_months':
        if member and member.premium_since:
            return int((now - member.premium_since).days / 30)
        return 0
    if path == 'member.status': 
        return str(member.status) if member and hasattr(member, 'status') else "offline"
    if path == 'member.activity': 
        return member.activity.name if member and member.activity else "None"
    if path == 'member.is_on_mobile': 
        return member.is_on_mobile() if member and hasattr(member, 'is_on_mobile') else False
    if path == 'member.is_bot':
        return member.bot if member else False
    if path == 'member.avatar_url': 
        return str(member.display_avatar.url) if member else ""

    # CHANNELS
    if path == 'channel.category_name': 
        return channel.category.name if channel and getattr(channel, 'category', None) else "None"
    if path == 'channel.is_nsfw': 
        return channel.nsfw if channel and hasattr(channel, 'nsfw') else False
    if path == 'channel.is_news': 
        return channel.is_news() if channel and hasattr(channel, 'is_news') else False
    if path == 'channel.slowmode': 
        return channel.slowmode_delay if channel and hasattr(channel, 'slowmode_delay') else 0
    if path == 'channel.user_limit': 
        return channel.user_limit if channel and hasattr(channel, 'user_limit') else 0
    if path == 'channel.bitrate': 
        return channel.bitrate if channel and hasattr(channel, 'bitrate') else 0
    
    # GUILD
    if path == 'guild.owner_name': 
        return guild.owner.name if guild and guild.owner else "Unknown"
    if path == 'guild.owner_id': 
        return str(guild.owner_id) if guild else "0"
    if path == 'guild.boost_count': 
        return guild.premium_subscription_count if guild else 0
    if path == 'guild.boost_tier': 
        return guild.premium_tier if guild else 0
    if path == 'guild.human_count': 
        return len([m for m in guild.members if not m.bot]) if guild else 0
    if path == 'guild.bot_count': 
        return len([m for m in guild.members if m.bot]) if guild else 0
    if path == 'guild.role_count': 
        return len(guild.roles) if guild else 0
    if path == 'guild.channel_count': 
        return len(guild.channels) if guild else 0
    if path == 'guild.created_age': 
        return (now - guild.created_at).days if guild else 0

    # VOICE STATUS
    if path == 'voice.user_count':
        return len(voice_obj.members) if voice_obj else 0
    if path == 'voice.human_count':
        return len([m for m in voice_obj.members if not m.bot]) if voice_obj else 0
    if path == 'voice.is_full':
        if voice_obj and voice_obj.user_limit != 0:
            return len(voice_obj.members) >= voice_obj.user_limit
        return False
    if path == 'voice.category_name':
        return voice_obj.category.name if voice_obj and voice_obj.category else "None"

    # VOICE STATE
    if path == 'member.is_self_muted':
        return member.voice.self_mute if member and member.voice else False
    if path == 'member.is_server_muted':
        return member.voice.mute if member and member.voice else False
    if path == 'member.is_streaming':
        return member.voice.self_stream if member and member.voice else False
    if path == 'member.is_video_on':
        return member.voice.self_video if member and member.voice else False

    # VOICE EVENT STATUS
    if path in ['voice.joined', 'voice.left', 'voice.moved']:
        return context.get('event', {}).get(path.split('.')[1], False)

    # TIMES
    if path == 'time.hour': return now.hour
    if path == 'time.minute': return now.minute
    if path == 'time.second': return now.second
    if path == 'time.day': return now.strftime('%A')
    if path == 'time.month': return now.strftime('%B')
    if path == 'time.year': return now.year
    if path == 'time.iso': return now.isoformat()
    if path == 'time.timestamp': return now.timestamp()

    # VARIABLES
    if path.startswith('temp.'): 
        return context.get('temp_vars', {}).get(path.split('.', 1)[1], 0)
    if path.startswith('var.'):
        val = server_variables.get(str(guild.id if guild else 0), {}).get(path.split('.', 1)[1], 0)
        return val
    if path.startswith('uvar.'): 
        return server_variables.get(str(guild.id if guild else 0), {}).get('users', {}).get(str(member.id if member else 0), {}).get(path.split('.', 1)[1], 0)
    if path in ['added_roles', 'removed_roles']:
        val = context.get(path, [])
        return ", ".join(val) if val else "None"

    if member:
        if path == 'member.age_days': return (now - member.created_at).days
        if path == 'member.joined_days': return (now - member.joined_at).days if member.joined_at else 0

    if path.startswith('random.'):
        try:
            param_str = path.split('.', 1)[1]
            if ',' in param_str:
                parts = param_str.split(',')
                val_a = int(parts[0].strip())
                val_b = int(parts[1].strip())
                return random.randint(min(val_a, val_b), max(val_a, val_b))
        except: 
            return 0

    parts = path.split('.')
    root_key = parts[0]
    current_obj = context.get(root_key)
    
    if current_obj is None and root_key not in ['member', 'guild', 'channel', 'message', 'emoji', 'voice', 'before', 'after', 'event']: 
        return path
    
    if current_obj is None: return "None" 

    try:
        for part in parts[1:]:
            if part.startswith('_') or part in ['token', 'http', 'client', 'pool']: return "None"
            
            if isinstance(current_obj, dict):
                current_obj = current_obj.get(part, "None")
            else:
                current_obj = getattr(current_obj, part, "None")

        if isinstance(current_obj, datetime): return current_obj.strftime('%Y-%m-%d')
        
        if hasattr(current_obj, 'name') and not isinstance(current_obj, (bool, int, str)): 
            return str(current_obj.name)
            
        return current_obj
    except: 
        return "None"
    

# PARSING AND EXECUTION

def parse_condition(condition: str, context: Dict[str, Any], depth: int = 0) -> bool:
    try:
        if depth > 10: return False 
        cond = condition.strip()
        
        if cond == "True": return True
        if cond == "False": return False
        if '(' in cond:
             pass 

        custom_ops = r'(?i)^(.+?)\s+(startswith|endswith|matches)\s+(.+)$'
        match = re.match(custom_ops, cond)
        
        if match:
            left_side, op, right_side = match.groups()
            engine = SafeLogicEngine(resolve_dynamic_value, context)
            left_val = str(engine.evaluate(left_side.strip()))
            right_val = right_side.strip().strip('"\'')
            op = op.lower()
            
            if op == 'startswith': return left_val.lower().startswith(right_val.lower())
            if op == 'endswith': return left_val.lower().endswith(right_val.lower())
            if op == 'matches': return bool(re.search(right_val, left_val, re.I))
            return False

        engine = SafeLogicEngine(resolve_dynamic_value, context)
        result = engine.evaluate(cond)
        
        return bool(result)

    except Exception as e:
        logger.error(f"Condition Parse Error: {e} | Input: {condition}")
        return False


def substitute_variables(text: str, context: Dict[str, Any]) -> str:
    if not isinstance(text, str) or '{' not in text: 
        return text
    
    def replacer(match):
        path = match.group(1).strip()
        val = resolve_dynamic_value(path, context)
        if val is None or val == "None":
            return match.group(0) 
        return str(val)

    return REGEX_VAR_SUB.sub(replacer, text)


def parse_lazy_table(input_str: str, context: Dict[str, Any]) -> Dict[str, Any]:
    clean = input_str.strip().strip('"').strip().strip('{').strip('}').strip()
    
    # Split by commas, but only outside of quotes
    segments = []
    current = []
    in_quotes = False
    
    for i, char in enumerate(clean):
        if char == '"' and (i == 0 or clean[i-1] != '\\'):
            in_quotes = not in_quotes
        elif char == ',' and not in_quotes:
            remaining = clean[i+1:].lstrip()
            if re.match(r'\w+:', remaining):
                segments.append(''.join(current).strip())
                current = []
                continue
        current.append(char)
    
    if current:
        segments.append(''.join(current).strip())
    
    data = {}
    mapping = {
        'title': 'title', 'desc': 'description', 'description': 'description',
        'color': 'color', 'thumb': 'thumbnail', 'thumbnail': 'thumbnail',
        'image': 'image', 'footer': 'footer', 'url': 'url'
    }

    for segment in segments:
        if ":" not in segment:
            continue
            
        key, _, val = segment.partition(":")
        k = key.lower().strip()
        v = substitute_variables(val.strip(), context)
        
        if k in mapping:
            data[mapping[k]] = v
        elif k.startswith('field'):
            if 'fields' not in data: 
                data['fields'] = []
            f_parts = v.split('|')
            data['fields'].append({
                'name': f_parts[0].strip() if len(f_parts) > 0 else "None",
                'value': f_parts[1].strip() if len(f_parts) > 1 else "None",
                'inline': f_parts[2].strip().lower() == 'true' if len(f_parts) > 2 else False
            })
    return data


async def save_session_to_db(message, session):
    guild_id = session['guild_id']
    script_id = session['script_id']
    raw_source = session['buffer'].strip()

    parser = ScriptParser()
    try:
        full_ast = parser.parse(raw_source)
    except Exception as e:
        raise ValueError(f"Syntax Error: {e}")

    # Do NOT filter out comments or empty lines; preserve all lines for editing
    condition_str = "True"
    actions_ast = full_ast
    init_ast = []

    # Optimization: Single IF block with no ELSE
    logic_nodes = [n for n in full_ast if not (isinstance(n, str) and not n.strip())]
    if len(logic_nodes) == 1 and isinstance(logic_nodes[0], dict) and logic_nodes[0]['type'] == 'if' and not logic_nodes[0]['else']:
        condition_str = logic_nodes[0]['condition']
        actions_ast = logic_nodes[0]['then']
        # Find initialization: everything BEFORE the IF block (preserve comments and empty lines)
        if_index = full_ast.index(logic_nodes[0])
        init_ast = [n for n in full_ast[:if_index]]
    else:
        condition_str = "True"
        actions_ast = full_ast
        init_ast = []

    await load_scripts(guild_id)
    scripts = automation_scripts.get(guild_id, [])
    target = next((r for r in scripts if r['id'] == script_id), None)
    
    if target:
        target['condition'] = condition_str
        target['actions'] = actions_ast
        target['initialization'] = init_ast
        await save_scripts(guild_id)
    else:
        raise ValueError("Script was deleted while editing!")


async def execute_action(action: str, context: Dict[str, Any]):
    if action.lower().strip().strip(';') == 'endif': return
    if action.strip().startswith('//'): return

    chan = context.get('channel')
    
    try:
        action = substitute_variables(action, context).strip()
        
        guild = context.get('guild')
        member = context.get('member')
        message = context.get('message')
        channel = context.get('channel')
        
        if not guild: return
        guild_id = str(guild.id)

        # VAR / UVAR / TEMP LOGIC
        var_match = re.match(r'^(var|uvar|temp)\s+([a-zA-Z0-9_]+)\s*(\+?=| -?=| \*?=| /?=| %=|=)\s*(.*)$', action, re.IGNORECASE)
        if var_match:
            v_type, v_name, v_op, v_expr = var_match.groups()
            v_type, v_op = v_type.lower(), v_op.strip()
            
            engine = SafeLogicEngine(resolve_dynamic_value, context)
            right_val = engine.evaluate(v_expr)
            
            current_val = resolve_dynamic_value(f"{v_type}.{v_name}", context)
            
            # MATH LOGIC
            if v_op in ['+=', '-=', '*=', '/=', '%=']:
                try:
                    curr = float(current_val) if current_val and current_val != "None" else 0.0
                    r_val = float(right_val)
                    
                    if v_op == '+=': res = curr + r_val
                    elif v_op == '-=': res = curr - r_val
                    elif v_op == '*=': res = curr * r_val
                    elif v_op == '/=': res = curr / r_val if r_val != 0 else curr
                    elif v_op == '%=': res = curr % r_val
                    
                    if res.is_integer():
                        final_val = int(res)
                    else:
                        final_val = res
                        
                except (ValueError, TypeError):
                    if v_op == '+=':
                        final_val = str(current_val) + str(right_val)
                    else:
                        final_val = right_val
            else:
                final_val = right_val
                
            # SAVE LOGIC
            if v_type == 'var':
                server_variables.setdefault(guild_id, {})[v_name] = final_val
            elif v_type == 'uvar' and member:
                server_variables.setdefault(guild_id, {}).setdefault('users', {}).setdefault(str(member.id), {})[v_name] = final_val
            elif v_type == 'temp':
                context.setdefault('temp_vars', {})[v_name] = final_val
                
            dirty_guilds.add(guild_id)
            return

        # COMMAND EXECUTION
        match = re.match(r'^([\w\.]+)(?:\s+(.*))?$', action, re.DOTALL)
        if not match: return
        cmd, val = match.group(1).lower(), (match.group(2).strip() if match.group(2) else "")
        def clean_text(t): return t.strip('"\'').replace('\\n', '\n')

        # CHANNELS
        if cmd == 'channel.send' and channel:
            await channel.send(clean_text(val))
        elif cmd == 'channel.send_to':
            match_to = re.search(r'^(\d+):"(.*)"$', val)
            if match_to:
                t_id, t_msg = match_to.group(1), match_to.group(2)
                t_chan = guild.get_channel(int(t_id))
                if t_chan: await t_chan.send(t_msg.replace('\\n', '\n'))
            elif ":" in val:
                t_id, t_msg = val.split(":", 1)
                t_chan = guild.get_channel(int(t_id.strip()))
                if t_chan: await t_chan.send(clean_text(t_msg))
        elif cmd == 'channel.send_embed_to':
            if ":" in val:
                target_ident, table_content = val.split(":", 1)
                target_channel = guild.get_channel(int(target_ident.strip()))
                if target_channel:
                    try:
                        data = parse_lazy_table(table_content, context)
                        c_val = str(data.get('color', '0x00ff00'))
                        try: c_int = int(c_val.replace('#', '').replace('0x', ''), 16)
                        except: c_int = 0x00ff00

                        emb = discord.Embed(
                            title=data.get('title'), 
                            description=data.get('description'), 
                            color=c_int
                        )
                        if data.get('thumbnail'): emb.set_thumbnail(url=data['thumbnail'])
                        if data.get('image'): emb.set_image(url=data['image'])
                        if data.get('footer'): emb.set_footer(text=data['footer'])
                        if data.get('url'): emb.url = data['url']
                        
                        if 'fields' in data:
                            for f in data['fields']:
                                emb.add_field(name=f['name'], value=f['value'], inline=f['inline'])
                        
                        await target_channel.send(embed=emb)
                    except Exception as e:
                        logger.error(f"Lazy-Table Error: {e}")
                        
        # WEBHOOKS
        elif cmd == 'webhook.send':
            try:
                parts = val.split(maxsplit=1)
                if len(parts) >= 2:
                    webhook_url, payload = parts[0].strip(), parts[1].strip()
                    async with discord.Webhook.from_url(webhook_url, session=bot.http._HTTPClient__session) as webhook:
                        if payload.startswith('{') and payload.endswith('}'):
                            data = parse_lazy_table(payload, context)
                            await webhook.send(
                                content=data.get('content', 'No content'),
                                username=data.get('username', "Automation Logs"),
                                avatar_url=data.get('avatar', None)
                            )
                        else:
                            await webhook.send(content=clean_text(payload), username="Automation Logs")
            except Exception as e:
                logger.error(f"Webhook Error: {e}")

        elif cmd == 'webhook.send_embed':
            try:
                parts = val.split(maxsplit=1)
                if len(parts) >= 2:
                    webhook_url, table_content = parts[0].strip(), parts[1].strip()
                    async with discord.Webhook.from_url(webhook_url, session=bot.http._HTTPClient__session) as webhook:
                        data = parse_lazy_table(table_content, context)
                        c_val = str(data.get('color', '0x00ff00'))
                        try: c_int = int(c_val.replace('#', '').replace('0x', ''), 16)
                        except: c_int = 0x00ff00
                        
                        emb = discord.Embed(
                            title=data.get('title'),
                            description=data.get('desc') or data.get('description'),
                            color=c_int
                        )
                        if data.get('thumb'): emb.set_thumbnail(url=data['thumb'])
                        if data.get('image'): emb.set_image(url=data['image'])
                        if data.get('footer'): emb.set_footer(text=data['footer'])
                        
                        if 'fields' in data:
                            for f in data['fields']:
                                emb.add_field(name=f['name'], value=f['value'], inline=f['inline'])

                        await webhook.send(
                            embed=emb, 
                            username=data.get('username', "Automation Logs"),
                            avatar_url=data.get('avatar', None)
                        )
            except Exception as e:
                logger.error(f"Webhook Embed Error: {e}")

        # CHANNEL MANIPULATION
        elif cmd == 'channel.purge' and channel:
            await channel.purge(limit=int(val))
        elif cmd == 'channel.delete' and channel:
            await channel.delete()
        elif cmd == 'channel.create':
            await guild.create_text_channel(clean_text(val))
        elif cmd == 'channel.create_voice':
            await guild.create_voice_channel(clean_text(val))

        # MESSAGE MANIPULATION
        elif cmd == 'message.edit' and message:
            new_content = clean_text(val)
            if message.content != new_content:
                await message.edit(content=new_content)
        elif cmd == 'message.delete' and message:
            await message.delete()
        elif cmd == 'message.reply' and message:
            await message.reply(clean_text(val))
        elif cmd == 'message.pin' and message:
            if not message.pinned: await message.pin()
        elif cmd == 'message.unpin' and message:
            if message.pinned: await message.unpin()

        # THREADS
        elif cmd == 'thread.create' and message:
            thread_name = clean_text(val)
            if not any(t.name == thread_name for t in guild.threads):
                await message.create_thread(name=thread_name)
        elif cmd == 'thread.archive' and isinstance(channel, discord.Thread):
            await channel.edit(archived=True)

        # MEMBERS
        elif cmd == 'member.nickname' and member:
            new_nick = clean_text(val)
            if member.nick != new_nick: await member.edit(nick=new_nick)
        elif cmd == 'member.timeout' and member:
            until = discord.utils.utcnow() + timedelta(minutes=int(val))
            await member.timeout(until)
        elif cmd == 'member.addrole' and member:
            role = discord.utils.get(guild.roles, name=clean_text(val))
            if role and role not in member.roles: await member.add_roles(role)
        elif cmd == 'member.removerole' and member:
            role = discord.utils.get(guild.roles, name=clean_text(val))
            if role and role in member.roles: await member.remove_roles(role)
        elif cmd == 'member.kick' and member:
            await member.kick()
        elif cmd == 'member.ban' and member:
            await member.ban()
        elif cmd == 'member.unban':
            try:
                user_id = int(val)
                user = await bot.fetch_user(user_id)
                await guild.unban(user)
            except: pass
        elif cmd == 'member.dm' and member:
            await member.send(clean_text(val))

        # ROLES/GUILD
        elif cmd == 'role.create':
            await guild.create_role(name=clean_text(val))
        elif cmd == 'role.delete':
            role = discord.utils.get(guild.roles, name=clean_text(val))
            if role: await role.delete()
        elif cmd == 'guild.setname':
            if guild.name != clean_text(val): await guild.edit(name=clean_text(val))

        # REACTIONS
        elif cmd == 'reaction.add' and message:
            await message.add_reaction(clean_text(val))
        elif cmd == 'reaction.remove' and message:
            await message.clear_reaction(clean_text(val))

        # VARIABLES (Legacy)
        elif cmd == 'var.set':
            parts = val.split(maxsplit=1)
            if len(parts) == 2:
                server_variables.setdefault(guild_id, {})[parts[0].strip('"\'')] = parts[1]
                dirty_guilds.add(guild_id)
        elif cmd == 'var.del':
            if guild_id in server_variables:
                server_variables[guild_id].pop(val.strip('"\''), None)
                dirty_guilds.add(guild_id)
        
        # SYSTEM
        elif cmd == 'system.wait':
            await asyncio.sleep(float(val))
        elif cmd == 'temp.set':
            parts = val.split(maxsplit=1)
            if len(parts) == 2:
                context.setdefault('temp_vars', {})[parts[0].strip('"\'')] = parts[1]

    except Exception as e:
        logger.error(f"Script Error: {e}")
        if chan:
            await chan.send(f"Error: Script execution failed. Action: {action[:100]}. Details: {e}.")

    if cmd not in VALID_COMMANDS:
        if chan:
            await chan.send(f"Error: Unknown command '{cmd}'.")


async def execute_ast(actions: List[Any], context: Dict[str, Any], guild_id: str, depth: int = 0):
    if depth > 10: 
        logger.error(f"Recursion limit hit in guild {guild_id}!")
        return

    for item in actions:
        if isinstance(item, str):
            await execute_action(item, context)
            await asyncio.sleep(0.25) 

        elif isinstance(item, dict) and item.get('type') == 'if':
            condition = item.get('condition', 'False')
            
            try:
                is_true = parse_condition(condition, context)
            except Exception:
                is_true = False

            if is_true:
                await execute_ast(item.get('then', []), context, guild_id, depth + 1)
            else:
                await execute_ast(item.get('else', []), context, guild_id, depth + 1)


async def run_script_actions(script: Dict[str, Any], context: Dict[str, Any], guild_id: str):
    try:
        confirm_execution(guild_id, script['id'])
        await execute_ast(script['actions'], context, guild_id)
    except Exception as e:
        logger.error(f"Script execution error {script['id']} in {guild_id}: {e}")
        if 'channel' in context and context['channel']:
            await context['channel'].send(f"Error: Script execution failed. Script ID: {script['id']}. Details: {e}.")


async def check_and_execute_scripts(context: Dict[str, Any]):
    guild = context.get('guild')
    
    if not guild: return
    
    guild_id = str(guild.id)
    context['now'] = discord.utils.utcnow()

    if guild_id not in server_variables: await load_variables(guild_id)
    if guild_id not in automation_scripts: await load_scripts(guild_id)

    scripts = automation_scripts.get(guild_id, [])
    triggered_count = 0
    
    for script in scripts:
        if triggered_count >= BURST_LIMIT: break 
        if not script.get('enabled', True): continue
        if not check_rate_limit(guild_id, script['id']): continue 
        
        try:
            script_context = context.copy()
            
            if 'temp_vars' not in script_context:
                script_context['temp_vars'] = {}
            if 'initialization' in script and script['initialization']:
                await execute_ast(script['initialization'], script_context, guild_id)
            if parse_condition(script['condition'], script_context, depth=0):
                asyncio.create_task(run_script_actions(script, script_context, guild_id))
                triggered_count += 1
                
        except Exception as e:
            logger.error(f"Script execution error {script['id']} in {guild_id}: {e}")

            
def manage_cache_size():
    if len(message_cache) > MAX_CACHE_SIZE:
        remove = MAX_CACHE_SIZE // 5
        keys = list(message_cache.keys())[:remove]
        
        for k in keys: del message_cache[k]

            
# BACKGROUND TASKS

@tasks.loop(minutes=2) 
async def autosave_vars():
    if not pool or not dirty_guilds: return
    
    to_save = list(dirty_guilds)
    
    logger.info(f"Auto-saving {len(to_save)} dirty guilds!")
    
    for guild_id in to_save:
        try:
            await save_variables(guild_id)
            dirty_guilds.discard(guild_id)
        except Exception as e:
            logger.error(f"Auto-save failed for {guild_id}: {e}!")

            
@tasks.loop(hours=1)
async def cleanup_cooldowns():
    current_time = discord.utils.utcnow().timestamp()
    cutoff = current_time - 3600
    to_remove = [k for k, v in script_cooldowns.items() if v.timestamp() < cutoff]
    
    for k in to_remove:
        del script_cooldowns[k]
        
    if to_remove:
        logger.info(f"Cleaned up {len(to_remove)} old cooldowns!")

        
# EVENTS

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')
    await init_db()
    
    for guild in bot.guilds:
        g_id = str(guild.id)
        if g_id not in server_variables:
            await load_variables(g_id)
        if g_id not in automation_scripts:
            await load_scripts(g_id)
            
    if not cleanup_cooldowns.is_running():
        cleanup_cooldowns.start()
        
    if not autosave_vars.is_running():
        autosave_vars.start()
        
    logger.info("Bot ready!")

    
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # EDITING SESSION LOGIC
    if message.author.id in editing_sessions:
        session = editing_sessions[message.author.id]
        
        if message.channel.id != session['channel_id']:
            return

        content = message.content.strip()
        await message.delete()

        # EXIT
        if content.lower() == 'exit':
            del editing_sessions[message.author.id]
            try:
                original_msg = await message.channel.fetch_message(session['message_id'])
                await original_msg.edit(content=f"Script {session['script_id']}.vrk editing cancelled.")
            except: pass
            return

        # SAVE
        if content.lower() == 'save':
            try:
                await save_session_to_db(message, session)
                del editing_sessions[message.author.id]
                await message.channel.send(f"Script {session['script_id']}.vrk saved and compiled.")
            except Exception as e:
                await message.channel.send(f"Error: Compile failed. Details: {e}.")
            return

        # LINE EDITING
        try:
            current_buffer = session['buffer']
            
            new_buffer = LineEditor.apply_edit(current_buffer, content)
            
            if new_buffer is None:
                if current_buffer:
                    new_buffer = current_buffer + "\n" + content
                else:
                    new_buffer = content

            session['buffer'] = new_buffer
            
            numbered_view = LineEditor.render_with_numbers(new_buffer)
            code_block = f"Editing {session['script_id']}.vrk\nType `save` to apply, `exit` to cancel.\n```lua\n{numbered_view}\n```"
            
            try:
                original_msg = await message.channel.fetch_message(session['message_id'])
                await original_msg.edit(content=code_block)
            except:
                new_msg = await message.channel.send(code_block)
                session['message_id'] = new_msg.id

        except Exception as e:
            await message.channel.send(f"Error: Editor failure. Details: {e}.", delete_after=5)
        
        return 

    # Normal Message Processing
    message_cache[message.id] = message
    manage_cache_size()
    await bot.process_commands(message)

    asyncio.create_task(check_and_execute_scripts({
        'event_type': 'message', 'message': message, 'member': message.author,
        'guild': message.guild, 'channel': message.channel
    }))
    
    
@bot.event
async def on_member_join(member):
    await check_and_execute_scripts({
        'event_type': 'member_join', 'member': member, 'guild': member.guild, 'channel': member.guild.system_channel
    })

    
@bot.event
async def on_member_remove(member):
    await check_and_execute_scripts({
        'event_type': 'member_leave', 'member': member, 'guild': member.guild, 'channel': member.guild.system_channel
    })

    
@bot.event
async def on_member_ban(guild, user):
    await check_and_execute_scripts({'event_type': 'member_ban', 'member': user, 'guild': guild, 'channel': guild.system_channel})

    
@bot.event
async def on_member_unban(guild, user):
    await check_and_execute_scripts({'event_type': 'member_unban', 'member': user, 'guild': guild, 'channel': guild.system_channel})

    
@bot.event
async def on_voice_state_update(member, before, after):
    is_join = before.channel is None and after.channel is not None
    is_leave = before.channel is not None and after.channel is None
    is_move = before.channel is not None and after.channel is not None and before.channel != after.channel
    target_output_channel = member.guild.system_channel or (member.guild.text_channels[0] if member.guild.text_channels else None)
    
    if not target_output_channel:
        return 
    
    context = {
        'event_type': 'voice_update',
        'member': member,
        'guild': member.guild,
        'channel': target_output_channel, 
        'voice': after.channel if after.channel else before.channel, 
        'event': {
            'joined': is_join, 'left': is_leave, 'moved': is_move,
            'afk': after.afk, 'muted': after.self_mute or after.mute, 'deafened': after.self_deaf or after.deaf
        }
    }
    
    await check_and_execute_scripts(context)

    
@bot.event
async def on_message_delete(message):
    if isinstance(message, discord.Message):
        await check_and_execute_scripts({'event_type': 'message_delete', 'message': message, 'member': message.author, 'guild': message.guild, 'channel': message.channel})
    if message.id in message_cache: del message_cache[message.id]

        
@bot.event
async def on_message_edit(before, after):
    if isinstance(after, discord.Message):
        await check_and_execute_scripts({'event_type': 'message_edit', 'message': after, 'member': after.author, 'guild': after.guild, 'channel': after.channel})
        message_cache[after.id] = after


@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user: return
    
    msg = reaction.message
    
    if not msg.content:
        try: msg = await msg.channel.fetch_message(msg.id)
        except: pass
        
    await check_and_execute_scripts({
        'event_type': 'reaction_add', 'reaction': reaction, 'emoji': reaction.emoji,
        'message': msg, 'member': user, 'guild': msg.guild, 'channel': msg.channel
    })

    
@bot.event
async def on_reaction_remove(reaction, user):
    if user == bot.user: return
    
    msg = reaction.message
    
    if not msg.content:
        try: msg = await msg.channel.fetch_message(msg.id)
        except: pass
    await check_and_execute_scripts({
        'event_type': 'reaction_remove', 'reaction': reaction, 'emoji': reaction.emoji,
        'message': msg, 'member': user, 'guild': msg.guild, 'channel': msg.channel
    })

    
@bot.event
async def on_guild_channel_create(channel):
    await check_and_execute_scripts({'event_type': 'channel_create', 'channel': channel, 'guild': channel.guild})

    
@bot.event
async def on_guild_channel_delete(channel):
    await check_and_execute_scripts({'event_type': 'channel_delete', 'channel': channel, 'guild': channel.guild})

    
@bot.event
async def on_guild_update(before, after):
    context = {
        'event_type': 'guild_update', 'guild': after,
        'name_changed': before.name != after.name,
        'old_name': before.name, 'new_name': after.name, 'icon_changed': before.icon != after.icon
    }
    
    await check_and_execute_scripts(context)

    
# UTILS

@bot.command(name='import')
@commands.has_permissions(administrator=True)
async def direct_import(ctx):
    if not ctx.message.attachments:
        return await ctx.send("Error: Please attach a valid JSON file.")

    guild_id = str(ctx.guild.id)
    await load_variables(guild_id)
    await load_scripts(guild_id)
    
    success = False

    for file in ctx.message.attachments:
        if not file.filename.endswith('.json'):
            continue
            
        try:
            content = await file.read()
            module_data = json.loads(content)

            if not validate_module_schema(module_data):
                continue

            current_vars = server_variables.get(guild_id, {})
            for key, val in module_data.get('variables', {}).items():
                if key not in current_vars:
                    current_vars[key] = val
            server_variables[guild_id] = current_vars
            dirty_guilds.add(guild_id)

            current_scripts = automation_scripts.get(guild_id, [])
            for r in module_data['scripts']:
                original_id = r.get('id', 'imported_script')
                final_id = original_id
                
                counter = 1
                while any(str(existing['id']).lower() == str(final_id).lower() for existing in current_scripts):
                    final_id = f"{original_id}_{counter}"
                    counter += 1

                new_script = {
                    'id': final_id,
                    'condition': r['condition'],
                    'actions': r['actions'],
                    'initialization': r.get('initialization', []),
                    'enabled': True,
                    'guild_id': guild_id,
                    'priority': r.get('priority', 10)
                }
                current_scripts.append(new_script)
            
            automation_scripts[guild_id] = current_scripts
            success = True

        except Exception:
            continue

    if success:
        await save_scripts(guild_id)
        await ctx.send("Script imported.")
    else:
        await ctx.send("Error: Failed to import file.")


@bot.command(name='export')
@commands.has_permissions(administrator=True)
async def direct_export(ctx, script_name: str):
    guild_id = str(ctx.guild.id)
    await load_scripts(guild_id)
    
    target_script = next((r for r in automation_scripts.get(guild_id, []) 
                          if str(r['id']).lower() == script_name.lower()), None)
    
    if not target_script:
        return await ctx.send(f"Error: Script {script_name}.vrk not found.")

    module_data = {
        "meta": {
            "name": str(target_script['id']),
            "version": "1.0",
            "author": ctx.author.name,
            "exported_at": str(datetime.now())
        },
        "variables": {}, 
        "scripts": [{
            "id": target_script['id'],
            "condition": target_script['condition'],
            "actions": target_script['actions'],
            "priority": target_script.get('priority', 0),
            "initialization": target_script.get('initialization', [])
        }]
    }

    buffer = io.BytesIO(json.dumps(module_data, indent=4).encode('utf-8'))
    filename = f"{target_script['id']}.json"
    await ctx.send(f"Exported script as {filename}.", file=discord.File(buffer, filename=filename))

    
# VARIABLES

@bot.group(name='var', invoke_without_command=True)
@commands.has_permissions(administrator=True)
async def var_group(ctx):
    await ctx.send("Variable Commands: vvar list, vvar get <key>, vvar set <key> <val>, vvar del <key>, vvar clear")

    
@var_group.command(name='set')
async def var_set(ctx, key: str, *, value: str):
    guild_id = str(ctx.guild.id)
    
    if guild_id not in server_variables: await load_variables(guild_id)
    
    final_val = detect_type(value)
    server_variables[guild_id][key] = final_val
    dirty_guilds.add(guild_id)
    await ctx.send(f"Variable set. {key} = {final_val} ({type(final_val).__name__})")

    
@var_group.command(name='get')
async def var_get(ctx, key: str):
    guild_id = str(ctx.guild.id)
    
    if guild_id not in server_variables: await load_variables(guild_id)
        
    val = server_variables.get(guild_id, {}).get(key)
    
    if val is None: return await ctx.send(f"Variable {key} does not exist.")
    
    val_str = str(val)
    
    if len(val_str) <= 1900: 
        await ctx.send(f"{key} = {val_str} ({type(val).__name__})")
    else:
        buffer = io.BytesIO(json.dumps({"key": key, "value": val}, indent=4).encode('utf-8'))
        await ctx.send(f"Error: Value too large.", file=discord.File(buffer, filename=f"var_{key}.json"))

        
@var_group.command(name='del')
async def var_del(ctx, key: str):
    guild_id = str(ctx.guild.id)
    if guild_id not in server_variables: await load_variables(guild_id)
        
    if key in server_variables[guild_id]:
        del server_variables[guild_id][key]
        dirty_guilds.add(guild_id)
        await ctx.send(f"Deleted variable {key}.")
    else:
        await ctx.send(f"Error: Variable {key} not found.")

        
@var_group.command(name='clear')
@commands.has_permissions(administrator=True)
async def var_clear(ctx):
    guild_id = str(ctx.guild.id)
    server_variables[guild_id] = {}
    
    if pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("DELETE FROM guild_data WHERE guild_id = %s", (guild_id,))
        await ctx.send(f"All variables wiped for {ctx.guild.name}.")

        
@bot.command(name='vardex')
@commands.has_permissions(administrator=True) 
async def vardex(ctx, page: int = 1):
    guild_id = str(ctx.guild.id)
    
    if guild_id not in server_variables: await load_variables(guild_id)
    
    vars_dict = server_variables.get(guild_id, {})
    
    if not vars_dict: return await ctx.send("No variables set for this server.")

    all_vars = sorted(vars_dict.items(), key=lambda x: x[0])
    items_per_page = 10
    total_pages = (len(all_vars) + items_per_page - 1) // items_per_page
    page = max(1, min(page, total_pages))
    start = (page - 1) * items_per_page
    current_page_vars = all_vars[start:start+items_per_page]
    lines = [f"[{len(all_vars)}] **{ctx.guild.name}'s VarDex**"]
    
    for key, val in current_page_vars:
        val_str = str(val)
        if len(val_str) > 50: val_str = val_str[:50] + "..."
        lines.append(f"({type(val).__name__}) {key} = {val_str}")

    lines.append(f"-# Showing page {page} of {total_pages}")
    msg = "\n".join(lines)
    
    if len(msg) > 1950: 
        await ctx.send(msg[:1950] + "\n-# Page truncated due to length!")
    else: 
        await ctx.send(msg)


@bot.command(name='uvardex')
@commands.has_permissions(administrator=True) 
async def uvardex(ctx, member: discord.Member = None, page: int = 1):
    if not member: member = ctx.author
    guild_id = str(ctx.guild.id)
    user_id = str(member.id)
    
    if guild_id not in server_variables: await load_variables(guild_id)
    
    user_vars = server_variables.get(guild_id, {}).get('users', {}).get(user_id, {})
    
    if not user_vars: 
        return await ctx.send(f"No variables found for {member.display_name}.")

    all_vars = sorted(user_vars.items(), key=lambda x: x[0])
    items_per_page = 10
    total_pages = (len(all_vars) + items_per_page - 1) // items_per_page
    page = max(1, min(page, total_pages))
    
    start = (page - 1) * items_per_page
    current_page_vars = all_vars[start:start+items_per_page]

    lines = [f"[{len(all_vars)}] **{member.display_name}'s UvarDex**"]
    
    for key, val in current_page_vars:
        val_str = str(val)
        if len(val_str) > 50: val_str = val_str[:50] + "..."
        lines.append(f"({type(val).__name__}) {key} = {val_str}")

    lines.append(f"-# Showing page {page} of {total_pages}")
    
    msg = "\n".join(lines)
    if len(msg) > 1950: 
        await ctx.send(msg[:1950] + "\n-# Page truncated due to length!")
    else: 
        await ctx.send(msg)


@bot.group(name='uvar', invoke_without_command=True)
@commands.has_permissions(administrator=True)
async def uvar_group(ctx):
    await ctx.send("Uvar Commands: vuvar set <@user> <key> <val>, vuvar del <@user> <key>")


@uvar_group.command(name='set')
async def uvar_set_cmd(ctx, member: discord.Member, key: str, *, value: str):
    guild_id = str(ctx.guild.id)
    user_id = str(member.id)
    
    if guild_id not in server_variables: await load_variables(guild_id)

    final_val = detect_type(value)

    server_variables.setdefault(guild_id, {}).setdefault('users', {}).setdefault(user_id, {})[key] = final_val
    dirty_guilds.add(guild_id)
    
    await ctx.send(f"{member.display_name}'s Uvar set. {key} = {final_val} ({type(final_val).__name__})")
    

@uvar_group.command(name='del')
async def uvar_del_cmd(ctx, member: discord.Member, key: str):
    guild_id = str(ctx.guild.id)
    user_id = str(member.id)
    
    if guild_id not in server_variables: await load_variables(guild_id)
        
    try:
        del server_variables[guild_id]['users'][user_id][key]
        dirty_guilds.add(guild_id)
        await ctx.send(f"Deleted variable {key} for {member.display_name}.")
    except KeyError:
        await ctx.send(f"Error: Variable not found for {member.display_name}.")

        
@uvar_group.command(name='clear')
@commands.has_permissions(administrator=True)
async def uvar_clear(ctx):
    guild_id = str(ctx.guild.id)
    if guild_id in server_variables and 'users' in server_variables[guild_id]:
        server_variables[guild_id]['users'] = {}
        dirty_guilds.add(guild_id)
        await ctx.send('All user variables have been cleared for this server.')
    else:
        await ctx.send('No user variables found to clear for this server.')

    
# SCRIPTS

@bot.group(name='script', invoke_without_command=True)
@commands.has_permissions(administrator=True)
async def script_group(ctx):
    pass


@script_group.command(name='edit')
@commands.has_permissions(administrator=True)
async def script_edit(ctx, script_name: str):
    guild_id = str(ctx.guild.id)
    await load_scripts(guild_id)
    scripts = automation_scripts.get(guild_id, [])
    target_script = next((r for r in scripts if str(r['id']).lower() == script_name.lower()), None)
    
    if not target_script:
        return await ctx.send(f"Error: Script {script_name}.vrk not found.")

    raw_lines = prettify_ast_numbered(
        target_script['condition'], 
        target_script['actions'], 
        target_script.get('initialization')
    )
    current_source = "\n".join(raw_lines)
    
    numbered_view = LineEditor.render_with_numbers(current_source)

    enabled = target_script.get('enabled', True)
    display_name = f"~~{target_script['id']}~~" if not enabled else target_script['id']
    
    msg_content = f"{display_name}.vrk\nType `save` to apply changes, `exit` to cancel.\n```lua\n{numbered_view}\n```"
    
    sent_message = await ctx.send(msg_content)
    
    editing_sessions[ctx.author.id] = {
        'script_id': target_script['id'], 
        'guild_id': guild_id,
        'channel_id': ctx.channel.id,
        'message_id': sent_message.id,
        'buffer': current_source
    }


@script_group.command(name='create')
@commands.has_permissions(administrator=True)
async def script_create(ctx, script_name: str, *, raw_input: str):
    guild_id = str(ctx.guild.id)
    if guild_id not in automation_scripts: await load_scripts(guild_id)

    text = raw_input.replace('\r', '').strip()
    
    priority = 0
    p_match = re.search(r'(?i)priority\s+(\d+)', text)
    if p_match:
        priority = int(p_match.group(1))
        text = re.sub(r'(?i)priority\s+\d+', '', text).strip()

    try:
        parser = ScriptParser()
        full_ast = parser.parse(text)
        
        # Filter out empty strings AND comments
        logic_nodes = [
            n for n in full_ast 
            if not (isinstance(n, str) and (not n.strip() or n.strip().startswith('//')))
        ]

        # Single IF optimization
        if len(logic_nodes) == 1 and isinstance(logic_nodes[0], dict) and logic_nodes[0]['type'] == 'if' and not logic_nodes[0]['else']:
            condition_str = logic_nodes[0]['condition']
            actions_ast = logic_nodes[0]['then']
            
            if_index = full_ast.index(logic_nodes[0])
            init_ast = [
                n for n in full_ast[:if_index] 
                if isinstance(n, str) and n.strip() and not n.strip().startswith('//')
            ]
        else:
            # Global mode
            condition_str = "True"
            actions_ast = full_ast
            init_ast = []

        new_script = {
            'id': script_name,
            'condition': condition_str,
            'initialization': init_ast, 
            'actions': actions_ast,
            'enabled': True,
            'guild_id': guild_id,
            'priority': priority, 
        }
        
        current_scripts = [r for r in automation_scripts.get(guild_id, []) if str(r['id']).lower() != script_name.lower()]
        current_scripts.append(new_script)
        automation_scripts[guild_id] = current_scripts
        
        await save_scripts(guild_id)
        await ctx.send(f"Script {script_name}.vrk created.")
        
    except Exception as e:
        logger.error(f"Creation Error: {e}")
        await ctx.send(f"Error: Failed to parse script. Details: {e}.")


@script_group.command(name='del')
@commands.has_permissions(administrator=True)
async def script_del(ctx, script_name: str): 
    guild_id = str(ctx.guild.id)
    await load_scripts(guild_id)
    scripts = automation_scripts.get(guild_id, [])
    new_scripts = [r for r in scripts if str(r['id']).lower() != script_name.lower()]
    if len(new_scripts) < len(scripts):
        automation_scripts[guild_id] = new_scripts
        await save_scripts(guild_id)
        return await ctx.send(f"Script {script_name}.vrk deleted.")
    await ctx.send(f"Error: Script {script_name}.vrk not found.")


@script_group.command(name='toggle')
@commands.has_permissions(administrator=True)
async def script_toggle(ctx, script_name: str):
    guild_id = str(ctx.guild.id)
    await load_scripts(guild_id)
    for r in automation_scripts.get(guild_id, []):
        if str(r['id']).lower() == script_name.lower():
            r['enabled'] = not r['enabled']
            await save_scripts(guild_id)
            return await ctx.send(f"Script [{r['id']}] is now {'enabled' if r['enabled'] else 'disabled'}.")
    await ctx.send(f"Error: Script {script_name}.vrk not found.")


@script_group.command(name='clear')
@commands.has_permissions(administrator=True)
async def script_clear(ctx):
    guild_id = str(ctx.guild.id)
    automation_scripts[guild_id] = []
    if pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute("DELETE FROM guild_scripts WHERE guild_id = %s", (guild_id,))
    await ctx.send(f"All scripts wiped for {ctx.guild.name}.")


@bot.command(name='codex')
@commands.has_permissions(administrator=True) 
async def codex(ctx, page: int = 1):
    guild_id = str(ctx.guild.id)
    await load_scripts(guild_id, force_reload=True)
    raw_scripts = automation_scripts.get(guild_id, [])
    if not raw_scripts: 
        return await ctx.send("No scripts found.")
    scripts_per_page = 10
    total_pages = (len(raw_scripts) + scripts_per_page - 1) // scripts_per_page
    page = max(1, min(page, total_pages))
    start = (page - 1) * scripts_per_page
    current_page_scripts = raw_scripts[start:start+scripts_per_page]
    lines = [f"[{len(raw_scripts)}] **{ctx.guild.name}'s Codex**"]
    for r in current_page_scripts:
        name = str(r['id'])
        priority = r.get('priority', 0)
        display_name = f"~~{name}~~" if not r.get('enabled', True) else name
        lines.append(f"[{priority}] {display_name}.vrk")
    lines.append(f"-# Showing page {page} of {total_pages}")
    await ctx.send("\n".join(lines))


@bot.command(name='print')
async def debug_print(ctx, *, content: str):
    content = content.strip()
    if not (content.startswith('(') and content.endswith(')')):
        return await ctx.send("Error: Syntax. Parentheses required. Use vprint (value)")
    inner_content = content[1:-1].strip()
    context = {
        'guild': ctx.guild,
        'member': ctx.author,
        'message': ctx.message,
        'channel': ctx.channel,
        'now': discord.utils.utcnow()
    }
    if ctx.author.voice and ctx.author.voice.channel:
        context['voice'] = ctx.author.voice.channel
        context['event'] = {'joined': False, 'left': False, 'moved': False}
    direct_value = resolve_dynamic_value(inner_content, context)
    if str(direct_value) != inner_content or not isinstance(direct_value, str):
        final_output = str(direct_value)
    else:
        if inner_content.startswith('"') and inner_content.endswith('"'):
            inner_content = inner_content[1:-1]
        elif inner_content.startswith("'") and inner_content.endswith("'"):
            inner_content = inner_content[1:-1]
        final_output = substitute_variables(inner_content, context)
    await ctx.send(final_output)
    
    
# BACKUP AND RESTORE

@bot.command(name='backup')
@commands.has_permissions(administrator=True)
async def module_backup(ctx):
    guild_id = str(ctx.guild.id)
    await load_scripts(guild_id)
    data = automation_scripts.get(guild_id, [])
    buffer = io.BytesIO(json.dumps(data, indent=4).encode('utf-8'))
    timestamp = int(datetime.now().timestamp())
    await ctx.send("Full backup created.", file=discord.File(buffer, filename=f"backup_{guild_id}_{timestamp}.json"))


@bot.command(name='restore')
@commands.has_permissions(administrator=True)
async def module_restore(ctx):
    if not ctx.message.attachments:
        return await ctx.send("Error: Please attach a backup JSON file.")
    try:
        content = await ctx.message.attachments[0].read()
        raw_scripts = json.loads(content)
        valid_scripts = [r for r in raw_scripts if validate_script_structure(r)]
        if not valid_scripts:
            return await ctx.send("Error: No valid scripts found.")
        guild_id = str(ctx.guild.id)
        await load_scripts(guild_id)
        current_scripts = automation_scripts.get(guild_id, [])
        # Use a set for fast lookup of existing IDs (case-insensitive)
        existing_ids = {str(existing['id']).lower() for existing in current_scripts}
        for r in valid_scripts:
            original_name = str(r.get('id', 'restored_script'))
            final_name = original_name
            counter = 1
            # Ensure unique script IDs (case-insensitive)
            while final_name.lower() in existing_ids:
                final_name = f"{original_name}_{counter}"
                counter += 1
            r['id'] = final_name
            r['guild_id'] = guild_id
            current_scripts.append(r)
            existing_ids.add(final_name.lower())
        automation_scripts[guild_id] = current_scripts
        await save_scripts(guild_id)
        await ctx.send("Restore complete.")
    except Exception as e:
        await ctx.send(f"Error: Restore failed. Details: {e}.")

        
# MAIN

async def main():
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    async with bot:
        try:
            await bot.start(TOKEN)
        except KeyboardInterrupt:
            pass
        finally:
            logger.info("Shutdown initiated. Saving all data...")
            for guild_id in list(server_variables.keys()):
                await save_variables(guild_id)
            if pool:
                pool.close()
                await pool.wait_closed()
            await bot.close()
            print("Bot shut down safely. Data saved.")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
