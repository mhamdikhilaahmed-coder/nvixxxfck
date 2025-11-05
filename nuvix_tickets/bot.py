# nuvix_tickets/bot.py
import os, sys, io, json, asyncio, datetime
from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# ---- rutas y utilidades ----
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import (
    BANNER_URL, FOOTER_TEXT, LOGS_CMD_USE_CHANNEL_ID,
    can_staff, can_highstaff_or_above, can_owner_or_coowner, log_to_json
)

load_dotenv()

# ---- configuración general ----
INTENTS = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=INTENTS)
tree = app_commands.CommandTree(bot)
NUVIX_COLOR = 0x9b19ff

# ---- categorías ----
TICKETS_CATEGORY_MAP = {
    "purchases": "🛒 purchases",
    "not_received": "⛔ not-received",
    "replace": "🛠 replace",
    "support": "💬 support",
}

DATA_DIR = "data"
TICKETS_DIR = os.path.join(DATA_DIR, "tickets_logs")
os.makedirs(TICKETS_DIR, exist_ok=True)


# =====================================================
# 🔸 FUNCIONES AUXILIARES
# =====================================================
def base_embed(title: str, desc: str = "") -> discord.Embed:
    e = discord.Embed(title=title, description=desc, color=NUVIX_COLOR)
    if BANNER_URL:
        e.set_thumbnail(url=BANNER_URL)
    if FOOTER_TEXT:
        e.set_footer(text=FOOTER_TEXT)
    return e


def logs_channel(guild: discord.Guild) -> Optional[discord.TextChannel]:
    try:
        if LOGS_CMD_USE_CHANNEL_ID:
            ch = guild.get_channel(int(LOGS_CMD_USE_CHANNEL_ID))
            if isinstance(ch, discord.TextChannel):
                return ch
    except Exception:
        pass
    return None


async def log_cmd(inter: discord.Interaction, name: str):
    """Guarda logs de comandos."""
    try:
        ch = logs_channel(inter.guild) if inter.guild else None
        if ch:
            await ch.send(f"`{inter.user}` used `/{name}` in {inter.channel.mention}")
    except Exception:
        pass
    log_to_json("cmd_use.json", {
        "user": str(inter.user),
        "cmd": name,
        "channel": getattr(inter.channel, "id", None),
        "ts": datetime.datetime.utcnow().isoformat()
    })


async def ensure_category(guild: discord.Guild, cat_name: str) -> discord.CategoryChannel:
    """Crea categorías automáticamente si no existen."""
    cat = discord.utils.get(guild.categories, name=cat_name)
    if cat:
        return cat
    overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False)}
    return await guild.create_category(cat_name, overwrites=overwrites, reason="Nuvix Tickets: auto-create category")


# =====================================================
# 🔸 SISTEMA DE TICKETS
# =====================================================
async def open_ticket(inter: discord.Interaction, kind: str):
    await log_cmd(inter, f"ticket_open:{kind}")
    guild = inter.guild
    assert guild is not None

    cat_name = TICKETS_CATEGORY_MAP.get(kind, "💬 support")
    category = await ensure_category(guild, cat_name)

    name = f"{inter.user.name}-{datetime.datetime.utcnow().strftime('%H%M%S')}"
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        inter.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
    }

    ch = await guild.create_text_channel(name=name, category=category, overwrites=overwrites)
    embed = base_embed(
        "🎫 Support Ticket",
        "Please wait until one of our support team members can help you.\nResponse time may vary to many factors, so please be patient."
    )
    embed.add_field(name="Assigned staff", value="Pending", inline=False)
    embed.add_field(name="❓ How can we help you?", value="Describe your issue below.", inline=False)
    embed.set_author(name=str(inter.user), icon_url=inter.user.display_avatar.url)

    view = TicketControls(ch_id=ch.id)
    await ch.send(embed=embed, view=view)
    await inter.response.send_message(embed=base_embed("✅ Ticket opened", f"Channel: {ch.mention}"), ephemeral=True)


