import customtkinter as ctk
import logging


logger = logging.getLogger(__name__)


class AboutWindow(ctk.CTkToplevel):
    """Отдельное окно для информации о авторе и проекте"""
    def __init__(self, master, title: str = "Информация о приложении",):
        super().__init__(master)
        self.parent = master
        self.title('Информация')
        self.geometry('550x550')
        self.resizable(False, False)

        # Фокус на окне и модальность
        self.focus_set()
        self.grab_set()

        # Основной контейнер с прокруткой (на случай длинного текста)
        self.scroll_frame = ctk.CTkScrollableFrame(
            self, label_text=""
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Разделы информации
        self._add_author_section()
        self._add_instructions_section()

        # Кнопка закрытия
        self.btn_close = ctk.CTkButton(
            self.scroll_frame,
            text="Закрыть",
            command=self.destroy,
            width=100
        )
        self.btn_close.pack(pady=20)

    def _add_author_section(self):
        """Добавляет блок с информацией об авторе"""
        # Заголовок раздела
        title = ctk.CTkLabel(
            self.scroll_frame,
            text="👤 Об авторе",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(pady=(10, 5), anchor="w")

        # Текст об авторе
        author_text = (
            "Приложение разработано Ark.\n"
            "Контакт: Ark9119@yandex.ru\n"
            "GitHub: https://github.com/Ark9119/\n\n"
            "Версия приложения: 1.0.0"
        )
        author_label = ctk.CTkLabel(
            self.scroll_frame,
            text=author_text,
            justify="left",
            wraplength=500
        )
        author_label.pack(pady=5, anchor="w")

        # Разделитель
        separator = ctk.CTkFrame(self.scroll_frame, height=2, fg_color="gray30")
        separator.pack(fill="x", pady=15)

    def _add_instructions_section(self):
        """Добавляет блок с инструкцией по использованию"""
        # Заголовок раздела
        title = ctk.CTkLabel(
            self.scroll_frame,
            text="📖 Инструкция по использованию",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.pack(pady=(10, 5), anchor="w")

        # Текст инструкции
        instructions = (
            "1. В блоке «Настройки» укажите параметры генерации:\n"
            "   • Чисел в примере: количество чисел в одном выражении (2-10)\n"
            "   • Кол-во примеров: сколько примеров сгенерировать (1-100)\n"
            "   • Мин/Макс число: диапазон значений для чисел в примерах\n\n"
            "2. В блоке «Знаки» выберите допустимые операции:\n"
            "   +, −, ×, ÷ — отметьте нужные галочками\n\n"
            "3. В блоке «Правила» настройте ограничения:\n"
            "   • Без отрицательных — результат промежуточных действий ≥ 0\n"
            "   • Без дробей — деление только нацело\n"
            "   • Без нуля — исключить 0 из генерации чисел\n\n"
            "4. Нажмите «Сгенерировать» — примеры сохранятся в файл.\n"
            "5. Кнопка «Решать примеры» откроет тренажёр для решения.\n"
            "6. Кнопка «Логи» покажет детальную информацию о работе программы."
        )
        instr_label = ctk.CTkLabel(
            self.scroll_frame,
            text=instructions,
            justify="left",
            wraplength=500
        )
        instr_label.pack(pady=5, anchor="w")
