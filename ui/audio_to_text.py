from init import *
import whisper
import warnings

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU*")


class AudioToTextApp:
    def __init__(self, root, context):
        self.root = root
        self.root.update_idletasks()

        self.context = context
        self.appname = "AudioToTextApp"
        self.config = self.context.get_config(self.appname)
        self.audio_extensions = self.context.get_config("global").get("audio_extensions", [])

        self.audio_directory = Path(self.config.get("audio_dir", "./audio_contert_to_txt"))
        self.txt_directory = Path(self.config.get("created_txt_directory", "./converted_txt"))
        self.txt_directory.mkdir(parents=True, exist_ok=True)

        self.use_folder_var = tk.BooleanVar(value=False)
        self.lang_detect_var = tk.BooleanVar(value=self.config.get("language_detection", False))
        self.selected_files = []
        self.cancel_requested = False
        self.start_time = None
        self.timer_running = False

        self.context.listener_manager.register_listener(self.on_config_updated, "config")

        self.setup_ui()

        self.context.listener_manager.register_listener(self.update_ui_language, "language")


    def setup_ui(self):
        frame = ttkb.Frame(self.root, padding=10)
        frame.pack(fill="both", expand=True)

        self.element_schema = {
            "horizontal_frame_1": {
                "type": "frame",
                "layout": {"fill": "x", "pady": 5},
            },
            "label_info": {
                "type": "label",
                "translate": "info",
                "group": "label",
                "parent": "horizontal_frame_1",
                "options": {"anchor": "w"},
                "layout": {"side": "left", "padx": 20},
            },
            "chk_use_folder": {
                "type": "checkbutton",
                "translate": "use_folder",
                "group": "checkbutton",
                "parent": "horizontal_frame_1",
                "options": {"text":"Сhoose a folder", "variable": self.use_folder_var},
                "layout": {"side": "right", "padx": 20}
            },
            "btn_select": {
                "type": "button",
                "translate": "select",
                "group": "button",
                "options": {"command": self.select_audio_source, "bootstyle": "PRIMARY"},
                "layout": {"fill": "x", "pady": 10}
            },
            "label_selected_path": {
                "type": "label",
                "translate": "selected_path",
                "group": "label",
                "options": {"anchor": "w"},
                "layout": {"fill": "x", "pady": 5}
            },
            "horizontal_frame_2": {
                "type": "frame",
                "layout": {"fill": "x", "pady": 5}
            },
            "chk_lang_detect": {
                "type": "checkbutton",
                "translate": "lang_detect",
                "group": "checkbutton",
                "parent": "horizontal_frame_2",
                "options": {"text": "Language auto-selection", "variable": self.lang_detect_var, "command": self.on_toggle_lang_detect},
                "layout": {"side": "left", "padx": 20, "pady": 5}
            },
            "label_whisper_language": {
                "type": "label",
                "translate": "current_whisper_lang",
                "group": "label",
                "parent": "horizontal_frame_2",
                "options": {"anchor": "e"},
                "layout": {"side": "right", "padx": 20, "pady": 5}
            },
            "btn_convert": {
                "type": "button",
                "translate": "start_conversion",
                "group": "button",
                "options": {"command": self.start_conversion, "bootstyle": "SUCCESS", "state": "normal"},
                "layout": {"fill": "x", "pady": 10}
            },
            "btn_cancel": {
                "type": "button",
                "translate": "cancel",
                "group": "button",
                "options": {"command": self.cancel_conversion, "bootstyle": "DANGER", "state": "disabled"},
                "layout": {"fill": "x", "pady": 5}
            },
            "progbar_current": {
                "type": "progressbar",
                "group": "progressbar",
                "options": {"length": 300},
                "layout": {"fill": "x", "pady": (5, 0)}
            },
            "progbar_total": {
                "type": "progressbar",
                "group": "progressbar",
                "options": {"length": 300},
                "layout": {"fill": "x", "pady": 5}
            },
            "label_timer": {
                "type": "label",
                "translate": "timer",
                "group": "label",
                "options": {"anchor": "center"},
                "layout": {"fill": "x", "pady": 5}
            }
        }

        self.widgets = UICreate.uiCreator(
            tk=ttkb,
            parent=frame,
            schema=self.element_schema,
            context=self.context,
            app_name=self.appname
        )

        for name, widget in self.widgets.items():
            setattr(self, name, widget)


        self.update_label()

    def on_toggle_lang_detect(self):
        value = self.lang_detect_var.get()
        self.context.update_app_config(self.appname, {"language_detection": value})
        self.config["language_detection"] = value
        self.update_label()

    def update_label(self):
        config = self.context.get_config(self.appname)
        lang_code = self.context.get_config(self.appname).get("language", "uk")
        lang_name = self.context.get_language_name(lang_code, default=lang_code)
        self.widgets["label_whisper_language"].config(text=f"Мова моделі: {lang_code} — {lang_name}")

    def on_config_updated(self, app_name):
        if app_name == self.appname:
            self.update_label()

    def select_audio_source(self):
        self.selected_files = []

        if self.use_folder_var.get():
            folder = filedialog.askdirectory(title="Виберіть теку з аудіофайлами")
            if folder:
                files = [f for f in Path(folder).glob("*") if f.suffix.lower() in self.audio_extensions]
                self.selected_files = files
                self.widgets["label_selected_path"].config(text=f"Тека: {folder} ({len(files)} файлів)")
        else:
            files = filedialog.askopenfilenames(
                title="Оберіть до 10 аудіофайлів",
                filetypes=[("Аудіофайли", "*.mp3 *.wav *.m4a *.ogg *.webm")]
            )
            if len(files) > 10:
                messagebox.showwarning("Забагато файлів", "Максимум — 10 файлів. Щоб обробити більше — оберіть теку.")
                return
            self.selected_files = [Path(f) for f in files]
            self.widgets["label_selected_path"].config(text=f"Файлів вибрано: {len(files)}")

    def start_conversion(self):
        if not self.selected_files:
            messagebox.showwarning("Немає файлів", "Будь ласка, оберіть файли або теку.")
            return

        self.cancel_requested = False
        self.widgets["progbar_current"]["value"] = 0
        self.widgets["progbar_total"]["value"] = 0
        self.widgets["btn_convert"].config(state="disabled")
        self.widgets["btn_cancel"].config(state="normal")

        threading.Thread(target=self.process_audio_files).start()
        self.start_timer()

    def cancel_conversion(self):
        self.cancel_requested = True
        self.timer_running = False
        self.widgets["btn_cancel"].config(state="disabled")
        self.widgets["btn_convert"].config(state="normal")

    def process_audio_files(self):
        if not hasattr(self, "model"):
            self.model = whisper.load_model(self.config.get("model", "small"))

        lang_detect = self.lang_detect_var.get()
        language = None if lang_detect else self.config.get("language", "uk")
        self.selected_files = [f for f in self.selected_files if f.suffix.lower() in self.audio_extensions]

        total_files = len(self.selected_files)
        for idx, audio_file in enumerate(self.selected_files):
            if self.cancel_requested:
                self.timer_running = False
                print("Створення скасовано користувачем")
                break

            self.root.after(0, lambda: self.widgets["progbar_current"].config(value=0))

            print(f"🔊 Обробка: {audio_file.name}")
            result = self.model.transcribe(str(audio_file), language=language)
            output_file = self.txt_directory / (audio_file.stem + ".txt")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result["text"])

            self.root.after(0, lambda: self.widgets["progbar_current"].config(value=100))

            progress = ((idx + 1) / total_files) * 100
            self.root.after(0, lambda p=progress: self.widgets["progbar_total"].config(value=p))

        self.timer_running = False
        self.root.after(0, lambda: self.widgets["btn_convert"].config(state="normal"))
        self.root.after(0, lambda: self.widgets["btn_cancel"].config(state="disabled"))
        self.root.after(0, lambda: messagebox.showinfo("Готово", "Конвертація завершена."))

    def start_timer(self):
        self.start_time = time.time()
        self.timer_running = True
        self.update_timer()

    def update_timer(self):
        if not self.timer_running:
            return
        elapsed = int(time.time() - self.start_time)
        h, rem = divmod(elapsed, 3600)
        m, s = divmod(rem, 60)
        self.widgets["label_timer"].config(text=f"Час: {h:02}:{m:02}:{s:02}")
        self.root.after(1000, self.update_timer)

    def update_ui_language(self):
        UICreate.update_translations(
            tk=ttkb,
            widgets=self.widgets,
            schema=self.element_schema,
            context=self.context,
            app_name=self.appname
        )