from init import *

class LogsApp:
    def __init__(self, root, context):
        self.root = root
        self.root.update_idletasks()

        self.context = context  # зберігаємо посилання на context

        self.element_schema = {
            "logs_text": {
                "type": "text",
                "translate": "logs",           # якщо потрібно, і є в translates.json
                "group": "label",              # або "text", якщо зробиш окрему групу
                "options": {
                    "state": "disabled",       # readonly
                    "wrap": "word"
                },
                "layout": {"fill": "both", "expand": True, "pady": 5}
            },
            "btn_save_logs": {
                "type": "button",
                "translate": "save_logs",
                "group": "button",
                "options": {
                    "command": self.save_logs,
                    "bootstyle": "PRIMARY"
                },
                "layout": {"fill": "x", "pady": 5}
            }

        }

        self.setup_ui()
        self.context.listener_manager.register_listener(self.display_logs, 'logs')
        # self.context.listener_manager.notify_listeners('logs', self.display_logs())


    # GUI
    def setup_ui(self):
        frame = ttkb.Frame(self.root, padding=10)
        frame.pack(fill="both", expand=True)

        self.widgets = UICreate.uiCreator(
            tk=ttkb,
            parent=frame,
            schema=self.element_schema,
            context=self.context,  # AppContext
            app_name="SettingsApp"  # назва вкладки для translates.json
        )

        for name, widget in self.widgets.items():
            setattr(self, name, widget)

        self.display_logs()


    def display_logs(self):
        if "logs_text" not in self.widgets:
            return

        logs = "\n".join(self.context.logs)
        widget = self.widgets["logs_text"]

        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", logs)
        widget.config(state="disabled")

    def save_logs(self):
        if not self.context.logs:
            messagebox.showinfo("ℹ️", "Логи порожні")
        self.context.write_log_file()
        messagebox.showinfo("Збережено", "Логи збережено у файл.")
