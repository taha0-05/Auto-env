import winreg
import os

def get_installed_software():
    software_list = []
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
                            name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            try:
                                install_loc = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                            except FileNotFoundError:
                                install_loc = None
                            
                            try:
                                display_icon = winreg.QueryValueEx(subkey, "DisplayIcon")[0]
                            except FileNotFoundError:
                                display_icon = None

                            software_list.append({
                                "name": name,
                                "install_loc": install_loc,
                                "icon": display_icon
                            })
                    except OSError:
                        pass
        except OSError:
            pass
            
    return software_list

for sw in get_installed_software():
    name = sw["name"].lower()
    if "code" in name or "ide" in name or "studio" in name or "antigravity" in name or "cursor" in name or "pycharm" in name or "kiro" in name:
        print(sw)
