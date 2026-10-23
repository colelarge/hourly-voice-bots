import discord
from discord.ext import tasks, commands
import asyncio
import os
import datetime
from zoneinfo import ZoneInfo  # Direct timezone tracker
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is online!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.voice_states = True 

bot = commands.Bot(command_prefix="!", intents=intents)

VOICE_CHANNEL_ID = int(os.environ.get('VOICE_CHANNEL_ID'))
SOUND_FILE = "B77CEE08-6AB2-4F60-BEFA-B339E12B1A98.mp3" 

# Direct Ohio Time Array: Forces the loop to run at :00 matching America/New_York clock
OHIO_TZ = ZoneInfo("America/New_York")
OHIO_TIMES = [datetime.time(hour=h, minute=0, tzinfo=OHIO_TZ) for h in range(24)]

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}')
    hourly_sound_loop.start() 

@tasks.loop(time=OHIO_TIMES)
async def hourly_sound_loop():
    await bot.wait_until_ready()
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    
    if isinstance(channel, discord.VoiceChannel):
        human_count = sum(1 for member in channel.members if not member.bot)
        
        if human_count == 0:
            print(f"Skipping top of the hour: No users in voice channel.")
            return
            
        try:
            vc = await channel.connect() 
            source = discord.FFmpegPCMAudio(SOUND_FILE)
            vc.play(source)
            
            while vc.is_playing():
                await asyncio.sleep(1) 
                
            await vc.disconnect() 
            
        except Exception as e:
            print(f"Error in voice loop: {e}")

keep_alive()
bot.run(os.environ.get('DISCORD_TOKEN'))
