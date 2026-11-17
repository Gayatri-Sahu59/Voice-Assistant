
from google import genai
from backend.config import GEMINI_API_KEY, GEMINI_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)

response = client.models.generate_content(
    model=GEMINI_MODEL,
    contents="Reply in one sentence: Hello, I am NexovAI Doctor Assistant."
)

print("Gemini response:")
print(response.text)
