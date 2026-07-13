import json
import os
import re

def parse_prompt(prompt: str) -> dict:
    """Very lightweight parser for demo purposes.
    Extracts:
        - language (python, node, rust, java, go)
        - framework (flask, django, express, actix, etc.)
        - port (numeric)
        - preferred IDE (vscode, pycharm, intellij)
    Returns a dict with keys 'language', 'framework', 'port', 'ide'.
    """
    prompt_lower = prompt.lower()
    # Simple keyword extraction
    language = None
    for lang in ["python", "node", "javascript", "typescript", "rust", "go", "java"]:
        if lang in prompt_lower:
            language = "python" if lang in ["python"] else ("node" if lang in ["node", "javascript", "typescript"] else lang)
            break
    framework = None
    for fw in ["flask", "django", "fastapi", "express", "nestjs", "actix", "rocket", "spring"]:
        if fw in prompt_lower:
            framework = fw
            break
    port_match = re.search(r"port\s*(\d{2,5})", prompt_lower)
    port = int(port_match.group(1)) if port_match else None
    ide = None
    for ide_name in ["vscode", "visual studio code", "pycharm", "intellij", "code"]:
        if ide_name in prompt_lower:
            ide = "vscode" if "vscode" in ide_name or "code" in ide_name else ide_name
            break
    return {
        "language": language,
        "framework": framework,
        "port": port,
        "ide": ide,
    }

# Example usage (would be called by the engine)
if __name__ == "__main__":
    example = "Create a Python Flask web app on port 5000 and open it in VS Code"
    print(json.dumps(parse_prompt(example), indent=2))
