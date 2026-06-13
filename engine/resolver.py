import os

def resolve_dependencies(parsed: dict, system_info: dict) -> list:
    """Create a list of action dictionaries that the installer will execute.
    Each action dict contains:
        - type: e.g. 'install_runtime', 'create_venv', 'pip_install', 'open_port', 'launch_ide'
        - details: dict with any needed parameters
    The function is deliberately simple for this demo.
    """
    actions = []
    lang = parsed.get('language')
    framework = parsed.get('framework')
    port = parsed.get('port')
    ide = parsed.get('ide')

    # 1. Ensure the required runtime is present
    if lang == 'python':
        if not system_info['runtimes'].get('python'):
            actions.append({
                'type': 'install_runtime',
                'details': {'runtime': 'python', 'installer': 'winget', 'package': 'Python.Python.3'}
            })
    elif lang == 'node':
        if not system_info['runtimes'].get('node'):
            actions.append({
                'type': 'install_runtime',
                'details': {'runtime': 'node', 'installer': 'winget', 'package': 'OpenJS.NodeJS'}
            })
    # Add more languages as needed ...

    # 2. Create virtual environment for python projects
    if lang == 'python':
        actions.append({
            'type': 'create_venv',
            'details': {'path': '.venv'}
        })
        # Install the requested framework via pip
        if framework:
            actions.append({
                'type': 'pip_install',
                'details': {'packages': [framework]}
            })

    # 3. Open a port if required and it's currently in use
    if port:
        if port in system_info.get('open_ports', []):
            actions.append({
                'type': 'resolve_port_conflict',
                'details': {'port': port}
            })
        else:
            actions.append({
                'type': 'reserve_port',
                'details': {'port': port}
            })

    # 4. Launch the IDE at the end of setup
    if ide:
        actions.append({
            'type': 'launch_ide',
            'details': {'ide': ide, 'project_path': os.getcwd()}
        })

    return actions
