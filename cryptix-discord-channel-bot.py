import discord
import aiohttp
import asyncio
from discord import app_commands

TOKEN = 'abcdefghgahde'
CHANNEL_ID_HASHRATE = 1111111111111111 
CHANNEL_ID_PRICE = 222222222222222   

API_URL_HASHRATE = "https://api.com"
API_URL_PRICE = "https://api.com"

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

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

@client.event
async def on_ready():
    print(f"Bot is logged in as {client.user}")
    await tree.sync()
    client.loop.create_task(update_channel_name())

@tree.command(name="cryptix-price", description="Show the current Cryptix price.")
async def cryptix_price_command(interaction: discord.Interaction):
    price = await fetch_price()
    if price is not None:
        await interaction.response.send_message(f"💲 Current Cryptix Price: {price:.6f} USDT")
    else:
        await interaction.response.send_message("Error fetching price.")

@tree.command(name="cryptix-hashrate", description="Show the current Cryptix hashrate.")
async def cryptix_hashrate_command(interaction: discord.Interaction):
    hashrate = await fetch_hashrate()
    if hashrate is not None:
        await interaction.response.send_message(f"🌐 Current Hashrate: {hashrate:.3f} TH/s")
    else:
        await interaction.response.send_message("Error fetching hashrate.")

async def update_channel_name():
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            hashrate = await fetch_hashrate()
            if hashrate is None:
                continue
            
            formatted_hashrate = f"🌐・{hashrate:.3f}-ths".replace('.', '_')
            price = await fetch_price()
            if price is None:
                continue
            
            formatted_price = f"💲・{price:.6f}-usdt".replace('.', '_')
            channel_hashrate = client.get_channel(CHANNEL_ID_HASHRATE)
            if channel_hashrate:
                new_name_hashrate = f"{formatted_hashrate}"
                if channel_hashrate.name != new_name_hashrate:
                    await channel_hashrate.edit(name=new_name_hashrate)
            channel_price = client.get_channel(CHANNEL_ID_PRICE)
            if channel_price:
                new_name_price = f"{formatted_price}"
                if channel_price.name != new_name_price:
                    await channel_price.edit(name=new_name_price)
        except discord.errors.HTTPException as e:
            if e.status == 429:
                retry_after = int(e.response.headers.get('Retry-After', 1))
                await asyncio.sleep(retry_after)
        except Exception as e:
            print(f"Error during channel update: {e}")
        await asyncio.sleep(240)

client.run(TOKEN)
