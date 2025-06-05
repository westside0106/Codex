import os
import importlib.util
from urllib.parse import parse_qs

PLUGIN_DIR = os.path.dirname(__file__)

def get_plugins():
    return [
        f[:-3] for f in os.listdir(PLUGIN_DIR)
        if f.endswith(".py") and f not in ("__init__.py",)
    ]

def run_plugin(query):
    if "?" in query:
        name, args_str = query.split("?", 1)
        args = {k: v[0] for k, v in parse_qs(args_str).items()}
    else:
        name, args = query, {}

    path = os.path.join(PLUGIN_DIR, f"{name}.py")
    if not os.path.isfile(path):
        return f"Plugin '{name}' not found."

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.run(**args) if hasattr(module, "run") else f"No run() in {name}"
