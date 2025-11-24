# utils/memory.py
import os
import json
from datetime import datetime

MEMORY_FILE = os.getenv("MEMORY_FILE", "memory.json")

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

def remember(role, content):
    memory = load_memory()
    memory.append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "role": role,
        "content": content
    })
    save_memory(memory)
