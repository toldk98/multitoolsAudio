import whisper
import os
from pathlib import Path

import warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU*")

# Завантаження моделі
model = whisper.load_model("small")

# Папка з аудіофайлами
audio_extensions = [".mp3", ".wav", ".m4a", ".ogg", ".webm"]
audio_directory = Path("audio_contert_to_txt")
txt_directory = Path("converted_txt")

audio_files = [f for f in audio_directory.iterdir() if f.suffix in audio_extensions]

if not audio_files:
    print("❌ Аудіофайли не знайдені в поточній папці.")
    exit()

for audio_file in audio_files:
    print(f"🔊 Обробка: {audio_file.name}")
    result = model.transcribe(str(audio_file), language="ru")

    output_file = audio_file.with_suffix(".txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result["text"])
    print(f"✅ Збережено: {output_file.name}")
