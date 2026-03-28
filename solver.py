# solver.py
import customtkinter as ctk
import tkinter.messagebox as messagebox
from docx import Document
import re
import os

class SolverWindow(ctk.CTkToplevel):
    """Отдельное окно для решения примеров"""

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Решение примеров")
        self.geometry("600x500")
        self.resizable(False, False)

        # Фокус на окне и модальность
        self.focus_set()
        self.grab_set()
 
        self.entry_fields = []
        self.examples = []
        self.answers = []

        self._load_examples()
        self._create_widgets()

        # Обработка закрытия окна
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _load_examples(self):
        """Загружает примеры и ответы из файлов"""
        try:
            # Читаем примеры
            if os.path.exists('examples.txt'):
                with open('examples.txt', 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            # Убираем номер и пробелы: "1) 2 + 2 =  _____" -> "2 + 2 ="
                            match = re.match(r'\d+\)\s*(.+)', line)
                            if match:
                                example = match.group(1).replace('_____', '').strip()
                                self.examples.append(example)
            else:
                raise FileNotFoundError("Файл examples.txt не найден. Сначала сгенерируйте примеры.")

            # Читаем ответы
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
                raise FileNotFoundError("Файл answers.txt не найден.")

            if len(self.examples) != len(self.answers):
                raise ValueError("Количество примеров и ответов не совпадает!")

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.destroy()

    def _create_widgets(self):
        """Создаёт элементы интерфейса"""
        # Прокручиваемый холст для примеров
        self.canvas = ctk.CTkCanvas(self, highlightthickness=0)
        self.scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.scrollbar.pack(side="right", fill="y", pady=10)

        # Поля с примерами
        for i, example in enumerate(self.examples):
            row_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=10, pady=5)

            lbl_num = ctk.CTkLabel(row_frame, text=f"{i+1})", width=30)
            lbl_num.pack(side="left", padx=(0, 5))

            lbl_example = ctk.CTkLabel(row_frame, text=example, anchor="w")
            lbl_example.pack(side="left", padx=(0, 10))

            lbl_eq = ctk.CTkLabel(row_frame, text="=", width=20)
            lbl_eq.pack(side="left", padx=(0, 5))

            entry = ctk.CTkEntry(row_frame, width=100, placeholder_text="Ответ")
            entry.pack(side="left", padx=(0, 10))
            self.entry_fields.append(entry)

        # Нижняя панель с кнопками
        self.bottom_frame = ctk.CTkFrame(self, height=80)
        self.bottom_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.bottom_frame.pack_propagate(False)

        self.btn_check = ctk.CTkButton(
            self.bottom_frame, 
            text="Проверить ответы",
            command=self._check_answers,
            height=40
        )
        self.btn_check.pack(pady=10, padx=10, fill="x")

        self.btn_close = ctk.CTkButton(
            self.bottom_frame,
            text="Закрыть",
            command=self._on_close,
            height=40,
            fg_color="gray"
        )
        self.btn_close.pack(pady=(0, 10), padx=10, fill="x")

        self.lbl_result = ctk.CTkLabel(self.bottom_frame, text="", text_color="gray")
        self.lbl_result.pack(pady=(5, 0))

    def _check_answers(self):
        """Проверяет ответы и показывает статистику"""
        correct = 0
        incorrect = 0
        total = len(self.examples)

        for i, entry in enumerate(self.entry_fields):
            user_answer = entry.get().strip()
            correct_answer = self.answers[i] if i < len(self.answers) else ""

            # Сравниваем ответы (с учётом возможных форматов)
            try:
                user_val = float(user_answer.replace(',', '.'))
                correct_val = float(correct_answer.replace(',', '.'))
                if abs(user_val - correct_val) < 0.001:
                    correct += 1
                    entry.configure(border_color="green")
                else:
                    incorrect += 1
                    entry.configure(border_color="red")
            except ValueError:
                incorrect += 1
                entry.configure(border_color="red")

        # Показываем статистику
        percentage = (correct / total * 100) if total > 0 else 0
        self.lbl_result.configure(
            text=f"✅ Правильно: {correct} | ❌ Неправильно: {incorrect} | 📊 Точность: {percentage:.1f}%",
            text_color="green" if percentage >= 50 else "red"
        )

        # Блокируем кнопку проверки после проверки
        self.btn_check.configure(state="disabled", text="Проверено")

        # Показываем сообщение
        messagebox.showinfo(
            "Результат", 
            f"Вы решили {correct} из {total} примеров.\nТочность: {percentage:.1f}%"
        )

    def _on_close(self):
        """Закрытие окна"""
        self.destroy()


def open_solver(parent):
    """Функция для открытия окна решения из главного окна"""
    solver = SolverWindow(parent)
    solver.wait_window()  # Ждём закрытия окна решения
