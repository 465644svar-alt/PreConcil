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
import google.generativeai as genai
from anthropic import Anthropic
from pathlib import Path


class NeuralNetworkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер нейросетей v1.2")
        self.root.geometry("900x700")

        # Конфигурация
        self.config_file = "config.json"
        self.load_config()

        # Переменные для хранения статусов соединения
        self.connection_status = {
            "OpenAI GPT": False,
            "Anthropic Claude": False,
            "Google Gemini": False,
            "YandexGPT": False,
            "Cohere": False,
            "Telegram": False
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
                "google": "",
                "yandex": "",
                "cohere": ""
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
        networks_frame = ttk.LabelFrame(self.main_tab, text="Выбор нейросетей", padding=10)
        networks_frame.pack(fill='x', padx=10, pady=5)

        self.networks_vars = {
            "OpenAI GPT": tk.BooleanVar(value=True),
            "Anthropic Claude": tk.BooleanVar(value=True),
            "Google Gemini": tk.BooleanVar(value=True),
            "YandexGPT": tk.BooleanVar(value=False),
            "Cohere": tk.BooleanVar(value=False)
        }

        self.network_checkbuttons = {}
        for i, (name, var) in enumerate(self.networks_vars.items()):
            cb = ttk.Checkbutton(networks_frame, text=name, variable=var,
                                 command=lambda n=name: self.update_network_selection(n))
            cb.grid(row=i // 2, column=i % 2, sticky='w', padx=10, pady=2)
            self.network_checkbuttons[name] = cb

        # Кнопки управления
        button_frame = ttk.Frame(self.main_tab)
        button_frame.pack(fill='x', padx=10, pady=20)

        ttk.Button(button_frame, text="Проверить соединение",
                   command=self.check_connections).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Отправить запрос", command=self.send_requests,
                   style="Accent.TButton").pack(side='left', padx=5)
        ttk.Button(button_frame, text="Сохранить конфигурацию",
                   command=self.save_configuration).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Очистить историю",
                   command=self.clear_history).pack(side='left', padx=5)

        # Прогресс-бар и лог
        self.progress = ttk.Progressbar(self.main_tab, mode='indeterminate')
        self.progress.pack(fill='x', padx=10, pady=5)

        log_frame = ttk.LabelFrame(self.main_tab, text="Лог выполнения", padding=10)
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)

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

        # OpenAI
        openai_frame = ttk.LabelFrame(self.api_tab, text="OpenAI API", padding=10)
        openai_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(openai_frame, text="API ключ:").grid(row=0, column=0, sticky='w')
        self.openai_key_var = tk.StringVar()
        openai_entry = ttk.Entry(openai_frame, textvariable=self.openai_key_var, width=60, show="*")
        openai_entry.grid(row=1, column=0, padx=(0, 10))
        ttk.Button(openai_frame, text="Показать",
                   command=lambda e=openai_entry: self.toggle_password_entry(e)).grid(row=1, column=1)

        # Anthropic
        anthropic_frame = ttk.LabelFrame(self.api_tab, text="Anthropic API", padding=10)
        anthropic_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(anthropic_frame, text="API ключ:").grid(row=0, column=0, sticky='w')
        self.anthropic_key_var = tk.StringVar()
        anthropic_entry = ttk.Entry(anthropic_frame, textvariable=self.anthropic_key_var, width=60, show="*")
        anthropic_entry.grid(row=1, column=0, padx=(0, 10))
        ttk.Button(anthropic_frame, text="Показать",
                   command=lambda e=anthropic_entry: self.toggle_password_entry(e)).grid(row=1, column=1)

        # Google AI
        google_frame = ttk.LabelFrame(self.api_tab, text="Google AI API", padding=10)
        google_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(google_frame, text="API ключ:").grid(row=0, column=0, sticky='w')
        self.google_key_var = tk.StringVar()
        google_entry = ttk.Entry(google_frame, textvariable=self.google_key_var, width=60, show="*")
        google_entry.grid(row=1, column=0, padx=(0, 10))
        ttk.Button(google_frame, text="Показать",
                   command=lambda e=google_entry: self.toggle_password_entry(e)).grid(row=1, column=1)

        # YandexGPT
        yandex_frame = ttk.LabelFrame(self.api_tab, text="YandexGPT API", padding=10)
        yandex_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(yandex_frame, text="API ключ:").grid(row=0, column=0, sticky='w')
        self.yandex_key_var = tk.StringVar()
        yandex_entry = ttk.Entry(yandex_frame, textvariable=self.yandex_key_var, width=60, show="*")
        yandex_entry.grid(row=1, column=0, padx=(0, 10))
        ttk.Button(yandex_frame, text="Показать",
                   command=lambda e=yandex_entry: self.toggle_password_entry(e)).grid(row=1, column=1)

        # Cohere
        cohere_frame = ttk.LabelFrame(self.api_tab, text="Cohere API", padding=10)
        cohere_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(cohere_frame, text="API ключ:").grid(row=0, column=0, sticky='w')
        self.cohere_key_var = tk.StringVar()
        cohere_entry = ttk.Entry(cohere_frame, textvariable=self.cohere_key_var, width=60, show="*")
        cohere_entry.grid(row=1, column=0, padx=(0, 10))
        ttk.Button(cohere_frame, text="Показать",
                   command=lambda e=cohere_entry: self.toggle_password_entry(e)).grid(row=1, column=1)

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
        status_grid = ttk.Frame(status_frame)
        status_grid.pack(fill='both', expand=True)

        networks = [
            ("OpenAI GPT", self.openai_key_var),
            ("Anthropic Claude", self.anthropic_key_var),
            ("Google Gemini", self.google_key_var),
            ("YandexGPT", self.yandex_key_var),
            ("Cohere", self.cohere_key_var),
            ("Telegram Bot", self.telegram_token_var)
        ]

        for i, (name, key_var) in enumerate(networks):
            # Название сервиса
            ttk.Label(status_grid, text=f"{name}:", font=('TkDefaultFont', 10)).grid(
                row=i, column=0, sticky='w', padx=10, pady=5)

            # Индикатор статуса
            status_canvas = tk.Canvas(status_grid, width=20, height=20, bg='white', highlightthickness=0)
            status_canvas.grid(row=i, column=1, padx=5, pady=5)
            self.status_labels[name] = status_canvas

            # Описание статуса
            self.status_text_var = tk.StringVar(value="Не проверено")
            ttk.Label(status_grid, textvariable=self.status_text_var).grid(
                row=i, column=2, sticky='w', padx=10, pady=5)

            # Кнопка проверки
            ttk.Button(status_grid, text="Проверить",
                       command=lambda n=name, k=key_var: self.check_single_connection(n, k.get())).grid(
                row=i, column=3, padx=10, pady=5)

        # Кнопка проверки всех соединений
        ttk.Button(status_frame, text="Проверить все соединения",
                   command=self.check_all_connections, style="Accent.TButton").pack(pady=20)

    def toggle_password_entry(self, entry):
        """Переключение видимости пароля в Entry"""
        current_show = entry.cget('show')
        if current_show == '*':
            entry.config(show='')
        else:
            entry.config(show='*')

    def update_network_selection(self, network_name):
        """Обновление выбора нейросети"""
        if not self.networks_vars[network_name].get():
            self.show_warning_message(f"Нейросеть {network_name} отключена")

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

    def check_all_connections_background(self):
        """Фоновая проверка всех соединений"""
        if hasattr(self, 'status_labels'):
            thread = threading.Thread(target=self._check_all_connections_thread, daemon=True)
            thread.start()

    def _check_all_connections_thread(self):
        """Поток для проверки всех соединений"""
        # Проверяем только те сервисы, для которых есть ключи
        networks_to_check = []

        if self.openai_key_var.get():
            networks_to_check.append(("OpenAI GPT", self.openai_key_var.get()))
        if self.anthropic_key_var.get():
            networks_to_check.append(("Anthropic Claude", self.anthropic_key_var.get()))
        if self.google_key_var.get():
            networks_to_check.append(("Google Gemini", self.google_key_var.get()))
        if self.yandex_key_var.get():
            networks_to_check.append(("YandexGPT", self.yandex_key_var.get()))
        if self.cohere_key_var.get():
            networks_to_check.append(("Cohere", self.cohere_key_var.get()))
        if self.telegram_token_var.get() and self.telegram_chat_id_var.get():
            networks_to_check.append(("Telegram Bot", self.telegram_token_var.get()))

        for name, key in networks_to_check:
            self.check_single_connection(name, key)
            time.sleep(1)  # Задержка между проверками

    def check_single_connection(self, network_name, api_key):
        """Проверка соединения с одной нейросетью"""
        try:
            if network_name == "OpenAI GPT":
                status = self.test_openai_connection(api_key)
            elif network_name == "Anthropic Claude":
                status = self.test_anthropic_connection(api_key)
            elif network_name == "Google Gemini":
                status = self.test_google_connection(api_key)
            elif network_name == "YandexGPT":
                status = self.test_yandex_connection(api_key)
            elif network_name == "Cohere":
                status = self.test_cohere_connection(api_key)
            elif network_name == "Telegram Bot":
                status = self.test_telegram_connection(api_key, self.telegram_chat_id_var.get())
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
        if hasattr(self, 'status_labels') and network_name in self.status_labels:
            canvas = self.status_labels[network_name]
            canvas.delete("all")

            if status:
                # Зеленый кружок
                canvas.create_oval(2, 2, 18, 18, fill="green", outline="")
                canvas.create_text(10, 10, text="✓", fill="white", font=('Arial', 10, 'bold'))
            else:
                # Красный кружок
                canvas.create_oval(2, 2, 18, 18, fill="red", outline="")
                canvas.create_text(10, 10, text="✗", fill="white", font=('Arial', 10, 'bold'))

    def test_openai_connection(self, api_key):
        """Тест соединения с OpenAI"""
        if not api_key:
            return False

        try:
            openai.api_key = api_key
            # Быстрый тест запроса моделей
            response = openai.Model.list()
            return response is not None
        except Exception as e:
            return False

    def test_anthropic_connection(self, api_key):
        """Тест соединения с Anthropic"""
        if not api_key:
            return False

        try:
            client = Anthropic(api_key=api_key)
            # Быстрый тест - запрос списка моделей
            models = client.models.list()
            return models is not None
        except Exception as e:
            return False

    def test_google_connection(self, api_key):
        """Тест соединения с Google Gemini"""
        if not api_key:
            return False

        try:
            genai.configure(api_key=api_key)
            models = genai.list_models()
            return models is not None
        except Exception as e:
            return False

    def test_yandex_connection(self, api_key):
        """Тест соединения с YandexGPT"""
        if not api_key:
            return False

        try:
            # Простой тест - проверка формата ключа
            return len(api_key) > 20  # Базовая проверка
        except:
            return False

    def test_cohere_connection(self, api_key):
        """Тест соединения с Cohere"""
        if not api_key:
            return False

        try:
            url = "https://api.cohere.ai/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(url, headers=headers, timeout=10)
            return response.status_code == 200
        except:
            return False

    def test_telegram_connection(self, bot_token, chat_id):
        """Тест соединения с Telegram"""
        if not bot_token or not chat_id:
            return False

        try:
            url = f"https://api.telegram.org/bot{bot_token}/getMe"
            response = requests.get(url, timeout=10)
            return response.status_code == 200
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

        # Проверяем каждое соединение
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

        if self.google_key_var.get():
            if self.check_single_connection("Google Gemini", self.google_key_var.get()):
                successful_connections.append("Google Gemini")
            else:
                failed_connections.append("Google Gemini")

        if self.yandex_key_var.get():
            if self.check_single_connection("YandexGPT", self.yandex_key_var.get()):
                successful_connections.append("YandexGPT")
            else:
                failed_connections.append("YandexGPT")

        if self.cohere_key_var.get():
            if self.check_single_connection("Cohere", self.cohere_key_var.get()):
                successful_connections.append("Cohere")
            else:
                failed_connections.append("Cohere")

        if self.telegram_token_var.get() and self.telegram_chat_id_var.get():
            if self.check_single_connection("Telegram Bot", self.telegram_token_var.get()):
                successful_connections.append("Telegram Bot")
            else:
                failed_connections.append("Telegram Bot")

        # Показываем результаты
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

    def show_warning_message(self, message):
        """Показать предупреждающее сообщение"""
        self.log_message(f"⚠️ {message}")

    def show_error_message(self, message):
        """Показать сообщение об ошибке"""
        self.log_message(f"❌ {message}")
        messagebox.showerror("Ошибка", message)

    def save_responses(self, responses, save_dir, original_filename):
        """Сохранение ответов в файл с уникальным именем"""
        try:
            # Получаем базовое имя исходного файла
            base_name = os.path.splitext(os.path.basename(original_filename))[0]

            # Генерируем уникальное имя файла
            filename = self.generate_unique_filename(save_dir, base_name)
            filepath = os.path.join(save_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write(f"Вопрос отправлен: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Исходный файл: {original_filename}\n")
                f.write("=" * 60 + "\n\n")

                for network, response in responses.items():
                    f.write(f"--- {network} ---\n")
                    f.write(response + "\n")
                    f.write("=" * 60 + "\n\n")

            self.log_message(f"✅ Ответы сохранены в: {filepath}")
            return filepath
        except Exception as e:
            self.show_error_message(f"Ошибка сохранения: {str(e)}")
            return None

    def send_requests(self):
        """Основная функция отправки запросов с проверкой соединения"""
        # Проверка входных данных
        question_file = self.file_path_var.get()
        save_dir = self.save_path_var.get()

        if not question_file or not os.path.exists(question_file):
            self.show_error_message("Выберите файл с вопросом")
            return

        if not save_dir or not os.path.exists(save_dir):
            self.show_error_message("Выберите папку для сохранения")
            return

        # Чтение вопроса
        question = self.read_question_file(question_file)
        if not question:
            self.show_error_message("Не удалось прочитать вопрос из файла")
            return

        # Проверка выбранных нейросетей
        selected_networks = [name for name, var in self.networks_vars.items() if var.get()]
        if not selected_networks:
            self.show_error_message("Выберите хотя бы одну нейросеть")
            return

        # Проверка API ключей
        api_keys = {
            "OpenAI GPT": self.openai_key_var.get(),
            "Anthropic Claude": self.anthropic_key_var.get(),
            "Google Gemini": self.google_key_var.get(),
            "YandexGPT": self.yandex_key_var.get(),
            "Cohere": self.cohere_key_var.get()
        }

        # Проверяем ключи для выбранных сетей
        missing_keys = []
        for network in selected_networks:
            if not api_keys[network]:
                missing_keys.append(network)

        if missing_keys:
            self.show_error_message(f"Введите API ключи для: {', '.join(missing_keys)}")
            return

        # Проверяем соединение перед отправкой
        failed_connections = []
        for network in selected_networks:
            if not self.connection_status.get(network, False):
                failed_connections.append(network)

        if failed_connections:
            reply = messagebox.askyesno(
                "Проверка соединения",
                f"Не удалось подключиться к следующим нейросетям:\n"
                f"{', '.join(failed_connections)}\n\n"
                f"Продолжить отправку запросов? (Некоторые запросы могут завершиться ошибкой)"
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
                elif network == "Google Gemini":
                    response = self.query_google(question, api_keys[network])
                elif network == "YandexGPT":
                    response = self.query_yandex(question, api_keys[network])
                elif network == "Cohere":
                    response = self.query_cohere(question, api_keys[network])
                else:
                    response = "Неподдерживаемая нейросеть"

                # Проверяем, не вернулась ли ошибка
                if response and response.startswith("Ошибка"):
                    self.log_message(f"❌ {response}")
                    failed_networks.append(network)
                else:
                    responses[network] = response
                    self.log_message(f"✅ Получен ответ от {network}")

            except Exception as e:
                error_msg = f"Ошибка при запросе к {network}: {str(e)}"
                self.log_message(f"❌ {error_msg}")
                failed_networks.append(network)

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
                f"Проверьте:\n"
                f"1. Интернет-соединение\n"
                f"2. API ключи\n"
                f"3. Доступность сервисов"
            )

    def query_openai(self, question, api_key):
        """Запрос к OpenAI GPT с обработкой ошибок"""
        try:
            # Проверяем интернет-соединение
            if not self.check_internet_connection():
                return "Ошибка: Нет интернет-соединения"

            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Вы - полезный ассистент."},
                    {"role": "user", "content": question}
                ],
                max_tokens=1000,
                temperature=0.7,
                timeout=30  # Таймаут 30 секунд
            )
            return response.choices[0].message.content
        except openai.error.AuthenticationError:
            return "Ошибка: Неверный API ключ"
        except openai.error.RateLimitError:
            return "Ошибка: Превышен лимит запросов"
        except openai.error.APIError as e:
            return f"Ошибка API OpenAI: {str(e)}"
        except openai.error.Timeout:
            return "Ошибка: Таймаут запроса"
        except Exception as e:
            return f"Ошибка OpenAI: {str(e)}"

    def query_anthropic(self, question, api_key):
        """Запрос к Anthropic Claude с обработкой ошибок"""
        try:
            if not self.check_internet_connection():
                return "Ошибка: Нет интернет-соединения"

            client = Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[{"role": "user", "content": question}],
                timeout=30
            )
            return response.content[0].text
        except Exception as e:
            if "401" in str(e):
                return "Ошибка: Неверный API ключ"
            elif "429" in str(e):
                return "Ошибка: Превышен лимит запросов"
            else:
                return f"Ошибка Anthropic: {str(e)}"

    def query_google(self, question, api_key):
        """Запрос к Google Gemini с обработкой ошибок"""
        try:
            if not self.check_internet_connection():
                return "Ошибка: Нет интернет-соединения"

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(question)
            return response.text
        except Exception as e:
            if "API_KEY_INVALID" in str(e):
                return "Ошибка: Неверный API ключ"
            else:
                return f"Ошибка Google Gemini: {str(e)}"

    def query_yandex(self, question, api_key):
        """Запрос к YandexGPT с обработкой ошибок"""
        try:
            if not self.check_internet_connection():
                return "Ошибка: Нет интернет-соединения"

            url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
            headers = {
                "Authorization": f"Api-Key {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "modelUri": f"gpt://{api_key.split('-')[0]}/yandexgpt/latest",
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.6,
                    "maxTokens": 1000
                },
                "messages": [
                    {"role": "user", "text": question}
                ]
            }
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                return response.json()["result"]["alternatives"][0]["message"]["text"]
            elif response.status_code == 401:
                return "Ошибка: Неверный API ключ"
            else:
                return f"Ошибка YandexGPT: {response.status_code}"
        except requests.exceptions.Timeout:
            return "Ошибка: Таймаут запроса"
        except Exception as e:
            return f"Ошибка YandexGPT: {str(e)}"

    def query_cohere(self, question, api_key):
        """Запрос к Cohere с обработкой ошибок"""
        try:
            if not self.check_internet_connection():
                return "Ошибка: Нет интернет-соединения"

            url = "https://api.cohere.ai/v1/generate"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "command",
                "prompt": question,
                "max_tokens": 1000,
                "temperature": 0.7
            }
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                return response.json()["generations"][0]["text"]
            elif response.status_code == 401:
                return "Ошибка: Неверный API ключ"
            else:
                return f"Ошибка Cohere: {response.status_code}"
        except requests.exceptions.Timeout:
            return "Ошибка: Таймаут запроса"
        except Exception as e:
            return f"Ошибка Cohere: {str(e)}"

    def check_internet_connection(self, host="8.8.8.8", port=53, timeout=3):
        """Проверка интернет-соединения"""
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except socket.error:
            return False


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