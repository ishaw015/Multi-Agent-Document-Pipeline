import time
import google.genai as genai
from google.genai.errors import ServerError

def generate_with_retry(client, model, contents, max_retries=3):
    """
    Call Gemini with automatic retry on 503 server errors.
    """
    for attempt in range(max_retries):
        try:
            return client.models.generate_content(
                model=model,
                contents=contents
            )
        except ServerError as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                wait = (2 ** attempt) * 5  # 5s, 10s, 20s
                print(f"Gemini 503 — retrying in {wait}s (attempt {attempt+1}/{max_retries})")
                time.sleep(wait)
            else:
                raise  # re-raise non-503 errors immediately
    raise RuntimeError("Gemini API unavailable after max retries")