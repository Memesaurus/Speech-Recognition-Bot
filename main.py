import discord
from discord.ext import commands, tasks
import voskASR
import config
import speech_recognition as sr
import vosk

with open(config.BAD_WORDS, "r", encoding="utf-8") as f:
    badWords = f.read().splitlines()

intents = discord.Intents(messages=True, guilds=True, voice_states=True, message_content=True)
client = commands.Bot(intents=intents)
recognizer = sr.Recognizer()
recognizer.vosk_model = vosk.Model(config.MODEL_PATH)
asr_parse_freq = 5


@client.event
async def on_ready():
    print(f"Rdy as {client.user}")


async def narik_caught(ctx, user):
    await ctx.channel.send(f"{user.mention} попался, нарик!")


@client.slash_command(name="bad_list", description="get all the bad words!")
async def list_bad_words(ctx):
    file = discord.File(config.BAD_WORDS, filename="list.txt")
    await ctx.respond(file=file)


@client.slash_command(name="add_word", description="adds a new bad word to list!", required=True)
async def add_bad_word(ctx, word: str):
    word = word.strip()
    if not word:
        await ctx.respond("Please provide a valid word!")
    if word in badWords:
        await ctx.respond(f"Bot already has word: {word}")
    else:
        word = word.lower()
        badWords.append(word)
        with open(config.BAD_WORDS, "a", encoding="utf-8") as f:
            f.write(word + "\n")
        await ctx.respond(f"Added word {word} to list!")


@client.slash_command(name="remove_word", description="removes a bad word from the list!", required=True)
async def remove_bad_word(ctx, word: str):
    word = word.strip()
    if not word:
        await ctx.respond("Please provide a valid word!")
    if word in badWords:
        word = word.lower()
        badWords.remove(word)
        with open(config.BAD_WORDS, "w", encoding="utf-8") as f:
            f.writelines(badWords)
        await ctx.respond(f"Removed word {word} from list!")
    else:
        await ctx.respond(f"No such word as {word} in list!")


@client.slash_command(name="join", description="Join voice chat")
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()
    await start_record(ctx)
    end_if_connected.start(ctx)


@client.slash_command(name="stop", description="stop recording and leave voice chat!")
async def stop(ctx):
    connection = ctx.voice_client
    if connection:
        await connection.disconnect()
        end_if_connected.stop()


async def start_record(ctx):
    ctx.voice_client.start_recording(discord.sinks.WaveSink(), record_finish_callback, ctx)


@tasks.loop(seconds=asr_parse_freq)
async def end_if_connected(ctx):
    connection = ctx.voice_client
    if connection:
        await end_record(ctx)


async def end_record(ctx):
    ctx.voice_client.stop_recording()


async def record_finish_callback(sink, ctx):
    connection = ctx.voice_client
    if connection:
        await start_record(ctx)
    for user_id, audio in sink.audio_data.items():
        user = await client.fetch_user(user_id)
        file = discord.File(audio.file, user.name)
        if voskASR.are_nariks_speaking(badWords, file, recognizer):
            await narik_caught(ctx, user)


client.run(config.TOKEN)
