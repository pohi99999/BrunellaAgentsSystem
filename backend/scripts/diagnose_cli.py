import os, sys, shutil, json, importlib.util

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
VENV = os.path.join(BASE, '.venv311')
SCRIPTS = os.path.join(VENV, 'Scripts')

report = {}
report['python_executable'] = sys.executable
report['sys_version'] = sys.version
report['venv_exists'] = os.path.isdir(VENV)
report['langgraph_executable'] = shutil.which('langgraph')
report['scripts_dir_listing'] = []
if os.path.isdir(SCRIPTS):
    report['scripts_dir_listing'] = [f for f in os.listdir(SCRIPTS) if 'langgraph' in f.lower()]

# Check importability
for mod in ['langgraph', 'langgraph_cli', 'langgraph_api']:
    spec = importlib.util.find_spec(mod)
    report[f'module_{mod}_found'] = spec is not None

print(json.dumps(report, indent=2))
