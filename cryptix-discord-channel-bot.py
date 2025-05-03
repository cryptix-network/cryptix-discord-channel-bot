import discord
import aiohttp
import asyncio
from discord import app_commands

# ========== CONFIG ==========
TOKEN = '123213123123123123123213'

CHANNEL_ID_HASHRATE = 111111111111111
CHANNEL_ID_PRICE = 22222222222222222
CHANNEL_ID_VOLUME = 33333333333333333

API_URL_HASHRATE = "https://rest.seed1.cryptix-network.org/info/hashrate?stringOnly=false"
API_URL_PRICE = "https://rest.seed1.cryptix-network.org/info/price"
API_URL_MARKET = "https://market.cryptix-network.org/api/data"

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# ========== API FETCH FUNCTIONS ==========

async def fetch_hashrate():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL_HASHRATE) as response:
                data = await response.json()
                return round(data['hashrate'], 3)
    except Exception as e:
        print(f"Error fetching hashrate: {e}")
        return None

async def fetch_price():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL_PRICE) as response:
                data = await response.json()
                return round(data['price'], 6)
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

async def fetch_volume_24h():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL_MARKET) as response:
                data = await response.json()
                return round(float(data.get("target_volume_usdt", 0.0)), 2)
    except Exception as e:
        print(f"Error fetching 24h volume: {e}")
        return None

# ========== SLASH COMMANDS ==========

@tree.command(name="cryptix-price", description="Show the current Cryptix price in USDT.")
async def cryptix_price_command(interaction: discord.Interaction):
    price = await fetch_price()
    if price is not None:
        await interaction.response.send_message(f"💲 Current Cryptix Price: {price:.6f} USDT")
    else:
        await interaction.response.send_message("⚠️ Error fetching price.")

@tree.command(name="cryptix-hashrate", description="Show the current Cryptix network hashrate.")
async def cryptix_hashrate_command(interaction: discord.Interaction):
    hashrate = await fetch_hashrate()
    if hashrate is not None:
        await interaction.response.send_message(f"🌐 Current Hashrate: {hashrate:.3f} TH/s")
    else:
        await interaction.response.send_message("⚠️ Error fetching hashrate.")

@tree.command(name="cryptix-volume", description="Show the 24h trading volume of Cryptix.")
async def cryptix_volume_command(interaction: discord.Interaction):
    volume = await fetch_volume_24h()
    if volume is not None:
        await interaction.response.send_message(f"📊 24h Trading Volume: {volume:.2f} USDT")
    else:
        await interaction.response.send_message("⚠️ Error fetching 24h volume.")

# ========== CHANNEL NAME UPDATER ==========

async def update_channel_names():
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            hashrate = await fetch_hashrate()
            price = await fetch_price()
            volume = await fetch_volume_24h()

            if hashrate:
                formatted_hashrate = f"🌐・{hashrate:.3f}-ths".replace('.', '_')
                channel = client.get_channel(CHANNEL_ID_HASHRATE)
                if channel and channel.name != formatted_hashrate:
                    await channel.edit(name=formatted_hashrate)

            if price:
                formatted_price = f"💲・{price:.6f}-usdt".replace('.', '_')
                channel = client.get_channel(CHANNEL_ID_PRICE)
                if channel and channel.name != formatted_price:
                    await channel.edit(name=formatted_price)

            if volume:
                formatted_volume = f"📊・{volume:.2f}-vol".replace('.', '_')
                channel = client.get_channel(CHANNEL_ID_VOLUME)
                if channel and channel.name != formatted_volume:
                    await channel.edit(name=formatted_volume)

        except discord.errors.HTTPException as e:
            if e.status == 429:
                retry_after = int(e.response.headers.get('Retry-After', 1))
                await asyncio.sleep(retry_after)
        except Exception as e:
            print(f"Error during channel update: {e}")
        await asyncio.sleep(240)  # update every 4 minutes

# ========== BOT STARTUP ==========

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")
    await tree.sync()
    print("✅ Slash commands registered")
    client.loop.create_task(update_channel_names())

client.run(TOKEN)
