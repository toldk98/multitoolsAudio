from jnius_config import options

from .collapsing_frame import CollapsingFrame

class UICreate:
    @staticmethod
    def collapsing_block(tk, parent, block_config, context=None, app_name=None):
        """
        Створює CollapsingFrame з заголовком і повертає frame.body
        """
        options = block_config.get("options", {})
        layout = block_config.get("layout", {})
        title = block_config.get("translate", "Section")

        # переклад, якщо context передано
        if context and app_name and "translate" in block_config and "group" in block_config:
            lang = context.get_config("global_config").get("language", "uk")
            group = block_config["group"]
            trans_key = block_config["translate"]
            title = context.get_translate(lang, app_name, group, trans_key, default=trans_key)

        collapse_frame = CollapsingFrame(parent, title=title, **options)
        collapse_frame.pack(**layout)

        return collapse_frame.get_body()

    @staticmethod
    def create_element(tk, widget_type, parent, options):
        match widget_type:
            case 'label':
                return tk.Label(parent, **options)
            case 'button':
                return tk.Button(parent, **options)
            case 'combobox':
                return tk.Combobox(parent, **options)
            case 'progressbar':
                return tk.Progressbar(parent, **options)
            case 'text':
                return tk.Text(parent, **options)
            case 'checkbutton':
                return tk.Checkbutton(parent, **options)
            case 'frame':
                return tk.Frame(parent, **options)
            case _:
                raise ValueError(f"Unsupported widget type: {widget_type}")

    @staticmethod
    def uiCreator(tk, parent, schema: dict, context=None, app_name=None) -> dict:

        created = {}
        container_frames = {}  # для зберігання collapse'ів

        # Спочатку створюємо collapsing блоки
        for key, cfg in schema.items():

            if cfg.get("type") == "collapsing_block":
                frame = UICreate.collapsing_block(tk, parent, cfg, context, app_name)
                container_frames[key] = frame
                created[key] = frame

                if hasattr(frame, "toogle_btn"):
                    created[f"{key}_toggle"] = frame.toogle_btn
            elif cfg.get("type") == "frame":
                options = cfg.get('options', {})
                layout = cfg.get("layout", {})
                frame = tk.Frame(parent, **options)
                frame.pack(**layout)
                container_frames[key] = frame
                created[key] = frame

        for key, cfg in schema.items():
            if cfg.get("type") == "collapsing_block":
                continue  # вже створено
            if cfg.get("type") == "frame":
                continue  # вже створено

            widget_type = cfg['type']
            options = cfg.get('options', {}).copy()
            layout = cfg.get('layout', {})
            method = cfg.get('layout_method', 'pack')
            hidden = cfg.get('hidden', False)

            # Додати переклад, якщо передано context, app_name і ключ перекладу
            if context and app_name and "translate" in cfg and "group" in cfg:
                current_lang = context.get_config("global_config").get("language")
                lang = context.get_config().get("language", current_lang)
                group = cfg["group"]
                trans_key = cfg["translate"]
                translated_text = context.get_translate(lang, app_name, group, trans_key, default=trans_key)

                if widget_type in ("label", "button") and "text" not in options:
                    options["text"] = translated_text

            parent_key = cfg.get("parent")
            real_parent = container_frames.get(parent_key, parent)
            widget = UICreate.create_element(tk, widget_type, real_parent, options)

            # Підтримка .set() (наприклад, для combobox)
            if "set" in cfg and hasattr(widget, "set"):
                try:
                    widget.set(cfg["set"])
                except Exception as e:
                    print(f"[⚠️] Не вдалося виконати .set() для {key}: {e}")

            if not hidden:
                match method:
                    case 'pack':
                        widget.pack(**layout)
                    case 'grid':
                        widget.grid(**layout)
                    case 'place':
                        widget.place(**layout)
                    case _:
                        raise ValueError(f"Невідомий метод розташування: {method}")

            created[key] = widget

        return created

    @staticmethod
    def update_translations(tk, widgets: dict, schema: dict, context, app_name: str):
        """
        Оновлює текст усіх віджетів згідно з новою мовою.
        """
        current_lang = context.get_config("global_config").get("language")
        lang = context.get_config("global_config").get("language", current_lang)

        for key, widget in widgets.items():
            cfg = schema.get(key, {})
            group = cfg.get("group")
            trans_key = cfg.get("translate")

            if not group or not trans_key:
                continue  # нічого перекладати

            translated_text = context.get_translate(lang, app_name, group, trans_key, default=trans_key)

            if key.endswith("__toggle"):
                main_key = key.split("__")[0]
                cfg = schema.get(main_key, {})
            else:
                cfg = schema.get(key, {})

            group = cfg.get("group")
            trans_key = cfg.get("translate")

            if not group or not trans_key:
                continue

            if isinstance(widget, tk.Button):
                if key.endswith("__toggle"):
                    widget.config(text=f"▼ {translated_text}")
                else:
                    widget.config(text=translated_text)
            elif isinstance(widget, tk.Label):
                widget.config(text=translated_text)

            # Оновлення тексту
            if isinstance(widget, (tk.Label, tk.Button)):
                widget.config(text=translated_text)
            elif isinstance(widget, tk.Combobox) and "set" in cfg:
                try:
                    widget.set(cfg["set"])
                except Exception:
                    pass
