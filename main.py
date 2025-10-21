import discord
import requests
import asyncio
import aiohttp
from io import BytesIO
from flask import Flask
from threading import Thread
import time
import random

# 🔐 Replace with your actual token securely
TOKEN = 'MTQyNjgzOTg1MjE4MzE5NTcyMg.GreWx3.l1IUseC07viSCUCPVFHH_X6mHZVodWuYTyHdsg'
CHANNEL_ID = 1429404403055595681  # Target channel ID
ROLE_ID = 1429404925091119205     # Role to ping

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

CAT_API_URL = 'https://api.thecatapi.com/v1/images/search'
cooldowns = {}  # user_id: last_used_timestamp

# 🐱 Fetch cat image from API
async def fetch_cat_file():
    response = requests.get(CAT_API_URL)
    data = response.json()
    cat_url = data[0]['url']

    async with aiohttp.ClientSession() as session:
        async with session.get(cat_url) as resp:
            if resp.status != 200:
                return None
            image_data = BytesIO(await resp.read())
            return discord.File(image_data, filename="cat.jpg")

# 🕊 Daily cat ritual
async def send_cat_image():
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"Channel with ID {CHANNEL_ID} not found.")
        return
    while not client.is_closed():
        try:
            file = await fetch_cat_file()
            if file:
                await channel.send(
                    "# Dailly Cat <:planner:1429435831508140173>\n"
                    "** **\n"
                    "**Car Of Today <:catwelcome:1426236639176560754> **\n\n"
                    f"<@&{ROLE_ID}>",
                    file=file
                )
            else:
                await channel.send("Could not fetch cat image 😿")
        except Exception as e:
            print(f"Error: {e}")
            await channel.send("Could not fetch cat image 😿")
        await asyncio.sleep(86400)  # 24 hours

# 🧿 Bot ready event
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    client.loop.create_task(send_cat_image())

# 🐾 Command handler
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower() == '!cat':
        user_id = message.author.id
        now = time.time()
        last_used = cooldowns.get(user_id, 0)

        if now - last_used < 60:
            remaining = int(60 - (now - last_used))
            await message.channel.send(f"{message.author.mention} please wait {remaining} seconds before summoning another cat 🐾")
            return

        cooldowns[user_id] = now

        try:
            file = await fetch_cat_file()
            if file:
                await message.channel.send(
                    f"{message.author.mention} summoned a cat 🐾",
                    file=file
                )
            else:
                await message.channel.send("Could not fetch cat image 😿")
        except Exception as e:
            print(f"Error: {e}")
            await message.channel.send("Could not fetch cat image 😿")

    elif message.content.lower() == '!facts':
        facts = [
            "Cats have five toes on their front paws, but only four on the back.",
            "A group of cats is called a clowder.",
            "Cats sleep for 70% of their lives.",
            "The oldest known pet cat was found in a 9,500-year-old grave on Cyprus.",
            "Cats can rotate their ears 180 degrees."
        ]
        fact = random.choice(facts)
        await message.channel.send(f"🐾 Cat Fact: {fact}")

# 🔁 Flask keep-alive server
app = Flask('')

@app.route('/')
def home():
    return "Shrine bot is alive."

def run():
    app.run(host='0.0.0.0', port=8081)

def keep_alive():
    Thread(target=run).start()

# 🚀 Launch rituals
keep_alive()
client.run(TOKEN)
