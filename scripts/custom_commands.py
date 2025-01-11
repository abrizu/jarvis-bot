# =======================
# Command algorithms
# =======================


# BROKEN, AND NEEDS A REFACTOR

import random, pydirectinput, time, asyncio
import speech_recognition as sr, threading
from settings import store_memories
from scripts import (
    client,
    model,
    GENAI_TOKEN_ID,
    DISCORD_TOKEN_ID,
    ALLOWED_CHANNEL_ID,
    custom_commands,
    incorrect_responses_polite,
    incorrect_responses_aggressive,
    jarvis,
    mimi,
    snoop,
    fallback,
    limiter,
    current_personality,
    persona_switch,
    init_persona,
    load_custom_commands,
    load_ai_prompts,
)

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