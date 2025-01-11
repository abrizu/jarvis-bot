# =======================
# Jarvis bot v0.1.1 for discord, featuring silly voice commands and AI implementation
 
# Utilizes
# Gemini 1.5 Flash
# Discord.py API for Developers
# =======================

# ===========
# v0.2.1 implementations
# New personalities (Not just Jarvis)
# Persona randomizer
# Short term memory cache (Adjustable)
# ===========

# ===========
# TO IMPLEMENT
# Addressing chains
#    Example:
#      user: mimi, hello!
#      response: Hi!
#      user: how are you?
#      response: Good, you? (follow up without addressing name)
# Traits
#   
# Temperature slider (random) so answers may not be similar to each other given the same response
# small: bipolar randomly chooses when to switch personas rather than set variable
# trigger switches: If user says something off, such as "mimi you make me ANGRY (keyword) it switches to madge persona (may be very hard to implement)"

# FUTURE IMPLEMENTATION
# Actual discord bot server commands (introductions, welcome, moderation, etc)
# tts commands

# TO FIX
# Voice command stopping, update voice commands
# Fix inclusion (blow up, blow up., blow up..., should result in the same since it contains the string blow up)
# ===========


import os, discord, time, random, re, pydirectinput, asyncio, json
import speech_recognition as sr, threading
from pynput.mouse import Controller
import google.generativeai as genai
from dotenv import load_dotenv

# =======================
# Startup
# =======================

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
    with open('ai_responses.json', 'r') as responses:
        return json.load(responses)

data = load_custom_commands()

custom_commands = data["custom_commands"]
incorrect_responses_polite = data["incorrect_responses_polite"]
incorrect_responses_aggressive = data["incorrect_responses_aggressive"]

def load_ai_prompts():
    with open('ai_prompts.json', 'r') as prompts:
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


# =======================
# Settings
# =======================

