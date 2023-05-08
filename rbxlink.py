import discord
from discord.ext import commands
from discord import Activity, ActivityType, Status
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


def generate_code():
    words = ['apple', 'banana', 'cherry', 'dragon', 'elephant', 'flamingo', 'giraffe', 'hedgehog', 'iguana', 'jaguar', "racecar", "army", "military", "cool", "bat", "juice", "angel", "wings", "reindeer",
             "elk", "moose", "mouse", "tesla", "yeti", "peach", "roblox", "developer", "script", "lua", "part", "block", "python", "snake", "curl", "firefighter", "fire", "arm", "leg", "body"]
    return ' '.join(random.sample(words, 6))


# function to check if user's about me contains verification code
def check_about_me(user_id, verification_code):
    url = f"https://users.roblox.com/v1/users/{user_id}"
    response = requests.get(url)
    if response.status_code == 200:
        about_me = response.json()['description']
        if verification_code in about_me:
            return True
    return False


@bot.command()
async def getkey(ctx):
    if ctx.author.id not in verified_users:
        await ctx.send("You need to verify your Roblox account first. Use the `!verify` command to verify.")
        return

    key = ''
    let = string.ascii_letters
    num = string.digits
    ran = string.punctuation
    preJoin = [random.choice(let+num+ran) for i in range(20)]
    key = ''.join(preJoin)

    expires_in = 86400 - (ctx.message.created_at.timestamp() -
                          verified_users[ctx.author.id]['verified_time'])
    embed = discord.Embed(title="Key", color=0x00ff00)
    embed.add_field(name="Key:", value=f"``{key}``", inline=False)
    embed.add_field(name="Expires:",
                    value=f"<t:{int(ctx.message.created_at.timestamp() + expires_in)}:R>", inline=True)
    await ctx.author.send(embed=embed)

    # send key to web server
    requests.post('https://rblx-link.herokuapp.com/get_key', json={
        'user_id': verified_users[ctx.author.id]['roblox_user_id'],
        'key': key
    })


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
        msg = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=30.0)
        roblox_user_id = int(msg.content)
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond. Please try again.")
        return
    except ValueError:
        await ctx.send("Invalid user ID. Please try again.")
        return

    verification_code = generate_code()
    await ctx.send(f"Please set your About section to include the following code: **{verification_code}**\nType `done` once you have added it.")
    try:
        msg = await bot.wait_for("message", check=lambda m: m.author == ctx.author and m.content == "done", timeout=300.0)
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond. Please try again.")
        return

    if not check_about_me(roblox_user_id, verification_code):
        await ctx.send("Could not verify your Roblox account. Please make sure your About section includes the verification code.")
        return

    verified_users[ctx.author.id] = {
        'roblox_user_id': roblox_user_id, 'verified_time': ctx.message.created_at.timestamp()}

    with open("verified_users.json", "w") as f:
        json.dump(verified_users, f)

    await ctx.send("Successfully verified your Roblox account!")


bot.run(DISCORD_BOT_TOKEN)
