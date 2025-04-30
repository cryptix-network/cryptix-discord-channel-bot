import discord
import aiohttp
import asyncio

TOKEN = 'abcdefghgahde'
CHANNEL_ID_HASHRATE = 1111111111111111 
CHANNEL_ID_PRICE = 222222222222222   

API_URL_HASHRATE = "https://api.com"
API_URL_PRICE = "https://api.com"

intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def fetch_hashrate():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL_HASHRATE) as response:
                data = await response.json()
                print(f"Hashrate API Response: {data}") 
                return round(data['hashrate'], 3)
    except Exception as e:
        print(f"Error fetching hashrate: {e}")
        return None

async def fetch_price():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL_PRICE) as response:
                data = await response.json()
                print(f"Price API Response: {data}")  
                return round(data['price'], 6)
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None

async def update_channel_name():
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            hashrate = await fetch_hashrate()
            if hashrate is None:
                print("Skipping hashrate update due to error.")
                continue  
            
            formatted_hashrate = f"🌐・{hashrate:.3f}-ths".replace('.', '_')
            print(f"Hashrate: {formatted_hashrate} ths")
            
            price = await fetch_price()
            if price is None:
                print("Skipping price update due to error.")
                continue 
            
            formatted_price = f"💲・{price:.6f}-usdt".replace('.', '_')
            print(f"Price: {formatted_price} USDT")
            
            channel_hashrate = client.get_channel(CHANNEL_ID_HASHRATE)
            if channel_hashrate:
                print(f"Found Hashrate channel: {channel_hashrate.name}") 
                new_name_hashrate = f"{formatted_hashrate}"
                if channel_hashrate.name != new_name_hashrate:
                    await channel_hashrate.edit(name=new_name_hashrate)
                    print(f"Updated channel name to: {new_name_hashrate}")
                else:
                    print("Hashrate unchanged, no update needed.")
            else:
                print("Hashrate channel not found!")
            
            channel_price = client.get_channel(CHANNEL_ID_PRICE)
            if channel_price:
                print(f"Found Price channel: {channel_price.name}")  
                new_name_price = f"{formatted_price}"
                if channel_price.name != new_name_price:
                    await channel_price.edit(name=new_name_price)
                    print(f"Updated channel name to: {new_name_price}")
                else:
                    print("Price unchanged, no update needed.")
            else:
                print("Price channel not found!")

        except discord.errors.HTTPException as e:
            if e.status == 429:
                retry_after = int(e.response.headers.get('Retry-After', 1))
                print(f"Rate limit hit, retrying after {retry_after} seconds...")
                await asyncio.sleep(retry_after)  
            else:
                print(f"HTTP Error during channel update: {e}")
        
        except Exception as e:
            print(f"Error during channel update: {e}")

        await asyncio.sleep(240)

@client.event
async def on_ready():
    print(f"Bot is logged in as {client.user}")
    client.loop.create_task(update_channel_name())

client.run(TOKEN)