def store_memories(user_input, ai_response, file_path="memory_cache.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except FileNotFoundError:
        lines = [] 

    memories = [lines[i:i + 3] for i in range(0, len(lines), 3)]

    # Ensure we don't exceed set memories (value can be changed depending on AI accuracy with relevant memories)
    if len(memories) >= 5: # Set amount of memories
        memories.pop(0)

    # Add the new memory
    new_memory = [
        f"user_input: '{user_input}'\n",
        f"ai_response: {ai_response}\n"
    ]
    memories.append(new_memory)

    with open(file_path, "w", encoding="utf-8") as file:
        for memory in memories:
            file.writelines(memory)

def read_memories(file_path="memory_cache.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except FileNotFoundError:
        return []  

    memories = [lines[i:i+3] for i in range(0, len(lines), 3)]

    formatted_memories = []
    for memory in memories:
        if len(memory) == 3:
            user_input = memory[0].strip()
            ai_response = memory[1].strip()
            formatted_memories.append({"user_input": user_input, "ai_response": ai_response})

    return formatted_memories

def execute_memories(command, selected_persona, prompt_prefix, lim, memories=[]):
    memories = read_memories()
    memory_section = ""

    if memories:
        memory_section = "---- Relevant Memories ----\n"
        for memory in memories:
            memory_section += f"{memory['user_input']}\n"
            memory_section += f"{memory['ai_response']}\n"
        memory_section += "---------------------------\n\n"
        memory_section += "You are to remember these memories and incorporate them into your response only when necessary.\n\n"

    prompt = (
        f"{memory_section}"
        f"{prompt_prefix} Additionally, {selected_persona} Respond to the user with this personality. \nUser response: '{command}' \n{lim}\n\n"
    )

    return prompt

def bipolar(interval, current_persona):
    personas = current_personality.get("persona", {})
    global bipolar_temp_count
    # print(f"{bipolar_temp_count}, {interval}")

    if not personas:
        return current_persona

    if bipolar_temp_count >= interval:
        # print(f"{bipolar_temp_count}, {interval}")
        current_persona = random.choice(list(personas.values()))
        bipolar_temp_count = 0
    else:
        bipolar_temp_count += 1

    return current_persona


# =======================
# Client events
# =======================

@client.event
async def on_ready():  # Initial deployment
    print(f'{client.user} has connected to Discord!')
    channel = client.get_channel(ALLOWED_CHANNEL_ID)

    if current_personality == mimi:
        intro_prompt = current_personality["intro"]
        await channel.send(intro_prompt)
    else:
        intro_prompt = current_personality["intro"]
        intro = await handle_response(intro_prompt)
        await channel.send(intro)


@client.event
async def on_message(message): # Command operations
    try:

        global response_aggressiveness_toggle, sass_toggle, command

        tagline = current_personality["prefix"]
        fallback_ai = fallback["prefix"]

        personas = current_personality.get("persona", {})

        if message.author == client.user:
            return

        if message.channel.id == ALLOWED_CHANNEL_ID:
            match = re.match(r"^\w+,", message.content.strip())
            if match:
                # Split the message content by the first comma
                # Syntax: (bot), Hello!
                command_parts = message.content.strip().split(",", 1) 
                command = command_parts[0].strip().lower()

                # print(f"Command: '{command}', Text: '{text}'")

                # Check for specific bot commands
                if command.startswith(tagline) or command.startswith(fallback_ai):
                    prefix = tagline if command.startswith(tagline) else fallback_ai
                    command = command_parts[1].strip()

                    # print(f"Processed command: '{command}'") 

                    # Registers if a custom command is in the system before resorting to a gpt response
                    if command in custom_commands: 
                        await handle_custom_command(command, message)

                    else:
                        prompt_prefix = ( 
                            current_personality["prompt"] if prefix == tagline else fallback["prompt"]
                        )
                        lim = limiter # Ensure prompt does not exceed 4000 characters
                        if persona_switch == True and personas: # if the selected ai bot contains optional personas tag
                            global init_persona
                            
                            selected_persona = bipolar(3, init_persona)
                            init_persona = selected_persona
                            # print(f"Response: {selected_persona}")
                            prompt = execute_memories(command, selected_persona, prompt_prefix, lim)
                            print(f"{prompt}")
                        else:

                            #v0.1.1, does not include memories, extensive personalities, etc.

                            prompt = f"{prompt_prefix} User response: '{command}' {lim}"
                        # print(f"switching to Gemini \n{prompt}")
                        response_text = await handle_response(prompt)

                        await message.channel.send(response_text)

                else:
                    # Case where the command proceeds with correct syntax, but misspelled name
                    response = random.choice(incorrect_responses_polite if response_aggressiveness_toggle else incorrect_responses_aggressive)
                    await message.channel.send(response)
        
    except Exception as e:
            print(f"An error occurred: {e}")

# =======================
# Command selector
# =======================

async def handle_custom_command(command, message):
    global response_aggressiveness_toggle, sass_toggle
    action = custom_commands[command]
    print({action})

    match action:
        case "boom":
            await boombot()
        case "wheel":
            await message.channel.send("Of course.")
            take_the_wheel()
            await message.channel.send("Did we crash?")
        case "polite-IR":
            response_aggressiveness_toggle = True
            await message.channel.send("*passive*")
        case "aggressive-IR":
            response_aggressiveness_toggle = False
            await message.channel.send("*passive-aggressive*")
        case "enable-voice-commands":
            try:
                channel_id = client.get_channel(ALLOWED_CHANNEL_ID)
                await handle_response("I guess this preps the voice command, then gets immediately overriden?")
                await start_voice_command_listener(channel_id)
            except:
                print("Error enabling voice commands.")
        case "disable-voice-commmands":
            await message.channel.send("Ok fine.")
            stop_voice_command_listener()

async def handle_response(prompt):
    response = model.generate_content(prompt)
    global command

    store_memories(command, response.text)
    return response.text

# =======================
# Command algorithms
# =======================

# ==========
# MOVEMENT RANDOMIZER 0.1
# Fun movement randomizer that randomly selects movement keys to control your game (up to 5 minutes)
# MUST ONLY BE USED IN GAME APPLICATIONS ONLY, OTHERWISE WILL BREAK
# Forza, Minecraft, etc.

# Jarvis, take the wheel: Randomly generated movement directions
def take_the_wheel():

    movement_keys = ['w', 'a', 's', 'd']
    key_combinations = [
        ('w', 'a'),
        ('w', 'd'),
        ('s', 'a'),
        ('s', 'd'),
        ('w', 'space'),
        ('a', 'space'),
        ('s', 'space'),
        ('d', 'space'),
    ]

    key_sequence = [] 
    last_key = None
    last_combo_key = None
    
    # Generate a random sequence of key presses (single or combination of keys)
    for _ in range(random.randint(25, 50)): # 25-50 total iterations per key
        if random.random() > 0.33:  # Randomly pick single or combination of keys, movement_default 33% chance, key_combination 66% chance
            key_combination = random.choice(key_combinations)
            key_sequence.append(key_combination)
        else:
            key_sequence.append(random.choice(movement_keys))
    

    for keys in key_sequence:
        repeat_count = random.randint(9, 25)

        if isinstance(keys, tuple):  # If combination of keys
            if keys != last_combo_key:  # On combination change
                if last_combo_key:
                    pydirectinput.keyUp(last_combo_key[0])
                    pydirectinput.keyUp(last_combo_key[1])
                    time.sleep(0.02)

                # Apply new combination
                pydirectinput.keyDown(keys[0])
                pydirectinput.keyDown(keys[1])
                time.sleep(random.uniform(0.2, 0.5))
                last_combo_key = keys

            # Repeat combination press forrandomly chosen repeat count
            for _ in range(repeat_count):
                time.sleep(random.uniform(0.2, 0.5))
            pydirectinput.keyUp(keys[0])
            pydirectinput.keyUp(keys[1])
            time.sleep(0.02)
                
        else:  # Single key operations
            if keys != last_key:
                if last_key:
                    pydirectinput.keyUp(last_key)
                pydirectinput.keyDown(keys)
                last_key = keys

            # Repeat key press for randomly chosen repeat count
            for _ in range(repeat_count):
                time.sleep(random.uniform(0.2, 0.5)) 
            pydirectinput.keyUp(keys)
            time.sleep(0.02)

    if last_key:
        pydirectinput.keyUp(last_key)


# ==========
# JARVIS KILL SWITCH
# A simple kill switch operation through discord to program runtime

# FUNCTIONALITY
# Jarvis, blow up: Terminates the entire program after 5 seconds (NON-CANCELLABLE)
async def boombot():
        global is_listening
        is_listening = False
        channel = client.get_channel(ALLOWED_CHANNEL_ID)
        countdown_time = 5
        countdown_message = await channel.send(f"Terminating in {countdown_time}...")

        while countdown_time > 0:
            await asyncio.sleep(1) 
            countdown_time -= 1
            await countdown_message.edit(content=f"{countdown_time}...")
        
        await asyncio.sleep(1)
        await countdown_message.edit(content="Goodbye.")
        await asyncio.sleep(1)
        await countdown_message.delete()
        await client.close()

# ==========
# VOICE COMMAND 0.1.1 WORKING BETA (LOCAL MACHINE ONLY)
# OUTDATED

# FUNCTIONALITY 
# Jarvis, listen to me: Returns voice listener to address voice commands with
# All commands work as intended
# (BROKEN) Jarvis, stop listening: Stops voice listener and returns to normal text prompts   

# BUGS
# Stop listening does not work: It does not register its break out of the async loop
# Listens for commands one second out of final timeout 

# Jarvis, listen to me | stop listening
async def listen_for_commands(channel):
    message = await channel.send("Listening...")

    # Cycling messages
    cycle = ["Listening...", "Listening..", "Listening.", "Listening.."]
    cycle_index = 0

    recognizer = sr.Recognizer()
    global is_listening

    timeout_duration = 15
    start_time = time.time()

    with sr.Microphone() as source:
        print("Listening...")
        is_listening = True

        while is_listening:
            try:
                recognizer.adjust_for_ambient_noise(source)

                # Async.io thread management blocking I/O (Issue?)
                audio_task = asyncio.create_task(asyncio.to_thread(recognizer.listen, source, timeout=5))

                # Final timeout break operation
                while not audio_task.done():
                    elapsed_time = time.time() - start_time
                    if elapsed_time > timeout_duration:
                        print("Timeout exceeded. Stopping listening...")
                        is_listening = False
                        await message.edit(content="Listening timed out. ")
                        break
                    
                    # Cycle Listening... while waiting for input
                    await message.edit(content=cycle[cycle_index])
                    cycle_index = (cycle_index + 1) % len(cycle)
                    await asyncio.sleep(0.5)

                audio = await audio_task

                if not is_listening:
                    break

                # Parsing Jarvis out of voice command
                command = recognizer.recognize_google(audio).lower()
                processed_command = command
                if command.startswith("jarvis"):
                    processed_command = command[len("jarvis "):].strip()

                print(f"Voice Command: {processed_command}")
                await message.edit(content=f"Voice Command: {command}")

                # Process command
                if processed_command in custom_commands:
                    response_text = ""
                    await handle_custom_command(processed_command, response_text)
                else:
                    prompt_prefix = (
                        "Scenario: You are roleplaying as Michael Jackson. In one or two sentences, "
                    )
                    prompt = f"{prompt_prefix}{processed_command}"
                    print("Switching to Gemini")
                    response_text = await handle_response(prompt)

                    print(response_text)
                    await channel.send(response_text)

                start_time = time.time()
                message = await channel.send("Listening...")
                cycle_index = 0

            except sr.WaitTimeoutError:
                print("Listening timed out, waiting for new command.")
            except sr.UnknownValueError:
                print("Could not understand the command.")
            except sr.RequestError as e:
                print(f"Speech Recognition Error: {e}")
            except KeyboardInterrupt:
                print("Exit 400: Keyboard Interrupt")
                break

async def start_voice_command_listener(channel):
    global is_listening
    is_listening = True
    await listen_for_commands(channel)

def start_listening_thread(channel):
    listener_thread = threading.Thread(target=asyncio.run, args=(start_voice_command_listener(channel),))
    listener_thread.daemon = True
    listener_thread.start()
    print("Voice command listener started.")
    
def stop_voice_command_listener():
    global is_listening
    is_listening = False
    print("Voice command listener stopped.")


client.run(DISCORD_TOKEN_ID)