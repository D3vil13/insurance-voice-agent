import requests
import json
import os
from dotenv import load_dotenv

# Load API key
load_dotenv('c:/Users/d3vsh/Downloads/backupMH/apikeys.env')
api_key = os.environ.get('OPENAI_API_KEY')

print(f'API Key loaded: {api_key[:20]}...' if api_key else 'API Key: NOT FOUND')

# Test OpenRouter API
try:
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8888",
            "X-Title": "Test",
        },
        data=json.dumps({
            "model": "openai/gpt-4o-mini",
            "messages": [{"role": "user", "content": "Say hello in 3 words"}],
            "max_tokens": 10
        }),
        timeout=10
    )
    
    print(f'Status Code: {response.status_code}')
    print(f'Response: {response.text[:500]}')
    
except Exception as e:
    print(f'ERROR: {e}')
