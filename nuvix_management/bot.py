# nuvix_management/bot.py
import os
import sys
import datetime
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from utils import (
    BANNER_URL,
    FOOTER_TEXT,
    LOGS_CMD_USE_CHANNEL_ID,
    log_to_json,
    can_owner_or_coowner
)

# 🔹 Cargar variables del .env
load_dotenv()

# 🔹 Asegurar acceso a utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 🔹 Configurar intents y bot
INTENTS = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=INTENTS)

# ✅ Crear árbol de comandos Slash (necesario para Pycord 2.4+)
tree = app_commands.CommandTree(bot)
NUVIX_COLOR = 0x9b19ff


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


@bot.event
async def on_ready():
    try:
        await tree.sync()
        print("✅ Slash commands synced successfully.")
    except Exception as e:
        print(f"⚠️ Sync error: {e}")
    print(f"{bot.user} is online!")


# 🔹 Comandos de gestión
@tree.command(name="addrole", description="Add a role to a user")
@commands.check(can_owner_or_coowner)
async def addrole(inter: discord.Interaction, user: discord.Member, role: discord.Role):
    await log_cmd(inter, "addrole")
    try:
        await user.add_roles(role, reason="Nuvix Management")
        await inter.response.send_message(embed=emb("✅ Role Added", f"Added {role.mention} to {user.mention}"))
    except Exception as e:
        await inter.response.send_message(embed=emb("❌ Error", str(e)), ephemeral=True)


@tree.command(name="removerole", description="Remove a role from a user")
@commands.check(can_owner_or_coowner)
async def removerole(inter: discord.Interaction, user: discord.Member, role: discord.Role):
    await log_cmd(inter, "removerole")
    try:
        await user.remove_roles(role, reason="Nuvix Management")
        await inter.response.send_message(embed=emb("✅ Role Removed", f"Removed {role.mention} from {user.mention}"))
    except Exception as e:
        await inter.response.send_message(embed=emb("❌ Error", str(e)), ephemeral=True)


@tree.command(name="stafflist", description="List staff members online")
async def stafflist(inter: discord.Interaction, role: discord.Role):
    await log_cmd(inter, "stafflist")
    online = [m.mention for m in role.members if m.status != discord.Status.offline]
    await inter.response.send_message(embed=emb("🧑‍💼 Staff Online", ", ".join(online) or "No one is online right now."))


@tree.command(name="ping", description="Check bot latency (Pong!)")
async def ping(inter: discord.Interaction):
    await log_cmd(inter, "ping")
    await inter.response.send_message(
        embed=emb("🏓 Pong!", f"Latency: `{round(bot.latency * 1000)}ms`"),
        ephemeral=True
    )


# 🔹 Ejecutar bot
def run():
    token = os.getenv("NUVIX_MANAGEMENT_TOKEN")
    if not token:
        raise SystemExit("❌ Missing token: NUVIX_MANAGEMENT_TOKEN")
    bot.run(token)


if __name__ == "__main__":
    run()
