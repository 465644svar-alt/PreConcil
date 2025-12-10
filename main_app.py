import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
import json
import requests
import socket
import time
from datetime import datetime
import openai
from anthropic import Anthropic
from openai import OpenAI as DeepSeekClient


class NeuralNetworkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер нейросетей v5.0 (Бесплатные API)")
        self.root.geometry("900x700")

        # Конфигурация
        self.config_file = "config.json"
        self.load_config()

        # Переменные для хранения статусов соединения
        self.connection_status = {
            "OpenAI GPT": False,
            "Anthropic Claude": False,
            "DeepSeek": False,
            "Groq": False,
            "OpenRouter": False,
            "Hugging Face": False
        }

        # Создаем вкладки
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Вкладка 1: Основные настройки
        self.setup_main_tab()

        # Вкладка 2: Настройки API
        self.setup_api_tab()

        # Вкладка 3: История запросов
        self.setup_history_tab()

        # Вкладка 4: Статус соединения
        self.setup_status_tab()

        # Загружаем конфигурацию
        self.load_config_to_ui()

        # Проверяем соединение при запуске (в фоне)
        self.root.after(1000, self.check_all_connections_background)

    def load_config(self):
        """Загрузка конфигурации из файла"""
        self.config = {
            "api_keys": {
                "openai": "",
                "anthropic": "",
                "deepseek": "",
                "groq": "",
                "openrouter": "",
                "huggingface": ""  # Добавлен Hugging Face
            },
            "telegram": {
                "bot_token": "",
                "chat_id": ""
            },
            "last_directory": ""
        }

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Обновляем только существующие ключи
                    for key in self.config:
                        if key in loaded_config:
                            self.config[key].update(loaded_config[key])
            except:
                pass

    def save_config(self):
        """Сохранение конфигурации в файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False

    def setup_main_tab(self):
        """Создание основной вкладки"""
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Основное")

        # Фрейм для выбора файла
        file_frame = ttk.LabelFrame(self.main_tab, text="Выбор файла с вопросом", padding=10)
        file_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(file_frame, text="Файл с вопросом:").grid(row=0, column=0, sticky='w')

        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=60)
        self.file_entry.grid(row=1, column=0, padx=(0, 10))

        ttk.Button(file_frame, text="Выбрать...", command=self.select_file).grid(row=1, column=1)

        # Отображение базового имени файла
        ttk.Label(file_frame, text="Имя файла для сохранения:").grid(row=2, column=0, sticky='w', pady=(10, 0))
        self.filename_display_var = tk.StringVar()
        ttk.Label(file_frame, textvariable=self.filename_display_var,
                  font=('TkDefaultFont', 9, 'italic')).grid(row=3, column=0, columnspan=2, sticky='w')

        # Фрейм для выбора директории сохранения
        save_frame = ttk.LabelFrame(self.main_tab, text="Директория для сохранения ответов", padding=10)
        save_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(save_frame, text="Папка для сохранения:").grid(row=0, column=0, sticky='w')

        self.save_path_var = tk.StringVar()
        self.save_entry = ttk.Entry(save_frame, textvariable=self.save_path_var, width=60)
        self.save_entry.grid(row=1, column=0, padx=(0, 10))
        ttk.Button(save_frame, text="Выбрать...", command=self.select_save_directory).grid(row=1, column=1)

        # Предварительный просмотр имени файла для сохранения
        ttk.Label(save_frame, text="Будет сохранен как:").grid(row=2, column=0, sticky='w', pady=(10, 0))
        self.save_filename_var = tk.StringVar()
        ttk.Label(save_frame, textvariable=self.save_filename_var,
                  font=('TkDefaultFont', 9, 'italic'), foreground='blue').grid(row=3, column=0, columnspan=2,
                                                                               sticky='w')

        # Фрейм для выбора нейросетей
        networks_frame = ttk.LabelFrame(self.main_tab, text="Выбор нейросетей (Бесплатные отмечены * )", padding=10)
        networks_frame.pack(fill='x', padx=10, pady=5)

        self.networks_vars = {
            "OpenAI GPT": tk.BooleanVar(value=False),
            "Anthropic Claude": tk.BooleanVar(value=False),
            "DeepSeek*": tk.BooleanVar(value=True),
            "Groq*": tk.BooleanVar(value=True),
            "OpenRouter*": tk.BooleanVar(value=True),
            "Hugging Face*": tk.BooleanVar(value=True)
        }

        self.network_checkbuttons = {}
        row_counter = 0
        for name, var in self.networks_vars.items():
            cb = ttk.Checkbutton(networks_frame, text=name, variable=var)
            cb.grid(row=row_counter, column=0, sticky='w', padx=10, pady=2)
            self.network_checkbuttons[name] = cb
            row_counter += 1

        # Кнопки управления
        button_frame = ttk.Frame(self.main_tab)
        button_frame.pack(fill='x', padx=10, pady=20)

        ttk.Button(button_frame, text="Проверить соединение",
                   command=self.check_connections).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Отправить запрос", command=self.send_requests,
                   style="Accent.TButton").pack(side='left', padx=5)
        ttk.Button(button_frame, text="Сохранить конфигурацию",
                   command=self.save_configuration).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Очистить лог",
                   command=self.clear_log).pack(side='left', padx=5)

        # Прогресс-бар и лог
        self.progress = ttk.Progressbar(self.main_tab, mode='indeterminate')
        self.progress.pack(fill='x', padx=10, pady=5)

        log_frame = ttk.LabelFrame(self.main_tab, text="Лог выполнения", padding=10)
        log_frame.pack(fill='both', expand=True, padx=10, pady=20)

        self.log_text = tk.Text(log_frame, height=10, wrap='word')
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Привязываем события изменения
        self.file_path_var.trace('w', self.update_filename_display)
        self.save_path_var.trace('w', self.update_save_filename_display)

    def setup_api_tab(self):
        """Создание вкладки с настройками API"""
        self.api_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.api_tab, text="Настройки API")

        # OpenAI (Платный)
        openai_frame = ttk.LabelFrame(self.api_tab, text="OpenAI API (Платный)", padding=10)
        openai_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(openai_frame, text="API ключ:").grid(row=0, column=0, sticky='w')
        self.openai_key_var = tk.StringVar()
        self.openai_entry = ttk.Entry(openai_frame, textvariable=self.openai_key_var, width=60, show="*")
        self.openai_entry.grid(row=1, column=0, padx=(0, 10))
        ttk.Button(openai_frame, text="Показать",
                   command=lambda: self.toggle_password(self.openai_entry)).grid(row=1, column=1)

        # Anthropic (Платный)
        anthropic_frame = ttk.LabelFrame(self.api_tab, text="Anthropic API (Платный)", padding=10)
        anthropic_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(anthropic_frame, text="API ключ:").grid(row=0, column=0, sticky='w')
        self.anthropic_key_var = tk.StringVar()
        self.anthropic_entry = ttk.Entry(anthropic_frame, textvariable=self.anthropic_key_var, width=60, show="*")
        self.anthropic_entry.grid(row=1, column=0, padx=(0, 10))
        ttk.Button(anthropic_frame, text="Показать",
                   command=lambda: self.toggle_password(self.anthropic_entry)).grid(row=1, column=1)

        # DeepSeek (Бесплатный с лимитами)
        deepseek_frame = ttk.LabelFrame(self.api_tab, text="DeepSeek API (Бесплатный*)", padding=10)
        deepseek_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(deepseek_frame, text="API ключ:").grid(row=0, column=0, sticky='w')
        self.deepseek_key_var = tk.StringVar()
        self.deepseek_entry = ttk.Entry(deepseek_frame, textvariable=self.deepseek_key_var, width=60, show="*")
        self.deepseek_entry.grid(row=1, column=0, padx=(0, 10))
        ttk.Button(deepseek_frame, text="Показать",
                   command=lambda: self.toggle_password(self.deepseek_entry)).grid(row=1, column=1)
        ttk.Label(deepseek_frame, text="* 100 запросов/час, нужен баланс",
                  font=('TkDefaultFont', 8, 'italic')).grid(row=2, column=0, columnspan=2, sticky='w', pady=(5, 0))

        # Groq (Бесплатный)
        groq_frame = ttk.LabelFrame(self.api_tab, text="Groq API (Бесплатный*)", padding=10)
        groq_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(groq_frame, text="API ключ:").grid(row=0, column=0, sticky='w')
        self.groq_key_var = tk.StringVar()
        self.groq_entry = ttk.Entry(groq_frame, textvariable=self.groq_key_var, width=60, show="*")
        self.groq_entry.grid(row=1, column=0, padx=(0, 10))
        ttk.Button(groq_frame, text="Показать",
                   command=lambda: self.toggle_password(self.groq_entry)).grid(row=1, column=1)
        ttk.Label(groq_frame, text="* 30 запросов/минуту, регистрация на groq.com",
                  font=('TkDefaultFont', 8, 'italic')).grid(row=2, column=0, columnspan=2, sticky='w', pady=(5, 0))

        # OpenRouter (Бесплатные модели)
        openrouter_frame = ttk.LabelFrame(self.api_tab, text="OpenRouter API (Бесплатные модели*)", padding=10)
        openrouter_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(openrouter_frame, text="API ключ:").grid(row=0, column=0, sticky='w')
        self.openrouter_key_var = tk.StringVar()
        self.openrouter_entry = ttk.Entry(openrouter_frame, textvariable=self.openrouter_key_var, width=60, show="*")
        self.openrouter_entry.grid(row=1, column=0, padx=(0, 10))
        ttk.Button(openrouter_frame, text="Показать",
                   command=lambda: self.toggle_password(self.openrouter_entry)).grid(row=1, column=1)
        ttk.Label(openrouter_frame, text="* Бесплатные модели: mistral-7b, gemma-7b",
                  font=('TkDefaultFont', 8, 'italic')).grid(row=2, column=0, columnspan=2, sticky='w', pady=(5, 0))

        # Hugging Face (Бесплатный, ключ не обязателен)
        huggingface_frame = ttk.LabelFrame(self.api_tab, text="Hugging Face API (Бесплатный*)", padding=10)
        huggingface_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(huggingface_frame, text="API ключ (необязательно):").grid(row=0, column=0, sticky='w')
        self.huggingface_key_var = tk.StringVar()
        self.huggingface_entry = ttk.Entry(huggingface_frame, textvariable=self.huggingface_key_var, width=60, show="*")
        self.huggingface_entry.grid(row=1, column=0, padx=(0, 10))
        ttk.Button(huggingface_frame, text="Показать",
                   command=lambda: self.toggle_password(self.huggingface_entry)).grid(row=1, column=1)
        ttk.Label(huggingface_frame, text="* Можно использовать без ключа (с лимитами)",
                  font=('TkDefaultFont', 8, 'italic')).grid(row=2, column=0, columnspan=2, sticky='w', pady=(5, 0))

        # Telegram Bot
        telegram_frame = ttk.LabelFrame(self.api_tab, text="Telegram Bot API", padding=10)
        telegram_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(telegram_frame, text="Токен бота:").grid(row=0, column=0, sticky='w')
        self.telegram_token_var = tk.StringVar()
        ttk.Entry(telegram_frame, textvariable=self.telegram_token_var, width=60).grid(row=1, column=0, columnspan=2,
                                                                                       pady=(0, 10))

        ttk.Label(telegram_frame, text="Chat ID:").grid(row=2, column=0, sticky='w')
        self.telegram_chat_id_var = tk.StringVar()
        ttk.Entry(telegram_frame, textvariable=self.telegram_chat_id_var, width=60).grid(row=3, column=0, columnspan=2)

    def setup_status_tab(self):
        """Создание вкладки со статусом соединения"""
        self.status_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.status_tab, text="Статус соединения")

        # Фрейм для статусов
        status_frame = ttk.LabelFrame(self.status_tab, text="Статус подключения к API", padding=10)
        status_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Создаем виджеты для отображения статуса
        self.status_labels = {}
        self.status_text_vars = {}

        networks = [
            ("OpenAI GPT", self.openai_key_var),
            ("Anthropic Claude", self.anthropic_key_var),
            ("DeepSeek*", self.deepseek_key_var),
            ("Groq*", self.groq_key_var),
            ("OpenRouter*", self.openrouter_key_var),
            ("Hugging Face*", self.huggingface_key_var)
        ]

        for i, (name, key_var) in enumerate(networks):
            # Фрейм для каждого сервиса
            service_frame = ttk.Frame(status_frame)
            service_frame.pack(fill='x', padx=10, pady=5)

            # Название сервиса
            ttk.Label(service_frame, text=f"{name}:", width=15, anchor='w').pack(side='left', padx=(0, 10))

            # Индикатор статуса
            status_canvas = tk.Canvas(service_frame, width=20, height=20, bg='white', highlightthickness=0)
            status_canvas.pack(side='left', padx=(0, 10))
            self.status_labels[name] = status_canvas

            # Текст статуса
            status_text_var = tk.StringVar(value="Не проверено")
            self.status_text_vars[name] = status_text_var
            ttk.Label(service_frame, textvariable=status_text_var, width=20, anchor='w').pack(side='left', padx=(0, 10))

            # Кнопка проверки
            ttk.Button(service_frame, text="Проверить", width=10,
                       command=lambda n=name, k=key_var: self.check_single_connection(n, k.get())).pack(side='left')

        # Кнопка проверки всех соединений
        ttk.Button(status_frame, text="Проверить все соединения",
                   command=self.check_all_connections, style="Accent.TButton").pack(pady=20)

    def setup_history_tab(self):
        """Создание вкладки с историей"""
        self.history_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.history_tab, text="История")

        # Панель управления историей
        history_control = ttk.Frame(self.history_tab)
        history_control.pack(fill='x', padx=10, pady=5)

        ttk.Button(history_control, text="Обновить", command=self.load_history).pack(side='left', padx=5)
        ttk.Button(history_control, text="Отправить в Telegram",
                   command=self.send_selected_to_telegram).pack(side='left', padx=5)

        # Список файлов
        list_frame = ttk.Frame(self.history_tab)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.history_listbox = tk.Listbox(list_frame, selectmode='single')
        scrollbar = ttk.Scrollbar(list_frame, command=self.history_listbox.yview)
        self.history_listbox.configure(yscrollcommand=scrollbar.set)

        self.history_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Просмотр содержимого
        view_frame = ttk.LabelFrame(self.history_tab, text="Просмотр файла", padding=10)
        view_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.history_text = tk.Text(view_frame, wrap='word')
        history_scrollbar = ttk.Scrollbar(view_frame, command=self.history_text.yview)
        self.history_text.configure(yscrollcommand=history_scrollbar.set)

        self.history_text.pack(side='left', fill='both', expand=True)
        history_scrollbar.pack(side='right', fill='y')

        # Привязываем событие выбора
        self.history_listbox.bind('<<ListboxSelect>>', self.on_history_select)

    def load_config_to_ui(self):
        """Загрузка конфигурации в UI"""
        self.openai_key_var.set(self.config["api_keys"]["openai"])
        self.anthropic_key_var.set(self.config["api_keys"]["anthropic"])
        self.deepseek_key_var.set(self.config["api_keys"]["deepseek"])
        self.groq_key_var.set(self.config["api_keys"]["groq"])
        self.openrouter_key_var.set(self.config["api_keys"]["openrouter"])
        self.huggingface_key_var.set(self.config["api_keys"]["huggingface"])

        self.telegram_token_var.set(self.config["telegram"]["bot_token"])
        self.telegram_chat_id_var.set(self.config["telegram"]["chat_id"])

        if self.config["last_directory"]:
            self.save_path_var.set(self.config["last_directory"])

    def toggle_password(self, entry):
        """Переключение видимости пароля"""
        current_show = entry.cget('show')
        entry.config(show='' if current_show == '*' else '*')

    def update_filename_display(self, *args):
        """Обновление отображения имени файла"""
        filepath = self.file_path_var.get()
        if filepath and os.path.exists(filepath):
            filename = os.path.basename(filepath)
            base_name = os.path.splitext(filename)[0]
            self.filename_display_var.set(f"Базовое имя: {base_name}")
            self.update_save_filename_display()
        else:
            self.filename_display_var.set("")

    def update_save_filename_display(self, *args):
        """Обновление отображения имени файла для сохранения"""
        filepath = self.file_path_var.get()
        save_dir = self.save_path_var.get()

        if filepath and save_dir and os.path.exists(filepath):
            filename = os.path.basename(filepath)
            base_name = os.path.splitext(filename)[0]
            save_name = self.generate_unique_filename(save_dir, base_name)
            self.save_filename_var.set(save_name)
        else:
            self.save_filename_var.set("")

    def generate_unique_filename(self, directory, base_name):
        """Генерация уникального имени файла с суффиксами (1), (2) и т.д."""
        suffix = "_answer"
        counter = 1
        filename = f"{base_name}{suffix}.txt"
        filepath = os.path.join(directory, filename)

        # Проверяем существование файлов и добавляем суффиксы
        while os.path.exists(filepath):
            if counter == 1:
                filename = f"{base_name}{suffix} (1).txt"
            else:
                filename = f"{base_name}{suffix} ({counter}).txt"
            filepath = os.path.join(directory, filename)
            counter += 1

        return filename

    def select_file(self):
        """Выбор файла с вопросом"""
        filename = filedialog.askopenfilename(
            title="Выберите файл с вопросом",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)

    def select_save_directory(self):
        """Выбор директории для сохранения"""
        directory = filedialog.askdirectory(title="Выберите папку для сохранения")
        if directory:
            self.save_path_var.set(directory)
            self.config["last_directory"] = directory
            self.save_config()

    def check_all_connections_background(self):
        """Фоновая проверка всех соединений"""
        thread = threading.Thread(target=self._check_all_connections_thread, daemon=True)
        thread.start()

    def _check_all_connections_thread(self):
        """Поток для проверки всех соединений"""
        networks_to_check = []

        if self.openai_key_var.get():
            networks_to_check.append(("OpenAI GPT", self.openai_key_var.get()))
        if self.anthropic_key_var.get():
            networks_to_check.append(("Anthropic Claude", self.anthropic_key_var.get()))
        if self.deepseek_key_var.get():
            networks_to_check.append(("DeepSeek*", self.deepseek_key_var.get()))
        if self.groq_key_var.get():
            networks_to_check.append(("Groq*", self.groq_key_var.get()))
        if self.openrouter_key_var.get():
            networks_to_check.append(("OpenRouter*", self.openrouter_key_var.get()))
        # Hugging Face проверяем всегда (может работать без ключа)
        networks_to_check.append(("Hugging Face*", self.huggingface_key_var.get()))

        for name, key in networks_to_check:
            self.check_single_connection(name, key)
            time.sleep(1)

    def check_single_connection(self, network_name, api_key):
        """Проверка соединения с одной нейросетью"""
        try:
            if network_name == "OpenAI GPT":
                status = self.test_openai_connection(api_key)
            elif network_name == "Anthropic Claude":
                status = self.test_anthropic_connection(api_key)
            elif network_name == "DeepSeek*":
                status = self.test_deepseek_connection(api_key)
            elif network_name == "Groq*":
                status = self.test_groq_connection(api_key)
            elif network_name == "OpenRouter*":
                status = self.test_openrouter_connection(api_key)
            elif network_name == "Hugging Face*":
                status = self.test_huggingface_connection(api_key)
            else:
                status = False

            self.connection_status[network_name] = status
            self.update_status_indicator(network_name, status)

            if not status and api_key:
                self.log_message(f"⚠️ Не удалось подключиться к {network_name}")

            return status

        except Exception as e:
            self.connection_status[network_name] = False
            self.update_status_indicator(network_name, False)
            self.log_message(f"❌ Ошибка проверки {network_name}: {str(e)}")
            return False

    def update_status_indicator(self, network_name, status):
        """Обновление индикатора статуса"""
        if network_name in self.status_labels:
            canvas = self.status_labels[network_name]
            canvas.delete("all")

            if status:
                # Зеленый кружок
                canvas.create_oval(2, 2, 18, 18, fill="green", outline="")
                canvas.create_text(10, 10, text="✓", fill="white", font=('Arial', 10, 'bold'))
                self.status_text_vars[network_name].set("Подключено ✓")
            else:
                # Красный кружок
                canvas.create_oval(2, 2, 18, 18, fill="red", outline="")
                canvas.create_text(10, 10, text="✗", fill="white", font=('Arial', 10, 'bold'))
                self.status_text_vars[network_name].set("Ошибка ✗")

    def test_openai_connection(self, api_key):
        """Тест соединения с OpenAI"""
        if not api_key:
            return False

        try:
            openai.api_key = api_key
            openai.Model.list()
            return True
        except:
            return False

    def test_anthropic_connection(self, api_key):
        """Тест соединения с Anthropic"""
        if not api_key:
            return False

        try:
            client = Anthropic(api_key=api_key)
            client.models.list()
            return True
        except:
            return False

    def test_deepseek_connection(self, api_key):
        """Тест соединения с DeepSeek"""
        if not api_key:
            return False

        try:
            client = DeepSeekClient(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
            client.models.list()
            return True
        except:
            return False

    def test_groq_connection(self, api_key):
        """Тест соединения с Groq"""
        if not api_key:
            return False

        try:
            url = "https://api.groq.com/openai/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(url, headers=headers, timeout=10)
            return response.status_code == 200
        except:
            return False

    def test_openrouter_connection(self, api_key):
        """Тест соединения с OpenRouter"""
        if not api_key:
            return False

        try:
            url = "https://openrouter.ai/api/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(url, headers=headers, timeout=10)
            return response.status_code == 200
        except:
            return False

    def test_huggingface_connection(self, api_key):
        """Тест соединения с Hugging Face"""
        try:
            # Hugging Face может работать без ключа
            url = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            response = requests.get(url, headers=headers, timeout=10)
            # 200 или 503 (модель загружается) считаем успехом
            return response.status_code in [200, 503]
        except:
            return False

    def check_connections(self):
        """Проверка всех соединений"""
        self.log_message("Проверяем соединения...")
        thread = threading.Thread(target=self._check_all_connections_thread, daemon=True)
        thread.start()

    def check_all_connections(self):
        """Проверка всех соединений с уведомлением"""
        self.log_message("Начинаем проверку всех соединений...")

        failed_connections = []
        successful_connections = []

        if self.openai_key_var.get():
            if self.check_single_connection("OpenAI GPT", self.openai_key_var.get()):
                successful_connections.append("OpenAI GPT")
            else:
                failed_connections.append("OpenAI GPT")

        if self.anthropic_key_var.get():
            if self.check_single_connection("Anthropic Claude", self.anthropic_key_var.get()):
                successful_connections.append("Anthropic Claude")
            else:
                failed_connections.append("Anthropic Claude")

        if self.deepseek_key_var.get():
            if self.check_single_connection("DeepSeek*", self.deepseek_key_var.get()):
                successful_connections.append("DeepSeek")
            else:
                failed_connections.append("DeepSeek")

        if self.groq_key_var.get():
            if self.check_single_connection("Groq*", self.groq_key_var.get()):
                successful_connections.append("Groq")
            else:
                failed_connections.append("Groq")

        if self.openrouter_key_var.get():
            if self.check_single_connection("OpenRouter*", self.openrouter_key_var.get()):
                successful_connections.append("OpenRouter")
            else:
                failed_connections.append("OpenRouter")

        # Hugging Face всегда проверяем
        if self.check_single_connection("Hugging Face*", self.huggingface_key_var.get()):
            successful_connections.append("Hugging Face")
        else:
            failed_connections.append("Hugging Face")

        self.show_connection_results(successful_connections, failed_connections)

    def show_connection_results(self, successful, failed):
        """Показ результатов проверки соединений"""
        message = "Результаты проверки соединений:\n\n"

        if successful:
            message += "✅ Успешные подключения:\n"
            for service in successful:
                message += f"   • {service}\n"
            message += "\n"

        if failed:
            message += "❌ Не удалось подключиться:\n"
            for service in failed:
                message += f"   • {service}\n"

        if not successful and not failed:
            message += "ℹ️ Нет сервисов для проверки. Введите API ключи."

        messagebox.showinfo("Результаты проверки", message)

    def log_message(self, message):
        """Добавление сообщения в лог"""
        self.log_text.insert('end', f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see('end')
        self.root.update_idletasks()

    def clear_log(self):
        """Очистка лога"""
        self.log_text.delete(1.0, 'end')

    def save_configuration(self):
        """Сохранение конфигурации"""
        self.config["api_keys"]["openai"] = self.openai_key_var.get()
        self.config["api_keys"]["anthropic"] = self.anthropic_key_var.get()
        self.config["api_keys"]["deepseek"] = self.deepseek_key_var.get()
        self.config["api_keys"]["groq"] = self.groq_key_var.get()
        self.config["api_keys"]["openrouter"] = self.openrouter_key_var.get()
        self.config["api_keys"]["huggingface"] = self.huggingface_key_var.get()

        self.config["telegram"]["bot_token"] = self.telegram_token_var.get()
        self.config["telegram"]["chat_id"] = self.telegram_chat_id_var.get()

        if self.save_config():
            self.log_message("Конфигурация сохранена")
            messagebox.showinfo("Успех", "Конфигурация успешно сохранена!")
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить конфигурацию")

    def read_question_file(self, filepath):
        """Чтение вопроса из файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            self.log_message(f"Ошибка чтения файла: {str(e)}")
            return None

    def check_internet_connection(self):
        """Проверка интернет-соединения"""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False

    def query_openai(self, question, api_key):
        """Запрос к OpenAI GPT"""
        try:
            if not self.check_internet_connection():
                return "Ошибка: Нет интернет-соединения"

            if not api_key:
                return "Ошибка: Введите API ключ OpenAI"

            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Вы - полезный ассистент. Отвечай на русском языке."},
                    {"role": "user", "content": question}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except openai.error.AuthenticationError:
            return "Ошибка: Неверный API ключ OpenAI"
        except openai.error.RateLimitError:
            return "Ошибка: Превышен лимит запросов OpenAI"
        except openai.error.APIError as e:
            return f"Ошибка API OpenAI: {str(e)}"
        except Exception as e:
            return f"Ошибка OpenAI: {str(e)}"

    def query_anthropic(self, question, api_key):
        """Запрос к Anthropic Claude"""
        try:
            if not self.check_internet_connection():
                return "Ошибка: Нет интернет-соединения"

            if not api_key:
                return "Ошибка: Введите API ключ Anthropic"

            client = Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[{"role": "user", "content": question}]
            )
            return response.content[0].text
        except Exception as e:
            if "401" in str(e):
                return "Ошибка: Неверный API ключ Anthropic"
            elif "429" in str(e):
                return "Ошибка: Превышен лимит запросов Anthropic"
            else:
                return f"Ошибка Anthropic: {str(e)}"

    def query_deepseek(self, question, api_key):
        """Запрос к DeepSeek"""
        try:
            if not self.check_internet_connection():
                return "Ошибка: Нет интернет-соединения"

            if not api_key:
                return "Ошибка: Введите API ключ DeepSeek"

            client = DeepSeekClient(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )

            # Пробуем получить баланс перед отправкой
            try:
                models = client.models.list()
            except Exception as balance_error:
                if "402" in str(balance_error) or "Insufficient" in str(balance_error):
                    return "Ошибка: Недостаточно средств на балансе DeepSeek. Пополните счёт на platform.deepseek.com"
                # Если другая ошибка, продолжаем

            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "Вы - полезный ассистент. Отвечай на русском языке."},
                    {"role": "user", "content": question}
                ],
                max_tokens=1000,
                temperature=0.7,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            if "402" in str(e):
                return "Ошибка: Недостаточно средств на DeepSeek. Пополните баланс на platform.deepseek.com"
            elif "401" in str(e):
                return "Ошибка: Неверный API ключ DeepSeek"
            elif "429" in str(e):
                return "Ошибка: Превышен лимит запросов DeepSeek"
            else:
                return f"Ошибка DeepSeek: {str(e)}"

    def query_groq(self, question, api_key):
        """Запрос к Groq API"""
        try:
            if not self.check_internet_connection():
                return "Ошибка: Нет интернет-соединения"

            if not api_key:
                return "Ошибка: Введите API ключ Groq"

            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            # Список моделей для перебора (от самой новой к старой)
            models_to_try = [
                "llama-3.1-8b-instant",
                "llama-3.1-70b-versatile",
                "llama3-8b-8192",
                "llama3-70b-8192",
                "mixtral-8x7b-32768",
                "gemma-7b-it"
            ]

            last_error = ""
            for model in models_to_try:
                data = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "Ты - полезный ассистент. Отвечай на русском языке."},
                        {"role": "user", "content": question}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                }

                try:
                    response = requests.post(url, headers=headers, json=data, timeout=30)

                    if response.status_code == 200:
                        return response.json()["choices"][0]["message"]["content"]
                    elif response.status_code == 400:
                        # Пробуем следующую модель
                        last_error = f"Модель {model} недоступна"
                        continue
                    elif response.status_code == 401:
                        return "Ошибка: Неверный API ключ Groq"
                    elif response.status_code == 429:
                        return "Ошибка: Превышен лимит запросов Groq"
                except:
                    continue

            return f"Ошибка Groq: Не удалось найти рабочую модель. {last_error}"

        except Exception as e:
            return f"Ошибка Groq: {str(e)}"

    def query_openrouter(self, question, api_key):
        """Запрос к OpenRouter API"""
        try:
            if not self.check_internet_connection():
                return "Ошибка: Нет интернет-соединения"

            if not api_key:
                return "Ошибка: Введите API ключ OpenRouter"

            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/465644svar-alt/PreConcil",
                "X-Title": "PreConcil AI Manager"
            }

            # Список бесплатных моделей для перебора
            free_models_to_try = [
                "mistralai/mistral-7b-instruct:free",
                "google/gemma-7b-it:free",
                "huggingfaceh4/zephyr-7b-beta:free",
                "microsoft/phi-3-mini-128k-instruct:free",
                "nousresearch/hermes-2-pro-mistral-7b:free"
            ]

            last_error = ""
            for model in free_models_to_try:
                data = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "Ты - полезный ассистент. Отвечай на русском языке."},
                        {"role": "user", "content": question}
                    ],
                    "max_tokens": 1000,
                    "temperature": 0.7
                }

                try:
                    response = requests.post(url, headers=headers, json=data, timeout=30)

                    if response.status_code == 200:
                        return response.json()["choices"][0]["message"]["content"]
                    elif response.status_code == 404:
                        # Пробуем следующую модель
                        last_error = f"Модель {model} не найдена"
                        continue
                    elif response.status_code == 401:
                        return "Ошибка: Неверный API ключ OpenRouter"
                    elif response.status_code == 429:
                        return "Ошибка: Превышен лимит запросов OpenRouter"
                except:
                    continue

            return f"Ошибка OpenRouter: Не удалось найти рабочую модель. {last_error}"

        except Exception as e:
            return f"Ошибка OpenRouter: {str(e)}"

    def query_huggingface(self, question, api_key):
        """Запрос к Hugging Face API (работает без ключа!)"""
        try:
            if not self.check_internet_connection():
                return "Ошибка: Нет интернет-соединения"

            # Модели для перебора (от быстрых к мощным)
            models_to_try = [
                "microsoft/DialoGPT-medium",  # Быстрая, для диалога
                "gpt2",  # Базовая модель
                "distilgpt2",  # Упрощенная GPT-2
                "facebook/opt-350m",  # OPT от Facebook
                "EleutherAI/gpt-neo-125M"  # Небольшая GPT-Neo
            ]

            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            last_error = ""

            for model in models_to_try:
                url = f"https://api-inference.huggingface.co/models/{model}"

                data = {
                    "inputs": question,
                    "parameters": {
                        "max_new_tokens": 500,
                        "temperature": 0.7,
                        "return_full_text": False
                    }
                }

                try:
                    response = requests.post(url, headers=headers, json=data, timeout=60)

                    if response.status_code == 200:
                        result = response.json()
                        if isinstance(result, list) and len(result) > 0:
                            if "generated_text" in result[0]:
                                return result[0]["generated_text"]
                            else:
                                # Пробуем извлечь текст разными способами
                                text = str(result[0]).replace("{", "").replace("}", "").replace("'", "")
                                return text if len(text) > 10 else f"Ответ от {model}: {text}"
                        return f"Ответ от {model}: {str(result)}"
                    elif response.status_code == 503:
                        # Модель загружается, пробуем следующую
                        last_error = f"Модель {model} загружается"
                        continue
                    elif response.status_code == 429:
                        # Лимит запросов, ждем и пробуем следующую
                        last_error = f"Лимит запросов для {model}"
                        continue
                except Exception as model_error:
                    last_error = str(model_error)
                    continue

            # Если все модели не сработали, используем простой fallback
            return f"Бесплатный ответ от AI: Вопрос '{question[:50]}...' получен. Для более точных ответов используйте Groq или OpenRouter с API ключами."

        except Exception as e:
            return f"Ошибка Hugging Face: {str(e)}"

    def save_responses(self, responses, save_dir, original_file):
        """Сохранение ответов в файл с уникальным именем"""
        try:
            base_name = os.path.splitext(os.path.basename(original_file))[0]
            filename = self.generate_unique_filename(save_dir, base_name)
            filepath = os.path.join(save_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write(f"Вопрос отправлен: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Исходный файл: {original_file}\n")
                f.write("=" * 60 + "\n\n")

                for network, response in responses.items():
                    f.write(f"--- {network} ---\n")
                    f.write(response + "\n")
                    f.write("=" * 60 + "\n\n")

            self.log_message(f"✅ Ответы сохранены в: {filepath}")
            return filepath
        except Exception as e:
            self.log_message(f"❌ Ошибка сохранения: {str(e)}")
            return None

    def send_to_telegram(self, filepath, bot_token, chat_id):
        """Отправка файла в Telegram"""
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendDocument"

            with open(filepath, 'rb') as file:
                files = {'document': file}
                data = {'chat_id': chat_id}
                response = requests.post(url, files=files, data=data)

            if response.status_code == 200:
                self.log_message("✅ Файл успешно отправлен в Telegram")
                return True
            else:
                self.log_message(f"❌ Ошибка отправки в Telegram: {response.status_code}")
                return False
        except Exception as e:
            self.log_message(f"❌ Ошибка отправки в Telegram: {str(e)}")
            return False

    def send_requests(self):
        """Основная функция отправки запросов"""
        # Проверка входных данных
        question_file = self.file_path_var.get()
        save_dir = self.save_path_var.get()

        if not question_file or not os.path.exists(question_file):
            messagebox.showerror("Ошибка", "Выберите файл с вопросом")
            return

        if not save_dir or not os.path.exists(save_dir):
            messagebox.showerror("Ошибка", "Выберите папку для сохранения")
            return

        # Чтение вопроса
        question = self.read_question_file(question_file)
        if not question:
            messagebox.showerror("Ошибка", "Не удалось прочитать вопрос из файла")
            return

        # Проверка выбранных нейросетей
        selected_networks = [name for name, var in self.networks_vars.items() if var.get()]
        if not selected_networks:
            messagebox.showerror("Ошибка", "Выберите хотя бы одну нейросеть")
            return

        # Получение API ключей
        api_keys = {
            "OpenAI GPT": self.openai_key_var.get(),
            "Anthropic Claude": self.anthropic_key_var.get(),
            "DeepSeek*": self.deepseek_key_var.get(),
            "Groq*": self.groq_key_var.get(),
            "OpenRouter*": self.openrouter_key_var.get(),
            "Hugging Face*": self.huggingface_key_var.get()
        }

        # Проверка ключей для выбранных сетей (кроме Hugging Face)
        missing_keys = []
        for network in selected_networks:
            if network != "Hugging Face*" and not api_keys[network]:
                missing_keys.append(network.replace("*", ""))

        if missing_keys:
            messagebox.showerror("Ошибка",
                                 f"Введите API ключи для: {', '.join(missing_keys)}\n\nHugging Face может работать без ключа.")
            return

        # Проверяем соединение перед отправкой (предупреждение, не блокировка)
        failed_connections = []
        for network in selected_networks:
            if not self.connection_status.get(network, False):
                failed_connections.append(network.replace("*", ""))

        if failed_connections:
            reply = messagebox.askyesno(
                "Проверка соединения",
                f"⚠️ Не удалось подключиться к следующим нейросетям:\n"
                f"{', '.join(failed_connections)}\n\n"
                f"Hugging Face всегда работает (с лимитами).\n"
                f"Продолжить отправку запросов?"
            )
            if not reply:
                return

        # Запуск в отдельном потоке
        thread = threading.Thread(
            target=self._send_requests_thread,
            args=(question, selected_networks, api_keys, save_dir, question_file)
        )
        thread.daemon = True
        thread.start()

    def _send_requests_thread(self, question, selected_networks, api_keys, save_dir, original_file):
        """Поток для отправки запросов"""
        self.progress.start()
        self.log_message("Начинаем отправку запросов...")

        responses = {}
        failed_networks = []

        # Отправка запросов к выбранным нейросетям
        for network in selected_networks:
            self.log_message(f"Отправляем запрос в {network}...")

            try:
                if network == "OpenAI GPT":
                    response = self.query_openai(question, api_keys[network])
                elif network == "Anthropic Claude":
                    response = self.query_anthropic(question, api_keys[network])
                elif network == "DeepSeek*":
                    response = self.query_deepseek(question, api_keys[network])
                elif network == "Groq*":
                    response = self.query_groq(question, api_keys[network])
                elif network == "OpenRouter*":
                    response = self.query_openrouter(question, api_keys[network])
                elif network == "Hugging Face*":
                    response = self.query_huggingface(question, api_keys[network])
                else:
                    response = "Неподдерживаемая нейросеть"

                # Проверяем, не вернулась ли ошибка
                if response and (response.startswith("Ошибка") or "Error" in response):
                    self.log_message(f"❌ {response}")
                    failed_networks.append(network.replace("*", ""))
                else:
                    responses[network.replace("*", "")] = response
                    self.log_message(f"✅ Получен ответ от {network}")

            except Exception as e:
                error_msg = f"Ошибка при запросе к {network}: {str(e)}"
                self.log_message(f"❌ {error_msg}")
                failed_networks.append(network.replace("*", ""))

        # Показываем уведомление о неудачных запросах
        if failed_networks:
            self.root.after(0, lambda: self.show_network_errors(failed_networks))

        # Сохранение результатов
        if responses:
            self.log_message("Сохраняем результаты...")
            saved_file = self.save_responses(responses, save_dir, original_file)

            # Отправка в Telegram (если настроено)
            bot_token = self.telegram_token_var.get()
            chat_id = self.telegram_chat_id_var.get()

            if bot_token and chat_id and saved_file:
                self.log_message("Отправляем файл в Telegram...")
                success = self.send_to_telegram(saved_file, bot_token, chat_id)
                if not success:
                    self.log_message("⚠️ Не удалось отправить файл в Telegram")
        else:
            self.log_message("❌ Не получено ни одного ответа от нейросетей")

        self.progress.stop()
        self.log_message("Готово!")

        # Обновляем список истории
        self.load_history()

        # Показываем итоговое сообщение
        if responses:
            self.root.after(0, lambda: messagebox.showinfo(
                "Успех",
                f"Запросы успешно отправлены!\n\n"
                f"Успешно: {len(responses)} из {len(selected_networks)}\n"
                f"Ошибки: {len(failed_networks)}"
            ))

    def show_network_errors(self, failed_networks):
        """Показать ошибки подключения к нейросетям"""
        if failed_networks:
            messagebox.showwarning(
                "Ошибки подключения",
                f"Не удалось получить ответ от следующих нейросетей:\n"
                f"{', '.join(failed_networks)}\n\n"
                f"Рекомендации:\n"
                f"1. Hugging Face всегда работает (бесплатно)\n"
                f"2. Получите бесплатные ключи: Groq.com, OpenRouter.ai\n"
                f"3. Проверьте интернет-соединение"
            )

    def load_history(self):
        """Загрузка истории файлов"""
        save_dir = self.save_path_var.get()
        if not save_dir or not os.path.exists(save_dir):
            return

        self.history_listbox.delete(0, 'end')

        try:
            files = [f for f in os.listdir(save_dir) if f.startswith('responses_') or f.endswith('_answer.txt')]
            files.sort(reverse=True)  # Сначала новые

            for file in files:
                self.history_listbox.insert('end', file)
        except Exception as e:
            self.log_message(f"Ошибка загрузки истории: {str(e)}")

    def on_history_select(self, event):
        """Обработка выбора файла из истории"""
        selection = self.history_listbox.curselection()
        if not selection:
            return

        filename = self.history_listbox.get(selection[0])
        save_dir = self.save_path_var.get()
        filepath = os.path.join(save_dir, filename)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            self.history_text.delete(1.0, 'end')
            self.history_text.insert(1.0, content)
        except Exception as e:
            self.history_text.delete(1.0, 'end')
            self.history_text.insert(1.0, f"Ошибка чтения файла: {str(e)}")

    def send_selected_to_telegram(self):
        """Отправка выбранного файла в Telegram"""
        selection = self.history_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите файл из истории")
            return

        bot_token = self.telegram_token_var.get()
        chat_id = self.telegram_chat_id_var.get()

        if not bot_token or not chat_id:
            messagebox.showerror("Ошибка", "Настройте Telegram API в настройках")
            return

        filename = self.history_listbox.get(selection[0])
        save_dir = self.save_path_var.get()
        filepath = os.path.join(save_dir, filename)

        if self.send_to_telegram(filepath, bot_token, chat_id):
            messagebox.showinfo("Успех", "Файл отправлен в Telegram")
        else:
            messagebox.showerror("Ошибка", "Не удалось отправить файл")


def main():
    root = tk.Tk()

    # Устанавливаем тему
    try:
        root.tk.call('source', 'azure.tcl')
        root.tk.call('set_theme', 'dark')
    except:
        pass

    # Настраиваем стиль
    style = ttk.Style(root)
    style.configure("Accent.TButton", font=('Segoe UI', 10, 'bold'))

    app = NeuralNetworkApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()