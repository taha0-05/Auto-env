import os
import platform
import shutil

IS_WINDOWS = platform.system() == "Windows"

def find_ide_executable(cmd_name: str) -> str | None:
    path = shutil.which(cmd_name) or shutil.which(cmd_name + ".cmd") or shutil.which(cmd_name + ".exe")
    if path:
        return path

    if IS_WINDOWS:
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        prog_files = os.environ.get("PROGRAMFILES", "")
        
        paths_to_check = []
        if cmd_name == "code" or cmd_name == "vscode":
            paths_to_check = [
                os.path.join(local_app_data, "Programs", "Microsoft VS Code", "bin", "code.cmd"),
                os.path.join(prog_files, "Microsoft VS Code", "bin", "code.cmd"),
                os.path.join(local_app_data, "Programs", "Microsoft VS Code", "Code.exe"),
                os.path.join(prog_files, "Microsoft VS Code", "Code.exe")
            ]
        elif cmd_name == "cursor":
            paths_to_check = [
                os.path.join(local_app_data, "Programs", "cursor", "Cursor.exe"),
                os.path.join(local_app_data, "Programs", "cursor", "resources", "app", "bin", "cursor.cmd")
            ]
        elif cmd_name == "antigravity":
            paths_to_check = [
                os.path.join(local_app_data, "Programs", "antigravity", "antigravity.exe"),
                os.path.join(local_app_data, "Programs", "Antigravity IDE", "antigravity.exe"),
                os.path.join(prog_files, "antigravity", "antigravity.exe"),
                os.path.join(prog_files, "Antigravity IDE", "antigravity.exe")
            ]
        elif cmd_name == "kiro":
            paths_to_check = [
                os.path.join(local_app_data, "Programs", "kiro", "kiro.exe"),
                os.path.join(prog_files, "kiro", "kiro.exe")
            ]
            
        for p in paths_to_check:
            if os.path.isfile(p):
                return p

    return None

def discover_installed_ides():
    ides_found = []
    seen_labels = set()
    
    known_ides = [
        ("VS Code", ["visual studio code", "vs code"], ["code", "code.cmd"]),
        ("Cursor", ["cursor"], ["cursor", "cursor.cmd"]),
        ("Antigravity", ["antigravity"], ["antigravity", "antigravity.exe", "Antigravity IDE.exe"]),
        ("Kiro", ["kiro"], ["kiro", "kiro.exe"]),
        ("PyCharm", ["pycharm"], ["pycharm64", "pycharm"]),
        ("IntelliJ IDEA", ["intellij idea"], ["idea64", "idea"]),
        ("WebStorm", ["webstorm"], ["webstorm64", "webstorm"]),
        ("Android Studio", ["android studio"], ["studio64", "studio"]),
        ("Sublime Text", ["sublime text"], ["subl", "sublime_text"]),
        ("Notepad++", ["notepad++"], ["notepad++"]),
        ("Fleet", ["fleet"], ["fleet"]),
        ("Zed", ["zed"], ["zed"]),
        ("Neovim", ["neovim"], ["nvim"]),
        ("Vim", ["vim"], ["vim"]),
        ("Eclipse", ["eclipse"], ["eclipse"]),
        ("Visual Studio", ["visual studio build tools", "visual studio community", "visual studio professional", "visual studio enterprise"], ["devenv"]),
    ]
    
    if IS_WINDOWS:
        import winreg
        keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        ]
        for hive, key in keys:
            try:
                with winreg.OpenKey(hive, key) as reg_key:
                    for i in range(winreg.QueryInfoKey(reg_key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(reg_key, i)
                            with winreg.OpenKey(reg_key, subkey_name) as subkey:
                                try:
                                    name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                except FileNotFoundError:
                                    continue
                                
                                name_lower = name.lower()
                                
                                for label, keywords, _ in known_ides:
                                    if label in seen_labels:
                                        continue
                                    
                                    for kw in keywords:
                                        if kw in name_lower:
                                            try:
                                                display_icon = winreg.QueryValueEx(subkey, "DisplayIcon")[0]
                                                if display_icon and display_icon.lower().endswith(".exe"):
                                                    clean_path = display_icon.strip('"')
                                                    if os.path.exists(clean_path):
                                                        ides_found.append((label, clean_path))
                                                        seen_labels.add(label)
                                                        break
                                            except FileNotFoundError:
                                                pass
                                            break
                        except OSError:
                            pass
            except OSError:
                pass

    for label, _, cmds in known_ides:
        if label in seen_labels:
            continue
            
        for cmd in cmds:
            path = find_ide_executable(cmd)
            if path:
                ides_found.append((label, path))
                seen_labels.add(label)
                break
                
    if not ides_found:
        ides_found.append(("Explorer", "explorer"))
        
    return ides_found

print(discover_installed_ides())
