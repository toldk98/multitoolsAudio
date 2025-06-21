from init import *

voice_options = [
            "uk-UA-PolinaNeural",
            "uk-UA-OstapNeural",
            "en-US-GuyNeural",
            "en-US-JennyNeural",
            "de-DE-KatjaNeural"
]

speed_options = [
    "-50%",
    "-25%",
    "0%",
    "+25%",
    "+50%"
]

class SettingsApp:
    def __init__(self, root, context):
        self.appname = "SettingsApp"
        self.root = root
        self.root.update_idletasks()

        self.context = context  # зберігаємо посилання на context
        self.context.ffmpeg_installed = self.check_ffmpeg() # Перевірка наявності ffmpeg
        self.config = self.context.get_config(self.appname)

        self.current_lang_code = self.context.get_config("global_config").get("language", "uk")
        self.language_name = self.context.get_language_name(self.current_lang_code)
        self.current_lang = f"{self.current_lang_code} — {self.language_name}"

        self.language_values = [
            f"{code} — {lang['name']}"
            for code, lang in self.context.get_languages().items()
        ]
        self.selected_language = tk.StringVar()

        # Whisper languages - ключі з translates.json + "ru" (використовується коли треба перекласти аудіо на нормальні мови)
        self.whisper_languages = list(self.context.translates_raw.keys()) + ["ru"]
        self.whisper_lang_values = sorted(set(self.whisper_languages))
        self.selected_whisper_language = tk.StringVar()

        # Default settings
        fb2_config = self.context.get_config("fb2_to_mp3")
        self.selected_voice = tk.StringVar(value=fb2_config.get("voice", "uk-UA-PolinaNeural"))
        self.selected_speed = tk.StringVar(value=fb2_config.get("speed", "0%"))

        self.element_schema = {
            "settings_block": {
                "type": "collapsing_block",
                "translate": "settings_section",
                "group": "collapsing_block",
                "layout": {"fill": "x", "pady": 10}
            },
            "label_path": {
                "type": "label",
                "translate": "app_translate",
                "group": "label",
                "parent": "settings_block",
                "options": {"anchor": "w"},
                "layout": {"fill": "x", "pady": 5}
            },
            "combo_app_language": {
                "type": "combobox",
                "translate": "app_language",
                "group": "combobox",
                "parent": "settings_block",
                "options": {"textvariable": self.selected_language, "values": self.language_values,
                            "state": "readonly"},
                "set": self.current_lang,
                "layout": {"fill": "x", "pady": 5}
            },
            "btn_select": {
                "type": "button",
                "translate": "select",
                "group": "button",
                "parent": "settings_block",
                "options": {"command": self.update_app_language, "bootstyle": "SUCCESS"},
                "layout": {"fill": "x", "pady": 5}
            },
            "mp3_to_txt_block": {
                "type": "collapsing_block",
                "translate": "mp3_to_txt_section",
                "group": "collapsing_block",
                "layout": {"fill": "x", "pady": 10}
            },
            "label_choose_model_lang": {
                "type": "label",
                "translate": "choose_whisper_lang",
                "group": "label",
                "parent": "mp3_to_txt_block",
                "options": {"anchor": "w"},
                "layout": {"fill": "x", "pady": (10, 0)}
            },
            "whisper_lang_menu": {
                "type": "combobox",
                "translate": "whisper_lang_menu",
                "group": "combobox",
                "parent": "mp3_to_txt_block",
                "options": {"textvariable": self.selected_whisper_language, "values": "", "state": "readonly"},
                "layout": {"fill": "x", "pady": 5}
            },
            "btn_save_whisper_lang": {
                "type": "button",
                "translate": "save_whisper_lang",
                "group": "button",
                "parent": "mp3_to_txt_block",
                "options": {"command": self.save_whisper_language, "bootstyle": "SUCCESS"},
                "layout": {"fill": "x", "pady": 10}
            },
            "fb2_to_mp3_block": {
                "type": "collapsing_block",
                "translate": "fb2_to_mp3_section",
                "group": "collapsing_block",
                "layout": {"fill": "x", "pady": 10}
            },
            "label_save_dir": {  # label вибір теки
                "type": "label",
                "translate": "save_dir",
                "group": "label",
                "parent": "fb2_to_mp3_block",
                "options": {"anchor": "w"},
                "layout": {"fill": "x", "pady": 5}
            },
            "btn_choose_dir": {
                # button вибір теки
                "type": "button",
                "translate": "choose_dir",
                "group": "button",
                "parent": "fb2_to_mp3_block",
                "options": {"command": self.choose_directory, "bootstyle": "PRIMARY"},
                "layout": {"fill": "x", "pady": 5}
            },
            "label_choose_voice": {
                "type": "label",
                "translate": "choose_voice",
                "group": "label",
                "parent": "fb2_to_mp3_block",
                "options": {"anchor": "w"},
                "layout": {"fill": "x", "pady": (10, 0)}
            },
            "voice_menu": {
                "type": "combobox",
                "translate": "voice_menu",
                "group": "combobox",
                "parent": "fb2_to_mp3_block",
                "options": {"textvariable": self.selected_voice, "values": voice_options, "state": "readonly"},
                "layout": {"fill": "x", "pady": 5}
            },
            "label_choose_speed": {
                "type": "label",
                "translate": "choose_speed",
                "group": "label",
                "parent": "fb2_to_mp3_block",
                "options": {"anchor": "w"},
                "layout": {"fill": "x", "pady": (10, 0)}
            },
            "speed_menu": {
                "type": "combobox",
                "translate": "speed_menu",
                "group": "combobox",
                "parent": "fb2_to_mp3_block",
                "options": {"textvariable": self.selected_speed, "values": speed_options, "state": "readonly"},
                "layout": {"fill": "x", "pady": 5}
            },
            "btn_save_voice_speed": {
                "type": "button",
                "translate": "save_voice_speed",
                "group": "button",
                "parent": "fb2_to_mp3_block",
                "options": {"command": self.save_voice_and_speed, "bootstyle": "SUCCESS"},
                "layout": {"fill": "x", "pady": 10}
            },

        }

        self.langs = self.context.get_languages()
        self.combo = {}
        self.setup_ui()

        self.context.listener_manager.register_listener(self.update_ui_language, "language")

    # Перевірка наявності ffmpeg
    def check_ffmpeg(self):
        """Check if ffmpeg is installed."""
        return which("ffmpeg") is not None

    # GUI
    def setup_ui(self):
        frame = ttkb.Frame(self.root, padding=10)
        frame.pack(fill="both", expand=True)

        self.widgets = UICreate.uiCreator(
            tk=ttkb,
            parent=frame,
            schema=self.element_schema,
            context=self.context,         # AppContext
            app_name=self.appname        # назва вкладки для translates.json
        )

        for name, widget in self.widgets.items():
            setattr(self, name, widget)

        # Whisper: встановлення поточного значення
        self.widgets["whisper_lang_menu"]["values"] = self.whisper_lang_values
        whisper_lang = self.context.get_config("mp3_to_txt").get("language", "uk")
        self.selected_whisper_language.set(whisper_lang)
        lang_name = self.context.get_language_name(whisper_lang, whisper_lang)
        self.widgets["label_choose_model_lang"].config(text=f"Обрано для моделі: {lang_name} ({whisper_lang})")

        self.update_save_dir_label()

    def save_voice_and_speed(self):
        voice = self.selected_voice.get()
        speed = self.selected_speed.get()

        self.context.update_app_config("fb2_to_mp3", {
            "voice": voice,
            "speed": speed
        })

        # messagebox.showinfo("Збережено", f"Голос: {voice}\nШвидкість: {speed}")

    def save_whisper_language(self):
        lang = self.selected_whisper_language.get()
        self.context.update_app_config("mp3_to_txt", {"language": lang})

        lang_name = self.context.get_language_name(lang, lang)
        self.widgets["label_choose_model_lang"].config(text=f"Обрано для моделі: {lang_name} ({lang})")

        self.context.add_log(f"[🗣️] Whisper-мову збережено: {lang}")

    # Вибір теки для збереження
    def choose_directory(self):
        dir_path = filedialog.askdirectory(
            title="Виберіть теку для збереження"
        )
        if dir_path:
            self.save_dir = dir_path
            self.widgets["label_save_dir"].config(text=f"Тека для збереження: {self.save_dir}")
            self.context.update_app_config("fb2_to_mp3", {
            "created_audiobook_dir": self.save_dir
            })
            self.context.listener_manager.notify_listeners("config", "fb2_to_mp3")

    def update_app_language(self):
        value = self.selected_language.get()        # value приклад: "uk — Українська"
        lang_code = value.split(" — ")[0].strip()   # lang_code: "uk"
        self.context.update_global_config({"language": lang_code}) # Зберегти мову, яку вибрав користувач
        # messagebox.showinfo("Налаштування", f"Мову збережено: {lang_code}")
        self.context.add_log(f"[🈯] Мову інтерфейсу змінено на: {value}")

    def update_ui_language(self):
        UICreate.update_translations(
            tk=ttkb,
            widgets=self.widgets,
            schema=self.element_schema,
            context=self.context,
            app_name=self.appname
        )
        self.update_save_dir_label()

    def update_save_dir_label(self):
        save_dir = self.context.get_config("fb2_to_mp3").get("created_audiobook_dir", "./")
        if "label_save_dir" in self.widgets:
            # self.widgets["label_save_dir"].config(text=f"Тека: {save_dir}")
            self.widgets["label_save_dir"].config(text=f"{self.widgets['label_save_dir'].cget('text')} {save_dir}")
