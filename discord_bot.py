import os
import re
import logging
import discord
from discord.ext import commands

logging.basicConfig(level=logging.INFO)

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command()
async def imagine(ctx, *, prompt: str):
    prompt = re.sub(r"[^\w\s.,:;'\"!?()-]", "", prompt)
    await ctx.send(f"/imagine prompt: {prompt}")


@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"Error: {str(error)}")


if __name__ == "__main__":
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_BOT_TOKEN not set")
    bot.run(token)
