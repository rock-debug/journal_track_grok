"""
Basic Groq API connectivity test.
Run this to verify your GROQ_API_KEY works before starting the app.
"""
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GROQ_API_KEY", "")

print("=" * 50)
print("GROQ API CONNECTIVITY TEST")
print("=" * 50)
print(f"API Key configured: {bool(api_key) and api_key != 'your_groq_api_key_here'}")
print(f"API Key length: {len(api_key)}")

if not api_key or api_key == "your_groq_api_key_here":
    print("\n[FAIL] No API key found. Please set GROQ_API_KEY in your .env file.")
    print("   Get a free key at: https://console.groq.com/keys")
    exit(1)

try:
    from groq import Groq

    client = Groq(api_key=api_key)

    print("\n[INFO] Sending test message to Groq...")
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Reply in one sentence."
            },
            {
                "role": "user",
                "content": "Hello! This is a test message. Please confirm you're working."
            }
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        max_tokens=100,
    )

    response = chat_completion.choices[0].message.content
    print(f"\n[SUCCESS] Groq responded:")
    print(f"   {response}")
    print(f"\n   Model: {chat_completion.model}")
    print(f"   Tokens used: {chat_completion.usage.total_tokens}")

except ImportError:
    print("\n[FAIL] 'groq' package not installed. Run: pip install groq")
except Exception as e:
    print(f"\n[FAIL] Error: {str(e)}")

print("\n" + "=" * 50)
