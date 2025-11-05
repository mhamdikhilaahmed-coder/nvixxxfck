# nuvix_invoices/bot.py
import os
import sys
import datetime
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from utils import BANNER_URL, FOOTER_TEXT, LOGS_CMD_USE_CHANNEL_ID, log_to_json, can_staff

# 🔹 Cargar variables desde .env
load_dotenv()

# 🔹 Asegurar acceso a /utils/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

INTENTS = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=INTENTS)

# ✅ Crear árbol de comandos slash (necesario para Pycord 2.4+)
tree = app_commands.CommandTree(bot)
NUVIX_COLOR = 0x9b19ff


def logs_channel(guild: discord.Guild):
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


@bot.event
async def on_ready():
    try:
        await tree.sync()
        print("✅ Slash commands synced successfully.")
    except Exception as e:
        print(f"⚠️ Sync error: {e}")
    print(f"{bot.user} is online!")


@tree.command(name="invoice_create", description="Create a new invoice")
@commands.check(can_staff)
async def invoice_create(inter: discord.Interaction, user: discord.User, amount: float, note: str):
    await log_cmd(inter, "invoice_create")
    await inter.response.send_message(embed=emb(
        "Invoice created",
        f"For: {user.mention}\nAmount: **{amount:.2f}**\nNote: {note}"
    ))


@tree.command(name="invoice_status", description="Check an invoice status")
async def invoice_status(inter: discord.Interaction, invoice_id: str):
    await log_cmd(inter, "invoice_status")
    await inter.response.send_message(embed=emb(
        "Invoice status",
        f"Invoice `{invoice_id}` is **Pending**"
    ))


@tree.command(name="ping", description="Check bot latency (Pong!)")
async def ping(inter: discord.Interaction):
    await log_cmd(inter, "ping")
    await inter.response.send_message(
        embed=emb("Pong!", f"Latency: `{round(bot.latency * 1000)}ms`"),
        ephemeral=True
    )


def run():
    token = os.getenv("NUVIX_INVOICES_TOKEN")
    if not token:
        raise SystemExit("❌ Missing token: NUVIX_INVOICES_TOKEN")
    bot.run(token)


if __name__ == "__main__":
    run()
