# =======================
# Settings
# =======================

import random, json

def load_ai_prompts(file_path="properties/ai_prompts.json"):
    with open(file_path, 'r') as prompts:
        return json.load(prompts)
    
ai_personalities = load_ai_prompts()
mimi = ai_personalities["mimi_bot"]
current_personality = mimi
bipolar_temp_count = 0

def store_memories(user_input, ai_response, file_path="properties/memory_cache.txt"):
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

def read_memories(file_path="properties/memory_cache.txt"):
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