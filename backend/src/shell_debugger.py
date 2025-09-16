# G:\Brunella\projects\BrunellaAgentSystem\backend\src\shell_debugger.py

import sys
import traceback

print("---" + " Starting Interactive Import Debugger ---")

# A problémás importok listája
imports_to_test = [
    "from langchain_core.tools import tool",
    "from specialists.research_agent.graph import graph as research_graph",
    "from specialists.coder_agent import coder_chain",
    "from langchain_core.messages import HumanMessage",
    "from agent.graph import graph"
]

sys.path.insert(0, "/app")

for imp in imports_to_test:
    try:
        print(f"Executing: {imp}")
        exec(imp, globals(), locals())
        print("  -> OK")
    except Exception as e:
        print(f"\n---" + " !! IMPORT FAILED !! ---")
        print(f"Failed on import: {imp}")
        print(f"Exception Type: {type(e).__name__}")
        print(f"Exception Details: {e}")
        print("\n--- Full Traceback ---")
        traceback.print_exc()
        sys.exit(1) # Kilépés hibával

print("\n---" + " All imports successful. The issue might be in the application logic itself. ---")
