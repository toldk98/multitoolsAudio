from init import *
import whisper
import warnings

warnings.filterwarnings("ignore", message="FP16 is not supported on CPU*")

class AudioToTextApp:
    def __init__(self, root, context):
        self.root = root
        self.root.update_idletasks()

        self.context = context
        self.appname = "mp3_to_txt"
        self.config = self.context.get_config(self.appname)
        self.audio_extensions = self.context.get_config("global").get("audio_extensions", [])

        # Шлях до аудіо та txt
        self.audio_directory = Path(self.config.get("audio_dir", "./audio_contert_to_txt"))
        self.txt_directory = Path(self.config.get("created_txt_directory", "./converted_txt"))
        self.txt_directory.mkdir(parents=True, exist_ok=True)

        # Завантаження моделі
        self.model = whisper.load_model(self.config.get("model", "small"))
        self.use_folder_var = tk.BooleanVar(value=False)
        self.selected_files = []
        self.start_time = None
        self.timer_running = False
        self.lang_detect_var = tk.BooleanVar(value=self.config.get("language_detection", False))

        self.setup_ui()

        # Listener для мови моделі
        self.context.listener_manager.register_listener(self.on_config_updated, "config")

    def setup_ui(self):
        frame = ttkb.Frame(self.root, padding=10)
        frame.pack(fill="both", expand=True)

        self.horizontal_frame = ttkb.Frame(frame)
        self.horizontal_frame.pack(pady=5)

        self.label_info = ttkb.Label(
            self.horizontal_frame,
            text="Оберіть аудіофайли або теку для розпізнавання",
            anchor="w"
        )
        self.label_info.pack(side="left", padx=20)

        self.chk_use_folder = ttkb.Checkbutton(
            self.horizontal_frame,
            text="Обрати теку",
            variable=self.use_folder_var
        )
        self.chk_use_folder.pack(side="right", padx=20)

        self.btn_select = ttkb.Button(
            frame,
            text="Вибрати аудіо",
            command=self.select_audio_source,
            bootstyle="PRIMARY"
        )
        self.btn_select.pack(fill="x", pady=10)

        self.label_selected_path = ttkb.Label(frame, text="Файли не вибрано", anchor="w")
        self.label_selected_path.pack(fill="x", pady=5)

        self.horizontal_frame_2 = ttkb.Frame(frame)
        self.horizontal_frame_2.pack(pady=5)

        self.chk_lang_detect = ttkb.Checkbutton(
            self.horizontal_frame_2,
            text="Автовизначення мови (Whisper)",
            variable=self.lang_detect_var,
            command=self.on_toggle_lang_detect,
        )
        self.chk_lang_detect.pack(side="left", padx= 20, pady=5)

        self.label_whisper_language = ttkb.Label(self.horizontal_frame_2, text="", anchor="center")
        self.label_whisper_language.pack(side="right", padx= 20, pady=5)

        self.btn_convert = ttkb.Button(
            frame,
            text="Почати конвертацію",
            command=self.start_conversion,
            bootstyle="SUCCESS"
        )
        self.btn_convert.pack(fill="x", pady=10)

        self.progbar_current = ttkb.Progressbar(frame, length=300)
        self.progbar_current.pack(fill="x", pady=(5, 0))

        self.progbar_total = ttkb.Progressbar(frame, length=300)
        self.progbar_total.pack(fill="x", pady=5)

        self.label_timer = ttkb.Label(frame, text="Час: 00:00:00", anchor="center")
        self.label_timer.pack(fill="x", pady=5)

        self.update_language_label()

    def on_toggle_lang_detect(self):
        value = self.lang_detect_var.get()
        self.context.update_app_config(self.appname, {"language_detection": value})
        self.config["language_detection"] = value  # локальне оновлення
        self.update_language_label()  # одразу оновити відображення мови

    def update_language_label(self):
        lang_code = self.context.get_config("mp3_to_txt").get("language", "uk")
        lang_name = self.context.get_language_name(lang_code, default=lang_code)
        self.label_whisper_language.config(text=f"Мова моделі: {lang_code} — {lang_name}")

    def on_config_updated(self, app_name):
        if app_name == "mp3_to_txt":
            self.update_language_label()

    def select_audio_source(self):
        self.selected_files = []

        if self.use_folder_var.get():
            folder = filedialog.askdirectory(title="Виберіть теку з аудіофайлами")
            if folder:
                files = [f for f in Path(folder).glob("*") if f.suffix.lower() in self.audio_extensions]
                self.selected_files = files
                self.label_selected_path.config(text=f"Тека: {folder} ({len(files)} файлів)")
        else:
            files = filedialog.askopenfilenames(
                title="Оберіть до 10 аудіофайлів",
                filetypes=[("Аудіофайли", "*.mp3 *.wav *.m4a *.ogg *.webm")]
            )
            if len(files) > 10:
                messagebox.showwarning(
                    "Забагато файлів",
                    "Максимум — 10 файлів. Щоб обробити більше — оберіть теку."
                )
                return
            self.selected_files = [Path(f) for f in files]
            self.label_selected_path.config(text=f"Файлів вибрано: {len(files)}")

    def start_conversion(self):
        if not self.selected_files:
            messagebox.showwarning("Немає файлів", "Будь ласка, оберіть файли або теку.")
            return

        self.progbar_current["value"] = 0
        self.progbar_total["value"] = 0

        threading.Thread(target=self.process_audio_files).start()
        self.start_timer()

    def process_audio_files(self):
        lang_detect = self.config.get("language_detection", True)
        lang_detect = self.lang_detect_var.get()
        language = None if lang_detect else self.config.get("language", "uk")

        total_files = len(self.selected_files)
        for idx, audio_file in enumerate(self.selected_files):
            if audio_file.suffix.lower() not in self.audio_extensions:
                continue

            print(f"🔊 Обробка: {audio_file.name}")
            result = self.model.transcribe(str(audio_file), language=language)

            output_file = self.txt_directory / (audio_file.stem + ".txt")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result["text"])
            print(f"✅ Збережено: {output_file.name}")

            # Оновити прогресбар
            progress = ((idx + 1) / total_files) * 100
            self.root.after(0, lambda p=progress: self.progbar_total.config(value=p))

        self.timer_running = False
        messagebox.showinfo("Готово", "Конвертація завершена.")

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
        self.label_timer.config(text=f"Час: {h:02}:{m:02}:{s:02}")
        self.root.after(1000, self.update_timer)
