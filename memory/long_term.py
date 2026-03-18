from mem0 import MemoryClient

client = MemoryClient()

def save_memory(user_id: str, content: str):
    try:
        client.add(content, user_id=user_id)
        print(f"[Memory] Saved for user '{user_id}': {content[:60]}...")
    except Exception as e:
        print(f"[Memory] Could not save memory: {e}")

def get_memories(user_id: str) -> str:
    try:
        results = client.search(
            query="user preferences and history",
            filters={"user_id": user_id},
            limit=5
        )
        if not results:
            return ""
        # handle both list of dicts and list of strings
        memories = []
        for m in results:
            if isinstance(m, dict):
                text = m.get("memory") or m.get("text") or str(m)
            else:
                text = str(m)
            memories.append(f"- {text}")
        return "\n".join(memories)
    except Exception as e:
        print(f"[Memory] Could not load memories: {e}")
        return ""