import os
from dotenv import load_dotenv

# 🔹 Cargar el archivo .env desde la carpeta principal
load_dotenv()

# 🔹 Leer los IDs de los canales desde el .env
LOGS_CMD_USE_CHANNEL_ID = int(os.getenv("LOGS_CMD_USE_CHANNEL_ID", 0))
TICKETS_LOGS_CHANNEL_ID = int(os.getenv("TICKETS_LOGS_CHANNEL_ID", 0))
PRIVATE_BOT_LOGS_CHANNEL_ID = int(os.getenv("PRIVATE_BOT_LOGS_CHANNEL_ID", 0))

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from utils import BANNER_URL, FOOTER_TEXT, LOGS_CMD_USE_CHANNEL_ID, can_staff, can_highstaff_or_above, can_owner_or_coowner, log_to_json

load_dotenv()

INTENTS = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=INTENTS)

async def log_cmd_use(interaction: discord.Interaction, name: str):
    try:
        if LOGS_CMD_USE_CHANNEL_ID:
            ch = interaction.client.get_channel(LOGS_CMD_USE_CHANNEL_ID)
            if ch:
                await ch.send(f"[{interaction.user}] used `/{name}` in <#{interaction.channel.id}>")
    except Exception:
        pass
    log_to_json("cmd_use.json", {"user": str(interaction.user), "cmd": name, "channel": interaction.channel.id})

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
    except Exception as e:
        print("Sync error:", e)
    print(f"{bot.user} is online!")

@bot.tree.command(name="ping", description="Check bot latency (Pong!)")
async def ping(interaction: discord.Interaction):
    await log_cmd_use(interaction, "ping")
    embed = discord.Embed(title="Pong!", description=f"Latency: {round(bot.latency*1000)}ms")
    if BANNER_URL:
        embed.set_image(url=BANNER_URL)
    embed.set_footer(text=FOOTER_TEXT)
    await interaction.response.send_message(embed=embed, ephemeral=True)

def run(token_env: str):
    import os
    token = os.getenv(token_env)
    if not token:
        raise SystemExit(f"Missing token env: {token_env}")
    bot.run(token)

from discord import app_commands

@bot.tree.command(name="warn", description="Warn a member (High Staff+ only)")
@app_commands.describe(member="User to warn", reason="Reason")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    await log_cmd_use(interaction, "warn")
    from utils import can_highstaff_or_above
    if not can_highstaff_or_above(interaction.user):
        await interaction.response.send_message("Only High Staff+ can warn.", ephemeral=True)
        return
    await interaction.response.send_message(f"{member.mention} has been warned. Reason: {reason}", ephemeral=True)
    try:
        await member.send(f"You were warned in **{interaction.guild.name}**. Reason: {reason}")
    except Exception:
        pass

@bot.tree.command(name="ban", description="Ban a member (Owner/CoOwner only)")
@app_commands.describe(member="User to ban", reason="Reason")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str):
    await log_cmd_use(interaction, "ban")
    from utils import can_owner_or_coowner
    if not can_owner_or_coowner(interaction.user):
        await interaction.response.send_message("Only Owner/CoOwner can ban.", ephemeral=True)
        return
    try:
        await member.ban(reason=reason)
        await interaction.response.send_message(f"{member} banned. Reason: {reason}", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to ban: {e}", ephemeral=True)

if __name__ == "__main__":
    run("NUVIX_SANCTIONS_TOKEN")
