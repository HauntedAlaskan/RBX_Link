import discord
from discord.ext import commands
from discord import Activity, ActivityType, Status
import datetime
import string
import asyncio
import random
import requests
import os
import json


DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

verified_users = {}


@bot.event
async def on_ready():
    await bot.change_presence(
        activity=Activity(
            type=ActivityType.watching,
            name="you through the bushes"
        ),
        status=Status.online
    )


if os.path.isfile("verified_users.json"):
    with open("verified_users.json", "r") as f:
        verified_users = json.load(f)


keys = {}


def generate_code():
    words = ['apple', 'banana', 'cherry', 'dragon', 'elephant', 'flamingo', 'giraffe', 'hedgehog', 'iguana', 'jaguar', "racecar", "army", "military", "cool", "bat", "juice", "angel", "wings", "reindeer",
             "elk", "moose", "mouse", "tesla", "yeti", "peach", "roblox", "developer", "script", "lua", "part", "block", "python", "snake", "curl", "firefighter", "fire", "arm", "leg", "body"]
    return ' '.join(random.sample(words, 6))


def check_about_me(user_id, verification_code):
    url = f"https://users.roblox.com/v1/users/{user_id}"
    response = requests.get(url)

    if response.status_code != 200:
        return False

    about_me = response.json().get('description', '').lower()
    verification_code = verification_code.lower()

    return verification_code in about_me


@bot.command()
async def getkey(ctx):
    if not os.path.isfile("verified_users.json"):
        await ctx.send("You need to verify your Roblox account first. Use the `!verify` command to verify.")
        return

    with open("verified_users.json", "r") as f:
        verified_users_json = json.load(f)

    if str(ctx.author.id) not in verified_users_json:
        await ctx.send("You need to verify your Roblox account first. Use the `!verify` command to verify.")
        return

    verified_users[ctx.author.id] = verified_users_json[str(ctx.author.id)]

    key = ''.join(random.choice(string.ascii_letters +
                                string.digits + string.punctuation) for i in range(20))

    verified_time = datetime.datetime.fromtimestamp(
        verified_users[ctx.author.id]['verified_time'])
    expires_in = 86400 - (datetime.datetime.now() -
                          verified_time).total_seconds()

    embed = discord.Embed(title="Key", color=0x00ff00)
    embed.add_field(name="Key:", value=f"``{key}``", inline=False)
    embed.add_field(
        name="Expires:", value=f"<t:{int(datetime.datetime.now().timestamp() + expires_in)}:R>", inline=True)

    await ctx.author.send(embed=embed)

    # Send the key to the Flask server
    url = 'http://127.0.0.1:8000/getkey'
    payload = {
        'user_id': verified_users[ctx.author.id]['roblox_user_id'],
        'key': key
    }

    response = requests.post(url, json=payload)
    if response.status_code == 200:
        await ctx.send("Key sent successfully.")
    else:
        await ctx.send("Failed to send the key to the server.")


@bot.command()
async def verify(ctx):
    if ctx.author.id in verified_users:
        await ctx.send("You have already verified your Roblox account. Use the `!getkey` command to get your key.")
        return

    if os.path.isfile("verified_users.json"):
        with open("verified_users.json", "r") as f:
            verified_users_json = json.load(f)
        if str(ctx.author.id) in verified_users_json:
            verified_users[ctx.author.id] = verified_users_json[str(
                ctx.author.id)]
            await ctx.send("You have already verified your Roblox account. Use the `!getkey` command to get your key.")
            return

    await ctx.send("Please enter your Roblox user ID.")
    try:
        msg = await bot.wait_for(
            "message",
            check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
            timeout=30.0,
        )
        roblox_user_id = int(msg.content)
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond. Please try again.")
        return
    except ValueError:
        await ctx.send("Invalid user ID. Please try again.")
        return

    verification_code = generate_code()
    await ctx.send(
        f"Please set your About section to include the following code: **{verification_code}**\nType `done` once you have added it."
    )
    try:
        msg = await bot.wait_for(
            "message",
            check=lambda m: m.author == ctx.author and m.content == "done",
            timeout=300.0,
        )
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond. Please try again.")
        return

    if not check_about_me(roblox_user_id, verification_code):
        await ctx.send("Could not verify your Roblox account. Please make sure your About section includes the verification code.")
        return

    verified_users[ctx.author.id] = {
        "roblox_user_id": roblox_user_id,
        "verified_time": ctx.message.created_at.timestamp(),
    }

    with open("verified_users.json", "w") as f:
        json.dump(verified_users, f)

    await ctx.send("Successfully verified your Roblox account!")


bot.run("MTEwNDU0MzQ4Nzg5NjA1OTkzNQ.GJn3BF.iOezniMbR3GL2bU2LV0NZCEbJ-X4yNy7FAOUhM")
