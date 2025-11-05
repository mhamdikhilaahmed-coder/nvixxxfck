# nuvix_backup/bot.py
import os
import sys
import shutil
import datetime
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from utils import BANNER_URL, FOOTER_TEXT, LOGS_CMD_USE_CHANNEL_ID, log_to_json, can_highstaff_or_above

# 🔹 Cargar variables desde .env
load_dotenv()

# 🔹 Asegurar acceso a /utils/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

INTENTS = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=INTENTS)

# ✅ Crear árbol de comandos slash
tree = app_commands.CommandTree(bot)

NUVIX_COLOR = 0x9b19ff
DATA_DIR = "data"
BACKUP_DIR = os.path.join(DATA_DIR, "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)


def logs_channel(guild):
    try:
        if LOGS_CMD_USE_CHANNEL_ID:
            ch = guild.get_channel(int(LOGS_CMD_USE_CHANNEL_ID))
            if isinstance(ch, discord.TextChannel):
                return ch
    except:
        pass


async def log_cmd(inter, name):
    try:
        ch = logs_channel(inter.guild)
        if ch:
            await ch.send(f"`{inter.user}` used `/{name}` in {inter.channel.mention}")
    except:
        pass
    log_to_json("cmd_use.json", {"user": str(inter.user), "cmd": name, "ts": datetime.datetime.utcnow().isoformat()})


def emb(t, d=""):
    e = discord.Embed(title=t, description=d, color=NUVIX_COLOR)
    if BANNER_URL:
        e.set_thumbnail(url=BANNER_URL)
    if FOOTER_TEXT:
        e.set_footer(text=FOOTER_TEXT)
    return e


@bot.event
async def on_ready():
    try:
        await tree.sync()
        print("✅ Slash commands synced successfully.")
    except Exception as e:
        print("⚠️ Sync error:", e)
    print(f"{bot.user} is online!")


@tree.command(name="backup_create", description="Create a data backup")
@commands.check(can_highstaff_or_above)
async def backup_create(inter: discord.Interaction):
    await log_cmd(inter, "backup_create")
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%")
