# nuvix_backup/bot.py
import os, sys, shutil, datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

from utils import BANNER_URL, FOOTER_TEXT, LOGS_CMD_USE_CHANNEL_ID, log_to_json, can_highstaff_or_above

load_dotenv()
INTENTS = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=INTENTS)
NUVIX_COLOR = 0x9b19ff

DATA_DIR = "data"
BACKUP_DIR = os.path.join(DATA_DIR, "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

def logs_channel(guild):
    try:
        if LOGS_CMD_USE_CHANNEL_ID:
            ch = guild.get_channel(int(LOGS_CMD_USE_CHANNEL_ID))
            if isinstance(ch, discord.TextChannel): return ch
    except: pass

async def log_cmd(inter, name):
    try:
        ch = logs_channel(inter.guild)
        if ch: await ch.send(f"`{inter.user}` used `/{name}` in {inter.channel.mention}")
    except: pass
    log_to_json("cmd_use.json", {"user": str(inter.user), "cmd": name, "ts": datetime.datetime.utcnow().isoformat()})

def emb(t, d=""):
    e = discord.Embed(title=t, description=d, color=NUVIX_COLOR)
    if BANNER_URL: e.set_thumbnail(url=BANNER_URL)
    if FOOTER_TEXT: e.set_footer(text=FOOTER_TEXT)
    return e

@bot.event
async def on_ready():
    try: await bot.tree.sync()
    except Exception as e: print("Sync error:", e)
    print(f"{bot.user} is online!")

@bot.tree.command(name="backup_create", description="Create a data backup")
@commands.check(can_highstaff_or_above)
async def backup_create(inter: discord.Interaction):
    await log_cmd(inter, "backup_create")
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    dst = os.path.join(BACKUP_DIR, f"backup_{ts}")
    shutil.copytree(DATA_DIR, dst, dirs_exist_ok=True)
    await inter.response.send_message(embed=emb("Backup created", f"Saved at `/{dst}`"))

@bot.tree.command(name="backup_restore", description="Restore latest backup")
@commands.check(can_highstaff_or_above)
async def backup_restore(inter: discord.Interaction):
    await log_cmd(inter, "backup_restore")
    backs = sorted([p for p in os.listdir(BACKUP_DIR)], reverse=True)
    if not backs:
        return await inter.response.send_message(embed=emb("No backups", "There are no backups yet."), ephemeral=True)
    src = os.path.join(BACKUP_DIR, backs[0])
    shutil.copytree(src, DATA_DIR, dirs_exist_ok=True)
    await inter.response.send_message(embed=emb("Backup restored", f"Restored `{backs[0]}`"))

@bot.tree.command(name="ping", description="Check bot latency (Pong!)")
async def ping(inter: discord.Interaction):
    await log_cmd(inter, "ping")
    await inter.response.send_message(embed=emb("Pong!", f"Latency: `{round(bot.latency*1000)}ms`"), ephemeral=True)

bot.run(os.getenv("NUVIX_BACKUP_TOKEN"))
