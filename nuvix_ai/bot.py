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

# 🔹 Cargar el archivo .env desde la carpeta principal
load_dotenv()

# 🔹 Leer los IDs de los canales desde el .env
LOGS_CMD_USE_CHANNEL_ID = int(os.getenv("LOGS_CMD_USE_CHANNEL_ID", 0))
TICKETS_LOGS_CHANNEL_ID = int(os.getenv("TICKETS_LOGS_CHANNEL_ID", 0))
PRIVATE_BOT_LOGS_CHANNEL_ID = int(os.getenv("PRIVATE_BOT_LOGS_CHANNEL_ID", 0))

# 🔧 CORRECCIÓN AQUÍ: usa __file__, no file
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

INTENTS = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=INTENTS)

# ✅ Crea la instancia para slash commands
tree = app_commands.CommandTree(bot)

async def log_cmd_use(interaction: discord.Interaction, name: str):
    try:
        if LOGS_CMD_USE_CHANNEL_ID:
            ch = interaction.client.get_channel(LOGS_CMD_USE_CHANNEL_ID)
            if ch:
                await ch.send(f"[{interaction.user}] used /{name} in <#{interaction.channel.id}>")
    except Exception:
        pass
    log_to_json("cmd_use.json", {"user": str(interaction.user), "cmd": name, "channel": interaction.channel.id})

@bot.event
async def on_ready():
    try:
        await tree.sync()
        print("✅ Slash commands synced successfully.")
    except Exception as e:
        print("⚠️ Error syncing slash commands:", e)
    print(f"{bot.user} is online!")

@tree.command(name="ping", description="Check bot latency (Pong!)")
async def ping(interaction: discord.Interaction):
    await log_cmd_use(interaction, "ping")
    embed = discord.Embed(title="Pong!", description=f"Latency: {round(bot.latency*1000)}ms")
    if BANNER_URL:
        embed.set_image(url=BANNER_URL)
    embed.set_footer(text=FOOTER_TEXT)
    await interaction.response.send_message(embed=embed, ephemeral=True)

def run(token_env: str):
    token = os.getenv(token_env)
    if not token:
        raise SystemExit(f"Missing token env: {token_env}")
    bot.run(token)

# 🔧 CORRECCIÓN AQUÍ: usa __name__, no name
if __name__ == "__main__":
    run("NUVIX_AI_TOKEN")
