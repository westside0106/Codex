from plugins import run_plugin
import os

def ask_codex(prompt: str) -> str:
    # Beispielantwort – hier könnte OpenAI, Claude o.ä. verwendet werden
    if "plugin:" in prompt:
        plugin_name = prompt.split("plugin:")[1].strip()
        return run_plugin(plugin_name)
    return f"Simulierte Antwort auf: {prompt}"
