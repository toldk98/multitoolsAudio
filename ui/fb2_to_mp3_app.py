from init import *

voice_options = [
            "uk-UA-PolinaNeural",
            "uk-UA-OstapNeural",
            "en-US-GuyNeural",
            "en-US-JennyNeural",
            "de-DE-KatjaNeural"
        ]

speed_options = ["-50%", "-25%", "0%", "+25%", "+50%"]

class FB2ToMP3App:
    def __init__(self, root, context):
        self.appname = "FB2ToMP3App"
        self.root = root
        self.root.update_idletasks()
        self.context = context  # зберігаємо посилання на context
        self.context.listener_manager.register_listener(self.on_config_updated, "config")

        self.input_file = ""
        self.voice = ""

        self.fb2_file = ""
        self.save_dir = ""
        self.output_dir = ""
        self.cancel_requested = False
        self.start_time = None
        self.timer_running = False

        # Default settings
        self.selected_voice = tk.StringVar(value="uk-UA-PolinaNeural")
        self.selected_speed = tk.StringVar(value="0%")


        self.setup_ui()
        self.update_label()

    def update_label(self):
        config = self.context.get_config("fb2_to_mp3")
        self.save_dir = self.context.get_config("fb2_to_mp3").get("created_audiobook_dir", "./")
        self.voice = self.context.get_config("fb2_to_mp3").get("voice", "uk-UA-PolinaNeural")
        self.speed = self.context.get_config("fb2_to_mp3").get("speed", "0%")

        lang = self.context.get_current_language
        get_t = lambda key: self.context.get_translate(lang, self.appname, "label", key, key)

        self.widgets["label_save_dir"].config(text=f"{get_t('save_dir')}: {self.save_dir}")
        self.widgets["label_voice"].config(text=f"{get_t('choose_voice')}: {self.voice}")
        self.widgets["label_speed"].config(text=f"{get_t('choose_speed')}: {self.speed}")

    def on_config_updated(self, app_name):
        if app_name == "fb2_to_mp3":
            self.update_label()

    # GUI
    def setup_ui(self):
        frame = ttkb.Frame(self.root, padding=10)
        frame.pack(fill="both", expand=True)

        element_schema = {
            "label_file": { # label вибір файлу
                "type": "label",
                "translate": "file",
                "group": "label",
                "options": {"anchor": "w"},
                "layout": {"fill": "x", "pady": 5}
            },
            "btn_choose_file": { # button вибір файлу
                "type": "button",
                "translate": "choose_file",
                "group": "button",
                "options": {"command": self.choose_file, "bootstyle": "PRIMARY"},
                "layout": {"fill": "x", "pady": 5}
            },
            "label_save_dir": { # label вибір теки
                "type": "label",
                "translate": "save_dir",
                "group": "label",
                "options": {"anchor": "w"},
                "layout": {"fill": "x", "pady": 5}
            },
            "label_voice": {
                "type": "label",
                "translate": "voice",
                "group": "label",
                "options": {"anchor": "w"},
                "layout": {"fill": "x", "pady": (10, 0)}
            },
            "label_speed": {
                "type": "label",
                "translate": "speed",
                "group": "label",
                "options": {"anchor": "w"},
                "layout": {"fill": "x", "pady": (10, 0)}
            },
            "btn_create_mp3": {
                # button створення аудіокниги
                "type": "button",
                "translate": "create_mp3",
                "group": "button",
                "options": {"command": self.start_conversion, "bootstyle": "SUCCESS"},
                "layout": {"fill": "x", "pady": 5}
            },
            "btn_cancel": {
                # button відміна конвертації
                "type": "button",
                "translate": "cancel",
                "group": "button",
                "options": {"command": self.cancel_conversion, "state":"disabled", "bootstyle": "DANGER"},
                "layout": {"fill": "x", "pady": 5}
            },
            "label_progress_parts": {
                "type": "label",
                "translate": "progress_parts",
                "group": "label",
                "options": {"anchor": "w"},
                "layout": {"fill": "x", "pady": (10, 0)}
            },
            "progbar_progress_parts": {
                "type": "progressbar",
                "translate": "progress_parts",
                "group": "progressbar",
                "options": {"length": 300},
                "layout": {"fill": "x", "pady": 5}
            },
            "label_progress_merge": {
                "type": "label",
                "translate": "progress_merge",
                "group": "label",
                "options": {"anchor": "w"},
                "layout": {"fill": "x", "pady": (10, 0)}
            },
            "progbar_progress_merge": {
                "type": "progressbar",
                "translate": "progress_merge",
                "group": "progressbar",
                "options": {"length": 300},
                "layout": {"fill": "x", "pady": 5}
            },
            "label_time": {
                "type": "label",
                "translate": "time",
                "group": "label",
                "options": {"anchor": "center"},
                "layout": {"fill": "x", "pady": 5}
            },
        }
        self.widgets = UICreate.uiCreator(
            tk=ttkb,
            parent=frame,
            schema=element_schema,
            context=self.context,  # AppContext
            app_name="FB2ToMP3App"  # назва вкладки для translates.json
        )
        for name, widget in self.widgets.items():
            setattr(self, name, widget)

    # Вибір файлу для конвертації
    def choose_file(self):
        file_path = filedialog.askopenfilename(
            # filetypes=[("FB2 або TXT файли", "*.fb2 *.txt")],
            filetypes=[("", "*.fb2 *.txt")],
            title="Виберіть файл FB2 або TXT"
        )

        if file_path:
            self.fb2_file = file_path
            file_name = os.path.basename(file_path)
            self.widgets["label_file"].config(text=f"Обрано: {file_name}")
            self.widgets["btn_create_mp3"].config(state="normal")

    # очистка тексту від нестандартних символів
    def clean_text(self, text):
        # Залишаємо тільки літери (будь-якої мови), цифри, розділові знаки і пробіли
        text = regex.sub(r'[^\p{L}\p{N}\s.,!?;:\-()"«»]', ' ', text)
        text = regex.sub(r'\s+', ' ', text)
        return text.strip()

    def show_text_editor(self, full_text, on_save_callback):
        max_chars = 8000
        text_parts = [full_text[i:i + max_chars] for i in range(0, len(full_text), max_chars)]
        total_parts = len(text_parts)
        current_index = tk.IntVar(value=0)

        editor = tk.Toplevel(self.root)
        editor.title("Редагування тексту перед озвученням")
        editor.geometry("800x600")

        text_widget = tk.Text(editor, wrap="word")
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)

        nav_frame = ttk.Frame(editor)
        nav_frame.pack(pady=5)

        def update_buttons():
            prev_btn.config(state="normal" if current_index.get() > 0 else "disabled")
            next_btn.config(state="normal" if current_index.get() < total_parts - 1 else "disabled")
            save_btn.pack_forget()
            # if current_index.get() == total_parts - 1:
            save_btn.pack(pady=10)

        def show_current_part():
            text_widget.delete("1.0", "end")
            text_widget.insert("1.0", text_parts[current_index.get()])
            update_buttons()

        def prev_part():
            text_parts[current_index.get()] = text_widget.get("1.0", "end").strip()
            current_index.set(current_index.get() - 1)
            show_current_part()

        def next_part():
            text_parts[current_index.get()] = text_widget.get("1.0", "end").strip()
            current_index.set(current_index.get() + 1)
            show_current_part()

        def save_all():
            text_parts[current_index.get()] = text_widget.get("1.0", "end").strip()
            edited_text = "\n".join(text_parts)
            editor.destroy()
            on_save_callback(edited_text)

        prev_btn = ttkb.Button(nav_frame, text="← Попередня", command=prev_part, bootstyle=SECONDARY)
        next_btn = ttkb.Button(nav_frame, text="Наступна →", command=next_part, bootstyle=SECONDARY)
        save_btn = ttkb.Button(editor, text="Зберегти", command=save_all, bootstyle=SUCCESS)

        prev_btn.pack(side="left", padx=5)
        next_btn.pack(side="right", padx=5)

        show_current_part()

    def start_conversion(self):
        if not self.fb2_file or not self.save_dir:
            messagebox.showerror("Помилка", "Будь ласка, виберіть файл та теку для збереження.")
            return

        filename = os.path.splitext(os.path.basename(self.fb2_file))[0]
        self.output_dir = os.path.join(self.save_dir, filename)
        os.makedirs(self.output_dir, exist_ok=True)
        self.cancel_requested = False
        self.widgets["btn_create_mp3"].config(state="disabled")
        self.widgets["btn_cancel"].config(state="normal")
        self.widgets["progbar_progress_parts"]["value"] = 0
        self.widgets["progbar_progress_merge"]["value"] = 0
        self.start_time = time.time()
        self.timer_running = True
        threading.Thread(target=self.create_audiobook).start()
        self.update_timer()

    # перервати конвертацію
    def cancel_conversion(self):
        self.cancel_requested = True
        self.timer_running = False

    # оновлення таймера часу, який пройшов
    def update_timer(self):
        if self.timer_running:
            elapsed = int(time.time() - self.start_time)
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.widgets["label_time"].config(text=f"Час: {hours:02}:{minutes:02}:{seconds:02}")
            self.root.after(1000, self.update_timer)

    async def text_to_speech(self, text_parts):
        voice = self.selected_voice.get()
        rate = self.selected_speed.get()

        if voice not in voice_options:
            messagebox.showerror("Помилка голосу", f"Голос '{voice}' не підтримується.")

        for idx, part in enumerate(text_parts):
        #     if self.cancel_requested:
        #         self.append_log("Створення скасовано користувачем.")
        #         return

            rate = rate.strip()
            if not (rate.startswith('+') or rate.startswith('-')):
                rate = f"+{rate}"

            communicate = edge_tts.Communicate(text=part, voice=voice, rate=rate)
            output_file = os.path.join(self.output_dir, f"{idx + 1:03}.mp3")
            # self.append_log(f"Створюється частина {idx + 1}...")
            await communicate.save(output_file)
            self.widgets["progbar_progress_parts"]["value"] = ((idx + 1) / len(text_parts)) * 100
            # self.append_log(f"Озвучено частину {idx + 1}")

    # функція для відкриття теки зі створеним MP3 файлом
    @staticmethod
    def open_directory(path):
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", path])
        else:  # Linux and others
            subprocess.Popen(["xdg-open", path])

    # функція для об'єднання створених частинних MP3 файлів в один MP3 файл
    def merge_audio_parts(self):
        files = [os.path.join(self.output_dir, f) for f in sorted(os.listdir(self.output_dir)) if f.endswith(".mp3")]
        combined = pydub.AudioSegment.empty()

        for idx, file in enumerate(files):
            combined += pydub.AudioSegment.from_mp3(file)
            self.widgets["progbar_progress_merge"]["value"] = ((idx + 1) / len(files)) * 100
            # self.append_log(f"Додається частина {idx+1} до фінального файлу...")

        final_path = os.path.join(self.save_dir, "final_audiobook.mp3")
        combined.export(final_path, format="mp3")
        # self.append_log(f"Фінальний файл збережено як {final_path}")

        shutil.rmtree(self.output_dir)
        # self.append_log("Тимчасова тека видалена.")

        # open_directory(self.save_dir)

    # функція для створення аудіокниги з тексту конвертованого з fb2 книги
    def create_audiobook(self):
        if not self.fb2_file:
            messagebox.showwarning("Помилка", "Будь ласка, оберіть FB2 або TXT файл.")
            return

        try:
            with open(self.fb2_file, "r", encoding="utf-8") as file:
                text = file.read().strip()
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося прочитати файл: {e}")
            return

        if not text:
            messagebox.showwarning("Помилка", "Файл порожній.")
            return

        self.audiobook_path = self.output_dir
        text_file_path = os.path.join(self.output_dir, "audiobook_text.txt")

        with open(text_file_path, "w", encoding="utf-8") as f:
            f.write(text)
        # self.append_log(f"Текст збережено у {text_file_path}")

        def on_text_saved(edited_text):
            def process():
                try:
                    with open(text_file_path, "w", encoding="utf-8") as f:
                        f.write(edited_text)

                    max_chars = 8000
                    parts = [edited_text[i:i + max_chars] for i in range(0, len(edited_text), max_chars)]
                    # self.root.after(0, lambda: self.append_log(f"Текст розбитий на {len(parts)} частин(и)."))

                    # Озвучення
                    try:
                        asyncio.run(self.text_to_speech(parts))
                    except Exception as e:
                        self.root.after(0, lambda: messagebox.showerror("Помилка озвучення",
                                                                        f"Сталася помилка при озвученні: {e}"))
                        return
                    # Об'єднання
                    if not self.cancel_requested:
                        # if not self.check_ffmpeg():
                        #     self.root.after(0,
                        #                     lambda: self.append_log("ffmpeg не знайдено. Неможливо об'єднати аудіо."))
                        #     return
                        #
                        # self.root.after(0, lambda: self.append_log("Об'єднання частин у фінальний файл..."))
                        self.merge_audio_parts()

                finally:
                    self.root.after(0, lambda: self.widgets["btn_create_mp3"].config(state="normal"))
                    self.root.after(0, lambda: self.widgets["btn_cancel"].config(state="disabled"))
                    self.timer_running = False

            threading.Thread(target=process).start()

        self.root.after(0, lambda: self.show_text_editor(text, on_text_saved))