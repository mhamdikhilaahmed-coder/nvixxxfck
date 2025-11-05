# nuvix_sanctions/bot.py
import os
import sys
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from utils import (
    BANNER_URL,
    FOOTER_TEXT,
    LOGS_CMD_USE_CHANNEL_ID,
    can_staff,
    can_highstaff_or_above,
    can_owner_or_coowner,
    log_to_json
)

# 🔹 Cargar variables del .env
load_dotenv()

# 🔹 Asegurar acceso a /utils/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 🔹 Configurar intents y bot
INTENTS = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=INTENTS)

# ✅ Crear árbol de comandos Slash (Pycord 2.4+)
tree = app_commands.CommandTree(bot)
NUVIX_COLOR = 0x9b19ff


# 🔹 Función de logs
async def log_cmd_use(interaction: discord.Interaction, name: str):
    try:
        if LOGS_CMD_USE_CHANNEL_ID:
            ch = bot.get_channel(LOGS_CMD_USE_CHANNEL_ID)
            if ch:
                await ch.send(f"[{interaction.user}] used `/{name}` in <#{interaction.channel.id}>")
    except Exception:
        pass
    log_to_json("cmd_use.json", {
        "user": str(interaction.user),
        "cmd": name,
        "channel": interaction.channel.id
    })


def emb(title: str, desc: str = ""):
    embed = discord.Embed(title=title, description=desc, color=NUVIX_COLOR)
    if BANNER_URL:
        embed.set_thumbnail(url=BANNER_URL)
    if FOOTER_TEXT:
        embed.set_footer(text=FOOTER_TEXT)
    return embed


# 🔹 Evento de inicio
@bot.event
async def on_ready():
    try:
        await tree.sync()
        print("✅ Slash commands synced successfully.")
    except Exception as e:
        print(f"⚠️ Sync error: {e}")
    print(f"{bot.user} is online!")


# 🔹 Comando /ping
@tree.command(name="ping", description="Check bot latency (Pong!)")
async def ping(interaction: discord.Interaction):
    await log_cmd_use(interaction, "ping")
    await interaction.response.send_message(
        embed=emb("🏓 Pong!", f"Latency: `{round(bot.latency * 1000)}ms`"),
        ephemeral=True
    )


# 🔹 Comando /warn (solo High Staff+)
@tree.command(name="warn", description="Warn a member (High Staff+ only)")
@app_commands.describe(member="User to warn", reason="Reason")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    await log_cmd_use(interaction, "warn")
    if not can_highstaff_or_above(interaction.user):
        await interaction.response.send_message("🚫 Only High Staff+ can use this command.", ephemeral=True)
        return

    try:
        await member.send(f"You were warned in **{interaction.guild.name}**.\nReason: {reason}")
    except Exception:
        pass

    await interaction.response.send_message(
        embed=emb("⚠️ Member Warned", f"{member.mention} has been warned.\nReason: {reason}"),
        ephemeral=True
    )


# 🔹 Comando /ban (solo Owner/CoOwner)
@tree.command(name="ban", description="Ban a member (Owner/CoOwner only)")
@app_commands.describe(member="User to ban", reason="Reason")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str):
    await log_cmd_use(interaction, "ban")
    if not can_owner_or_coowner(interaction.user):
        await interaction.response.send_message("🚫 Only Owner/CoOwner can use this command.", ephemeral=True)
        return

    try:
        await member.ban(reason=reason)
        await interaction.response.send_message(
            embed=emb("🔨 Member Banned", f"{member} has been banned.\nReason: {reason}"),
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(
            embed=emb("❌ Ban Failed", str(e)),
            ephemeral=True
        )


# 🔹 Ejecutar el bot
def run():
    token = os.getenv("NUVIX_SANCTIONS_TOKEN")
    if not token:
        raise SystemExit("❌ Missing token: NUVIX_SANCTIONS_TOKEN")
    bot.run(token)


if __name__ == "__main__":
    run()
