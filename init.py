import os
import platform
import regex
import asyncio
import threading
import time
import subprocess
import shutil
# лише імпорт модуля для Android і не-Android, потім використовуємо BeautifulSoup всередині
from bs4 import BeautifulSoup
import edge_tts
from edge_tts import Communicate
import pydub
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import ttkbootstrap as ttkb
# theme_names = ttkb.Style().theme_names()
# print(theme_names)
from ttkbootstrap.constants import *
from shutil import which
from ui.ui_create import UICreate
import json
from pathlib import Path
# from ui.collapsing_frame import CollapsingFrame  # або з init якщо в тебе там
