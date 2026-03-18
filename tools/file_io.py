import os

def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def write_file(path: str, content: str) -> str:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File written successfully: {path}"
    except Exception as e:
        return f"Error writing file: {e}"

def list_files(directory: str = ".") -> str:
    try:
        files = os.listdir(directory)
        return "\n".join(files) if files else "No files found."
    except Exception as e:
        return f"Error listing files: {e}"