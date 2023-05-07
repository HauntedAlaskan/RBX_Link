import discord
from discord.ext import commands
import string
import asyncio
import random
import requests

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

verified_users = {}  # stores verified user IDs

# verification code generator function


def generate_code():
    words = ['apple', 'banana', 'cherry', 'dragon', 'elephant',
             'flamingo', 'giraffe', 'hedgehog', 'iguana', 'jaguar']
    return '-'.join(random.sample(words, 3))


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
    # check if user is verified
    if ctx.author.id not in verified_users:
        await ctx.send("You need to verify your Roblox account first. Use the `!verify` command to verify.")
        return

    # generate key
    key = ''
    let = string.ascii_letters
    num = string.digits
    ran = string.punctuation
    preJoin = [random.choice(let+num+ran) for i in range(20)]
    key = ''.join(preJoin)

    # send key as embed
    expires_in = 86400 - (ctx.message.created_at.timestamp() -
                          verified_users[ctx.author.id]['verified_time'])
    embed = discord.Embed(title="Key", color=0x00ff00)
    embed.add_field(name="Key:", value=f"``{key}``", inline=False)
    embed.add_field(name="Expires:",
                    value=f"<t:{int(ctx.message.created_at.timestamp() + expires_in)}:R>", inline=False)
    await ctx.author.send(embed=embed)


@bot.command()
async def verify(ctx):

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

    await ctx.send("Successfully verified your Roblox account!")

bot.run('MTEwNDU0MzQ4Nzg5NjA1OTkzNQ.GIqRxl.DgiJyrv4ncojXFJz60GmIxGvFwftRlVnaTzruU')
