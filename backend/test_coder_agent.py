# G:\Brunella\projects\BrunellaAgentSystem\backend\test_coder_agent.py

import requests
import json

# A LangGraph dev szerver címe
url = "http://localhost:8000/agent/invoke"

# A teszt prompt, ami a kódoló ügynököt célozza
payload = {
    "input": {
        "messages": [
            {
                "role": "human",
                "content": "Kérd meg a kódoló specialistát, hogy írjon egy Python függvényt `hello_world` néven, ami visszaadja a 'hello world' stringet."
            }
        ]
    }
}

print("--- Teszt indítása: Kódoló ügynök meghívása ---")

# API hívás a fő ügynökhöz
response = requests.post(url, json=payload)

print("--- Válasz a szerverről ---")
if response.status_code == 200:
    try:
        # A válasz streamek formájában érkezik, soronként dolgozzuk fel
        final_content = ""
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                # Minden sor egy esemény, pl. 'event: data', 'data: {...}'
                if decoded_line.startswith('data:'):
                    json_data = json.loads(decoded_line[len('data:'):])
                    # Keressük a tool kimenetét tartalmazó részt
                    if isinstance(json_data, dict) and 'messages' in json_data:
                        tool_outputs = [msg for msg in json_data['messages'] if msg['type'] == 'tool']
                        if tool_outputs:
                            final_content = tool_outputs[0]['content']
                            break # Megvan a tool kimenete, kilépünk
        
        print("--- Kódoló ügynök által generált kód ---")
        if final_content:
            print(final_content)
        else:
            print("# HIBA: Nem található tool kimenet a válaszban.")
            print("Teljes válasz:", response.text)

    except json.JSONDecodeError:
        print("# HIBA: A szerver válasza nem érvényes JSON.")
        print("Státuszkód:", response.status_code)
        print("Válasz:", response.text)
    except Exception as e:
        print(f"# HIBA: Hiba történt a válasz feldolgozása közben: {e}")
else:
    print(f"# HIBA: A szerver hibát adott vissza. Státuszkód: {response.status_code}")
    print("Válasz:", response.text)

print("--- Teszt befejezve ---")
