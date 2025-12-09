import os

def get_api_key(name: str) -> str:
    """
    Return API key from environment variables.

    Example:
        get_api_key("SPRINGER_API_KEY")
    """

    env_val = os.getenv(name)
    if env_val:
        return env_val.strip()

    raise RuntimeError("API Key not found!")
