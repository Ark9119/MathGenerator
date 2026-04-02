# solver.py
import re
import os
import time

import customtkinter as ctk
import tkinter.messagebox as messagebox


class SolverWindow(ctk.CTkToplevel):
    """Отдельное окно для решения примеров"""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title('Решение примеров')
        self.geometry('750x550')  # 🔥 Увеличил высоту для таймера
        self.resizable(False, False)

        self.focus_set()
        self.grab_set()

        self.entry_fields = []
        self.answer_labels = []
        self.examples = []
        self.answers = []
        self.answers_shown = False

        # 🔥 Переменные таймера
        self.start_time = None
        self.timer_running = False
        self.timer_job = None

        self._load_examples()
        self._create_widgets()

        # 🔥 Запускаем таймер после создания виджетов
        self._start_timer()

        self.protocol('WM_DELETE_WINDOW', self._on_close)

    def _load_examples(self):
        """Загружает примеры и ответы из файлов"""
        try:
            if os.path.exists('examples.txt'):
                with open('examples.txt', 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            match = re.match(r'\d+\)\s*(.+)', line)
                            if match:
                                example = match.group(1).replace(
                                    '_____', ''
                                ).strip()
                                self.examples.append(example)
            else:
                raise FileNotFoundError(
                    'Файл examples.txt не найден. '
                    'Сначала сгенерируйте примеры.'
                )

            if os.path.exists('answers.txt'):
                with open('answers.txt', 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            match = re.match(r'\d+\)\s*(.+)', line)
                            if match:
                                answer = match.group(1).strip()
                                self.answers.append(answer)
            else:
                raise FileNotFoundError('Файл answers.txt не найден.')

            if len(self.examples) != len(self.answers):
                raise ValueError('Количество примеров и ответов не совпадает!')

        except Exception as e:
            messagebox.showerror('Ошибка', str(e))
            self.destroy()

    def _create_widgets(self):
        """Создаёт элементы интерфейса"""
        # Прокручиваемый холст для примеров
        self.canvas = ctk.CTkCanvas(self, highlightthickness=0)
        self.scrollbar = ctk.CTkScrollbar(
            self, orientation='vertical', command=self.canvas.yview
        )
        self.scrollable_frame = ctk.CTkFrame(self.canvas)

        self.scrollable_frame.bind(
            '<Configure>',
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox('all')
            )
        )

        self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor='nw'
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(
            side='left', fill='both', expand=True, padx=10, pady=10
        )
        self.scrollbar.pack(side='right', fill='y', pady=10)

        # Заголовки столбцов
        header_frame = ctk.CTkFrame(
            self.scrollable_frame, fg_color='transparent'
        )
        header_frame.pack(fill='x', padx=10, pady=(0, 5))

        ctk.CTkLabel(
            header_frame, text='#', width=30
        ).pack(side='left', padx=(0, 5))
        ctk.CTkLabel(
            header_frame, text='Пример', anchor='w'
        ).pack(side='left', padx=(0, 10))
        ctk.CTkLabel(
            header_frame, text='Ваш ответ', width=100
        ).pack(side='left', padx=(0, 10))
        
        self.lbl_answer_header = ctk.CTkLabel(
            header_frame,
            text='Правильный ответ',
            width=100,
            fg_color='green',
            corner_radius=5
        )
        self.lbl_answer_header.pack(side='left', padx=(0, 10))
        self.lbl_answer_header.pack_forget()

        # Поля с примерами
        for i, example in enumerate(self.examples):
            row_frame = ctk.CTkFrame(
                self.scrollable_frame, fg_color='transparent'
            )
            row_frame.pack(fill='x', padx=10, pady=5)

            lbl_num = ctk.CTkLabel(row_frame, text=f'{i+1})', width=30)
            lbl_num.pack(side='left', padx=(0, 5))

            lbl_example = ctk.CTkLabel(row_frame, text=example, anchor='w')
            lbl_example.pack(side='left', padx=(0, 10))

            lbl_eq = ctk.CTkLabel(row_frame, text='=', width=20)
            lbl_eq.pack(side='left', padx=(0, 5))

            entry = ctk.CTkEntry(
                row_frame, width=100, placeholder_text='Ответ'
            )
            entry.pack(side='left', padx=(0, 10))
            self.entry_fields.append(entry)

            lbl_answer = ctk.CTkLabel(
                row_frame,
                text=self.answers[i],
                width=100,
                fg_color='green',
                corner_radius=5,
                text_color='white'
            )
            lbl_answer.pack(side='left', padx=(0, 10))
            lbl_answer.pack_forget()
            self.answer_labels.append(lbl_answer)

        # 🔥 Нижняя панель с кнопками
        self.bottom_frame = ctk.CTkFrame(self, height=180)
        self.bottom_frame.pack(fill='x', padx=10, pady=(0, 10))
        self.bottom_frame.pack_propagate(False)

        self.btn_check = ctk.CTkButton(
            self.bottom_frame,
            text='✅ Проверить ответы',
            command=self._check_answers,
            height=40,
            fg_color='blue'
        )
        self.btn_check.pack(pady=(10, 5), padx=10, fill='x')

        self.btn_close = ctk.CTkButton(
            self.bottom_frame,
            text='❌ Закрыть',
            command=self._on_close,
            height=40,
            fg_color='gray'
        )
        self.btn_close.pack(pady=(5, 5), padx=10, fill='x')

        self.btn_show_answers = ctk.CTkButton(
            self.bottom_frame,
            text='👁️ Посмотреть ответы',
            command=self._toggle_answers,
            height=40,
            fg_color='orange'
        )

        self.lbl_result = ctk.CTkLabel(
            self.bottom_frame, text='', text_color='gray'
        )

        # 🔥 Панель таймера (под панелью кнопок)
        self.timer_frame = ctk.CTkFrame(self, height=60, fg_color='gray20')
        self.timer_frame.pack(fill='x', padx=10, pady=(0, 10))
        self.timer_frame.pack_propagate(False)

        self.lbl_timer_title = ctk.CTkLabel(
            self.timer_frame,
            text='⏱️ Время решения:',
            font=('Arial', 14, 'bold'),
            text_color='white'
        )
        self.lbl_timer_title.pack(pady=(10, 0))

        self.lbl_timer = ctk.CTkLabel(
            self.timer_frame,
            text='00:00',
            font=('Arial', 28, 'bold'),
            text_color='yellow'
        )
        self.lbl_timer.pack(pady=(0, 10))

    def _start_timer(self):
        """Запускает таймер"""
        self.start_time = time.time()
        self.timer_running = True
        self._update_timer()

    def _update_timer(self):
        """Обновляет отображение таймера"""
        if self.timer_running:
            elapsed = time.time() - self.start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            self.lbl_timer.configure(text=f'{minutes:02d}:{seconds:02d}')
            # 🔥 Планируем следующее обновление через 1000 мс (1 секунда)
            self.timer_job = self.after(1000, self._update_timer)

    def _stop_timer(self):
        """Останавливает таймер"""
        self.timer_running = False
        if self.timer_job:
            self.after_cancel(self.timer_job)
            self.timer_job = None

    def _get_elapsed_time(self):
        """Возвращает прошедшее время в формате MM:SS"""
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        return f'{minutes:02d}:{seconds:02d}'

    def _check_answers(self):
        """Проверяет ответы и показывает статистику"""
        # 🔥 Останавливаем таймер при проверке
        self._stop_timer()
        final_time = self._get_elapsed_time()

        correct = 0
        incorrect = 0
        total = len(self.examples)

        for i, entry in enumerate(self.entry_fields):
            user_answer = entry.get().strip()
            correct_answer = self.answers[i] if i < len(self.answers) else ''

            try:
                user_val = float(user_answer.replace(',', '.'))
                correct_val = float(correct_answer.replace(',', '.'))
                
                user_val = round(user_val, 2)
                correct_val = round(correct_val, 2)

                if abs(user_val - correct_val) < 0.001:
                    correct += 1
                    entry.configure(border_color='green')
                else:
                    incorrect += 1
                    entry.configure(border_color='red')
            except ValueError:
                incorrect += 1
                entry.configure(border_color='red')

        percentage = (correct / total * 100) if total > 0 else 0
        
        self.btn_show_answers.pack(pady=(5, 5), padx=10, fill='x')

        # 🔥 Добавляем время в статистику
        self.lbl_result.configure(
            text=(
                f'✅ Правильно: {correct} | ❌ Неправильно: {incorrect} | '
                f'📊 Точность: {percentage:.1f}% | ⏱️ Время: {final_time}'),
            text_color='green' if percentage >= 50 else 'red'
        )

        self.btn_check.configure(state='disabled', text='Проверено')

        messagebox.showinfo(
            'Результат',
            f'Вы решили {correct} из {total} примеров.\n'
            f'Точность: {percentage:.1f}%\n'
            f'Время решения: {final_time}'
        )

    def _toggle_answers(self):
        """Показывает/скрывает столбец с правильными ответами"""
        if self.answers_shown:
            for lbl in self.answer_labels:
                lbl.pack_forget()
            self.lbl_answer_header.pack_forget()
            self.btn_show_answers.configure(text='👁️ Посмотреть ответы')
            self.answers_shown = False
        else:
            for lbl in self.answer_labels:
                lbl.pack(side='left', padx=(0, 10))
            self.lbl_answer_header.pack(side='left', padx=(0, 10))
            self.btn_show_answers.configure(text='🙈 Скрыть ответы')
            self.answers_shown = True

    def _on_close(self):
        """Закрытие окна"""
        self._stop_timer()  # 🔥 Останавливаем таймер при закрытии
        self.destroy()


def open_solver(parent):
    """Функция для открытия окна решения из главного окна"""
    solver = SolverWindow(parent)
    solver.wait_window()