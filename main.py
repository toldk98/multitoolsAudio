from init import *
from ui.fb2_to_mp3_app import FB2ToMP3App
from ui.settings_app import SettingsApp
from ui.audio_to_text import AudioToTextApp
from ui.logs_app import LogsApp
from  app_context import AppContext

class MainApp:
    def __init__(self, root):
        self.appname = "MainApp"
        self.root = root
        self.root.title("Aудіо/Книга мультитул")

        # Глобальний контекст (дані між вкладками)
        self.context = AppContext()
        self.context.main_app_ref = self  # ← для зручного доступу
        self.context.listener_manager.register_listener(self.update_tab_labels, "language")

        self.current_lang_code = self.context.get_config("global_config").get("language", "uk")

        self.setup_ui()
        self.check_ffmpeg_warning()

    def setup_ui(self):
        self.notebook = ttkb.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.tabs = {}  # Ініціалізація словника для зберігання екземплярів вкладок

        self.tab_keys = [  # ключі відповідають табам
            "AudioToTextApp",
            "TXTTranslateApp",
            "TXTToFB2App",
            "FB2ToMP3App",
            "SettingsApp",
            "LogsApp",
        ]

        # Список вкладок: (Назва вкладки, Клас UI)
        tabs = list(zip(self.tab_keys, [
            AudioToTextApp,
            AudioToTextApp,
            AudioToTextApp,
            FB2ToMP3App,
            SettingsApp,
            LogsApp
        ]))

        for tab_key, TabClass in tabs:
            frame = ttkb.Frame(self.notebook)
            frame.pack(fill="both", expand=True)

            # Ініціалізуємо піддодаток (клас вкладки)
            tab_instance = TabClass(frame, self.context)
            self.tabs[tab_key] = tab_instance  # Зберігаємо інстанси для подальшого використання

            tab_label = self.context.get_translate(
                self.current_lang_code, "MainApp", "tabs", tab_key, default=tab_key
            )
            # Додаємо вкладку до notebook
            self.notebook.add(frame, text=tab_label)

    def check_ffmpeg_warning(self):
        """Показує попередження, якщо ffmpeg не встановлений."""
        if self.context.ffmpeg_installed is False:
            messagebox.showwarning("FFmpeg", "На вашому пристрої не встановлено ffmpeg!")
            self.root.destroy()

    def update_tab_labels(self):
        current_lang = self.context.get_config("global_config").get("language")
        lang = self.context.get_config("global_config").get("language", current_lang)

        for idx, key in enumerate(self.tab_keys):
            translated = self.context.get_translate(lang, "MainApp", "tabs", key, default=key)
            self.notebook.tab(idx, text=translated)

if __name__ == "__main__":
    app = ttkb.Window(themename="minty")
    MainApp(app)
    app.mainloop()