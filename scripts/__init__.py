# =======================
# Startup
# =======================

import os, discord, time, random, re, pydirectinput, asyncio, json
import speech_recognition as sr, threading
from pynput.mouse import Controller
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GENAI_TOKEN_ID = os.getenv('GENAI_TOKEN')
DISCORD_TOKEN_ID = os.getenv('DISCORD_BOT_TOKEN')
ALLOWED_CHANNEL_ID = int(os.getenv('CHANNEL_TOKEN'))

genai.configure(api_key=GENAI_TOKEN_ID)
model = genai.GenerativeModel("gemini-1.5-flash")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

mouse = Controller()
recognizer = sr.Recognizer()

# Toggles

is_listening = False
response_aggressiveness_toggle = True
sass_toggle = False
bipolar_temp_count = 0

# Load commands

async def send_message(channel, message):
    asyncio.run_coroutine_threadsafe(channel.send(message), asyncio.get_event_loop())

def load_custom_commands():
    with open('properties/ai_responses.json', 'r') as responses:
        return json.load(responses)

data = load_custom_commands()

custom_commands = data["custom_commands"]
incorrect_responses_polite = data["incorrect_responses_polite"]
incorrect_responses_aggressive = data["incorrect_responses_aggressive"]

def load_ai_prompts():
    with open('properties/ai_prompts.json', 'r') as prompts:
        return json.load(prompts)
    
ai_personalities = load_ai_prompts()

jarvis = ai_personalities["jarvis_bot"]
mimi = ai_personalities["mimi_bot"]
snoop = ai_personalities["snoop_dog_bot"]

fallback = ai_personalities["fallback"]
limiter = ai_personalities["limiter"]

current_personality = mimi # Switch personalities
persona_switch = True # True returns random persona
init_persona = current_personality["persona"]["normal"]

__all__ = [
    "client",
    "model",
    "GENAI_TOKEN_ID",
    "DISCORD_TOKEN_ID",
    "ALLOWED_CHANNEL_ID",
    "custom_commands",
    "incorrect_responses_polite",
    "incorrect_responses_aggressive",
    "ai_personalities",
    "jarvis",
    "mimi",
    "snoop",
    "fallback",
    "limiter",
    "current_personality",
    "persona_switch",
    "init_persona",
    "load_custom_commands",
    "load_ai_prompts",
    "store_memories"
]