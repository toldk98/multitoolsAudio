from init import *

class AudioToTextApp:
    def __init__(self, root, context):
        self.root = root
        self.root.update_idletasks()

        self.setup_ui()

    # Перевірка наявності ffmpeg
    def check_ffmpeg(self):
        """Check if ffmpeg is installed."""
        if which("ffmpeg") is None:
            messagebox.showerror("Помилка", "FFmpeg не знайдено. Будь ласка, встановіть ffmpeg.")
            self.append_log("FFmpeg не знайдено. Скасування процесу.")
            self.cancel_requested = True
            self.timer_running = False
            return False
        return True

    # GUI
    def setup_ui(self):
        frame = ttkb.Frame(self.root, padding=10)
        frame.pack(fill=BOTH, expand=True)

        self.label_file = ttkb.Label(frame, text="Файл: не вибрано", anchor="w")
        self.label_file.pack(fill=X, pady=5)
    # функція для відкриття теки зі створеним MP3 файлом
    @staticmethod
    def open_directory(path):
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", path])
        else:  # Linux and others
            subprocess.Popen(["xdg-open", path])
