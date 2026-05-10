import customtkinter as ctk
import threading
import tkinter.messagebox as messagebox
import webbrowser

from algoritm.main_algoritm import run_generation
from interface.solver_window import open_solver
from interface.log_window import LogViewer

import logging


logger = logging.getLogger(__name__)

ctk.set_appearance_mode('System')
ctk.set_default_color_theme('blue')


class MyCheckboxFrame(ctk.CTkFrame):
    def __init__(self, master, title, values):
        """
        values: список кортежей (internal_value, 'display_text')
        Пример: [('not_float', 'Без дробей'), ('+', 'Плюс')]
        """
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.checkboxes = []

        self.title_label = ctk.CTkLabel(
            self, text=title, fg_color='gray30', corner_radius=6
        )
        self.title_label.grid(
            row=0, column=0, padx=10, pady=(10, 0), sticky='ew'
        )

        for i, (internal_val, display_text) in enumerate(values):
            # Отображаем display_text, но храним internal_val
            checkbox = ctk.CTkCheckBox(self, text=display_text)
            # Сохраняем внутреннее значение
            checkbox._internal_value = internal_val
            checkbox.grid(
                row=i + 1, column=0, padx=10, pady=(5, 0), sticky='w'
            )
            self.checkboxes.append(checkbox)

    def get(self):
        """Возвращает список внутренних значений (internal_value)"""
        checked = []
        for checkbox in self.checkboxes:
            if checkbox.get() == 1:
                # Берём внутреннее значение, а не текст
                checked.append(checkbox._internal_value)
        return checked


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Генератор математических примеров')
        # self.geometry('550x550')
        logger.info('Создано окно основного интерфейса')
        self.resizable(False, False)

        # Блок настроек
        self.frame_settings = ctk.CTkFrame(self)
        self.frame_settings.pack(pady=10, padx=10, fill='x')

        # Строка 1: Количество чисел и примеров
        self.lbl_count = ctk.CTkLabel(
            self.frame_settings, text='Чисел в примере:'
        )
        self.lbl_count.grid(row=0, column=0, padx=10, pady=5, sticky='w')

        self.entry_count = ctk.CTkEntry(self.frame_settings, width=50)
        self.entry_count.grid(row=0, column=1, padx=5, pady=5)
        self.entry_count.insert(0, '3')

        self.lbl_examples = ctk.CTkLabel(
            self.frame_settings, text='Кол-во примеров:'
        )
        self.lbl_examples.grid(row=0, column=2, padx=10, pady=5, sticky='w')

        self.entry_examples = ctk.CTkEntry(self.frame_settings, width=50)
        self.entry_examples.grid(row=0, column=3, padx=5, pady=5)
        self.entry_examples.insert(0, '20')

        # Строка 2: Мин и Макс числа
        self.lbl_min = ctk.CTkLabel(self.frame_settings, text='Мин. число:')
        self.lbl_min.grid(row=1, column=0, padx=10, pady=5, sticky='w')
        self.entry_min = ctk.CTkEntry(self.frame_settings, width=50)
        self.entry_min.grid(row=1, column=1, padx=5, pady=5)
        self.entry_min.insert(0, '1')

        self.lbl_max = ctk.CTkLabel(self.frame_settings, text='Макс. число:')
        self.lbl_max.grid(row=1, column=2, padx=10, pady=5, sticky='w')
        self.entry_max = ctk.CTkEntry(self.frame_settings, width=50)
        self.entry_max.grid(row=1, column=3, padx=5, pady=5)
        self.entry_max.insert(0, '50')

        # Блок знаков и правил
        self.frame_options = ctk.CTkFrame(self)
        self.frame_options.pack(pady=10, padx=10)

        self.frame_options.grid_columnconfigure(0, weight=1)
        self.frame_options.grid_columnconfigure(1, weight=1)

        self.checkbox_signs = MyCheckboxFrame(
            self.frame_options,
            'Знаки',
            values=[
                ('+', 'Плюс (+)'),
                ('-', 'Минус (-)'),
                ('*', 'Умножение (×)'),
                ('/', 'Деление (÷)')
            ]
        )
        self.checkbox_signs.grid(
            row=0, column=0, padx=10, pady=10, sticky='nsew'
        )

        self.checkbox_rules = MyCheckboxFrame(
            self.frame_options,
            'Правила',
            values=[
                ('not_negative', 'Без отрицательных'),
                ('not_float', 'Без дробей'),
                ('not_zero', 'Без нуля')
            ]
        )
        self.checkbox_rules.grid(
            row=0, column=1, padx=10, pady=10, sticky='nsew'
        )

        # По умолчанию выбираем + и -
        self.checkbox_signs.checkboxes[0].select()
        self.checkbox_signs.checkboxes[1].select()
        self.checkbox_rules.checkboxes[1].select()  # not_float

        # Фрейм: Сгенерировать и Решать примеры.
        self.first_btn_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.first_btn_frame.pack(padx=10, fill='x')

        self.first_btn_frame.grid_columnconfigure(0, weight=1)
        self.first_btn_frame.grid_columnconfigure(1, weight=1)

        self.btn_generate = ctk.CTkButton(
            self.first_btn_frame,
            text='Сгенерировать',
            command=self.start_generation_thread,
            height=40
        )
        # self.btn_generate.pack(
        #     side='left', pady=10, padx=(0, 10), fill='x', expand=True
        # )
        self.btn_generate.grid(
            row=0, column=0, padx=10, pady=10, sticky='nsew'
        )

        self.btn_solve = ctk.CTkButton(
            self.first_btn_frame,
            text='Решать примеры',
            command=self.open_solver_window,
            height=40,
            fg_color='green'
        )
        # self.btn_solve.pack(
        #     side='right', pady=10, padx=(10, 0), fill='x', expand=True
        # )
        self.btn_solve.grid(
            row=0, column=1, padx=10, pady=10, sticky='nsew'
        )

        # Фрейм: логи и о проекте.
        # self.second_btn_frame = ctk.CTkFrame(self, fg_color='transparent')
        # self.second_btn_frame.pack(padx=10, fill='x')

        # 🔹 Кнопка "Смотреть логи"
        self.btn_logs = ctk.CTkButton(
            # self.second_btn_frame,
            self.first_btn_frame,
            text='Логи',
            command=self.open_log_viewer,
            height=20,
            fg_color='gray30',  # Нейтральный цвет
            hover_color='gray25'
        )
        # self.btn_logs.pack(side='left', pady=10, padx=(10, 0))
        # self.btn_logs.pack(
        #     side='left', pady=10, padx=(0, 10), fill='x', expand=True
        # )
        self.btn_logs.grid(
            row=1, column=0, padx=10, pady=10, sticky='nsew'
        )
        # 🔹 Ссылка на окно логов (чтобы не открывать дубликаты)
        self.log_viewer_window = None

        self.lbl_status = ctk.CTkLabel(
            self, text='Готов к работе', text_color='gray'
        )
        self.lbl_status.pack(pady=(0, 10))

        # 🔹 Кнопка "О приложении"
        self.btn_instructions = ctk.CTkButton(
            # self.second_btn_frame,
            self.first_btn_frame,
            text='О приложении',
            command=self.open_log_viewer,
            height=20,
            fg_color='gray30',  # Нейтральный цвет
            hover_color='gray25'
        )
        # self.btn_instructions.pack(side='left', pady=10, padx=(10, 0))
        # self.btn_instructions.pack(
        #     side='left', pady=10, padx=(0, 10), fill='x', expand=True
        # )
        self.btn_instructions.grid(
            row=1, column=1, padx=10, pady=10, sticky='nsew'
        )

        # Строка с информацией об авторе и ссылки
        self.frame_about = ctk.CTkFrame(self)
        self.frame_about.pack(padx=(5, 5), fill='x')

        self.about = ctk.CTkLabel(
            self.frame_about,
            text='Created by Ark. Ark9119@yandex.ru.',
            text_color='gray'
        )
        self.about.pack(side='left', padx=(5, 5))

        self.about_git_link = ctk.CTkButton(
            self.frame_about,
            text='GitHub',
            command=lambda: webbrowser.open('https://github.com/Ark9119/'),
            fg_color='transparent',
            text_color='gray',
            width=0,
            height=0
        )
        self.about_git_link.pack(
            side='right', pady=5, padx=(0, 5)
        )

    def open_solver_window(self):
        """Открывает окно решения"""
        open_solver(self)

    def start_generation_thread(self):
        """Запускает генерацию в отдельном потоке"""
        self.btn_generate.configure(state='disabled', text='Генерация...')
        self.lbl_status.configure(
            text='Пожалуйста, подождите...', text_color='orange'
        )

        thread = threading.Thread(target=self.run_generation_task)
        thread.daemon = True
        thread.start()

    def run_generation_task(self):
        """Логика генерации (выполняется в фоне)"""
        logger.info('Получен запрос на генерацию.')
        try:
            # Сбор данных из интерфейса
            try:
                nums_count = int(self.entry_count.get())
                ex_count = int(self.entry_examples.get())
                min_num = int(self.entry_min.get())
                max_num = int(self.entry_max.get())
            except ValueError:
                self.update_status(
                    'Ошибка: введите числа в поля настроек', 'red'
                )
                self.reset_button()
                return

            signs = self.checkbox_signs.get()
            rules = self.checkbox_rules.get()

            if not signs:
                self.update_status('Ошибка: выберите хотя бы один знак', 'red')
                self.reset_button()
                return

            if min_num > max_num:
                self.update_status('Ошибка: Мин число больше Макс', 'red')
                self.reset_button()
                return

            config = {
                'numbers_count': nums_count,
                'examples_count': ex_count,
                'signs': signs,
                'rules': rules,
                'min_number': min_num,
                'max_number': max_num
            }

            # Запуск логики из main.py
            logger.debug('Пользователь передал аргументы:')
            logger.debug(f'Количество чисел в примере {nums_count}')
            logger.debug(f'Количество примеров {ex_count}')
            logger.debug(f'Используемые знаки {signs}')
            logger.debug(f'Правила {rules}')
            logger.debug(f'Диапазон чисел от {min_num} до {max_num}')
            success, message = run_generation(config)
            if success:
                self.update_status(message, 'green')
                messagebox.showinfo('Успех', message)
            else:
                self.update_status(message, 'red')
                messagebox.showerror('Ошибка', message)

        except Exception as e:
            self.update_status(f'Критическая ошибка: {str(e)}', 'red')
            messagebox.showerror('Ошибка', str(e))
        finally:
            self.reset_button()

    def update_status(self, text, color):
        self.lbl_status.configure(text=text, text_color=color)

    def reset_button(self):
        self.btn_generate.configure(state='normal', text='Сгенерировать')

    def open_log_viewer(self):
        """Открывает или фокусирует окно просмотра логов."""
        # Если окно уже открыто — поднимаем его на передний план
        if (
            self.log_viewer_window is not None and
            self.log_viewer_window.winfo_exists()
        ):
            self.log_viewer_window.focus_force()
            self.log_viewer_window.lift()
            return
        # Иначе создаём новое
        self.log_viewer_window = LogViewer(self, title="🪟 Логи приложения")
