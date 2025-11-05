# nuvix_machine/bot.py
import os
import sys
import json
import datetime
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from utils import BANNER_URL, FOOTER_TEXT, LOGS_CMD_USE_CHANNEL_ID, log_to_json, can_highstaff_or_above

# 🔹 Cargar variables desde .env
load_dotenv()

# 🔹 Asegurar acceso al módulo /utils/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 🔹 Configurar intents y bot
INTENTS = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=INTENTS)

# ✅ Crear árbol de comandos slash (requerido en Pycord 2.4+)
tree = app_commands.CommandTree(bot)

# 🔹 Colores y directorios
NUVIX_COLOR = 0x9b19ff
DATA_DIR = "data"
STOCK_DIR = os.path.join(DATA_DIR, "stock")
os.makedirs(STOCK_DIR, exist_ok=True)
STOCK_FILE = os.path.join(STOCK_DIR, "stock.json")

# 🔹 Funciones auxiliares
def read_stock():
    if not os.path.exists(STOCK_FILE):
        return {}
    with open(STOCK_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def write_stock(d):
    with open(STOCK_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)

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
    log_to_json("cmd_use.json", {
        "user": str(inter.user),
        "cmd": name,
        "ts": datetime.datetime.utcnow().isoformat()
    })

def emb(t, d=""):
    e = discord.Embed(title=t, description=d, color=NUVIX_COLOR)
    if BANNER_URL:
        e.set_thumbnail(url=BANNER_URL)
    if FOOTER_TEXT:
        e.set_footer(text=FOOTER_TEXT)
    return e

# 🔹 Eventos
@bot.event
async def on_ready():
    try:
        await tree.sync()
        print("✅ Slash commands synced successfully.")
    except Exception as e:
        print(f"⚠️ Sync error: {e}")
    print(f"{bot.user} is online!")

# 🔹 Comandos Slash
@tree.command(name="replace_add", description="Register a replacement for a user")
@commands.check(can_highstaff_or_above)
async def replace_add(inter: discord.Interaction, user: discord.User, product: str, reason: str):
    await log_cmd(inter, "replace_add")
    d = read_stock()
    d.setdefault("replacements", []).append({
        "user": user.id,
        "product": product,
        "reason": reason,
        "ts": datetime.datetime.utcnow().isoformat()
    })
    write_stock(d)
    await inter.response.send_message(embed=emb("Replacement Registered", f"{user.mention} • {product}\nReason: {reason}"))

@tree.command(name="stock_check", description="Check stock for a product")
async def stock_check(inter: discord.Interaction, product: str):
    await log_cmd(inter, "stock_check")
    d = read_stock()
    qty = d.get("stock", {}).get(product, 0)
    await inter.response.send_message(embed=emb("Stock", f"`{product}`: **{qty}**"))

@tree.command(name="ping", description="Check bot latency (Pong!)")
async def ping(inter: discord.Interaction):
    await log_cmd(inter, "ping")
    await inter.response.send_message(embed=emb("Pong!", f"Latency: `{round(bot.latency * 1000)}ms`"), ephemeral=True)

# 🔹 Ejecutar bot
def run():
    token = os.getenv("NUVIX_MACHINE_TOKEN")
    if not token:
        raise SystemExit("❌ Missing token: NUVIX_MACHINE_TOKEN")
    bot.run(token)

if __name__ == "__main__":
    run()
