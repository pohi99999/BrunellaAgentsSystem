import sys
import traceback
import importlib
import re

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

FROM_IMPORT_RE = re.compile(
    r"^from\s+(?P<module>[a-zA-Z_][\w\.]*)\s+import\s+(?P<name>[a-zA-Z_]\w*)(?:\s+as\s+(?P<alias>[a-zA-Z_]\w*))?\s*$"
)
IMPORT_RE = re.compile(
    r"^import\s+(?P<module>[a-zA-Z_][\w\.]*)(?:\s+as\s+(?P<alias>[a-zA-Z_]\w*))?\s*$"
)


def run_import_statement(statement: str) -> None:
    """Safely execute a limited set of import statements (no exec)."""
    stmt = statement.strip()

    m = FROM_IMPORT_RE.match(stmt)
    if m:
        module = importlib.import_module(m.group("module"))
        # Force attribute resolution to ensure the import target exists.
        getattr(module, m.group("name"))
        return

    m = IMPORT_RE.match(stmt)
    if m:
        importlib.import_module(m.group("module"))
        return

    raise ValueError(
        f"Unsupported import statement format (refusing to exec): {statement!r}"
    )


for imp in imports_to_test:
    try:
        print(f"Executing: {imp}")
        run_import_statement(imp)
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
