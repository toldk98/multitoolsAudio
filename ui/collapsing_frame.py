import tkinter as tk
from tkinter import ttk

class CollapsingFrame(ttk.Frame):
    open_frames = []

    def __init__(self, parent, title="", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._expanded = tk.BooleanVar(value=False)  # ⬅️ Закритий за замовчуванням

        self.configure_frame()
        self.create_toggle_button(title)
        self.create_body_wrapper()

    def configure_frame(self):
        self["padding"] = 5
        self["relief"] = "groove"
        self["borderwidth"] = 2

    def create_toggle_button(self, title):
        self.toggle_btn = ttk.Button(
            self,
            text=f"► {title}",  # ⬅️ Стартова стрілка для закритого стану
            command=self.toggle
        )
        self.toggle_btn.pack(fill="x")

    def create_body_wrapper(self):
        self.body_wrapper = ttk.Frame(self)
        self.body_wrapper.pack_forget()  # ⬅️ Стартово приховано

        self.body = ttk.Frame(self.body_wrapper)
        self.body.pack(fill="both", expand=True)

    def toggle(self):
        if self._expanded.get():
            self.collapse()
        else:
            # Закрити інші
            for frame in CollapsingFrame.open_frames[:]:
                if frame is not self:
                    frame.collapse()
            self.expand()

    def expand(self):
        self.body_wrapper.pack(fill="both", expand=True)
        self.toggle_btn.config(text=self.toggle_btn.cget("text").replace("►", "▼"))
        self._expanded.set(True)
        if self not in CollapsingFrame.open_frames:
            CollapsingFrame.open_frames.append(self)

    def collapse(self):
        self.body_wrapper.pack_forget()
        self.toggle_btn.config(text=self.toggle_btn.cget("text").replace("▼", "►"))
        self._expanded.set(False)
        if self in CollapsingFrame.open_frames:
            CollapsingFrame.open_frames.remove(self)

    def get_body(self):
        return self.body
