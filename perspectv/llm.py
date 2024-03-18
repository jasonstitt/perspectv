import os
import requests
import json


base_dir = os.path.dirname(os.path.abspath(__file__))
prompt_dir = os.path.join(base_dir, "prompts")


def openrouter(model, text):
    token = os.getenv("OPENROUTER_API_KEY")
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        timeout=120,
        headers={
            "Authorization": f"Bearer {token}",
        },
        data=json.dumps(
            {
                "model": model,
                "max_tokens": 10000,
                "messages": [{"role": "user", "content": text}],
            }
        ),
    )
    data = response.json()
    text = data["choices"][0]["message"]["content"]
    return text


def run_prompt(prompt_name, model, **params):
    path = os.path.join(prompt_dir, f"{prompt_name}.txt")
    with open(path, "r") as infile:
        text = infile.read()
    text = text.format(**params)
    return openrouter(model, text)