# =====================================================
# 🔸 VISTA DE BOTONES
# =====================================================
class TicketControls(discord.ui.View):
    def __init__(self, ch_id: int):
        super().__init__(timeout=None)
        self.ch_id = ch_id

    # --- cerrar ticket ---
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close(self, inter: discord.Interaction, button: discord.ui.Button):
        ch = inter.channel
        try:
            # obtener usuario creador
            user = None
            async for msg in ch.history(limit=10, oldest_first=True):
                if msg.author != inter.client.user:
                    user = msg.author
                    break

            # crear transcript
            msgs = []
            async for m in ch.history(limit=1000, oldest_first=True):
                t = m.created_at.strftime("[%Y-%m-%d %H:%M:%S]")
                msgs.append(f"{t} {m.author}: {m.content}")

            buf = "\n".join(msgs).encode("utf-8")
            fname = f"transcript_{ch.name}_{int(discord.utils.utcnow().timestamp())}.txt"

            os.makedirs(TICKETS_DIR, exist_ok=True)
            with open(os.path.join(TICKETS_DIR, fname), "wb") as f:
                f.write(buf)

            file = discord.File(io.BytesIO(buf), filename=fname)

            # enviar transcript a logs
            log_ch = inter.client.get_channel(1432829786018939076)
            if log_ch:
                await log_ch.send(f"🎫 Ticket `{ch.name}` closed by {inter.user.mention}", file=file)

            # enviar al usuario
            if user:
                try:
                    await user.send("📄 Here is the transcript of your ticket:", file=file)
                except:
                    pass

            await inter.response.send_message("🔒 Ticket closed. Transcript sent!", ephemeral=True)
            await asyncio.sleep(3)
            await ch.delete()

        except Exception as e:
            print("Error closing ticket:", e)

    # --- asignar staff ---
    @discord.ui.button(label="Assign me", style=discord.ButtonStyle.success, emoji="👋")
    async def assign(self, inter: discord.Interaction, button: discord.ui.Button):
        await log_cmd(inter, "ticket_assign")
        ch = inter.guild.get_channel(self.ch_id)
        if not ch:
            return await inter.response.send_message("Channel not found.", ephemeral=True)
        await ch.send(f"{inter.user.mention} assigned themselves to this ticket.")
        await inter.response.send_message("✅ Assigned.", ephemeral=True)

    # --- transcript manual ---
    @discord.ui.button(label="Transcript", style=discord.ButtonStyle.secondary, emoji="🗒")
    async def transcript(self, inter: discord.Interaction, button: discord.ui.Button):
        await log_cmd(inter, "ticket_transcript")
        ch = inter.guild.get_channel(self.ch_id)
        if not ch:
            return await inter.response.send_message("Channel not found.", ephemeral=True)
        msgs = []
        async for m in ch.history(limit=1000, oldest_first=True):
            t = m.created_at.strftime("[%Y-%m-%d %H:%M:%S]")
            msgs.append(f"{t} {m.author}: {m.content}")
        buf = "\n".join(msgs).encode("utf-8")
        fname = f"transcript_{ch.id}_{int(discord.utils.utcnow().timestamp())}.txt"
        file = discord.File(io.BytesIO(buf), filename=fname)
        await inter.response.send_message("Transcript generated.", ephemeral=True)
        lg = logs_channel(inter.guild)
        if lg:
            await lg.send(f"🗒 Transcript ({ch.mention})", file=file)


# =====================================================
# 🔸 SELECTOR DE PANEL
# =====================================================
class OpenSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Purchases", description="To purchase products", emoji="🛒", value="purchases"),
            discord.SelectOption(label="Product not received", description="Support for products not received", emoji="⛔", value="not_received"),
            discord.SelectOption(label="Replace", description="Request product replacement", emoji="🛠", value="replace"),
            discord.SelectOption(label="Support", description="Receive support from the staff team", emoji="💬", value="support"),
        ]
        super().__init__(placeholder="Select a ticket category...", min_values=1, max_values=1, options=options)

    async def callback(self, inter: discord.Interaction):
        await open_ticket(inter, self.values[0])


class PanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(OpenSelect())


# =====================================================
# 🔸 EVENTOS Y COMANDOS
# =====================================================
@bot.event
async def on_ready():
    try:
        bot.add_view(PanelView())  # hace persistente el panel
        bot.add_view(TicketControls(ch_id=0))
        await tree.sync()
        print("✅ Slash commands synced successfully.")
    except Exception as e:
        print(f"⚠️ Sync error: {e}")
    print(f"{bot.user} is online!")


@tree.command(name="panel", description="Post the Nuvix ticket panel")
@commands.check(can_staff)
async def panel(inter: discord.Interaction):
    await log_cmd(inter, "panel")
    e = base_embed(
        "🎟️ Nuvix Market Tickets",
        "If you need help, select the type of ticket you want to open.\n**Response time may vary, so please be patient.**"
    )
    if BANNER_URL:
        e.set_image(url=BANNER_URL)
    await inter.response.send_message(embed=e, view=PanelView())


@tree.command(name="ping", description="Check bot latency (Pong!)")
async def ping(inter: discord.Interaction):
    await log_cmd(inter, "ping")
    embed = base_embed("🏓 Pong!", f"Latency: `{round(bot.latency * 1000)}ms`")
    await inter.response.send_message(embed=embed, ephemeral=True)


# =====================================================
# 🔸 EJECUTAR BOT
# =====================================================
def run():
    token = os.getenv("NUVIX_TICKETS_TOKEN")
    if not token:
        raise SystemExit("❌ Missing token: NUVIX_TICKETS_TOKEN")
    bot.run(token)


if __name__ == "__main__":
    run() me 
