# G:\\Brunella\\projects\\BrunellaAgentSystem\\backend\\src\\debug_chain.py

import sys
# Add the app directory to the path to allow imports
sys.path.insert(0, "/app")

from specialists.coder_agent import coder_chain
import traceback

print("-- Starting internal chain debugger --")

test_payload = {
    "language": "Python",
    "prompt": "írj egy Python függvényt `hello_world` néven, ami visszaadja a 'hello world' stringet."
}

try:
    print(f"Invoking coder_chain with: {test_payload}")
    result = coder_chain.invoke(test_payload)
    print("\n--- Invocation successful ---")
    print("Result:")
    print(result)

except Exception as e:
    print("\n--- !! INVOCATION FAILED !! ---")
    print(f"Exception Type: {type(e).__name__}")
    print(f"Exception Details: {e}")
    print("\n--- Full Traceback ---")
    traceback.print_exc()

print("\n--- Debugger finished ---")
