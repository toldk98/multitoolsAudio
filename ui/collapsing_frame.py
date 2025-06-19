import tkinter as tk
from tkinter import ttk

class CollapsingFrame(ttk.Frame):
    def __init__(self, parent, title="", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.configure_frame()
        self.create_toggle_button(title)
        self.create_body_wrapper()

    def configure_frame(self):
        self["padding"] = 5
        self["relief"] = "groove"
        self["borderwidth"] = 2
        self._expanded = tk.BooleanVar(value=True)

    def create_toggle_button(self, title):
        self.toggle_btn = ttk.Button(
            self,
            text=f"▼ {title}",
            command=self.toggle
        )
        self.toggle_btn.pack(fill="x")

    def create_body_wrapper(self):
        # Обгортка для вмісту
        self.body_wrapper = ttk.Frame(self)
        self.body_wrapper.pack(fill="both", expand=True)

        self.body = ttk.Frame(self.body_wrapper)
        self.body.pack(fill="both", expand=True)
        self.update_idletasks()  # примусово оновити геометрію

    def toggle(self):
        if self._expanded.get():
            self.body_wrapper.pack_forget()
            self.toggle_btn.config(text=self.toggle_btn.cget("text").replace("▼", "►"))
        else:
            self.body_wrapper.pack(fill="both", expand=True)
            self.toggle_btn.config(text=self.toggle_btn.cget("text").replace("►", "▼"))
        self._expanded.set(not self._expanded.get())

    def get_body(self):
        return self.body
