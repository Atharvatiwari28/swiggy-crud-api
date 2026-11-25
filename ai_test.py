import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "system", "content": "Tum ek pirate ho. Har jawab pirate style Hinglish mein do."},
        {"role": "user", "content": "Meri chai ki dukaan ke liye ek naam batao"}
    ],
    temperature=1
)

print(response.choices[0].message.content)

print(response.usage)