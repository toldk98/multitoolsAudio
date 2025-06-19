import json
from pathlib import Path

class AppContext:
    def __init__(self):
        config_directory = Path("config")
        self.config_path = config_directory / "config.json"
        self.translates_path = config_directory / "translates.json"
        self.languages_path = config_directory / "languages.json"

        self.ffmpeg_installed = None
        self.logs = []

        self.config_raw = {}
        self.translates_raw = {}
        self.languages_raw = {}

        self._load_config()
        self._load_translations()
        self._load_languages()

        self._language_listeners = []
        self._config_listeners = []

    # ---------- CONFIG ----------

    def _load_config(self):
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config_raw = json.load(f)
        else:
            self.config_raw = {
                "global": {},
                "shared": {},
                "apps": {}
            }

    def get_config(self, app_name=None):
        if app_name is None:
            return self.config_raw

        result = {}
        global_config = self.config_raw.get("global", {})
        shared_config = self.config_raw.get("shared", {})
        app_specific = self.config_raw.get("apps", {}).get(app_name, {})

        result.update(global_config)

        for key, entry in shared_config.items():
            apps = entry.get("apps", [])
            if app_name in apps:
                result[key] = entry.get("value")

        result.update(app_specific)

        return result

    def update_global_config(self, updates: dict):
        if "global" not in self.config_raw:
            self.config_raw["global"] = {}

        self.config_raw["global"].update(updates)
        self.save_config()

        # Якщо змінилась мова — повідомляємо слухачів
        if "language" in updates:
            self.notify_language_change()

    # def update_global_config(self, updates: dict):
    #     """
    #     Оновлює значення у глобальній секції config["global"] і зберігає у файл.
    #     """
    #     if "global" not in self.config_raw:
    #         self.config_raw["global"] = {}
    #
    #     self.config_raw["global"].update(updates)
    #     self.save_config()

    def update_app_config(self, app_name, updates: dict):
        if "apps" not in self.config_raw:
            self.config_raw["apps"] = {}
        if app_name not in self.config_raw["apps"]:
            self.config_raw["apps"][app_name] = {}

        self.config_raw["apps"][app_name].update(updates)
        self.save_config()

    def save_config(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config_raw, f, indent=2, ensure_ascii=False)

    # ---------- TRANSLATIONS ----------

    def _load_translations(self):
        if self.translates_path.exists():
            with open(self.translates_path, "r", encoding="utf-8") as f:
                self.translates_raw = json.load(f)
        else:
            self.translates_raw = {}

    def get_translate(self, lang, app, group, key, default=""):
        """
        Повертає переклад для:
        - мови `lang`
        - програми `app` (наприклад, "FB2ToMP3App")
        - групи елементів `group` (label, button, ...)
        - ключа `key` (внутрішній id перекладного тексту)
        """
        return (
            self.translates_raw.get(lang, {})
            .get(app, {})
            .get(group, {})
            .get(key, default)
        )

    # ---------- LANGUAGES ----------

    def _load_languages(self):
        if self.languages_path.exists():
            with open(self.languages_path, "r", encoding="utf-8") as f:
                self.languages_raw = json.load(f)
        else:
            self.languages_raw = {}


    def get_languages(self) -> dict:
        """
        Повертає словник усіх мов, наприклад:
        { "ua": { "name": "Українська" }, "en": { "name": "Англійська" } }
        """
        return self.languages_raw

    def get_language_name(self, code: str, default="") -> str:
        """
        Повертає назву мови за кодом (наприклад "ua" → "Українська")
        """
        return self.languages_raw.get(code, {}).get("name", default or code)

    # @property
    def get_current_language(self) -> str:
        return self.config_raw.get("global", {}).get("language", "ua")

    # ---------- update -> if updated ----------

    def register_language_listener(self, callback: callable):
        """Реєструє функцію, яка буде викликана при зміні мови."""
        if callback not in self._language_listeners:
            self._language_listeners.append(callback)

    def notify_language_change(self):
        """Викликає всі callback'и, зареєстровані на зміну мови."""
        for callback in self._language_listeners:
            try:
                callback()
            except Exception as e:
                print(f"[⚠️] Language listener error: {e}")

    def register_config_listener(self, callback: callable):
        """Реєструє функцію, яка викликається при зміні конфігурації."""
        if callback not in self._config_listeners:
            self._config_listeners.append(callback)

    def notify_config_change(self, app_name: str):
        """Викликає всі callback'и при зміні конфігурації конкретного додатку."""
        for callback in self._config_listeners:
            try:
                callback(app_name)
            except Exception as e:
                print(f"[⚠️] Config listener error: {e}")
