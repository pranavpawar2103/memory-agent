_sessions = {}

def get_session(session_id: str) -> list:
    return _sessions.get(session_id, [])

def update_session(session_id: str, role: str, content: str):
    if session_id not in _sessions:
        _sessions[session_id] = []
    _sessions[session_id].append({"role": role, "content": content})