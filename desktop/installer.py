"""L'installateur Lenyay — un double-clic, deux boutons, zéro terminal.

PyInstaller emballe ce script en Lenyay-Setup.exe avec l'application
(Lenyay-app.zip) à l'intérieur. À l'exécution : petite fenêtre, bouton
Installer → extraction dans %LOCALAPPDATA%/Lenyay, raccourcis Bureau et
menu Démarrer, script de désinstallation, puis « Lancer Lenyay ».

Mode silencieux pour les tests et les curieux :
    Lenyay-Setup.exe --silent [--dir CHEMIN]
"""

import argparse
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

APP_NAME = "Lenyay"
PAYLOAD = "Lenyay-app.zip"


def payload_path() -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return base / PAYLOAD


def default_target() -> Path:
    return Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / APP_NAME


def _shortcut(lnk: Path, target: Path) -> None:
    """Crée un .lnk via WScript.Shell — présent sur tout Windows."""
    lnk.parent.mkdir(parents=True, exist_ok=True)
    script = (
        f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{lnk}');"
        f"$s.TargetPath='{target}';$s.WorkingDirectory='{target.parent}';$s.Save()"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", script],
                   check=True, creationflags=subprocess.CREATE_NO_WINDOW)


def install(target: Path, shortcuts: bool = True) -> Path:
    app_dir = target / "app"
    if app_dir.exists():
        shutil.rmtree(app_dir)  # réinstallation propre, les données de
        # l'utilisateur vivent ailleurs (%APPDATA%/Lenyay) et ne sont pas touchées
    app_dir.mkdir(parents=True)
    with zipfile.ZipFile(payload_path()) as z:
        z.extractall(app_dir)
    exe = app_dir / "Lenyay" / "Lenyay.exe"

    uninstall = target / "desinstaller.cmd"
    desktop_lnk = Path.home() / "Desktop" / f"{APP_NAME}.lnk"
    menu_lnk = (Path(os.environ.get("APPDATA", str(Path.home())))
                / "Microsoft/Windows/Start Menu/Programs" / f"{APP_NAME}.lnk")
    uninstall.write_text(
        "@echo off\n"
        f"taskkill /f /im Lenyay.exe >nul 2>&1\n"
        f"del \"{desktop_lnk}\" >nul 2>&1\n"
        f"del \"{menu_lnk}\" >nul 2>&1\n"
        f"rmdir /s /q \"{app_dir}\"\n"
        "echo Lenyay est desinstalle. Tes credits restent sur ton compte en ligne.\n"
        "pause\n",
        encoding="ascii", errors="replace",
    )
    if shortcuts:
        _shortcut(desktop_lnk, exe)
        _shortcut(menu_lnk, exe)
    return exe


def run_gui() -> None:
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.title(f"Installation de {APP_NAME}")
    root.geometry("460x300")
    root.resizable(False, False)
    root.configure(bg="#F2F6F3")

    tk.Label(root, text="Lenyay", font=("Segoe UI", 22, "bold"),
             bg="#F2F6F3", fg="#245247").pack(pady=(26, 2))
    tk.Label(root, text="L'IA servie par nos machines — sans datacenter.",
             font=("Segoe UI", 10), bg="#F2F6F3", fg="#5F7069").pack()
    tk.Label(root, text=f"Sera installé dans :\n{default_target() / 'app'}",
             font=("Segoe UI", 9), bg="#F2F6F3", fg="#5F7069",
             justify="center").pack(pady=12)

    launch = tk.BooleanVar(value=True)
    tk.Checkbutton(root, text="Lancer Lenyay à la fin", variable=launch,
                   bg="#F2F6F3", font=("Segoe UI", 9)).pack()

    status = tk.Label(root, text="", font=("Segoe UI", 9), bg="#F2F6F3",
                      fg="#3F8C79")
    status.pack(pady=(4, 0))

    def do_install():
        button.config(state="disabled")
        status.config(text="Installation en cours…")
        root.update()
        try:
            exe = install(default_target())
        except Exception as exc:  # l'utilisateur doit voir pourquoi
            messagebox.showerror(APP_NAME, f"Échec de l'installation :\n{exc}")
            button.config(state="normal")
            status.config(text="")
            return
        status.config(text="Installé ! Raccourcis créés sur le Bureau et le menu Démarrer.")
        if launch.get():
            subprocess.Popen([str(exe)], cwd=str(exe.parent))
        root.after(1200, root.destroy)

    button = tk.Button(root, text="Installer", font=("Segoe UI", 11, "bold"),
                       bg="#245247", fg="white", relief="flat", padx=28, pady=6,
                       command=do_install)
    button.pack(pady=10)
    root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(prog=f"{APP_NAME}-Setup")
    parser.add_argument("--silent", action="store_true",
                        help="installer sans fenêtre (tests, scripts)")
    parser.add_argument("--dir", type=Path, default=None,
                        help="dossier d'installation (mode silencieux)")
    args = parser.parse_args()
    if args.silent:
        exe = install(args.dir or default_target(), shortcuts=args.dir is None)
        print(exe)
        return
    run_gui()


if __name__ == "__main__":
    main()
