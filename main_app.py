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
from mistralai import Mistral as MistralClient  # Добавлено для Mistral[citation:1][citation:5]
from gigachat import GigaChat  # Добавлено для GigaChat[citation:3]

class NeuralNetworkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер нейросетей v6.0")
        self.root.geometry("900x700")

        self.config_file = "config.json"
        self.load_config()

        # Переменные для хранения статусов соединения
        self.connection_status = {
            "OpenAI GPT": False,
            "Anthropic Claude": False,
            "DeepSeek": False,
            "Groq": False,
            "OpenRouter": False,
            "Hugging Face": False,
            "Mistral AI": False,     # Добавлено
            "GigaChat": False,       # Добавлено
            "gen-api.ru": False      # Заглушка
        }

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.setup_main_tab()
        self.setup_api_tab()
        self.setup_history_tab()
        self.setup_status_tab()

        self.load_config_to_ui()
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
                "huggingface": "",
                "mistral": "",       # Добавлено[citation:1]
                "gigachat": "",      # Добавлено[citation:3]
                "genapi": ""         # Заглушка
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
                    for key in self.config:
                        if key in loaded_config:
                            self.config[key].update(loaded_config[key])
            except:
                pass

    def setup_main_tab(self):
        """Создание основной вкладки"""
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Основное")

        # ... (Код фреймов для выбора файла и директории остается без изменений, как в предыдущей версии) ...

        # Фрейм для выбора нейросетей
        networks_frame = ttk.LabelFrame(self.main_tab, text="Выбор нейросетей", padding=10)
        networks_frame.pack(fill='x', padx=10, pady=5)

        self.networks_vars = {
            "OpenAI GPT": tk.BooleanVar(value=False),
            "Anthropic Claude": tk.BooleanVar(value=False),
            "DeepSeek": tk.BooleanVar(value=True),
            "Groq": tk.BooleanVar(value=True),
            "OpenRouter": tk.BooleanVar(value=True),
            "Hugging Face": tk.BooleanVar(value=True),
            "Mistral AI": tk.BooleanVar(value=True),  # Добавлено
            "GigaChat": tk.BooleanVar(value=True),    # Добавлено
            "gen-api.ru": tk.BooleanVar(value=False)   # Заглушка
        }

        self.network_checkbuttons = {}
        row_counter = 0
        for name, var in self.networks_vars.items():
            cb = ttk.Checkbutton(networks_frame, text=name, variable=var)
            cb.grid(row=row_counter, column=0, sticky='w', padx=10, pady=2)
            self.network_checkbuttons[name] = cb
            row_counter += 1

        # ... (Код кнопок управления, прогресс-бара и лога остается без изменений) ...

    def setup_api_tab(self):
        """Создание вкладки с настройками API"""
        self.api_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.api_tab, text="Настройки API")

        # ... (Блоки для OpenAI, Anthropic, DeepSeek, Groq, OpenRouter, Hugging Face остаются без изменений) ...

        # Mistral AI - ДОБАВЛЕНО[citation:1][citation:5]
        mistral_frame = ttk.LabelFrame(self.api_tab, text="Mistral AI API", padding=10)
        mistral_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(mistral_frame, text="API ключ:").grid(row=0, column=0, sticky='w')
        self.mistral_key_var = tk.StringVar()
        self.mistral_entry = ttk.Entry(mistral_frame, textvariable=self.mistral_key_var, width=60, show="*")
        self.mistral_entry.grid(row=1, column=0, padx=(0, 10))
        ttk.Button(mistral_frame, text="Показать",
                  command=lambda: self.toggle_password(self.mistral_entry)).grid(row=1, column=1)
        ttk.Label(mistral_frame, text="Документация: https://docs.mistral.ai/",
                 font=('TkDefaultFont', 8, 'italic')).grid(row=2, column=0, columnspan=2, sticky='w', pady=(5,0))

        # GigaChat - ДОБАВЛЕНО[citation:3]
        gigachat_frame = ttk.LabelFrame(self.api_tab, text="GigaChat API (Sberbank)", padding=10)
        gigachat_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(gigachat_frame, text="Ключ авторизации (Authorization Key):").grid(row=0, column=0, sticky='w')
        self.gigachat_key_var = tk.StringVar()
        self.gigachat_entry = ttk.Entry(gigachat_frame, textvariable=self.gigachat_key_var, width=60, show="*")
        self.gigachat_entry.grid(row=1, column=0, padx=(0, 10))
        ttk.Button(gigachat_frame, text="Показать",
                  command=lambda: self.toggle_password(self.gigachat_entry)).grid(row=1, column=1)
        ttk.Label(gigachat_frame, text="Требуется установка сертификата НУЦ Минцифры",
                 font=('TkDefaultFont', 8, 'italic')).grid(row=2, column=0, columnspan=2, sticky='w', pady=(5,0))

        # gen-api.ru - ЗАГЛУШКА
        genapi_frame = ttk.LabelFrame(self.api_tab, text="gen-api.ru API (Требуется настройка)", padding=10)
        genapi_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(genapi_frame, text="API ключ (формат неизвестен):").grid(row=0, column=0, sticky='w')
        self.genapi_key_var = tk.StringVar()
        self.genapi_entry = ttk.Entry(genapi_frame, textvariable=self.genapi_key_var, width=60)
        self.genapi_entry.grid(row=1, column=0, padx=(0, 10))
        ttk.Label(genapi_frame, text="⚠️ Интеграция не реализована. Требуется документация API.",
                 font=('TkDefaultFont', 8, 'italic'), foreground='orange').grid(row=2, column=0, columnspan=2, sticky='w', pady=(5,0))

        # ... (Блок для Telegram Bot остается без изменений) ...

    def load_config_to_ui(self):
        """Загрузка конфигурации в UI"""
        # ... (Загрузка старых ключей) ...
        self.mistral_key_var.set(self.config["api_keys"]["mistral"])      # Добавлено
        self.gigachat_key_var.set(self.config["api_keys"]["gigachat"])    # Добавлено
        self.genapi_key_var.set(self.config["api_keys"]["genapi"])        # Заглушка
        # ... (Загрузка telegram и директории) ...

    def check_single_connection(self, network_name, api_key):
        """Проверка соединения с одной нейросетью"""
        try:
            if network_name == "OpenAI GPT":
                status = self.test_openai_connection(api_key)
            elif network_name == "Anthropic Claude":
                status = self.test_anthropic_connection(api_key)
            elif network_name == "DeepSeek":
                status = self.test_deepseek_connection(api_key)
            elif network_name == "Groq":
                status = self.test_groq_connection(api_key)
            elif network_name == "OpenRouter":
                status = self.test_openrouter_connection(api_key)
            elif network_name == "Hugging Face":
                status = self.test_huggingface_connection(api_key)
            elif network_name == "Mistral AI":          # Добавлено
                status = self.test_mistral_connection(api_key)
            elif network_name == "GigaChat":            # Добавлено
                status = self.test_gigachat_connection(api_key)
            elif network_name == "gen-api.ru":          # Заглушка
                status = False  # Не реализовано
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

    def test_mistral_connection(self, api_key):          # НОВАЯ ФУНКЦИЯ[citation:1][citation:5]
        """Тест соединения с Mistral AI"""
        if not api_key:
            return False
        try:
            # Простая проверка через запрос списка моделей
            client = MistralClient(api_key=api_key)
            models_response = client.models.list()
            return hasattr(models_response, 'data') and len(models_response.data) > 0
        except Exception as e:
            self.log_message(f"Ошибка Mistral: {str(e)}")
            return False

    def test_gigachat_connection(self, api_key):         # НОВАЯ ФУНКЦИЯ[citation:3]
        """Тест соединения с GigaChat"""
        if not api_key:
            return False
        try:
            # Пробуем получить токен доступа
            # Для теста используем verify_ssl_certs=False, но в продакшене нужен сертификат
            with GigaChat(credentials=api_key, verify_ssl_certs=False, scope="GIGACHAT_API_PERS") as giga:
                # Простой запрос на получение списка моделей
                models = giga.get_models()
                return True
        except Exception as e:
            self.log_message(f"Ошибка GigaChat: {str(e)}")
            return False

    def query_mistral(self, question, api_key):          # НОВАЯ ФУНКЦИЯ[citation:1][citation:5]
        """Запрос к Mistral AI API"""
        try:
            if not self.check_internet_connection():
                return "Ошибка: Нет интернет-соединения"
            if not api_key:
                return "Ошибка: Введите API ключ Mistral AI"

            client = MistralClient(api_key=api_key)
            # Используем одну из доступных моделей, например, mistral-small-latest
            chat_response = client.chat.complete(
                model="mistral-small-latest",
                messages=[
                    {"role": "user", "content": question}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return chat_response.choices[0].message.content
        except Exception as e:
            if "401" in str(e):
                return "Ошибка: Неверный API ключ Mistral AI"
            elif "429" in str(e):
                return "Ошибка: Превышен лимит запросов Mistral AI"
            else:
                return f"Ошибка Mistral AI: {str(e)}"

    def query_gigachat(self, question, api_key):         # НОВАЯ ФУНКЦИЯ[citation:3]
        """Запрос к GigaChat API"""
        try:
            if not self.check_internet_connection():
                return "Ошибка: Нет интернет-соединения"
            if not api_key:
                return "Ошибка: Введите ключ авторизации GigaChat"

            # ВНИМАНИЕ: Для работы в продакшене требуется установить корневой сертификат НУЦ Минцифры[citation:3]
            # Параметр verify_ssl_certs=False отключает проверку, что снижает безопасность[citation:3]
            with GigaChat(credentials=api_key, verify_ssl_certs=False, scope="GIGACHAT_API_PERS") as giga:
                response = giga.chat(question)
                return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            if "401" in error_msg or "authenticat" in error_msg.lower():
                return "Ошибка: Неверный ключ авторизации GigaChat"
            elif "certificate" in error_msg.lower() or "SSL" in error_msg:
                return "Ошибка GigaChat: Проблема с SSL-сертификатом. Требуется установка корневого сертификата НУЦ Минцифры."
            elif "429" in error_msg:
                return "Ошибка: Превышен лимит запросов GigaChat"
            else:
                return f"Ошибка GigaChat: {error_msg}"

    def query_genapi(self, question, api_key):           # ФУНКЦИЯ-ЗАГЛУШКА
        """Запрос к gen-api.ru (не реализовано)"""
        return "Ошибка: Интеграция с gen-api.ru не реализована. Отсутствует документация по API."

    def _send_requests_thread(self, question, selected_networks, api_keys, save_dir, original_file):
        """Поток для отправки запросов"""
        self.progress.start()
        self.log_message("Начинаем отправку запросов...")
        responses = {}
        failed_networks = []

        for network in selected_networks:
            self.log_message(f"Отправляем запрос в {network}...")
            try:
                if network == "OpenAI GPT":
                    response = self.query_openai(question, api_keys[network])
                elif network == "Anthropic Claude":
                    response = self.query_anthropic(question, api_keys[network])
                elif network == "DeepSeek":
                    response = self.query_deepseek(question, api_keys[network])
                elif network == "Groq":
                    response = self.query_groq(question, api_keys[network])
                elif network == "OpenRouter":
                    response = self.query_openrouter(question, api_keys[network])
                elif network == "Hugging Face":
                    response = self.query_huggingface(question, api_keys[network])
                elif network == "Mistral AI":          # Добавлено
                    response = self.query_mistral(question, api_keys[network])
                elif network == "GigaChat":            # Добавлено
                    response = self.query_gigachat(question, api_keys[network])
                elif network == "gen-api.ru":          # Заглушка
                    response = self.query_genapi(question, api_keys[network])
                else:
                    response = "Неподдерживаемая нейросеть"

                # Проверяем, не вернулась ли ошибка
                if response and (response.startswith("Ошибка") or "Error" in response):
                    self.log_message(f"❌ {response}")
                    failed_networks.append(network)
                else:
                    responses[network] = response
                    self.log_message(f"✅ Получен ответ от {network}")
            except Exception as e:
                error_msg = f"Ошибка при запросе к {network}: {str(e)}"
                self.log_message(f"❌ {error_msg}")
                failed_networks.append(network)

        # ... (Остальная часть метода _send_requests_thread без изменений) ...

    # ... (Все остальные методы класса NeuralNetworkApp остаются без изменений) ...

def main():
    root = tk.Tk()
    try:
        root.tk.call('source', 'azure.tcl')
        root.tk.call('set_theme', 'dark')
    except:
        pass
    style = ttk.Style(root)
    style.configure("Accent.TButton", font=('Segoe UI', 10, 'bold'))
    app = NeuralNetworkApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()