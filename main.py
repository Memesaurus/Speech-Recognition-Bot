import discord
from discord.ext import commands, tasks
import voskASR
import config
import speech_recognition as sr
import vosk
import time

with open(config.badWordsData, "r", encoding="utf-8") as f:
    badWords = f.read().splitlines()

intents = discord.Intents(messages=True, guilds=True, voice_states=True, message_content=True)
client = commands.Bot(intents=intents)
recognizer = sr.Recognizer()
recognizer.vosk_model = vosk.Model(config.modelPath)
asr_parse_freq = 5


@client.event
async def on_ready():
    print(f'Rdy as {client.user}')


@client.slash_command(name="join", description="Join voice chat")
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()
    await start_record(ctx)
    end_record.start(ctx)


async def narik_caught(ctx, user):
    await ctx.channel.send(f"{user.mention} попался нарик!")


@client.slash_command(name="stop", description="stop recording")
async def stop(ctx):
    end_record.stop()
    await end_record(ctx)


async def start_record(ctx):
    ctx.voice_client.start_recording(discord.sinks.WaveSink(), record_finish_callback, ctx)
    print(str(time.time()) + f" RECORD START, ending in {asr_parse_freq}s")


@tasks.loop(seconds=asr_parse_freq)
async def end_record(ctx):
    print(ctx.voice_client.decoder)
    ctx.voice_client.stop_recording()
    print(str(time.time()) + " RECORD END")


async def record_finish_callback(sink, ctx):
    await start_record(ctx)
    for user_id, audio in sink.audio_data.items():
        user = await client.fetch_user(user_id)
        file = discord.File(audio.file, user.name)
        if voskASR.are_nariks_speaking(badWords, file, recognizer):
            await narik_caught(ctx, user)


client.run(config.token)
