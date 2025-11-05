# nuvix_system/bot.py
import os, sys, time, datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils import BANNER_URL, FOOTER_TEXT, LOGS_CMD_USE_CHANNEL_ID, log_to_json

load_dotenv()
bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
NUVIX_COLOR = 0x9b19ff
START = time.time()

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

@bot.tree.command(name="ping", description="Check bot latency (Pong!)")
async def ping(inter: discord.Interaction):
    await log_cmd(inter, "ping")
    await inter.response.send_message(embed=emb("Pong!", f"Latency: `{round(bot.latency*1000)}ms`"), ephemeral=True)

@bot.tree.command(name="uptime", description="Show bot uptime")
async def uptime(inter: discord.Interaction):
    await log_cmd(inter, "uptime")
    secs = int(time.time() - START)
    h, r = divmod(secs, 3600); m, s = divmod(r, 60)
    await inter.response.send_message(embed=emb("Uptime", f"`{h}h {m}m {s}s`"))

@bot.tree.command(name="systemstatus", description="Basic system status")
async def systemstatus(inter: discord.Interaction):
    await log_cmd(inter, "systemstatus")
    await inter.response.send_message(embed=emb("System", "All systems nominal"))

bot.run(os.getenv("NUVIX_SYSTEM_TOKEN"))
