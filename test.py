import os
import subprocess
import platform

def open_directory(path):
    # Використовуємо subprocess без xdg-open для налагодження
    subprocess.Popen(["doublecmd", path])

open_directory("/home/toldk98/pyProjects/fb2_to_mp3/")