# =======================
# Jarvis bot v0.1.1 for discord, featuring silly voice commands and AI implementation
 
# SOFTWARE STACK GOING FORWARD
# LLM: Gemini 1.5 Flash (Conversational)
# Out: Discord API
# NER, Training: spaCy for pretrained data
# DB: JSON, CSV, TXT for smaller implementation; expand to SQL if ever needed
# 
# TTS: ElevenLabs Flash V2 (10k token limit)
#     Voice: Tess, Stability 35%, Similarity 55% (Similar to Hermione, Melina, etc.)
#
# MEMORY HANDLING PARAMETERS:
#    Voice & Text Response: Conversational Usage
#        User Input, AI Output
# =======================

# ===========
# v0.2.1 implementations
# New personalities (Not just Jarvis)
# Persona randomizer
# Short term memory cache (Adjustable)
# ===========

# ===========
# v0.3.1 implementations
# (Nothing yet, just AI Training / Fine tuning)
# ===========

# =====
# TO IMPLEMENT
# Addressing chains (deprecated) vvvv
#    Example:
#      user: mimi, hello!
#      response: Hi!
#      user: how are you?
#      response: Good, you? (follow up without addressing name)
# *I will most likely convert this bot to purely conversational, not require an address.*
# The bot also should be able to join in on conversations / ignore what they want to / don't want to.  

# Data Quality Improvements
# Tokenization only would occur on UI that contains relevant / new data, avoiding short one word responses.
# How this can happen: Sufficient data would be able to track common words / verbs: The, in, run, a, we, etc.
#                      Uncommon words: The sentence could be tracked then tokenized, added to the database.
#                          As I expand the database with more responses, the more it ignores common words compared to uncommon words.

# Temperature slider (random) so answers may not be similar to each other given the same response
# small: bipolar randomly chooses when to switch personas rather than set variable
# Text to Speech: ElevenLabs research (only)
# Seamless voice integration: conversational 

# Relevant Memories needs an update: Soft tokenize data, store into JSON, store more memories w/o overloading the prompt
# Voice commands needs an update: To be constantly running w/ fewer / nonexistent timeouts, act as conversational bot

# Future:
# trigger switches: If user says something off, such as "mimi you make me ANGRY (keyword) it switches to madge persona"
# Can be implemented using tokenization. If value of keyword increases (is added) and has a leading proposition (Mimi, you *make me* ANGRY or Mimi, I *am* ANGRY with you)
# Tracking token usage going into fine tuning models
# Look into PyTorch for training neural networks
# =====

# Fine Tuning: Utilize a large-scale dataset to condition the bot to perform better on its specific task, opposed to just feeding it extensive prompts
#   - Will be used conversationally, where it will adapt to my humor / banter back at me (similar to NeuroSama)
# Relevant Memories: Be able to recall the last 10-15 memories in JSON format, highlighting key things such as Event, Date, Person, etc.
#   - Different from fine tuning as it will be fed in with the prompt, allowing for simpler leads into the next conversation.

# =====
# AI FOCUS WHEN DEVELOPING / TRAINING: 
#     Named Entity Recognition, (Categorizing People, Locations, Events, etc.) 
#     Event Recollection, (Remembering Events)
#     Diologue Flow Management, (Maintaining the feel and tone of conversation)
#     Common Keywords, (Emotes, Slang between users)
#     Intent Recognition, (Predict / determine the user's goal in the converation)
#     Personalized Responses, (Adapt to the user's preferences)
#     Sentiment Analysis (Recognize the emotional tone of the user's message) (Whether to be HYPER!!!!!, Serious.)
# =====

# =====
# CURRENT PROJECT
#   Advanced memory: Using databases, structured keywords and prompts, pattern recognition
#   SQL for database structures 

# - using Named Entity Recognition (NER), identify structured information such as Names, Dates, Events, Event Details, etc. 
#       (this automatically tokenizes the data and highlights key values used in pre-trained memory.)
# - this new dataset will replace my Relevant Memories dataset with set values for different memory outputs. 
#       I will be able to apply it to the model and formulate memories with it. Additionally, it should be able to append me
# =====

# =====
# BUGS / TO FIX
# Voice command stopping, update voice commands
# Fix command inclusion (depreciated as project moves forward)
# =====

# ===========

import random, re
from memory_handler import *
from config import *
from custom_commands import *

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
        intro = await handle_response(intro_prompt, False)
        await channel.send(intro)


@client.event
async def on_message(message): # Command operations
    try:

        global response_aggressiveness_toggle, sass_toggle, command

        tagline = current_personality["prefix"]
        fallback_ai = fallback["prefix"]

        personas = current_personality["persona"]

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
                        # print(command)
                        if (command_parts[0] != "override") and persona_switch == True and personas: # if the selected ai bot contains optional personas tag
                            global init_persona
                            
                            selected_persona = bipolar(20, init_persona)
                            init_persona = selected_persona
                            # print(f"Response: {selected_persona}")
                            prompt = execute_memories(command, selected_persona, prompt_prefix, lim)
                            print(f"{prompt}")
                            response_text = await handle_response(prompt, True)
                            await message.channel.send(response_text)
                        else:

                            #v0.1.1, does not include memories, extensive personalities, etc.

                            prompt = f"{prompt_prefix} User response: '{command}' {lim}"
                            response_text = await handle_response(prompt, False)
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

async def handle_response(prompt, memory_trigger):
    response = model.generate_content(prompt, 
        generation_config=genai.types.GenerationConfig(
            temperature=current_temp

        )
    )
    
    global command

    if memory_trigger == True:
        store_memories(command, response.text)

    return response.text

client.run(DISCORD_TOKEN_ID)