import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
import json
import requests
from datetime import datetime
import openai
import google.generativeai as genai
from anthropic import Anthropic


class NeuralNetworkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер нейросетей v1.0")
        self.root.geometry("900x700")

        # Конфигурация
        self.config_file = "config.json"
        self.load_config()

        # Создаем вкладки
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Вкладка 1: Основные настройки
        self.setup_main_tab()

        # Вкладка 2: Настройки API
        self.setup_api_tab()

        # Вкладка 3: История запросов
        self.setup_history_tab()

        # Загружаем конфигурацию
        self.load_config_to_ui()

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
        ttk.Entry(file_frame, textvariable=self.file_path_var, width=60).grid(row=1, column=0, padx=(0, 10))
        ttk.Button(file_frame, text="Выбрать...", command=self.select_file).grid(row=1, column=1)

        # Фрейм для выбора директории сохранения
        save_frame = ttk.LabelFrame(self.main_tab, text="Директория для сохранения ответов", padding=10)
        save_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(save_frame, text="Папка для сохранения:").grid(row=0, column=0, sticky='w')

        self.save_path_var = tk.StringVar()
        ttk.Entry(save_frame, textvariable=self.save_path_var, width=60).grid(row=1, column=0, padx=(0, 10))
        ttk.Button(save_frame, text="Выбрать...", command=self.select_save_directory).grid(row=1, column=1)

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

        for i, (name, var) in enumerate(self.networks_vars.items()):
            ttk.Checkbutton(networks_frame, text=name, variable=var).grid(row=i // 2, column=i % 2, sticky='w', padx=10,
                                                                          pady=2)

        # Кнопки управления
        button_frame = ttk.Frame(self.main_tab)
        button_frame.pack(fill='x', padx=10, pady=20)

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

    def setup_api_tab(self):
        """Создание вкладки с настройками API"""
        self.api_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.api_tab, text="Настройки API")

        # OpenAI
        openai_frame = ttk.LabelFrame(self.api_tab, text="OpenAI API", padding=10)
        openai_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(openai_frame, text="API ключ:").grid(row=0, column=0, sticky='w')
        self.openai_key_var = tk.StringVar()
        ttk.Entry(openai_frame, textvariable=self.openai_key_var, width=60, show="*").grid(row=1, column=0,
                                                                                           padx=(0, 10))
        ttk.Button(openai_frame, text="Показать",
                   command=lambda: self.toggle_password(self.openai_key_var)).grid(row=1, column=1)

        # Anthropic
        anthropic_frame = ttk.LabelFrame(self.api_tab, text="Anthropic API", padding=10)
        anthropic_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(anthropic_frame, text="API ключ:").grid(row=0, column=0, sticky='w')
        self.anthropic_key_var = tk.StringVar()
        ttk.Entry(anthropic_frame, textvariable=self.anthropic_key_var, width=60, show="*").grid(row=1, column=0,
                                                                                                 padx=(0, 10))
        ttk.Button(anthropic_frame, text="Показать",
                   command=lambda: self.toggle_password(self.anthropic_key_var)).grid(row=1, column=1)

        # Google AI
        google_frame = ttk.LabelFrame(self.api_tab, text="Google AI API", padding=10)
        google_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(google_frame, text="API ключ:").grid(row=0, column=0, sticky='w')
        self.google_key_var = tk.StringVar()
        ttk.Entry(google_frame, textvariable=self.google_key_var, width=60, show="*").grid(row=1, column=0,
                                                                                           padx=(0, 10))
        ttk.Button(google_frame, text="Показать",
                   command=lambda: self.toggle_password(self.google_key_var)).grid(row=1, column=1)

        # YandexGPT
        yandex_frame = ttk.LabelFrame(self.api_tab, text="YandexGPT API", padding=10)
        yandex_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(yandex_frame, text="API ключ:").grid(row=0, column=0, sticky='w')
        self.yandex_key_var = tk.StringVar()
        ttk.Entry(yandex_frame, textvariable=self.yandex_key_var, width=60, show="*").grid(row=1, column=0,
                                                                                           padx=(0, 10))
        ttk.Button(yandex_frame, text="Показать",
                   command=lambda: self.toggle_password(self.yandex_key_var)).grid(row=1, column=1)

        # Cohere
        cohere_frame = ttk.LabelFrame(self.api_tab, text="Cohere API", padding=10)
        cohere_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(cohere_frame, text="API ключ:").grid(row=0, column=0, sticky='w')
        self.cohere_key_var = tk.StringVar()
        ttk.Entry(cohere_frame, textvariable=self.cohere_key_var, width=60, show="*").grid(row=1, column=0,
                                                                                           padx=(0, 10))
        ttk.Button(cohere_frame, text="Показать",
                   command=lambda: self.toggle_password(self.cohere_key_var)).grid(row=1, column=1)

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
        self.google_key_var.set(self.config["api_keys"]["google"])
        self.yandex_key_var.set(self.config["api_keys"]["yandex"])
        self.cohere_key_var.set(self.config["api_keys"]["cohere"])

        self.telegram_token_var.set(self.config["telegram"]["bot_token"])
        self.telegram_chat_id_var.set(self.config["telegram"]["chat_id"])

        if self.config["last_directory"]:
            self.save_path_var.set(self.config["last_directory"])

    def toggle_password(self, var):
        """Переключение видимости пароля"""
        widget = var._root.tk.call('info', 'widget', var._name)
        current_show = var._root.tk.call(widget, 'cget', '-show')
        if current_show == '*':
            var._root.tk.call(widget, 'configure', '-show', '')
        else:
            var._root.tk.call(widget, 'configure', '-show', '*')

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

    def log_message(self, message):
        """Добавление сообщения в лог"""
        self.log_text.insert('end', f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see('end')
        self.root.update_idletasks()

    def save_configuration(self):
        """Сохранение конфигурации"""
        self.config["api_keys"]["openai"] = self.openai_key_var.get()
        self.config["api_keys"]["anthropic"] = self.anthropic_key_var.get()
        self.config["api_keys"]["google"] = self.google_key_var.get()
        self.config["api_keys"]["yandex"] = self.yandex_key_var.get()
        self.config["api_keys"]["cohere"] = self.cohere_key_var.get()

        self.config["telegram"]["bot_token"] = self.telegram_token_var.get()
        self.config["telegram"]["chat_id"] = self.telegram_chat_id_var.get()

        if self.save_config():
            self.log_message("Конфигурация сохранена")
            messagebox.showinfo("Успех", "Конфигурация успешно сохранена!")
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить конфигурацию")

    def clear_history(self):
        """Очистка истории в логе"""
        self.log_text.delete(1.0, 'end')

    def read_question_file(self, filepath):
        """Чтение вопроса из файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            self.log_message(f"Ошибка чтения файла: {str(e)}")
            return None

    def query_openai(self, question, api_key):
        """Запрос к OpenAI GPT"""
        try:
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Вы - полезный ассистент."},
                    {"role": "user", "content": question}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Ошибка OpenAI: {str(e)}"

    def query_anthropic(self, question, api_key):
        """Запрос к Anthropic Claude"""
        try:
            client = Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[{"role": "user", "content": question}]
            )
            return response.content[0].text
        except Exception as e:
            return f"Ошибка Anthropic: {str(e)}"

    def query_google(self, question, api_key):
        """Запрос к Google Gemini"""
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(question)
            return response.text
        except Exception as e:
            return f"Ошибка Google Gemini: {str(e)}"

    def query_yandex(self, question, api_key):
        """Запрос к YandexGPT"""
        try:
            url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
            headers = {
                "Authorization": f"Api-Key {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "modelUri": f"gpt://{api_key}/yandexgpt/latest",
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.6,
                    "maxTokens": 1000
                },
                "messages": [
                    {"role": "user", "text": question}
                ]
            }
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json()["result"]["alternatives"][0]["message"]["text"]
            else:
                return f"Ошибка YandexGPT: {response.status_code}"
        except Exception as e:
            return f"Ошибка YandexGPT: {str(e)}"

    def query_cohere(self, question, api_key):
        """Запрос к Cohere"""
        try:
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
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json()["generations"][0]["text"]
            else:
                return f"Ошибка Cohere: {response.status_code}"
        except Exception as e:
            return f"Ошибка Cohere: {str(e)}"

    def save_responses(self, responses, save_dir):
        """Сохранение ответов в файл"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"responses_{timestamp}.txt"
            filepath = os.path.join(save_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write(f"Вопрос отправлен: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")

                for network, response in responses.items():
                    f.write(f"--- {network} ---\n")
                    f.write(response + "\n")
                    f.write("=" * 60 + "\n\n")

            self.log_message(f"Ответы сохранены в: {filepath}")
            return filepath
        except Exception as e:
            self.log_message(f"Ошибка сохранения: {str(e)}")
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
                self.log_message("Файл успешно отправлен в Telegram")
                return True
            else:
                self.log_message(f"Ошибка отправки в Telegram: {response.status_code}")
                return False
        except Exception as e:
            self.log_message(f"Ошибка отправки в Telegram: {str(e)}")
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
            "Google Gemini": self.google_key_var.get(),
            "YandexGPT": self.yandex_key_var.get(),
            "Cohere": self.cohere_key_var.get()
        }

        # Проверка ключей для выбранных сетей
        for network in selected_networks:
            if not api_keys[network]:
                messagebox.showerror("Ошибка", f"Введите API ключ для {network}")
                return

        # Запуск в отдельном потоке
        thread = threading.Thread(
            target=self._send_requests_thread,
            args=(question, selected_networks, api_keys, save_dir)
        )
        thread.daemon = True
        thread.start()

    def _send_requests_thread(self, question, selected_networks, api_keys, save_dir):
        """Поток для отправки запросов"""
        self.progress.start()
        self.log_message("Начинаем отправку запросов...")

        responses = {}

        # Отправка запросов к выбранным нейросетям
        for network in selected_networks:
            self.log_message(f"Отправляем запрос в {network}...")

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

            responses[network] = response
            self.log_message(f"Получен ответ от {network}")

        # Сохранение результатов
        self.log_message("Сохраняем результаты...")
        saved_file = self.save_responses(responses, save_dir)

        # Отправка в Telegram (если настроено)
        bot_token = self.telegram_token_var.get()
        chat_id = self.telegram_chat_id_var.get()

        if bot_token and chat_id and saved_file:
            self.log_message("Отправляем файл в Telegram...")
            self.send_to_telegram(saved_file, bot_token, chat_id)

        self.progress.stop()
        self.log_message("Готово!")

        # Обновляем список истории
        self.load_history()

        messagebox.showinfo("Успех", "Запросы успешно отправлены и обработаны!")

    def load_history(self):
        """Загрузка истории файлов"""
        save_dir = self.save_path_var.get()
        if not save_dir or not os.path.exists(save_dir):
            return

        self.history_listbox.delete(0, 'end')

        try:
            files = [f for f in os.listdir(save_dir) if f.startswith('responses_') and f.endswith('.txt')]
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