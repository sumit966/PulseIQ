from dotenv import load_dotenv
load_dotenv()
import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

for model in ["openai/gpt-oss-20b", "qwen/qwen3.8-27b"]:
    print(f"\n=== {model} ===")
    try:
        r = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Reply with exactly: PulseIQ ready"}],
            max_tokens=100,
        )
        print("CONTENT:", repr(r.choices[0].message.content))
    except Exception as e:
        print("ERROR:", e)

