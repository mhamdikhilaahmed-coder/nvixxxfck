# nuvix_system/bot.py
import os
import sys
import time
import datetime
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from utils import BANNER_URL, FOOTER_TEXT, LOGS_CMD_USE_CHANNEL_ID, log_to_json

# 🔹 Cargar variables del entorno
load_dotenv()

# 🔹 Asegurar acceso a /utils/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 🔹 Configurar intents y bot
INTENTS = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=INTENTS)

# ✅ Crear árbol de comandos Slash (Pycord 2.4+)
tree = app_commands.CommandTree(bot)

# 🔹 Estilos y control de tiempo
NUVIX_COLOR = 0x9b19ff
START = time.time()


# ============================
# 🔸 FUNCIONES AUXILIARES
# ============================

def logs_channel(guild):
    try:
        if LOGS_CMD_USE_CHANNEL_ID:
            ch = guild.get_channel(int(LOGS_CMD_USE_CHANNEL_ID))
            if isinstance(ch, discord.TextChannel):
                return ch
    except:
        pass


async def log_cmd(inter, name):
    """Registra el uso de comandos."""
    try:
        ch = logs_channel(inter.guild)
        if ch:
            await ch.send(f"`{inter.user}` used `/{name}` in {inter.channel.mention}")
    except:
        pass
    log_to_json("cmd_use.json", {
        "user": str(inter.user),
        "cmd": name,
        "ts": datetime.datetime.utcnow().isoformat()
    })


def emb(title, desc=""):
    """Crea un embed estándar."""
    e = discord.Embed(title=title, description=desc, color=NUVIX_COLOR)
    if BANNER_URL:
        e.set_thumbnail(url=BANNER_URL)
    if FOOTER_TEXT:
        e.set_footer(text=FOOTER_TEXT)
    return e


# ============================
# 🔸 EVENTOS
# ============================

@bot.event
async def on_ready():
    try:
        await tree.sync()
        print("✅ Slash commands synced successfully.")
    except Exception as e:
        print(f"⚠️ Sync error: {e}")
    print(f"{bot.user} is online!")


# ============================
# 🔸 COMANDOS SLASH
# ============================

@tree.command(name="ping", description="Check bot latency (Pong!)")
async def ping(inter: discord.Interaction):
    await log_cmd(inter, "ping")
    await inter.response.send_message(
        embed=emb("🏓 Pong!", f"Latency: `{round(bot.latency * 1000)}ms`"),
        ephemeral=True
    )


@tree.command(name="uptime", description="Show bot uptime")
async def uptime(inter: discord.Interaction):
    await log_cmd(inter, "uptime")
    secs = int(time.time() - START)
    h, r = divmod(secs, 3600)
    m, s = divmod(r, 60)
    await inter.response.send_message(embed=emb("⏱️ Uptime", f"`{h}h {m}m {s}s`"))


@tree.command(name="systemstatus", description="Show basic system status")
async def systemstatus(inter: discord.Interaction):
    await log_cmd(inter, "systemstatus")
    await inter.response.send_message(embed=emb("🖥️ System", "✅ All systems nominal."))


# ============================
# 🔸 EJECUTAR BOT
# ============================

def run():
    token = os.getenv("NUVIX_SYSTEM_TOKEN")
    if not token:
        raise SystemExit("❌ Missing token: NUVIX_SYSTEM_TOKEN")
    bot.run(token)


if __name__ == "__main__":
    run()
