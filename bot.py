import discord
from discord.ext import tasks, commands
import asyncio
import os

intents = discord.Intents.default()
intents.voice_states = True 

bot = commands.Bot(command_prefix="!", intents=intents)

VOICE_CHANNEL_ID = int(os.environ.get('VOICE_CHANNEL_ID'))
SOUND_FILE = "B77CEE08-6AB2-4F60-BEFA-B339E12B1A98.mp3"
 

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}')
    hourly_sound_loop.start() 

@tasks.loop(hours=1)
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

bot.run(os.environ.get('DISCORD_TOKEN'))
