import discord 
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
import os 
import json
from datetime import time, timezone
import random

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

from keep_alive import keep_alive

DATA_FILE = "reminders.json"

med_gifs = [
    "https://cdn.discordapp.com/attachments/1171594421674967083/1486099443752374383/8aac6c5a_original.gif?ex=69c44575&is=69c2f3f5&hm=2bf8e100da90fd6e35f44045e9ae1eb9405e32483b28fee29401153d224ce32a&",
    "https://cdn.discordapp.com/attachments/1171594421674967083/1486100378360614956/687c815e_original.gif?ex=69c44654&is=69c2f4d4&hm=270c49e4df6e2c52dc20281cb09fed053665553a05216e4544196bf386898471&",
    "https://tenor.com/view/miku-hatsune-miku-kasane-teto-teto-neru-gif-1333595963665591686"
]


# --- STEP 1: AUTO-CREATE JSON FILE ---
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

reminder_data = load_data()

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# --- STEP 2: DEFINE BOTH TIMES ---
TIME_12AM = time(hour=12, minute=0, tzinfo=timezone.utc)
TIME_7AM = time(hour=7, minute=0, tzinfo=timezone.utc)

# Existing 11 AM Reminder
@tasks.loop(time=TIME_12AM)
async def reminder_12am():
    for user_id, channel_id in reminder_data.items():
        channel = bot.get_channel(int(channel_id))
        user = await bot.fetch_user(int(user_id))
        if channel and user:
            await channel.send(f"{user.mention} IT IS 12:00 PM! TAKE YOUR MEDICATION!!!", str(random.choice(med_gifs)))

# NEW 7 AM Reminder
@tasks.loop(time=TIME_7AM)
async def reminder_7am():
    for user_id, channel_id in reminder_data.items():
        channel = bot.get_channel(int(channel_id))
        user = await bot.fetch_user(int(user_id))
        if channel and user:
            await channel.send(f"{user.mention} GUTEN MORGEN! IT IS 7:00 AM. TAKE YOUR MEDS!!!", str(random.choice(med_gifs)))

@bot.event
async def on_ready(): 
    print(f"MEDICATION BOT ONLINE: {bot.user.name}")
    # Start both loops
    if not reminder_12am.is_running():
        reminder_12am.start()
    if not reminder_7am.is_running():
        reminder_7am.start()

@bot.command()
async def remindme(ctx):
    reminder_data[str(ctx.author.id)] = ctx.channel.id
    save_data(reminder_data)
    await ctx.send(f"AYE AYE {ctx.author.mention}")

@bot.command()
async def stop(ctx):
    """Removes user from daily reminders"""
    user_id_str = str(ctx.author.id)
    if user_id_str in reminder_data:
        del reminder_data[user_id_str]
        save_data(reminder_data)
        await ctx.send(f"NO MORE REMINDERS FOR {ctx.author.mention}. LOCK IN!")
    else:
        await ctx.send(f"SET A REMINDER FIRST, {ctx.author.mention}.")

@bot.command()
async def miku(ctx):
    random_gif = random.choice(med_gifs)
    await ctx.send(random_gif)

@bot.command()
async def vexes(ctx):
    await ctx.send(("https://www.youtube.com/watch?v=OqT1UHI6JKQ"))

@bot.command()
async def commands(ctx):
    await ctx.send("MY COMMANDS ARE !remindme AND !stop. YOU CAN GUESS WHAT THEY DO. ALSO TRY !miku and !vexes !!!!!!!!!!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if bot.user.mentioned_in(message):
        await message.channel.send("FUCK YOU")
        
    if "meds" in message.content.lower():
        await message.channel.send(f"{message.author.mention} TAKE YOUR MEDS")
    await bot.process_commands(message)
    if "retard" in message.content.lower():
        await message.channel.send(f"{message.author.mention} NO ABLEIST SLURS IN GENERAL")
    if "drugs" in message.content.lower():
        await message.channel.send(f"OH GOD PLEASE STOP")
    if "medicine" in message.content.lower():
        await message.channel.send(f"have you tried the medicine drug?")
    

if __name__ == "__main__":
    keep_alive()  # <--- START THE FLASK SERVER
    bot.run(token, log_handler=handler, log_level=logging.DEBUG)