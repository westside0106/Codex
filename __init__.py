from .example import run as example_run

def get_plugins():
    return ["example"]

def run_plugin(name):
    if name == "example":
        return example_run()
    return f"Plugin '{name}' nicht gefunden."
