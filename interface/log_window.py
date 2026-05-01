import customtkinter as ctk
import queue
import logging
import re
from typing import Optional


# 🔹 Глобальная очередь для логов (создаётся один раз)
_log_queue: Optional[queue.Queue] = None

logger = logging.getLogger(__name__)


def init_log_queue(max_size: int = 1000) -> queue.Queue:
    """Инициализирует очередь для логов. Вызывать один раз при старте."""
    global _log_queue
    _log_queue = queue.Queue(maxsize=max_size)
    return _log_queue


def get_log_queue() -> Optional[queue.Queue]:
    """Возвращает очередь логов."""
    return _log_queue


class QueueHandler(logging.Handler):
    """Хендлер: отправляет лог-записи в queue.Queue (потокобезопасно)."""
    def __init__(self, log_queue: queue.Queue, formatter: logging.Formatter):
        super().__init__()
        self.log_queue = log_queue
        self.setFormatter(formatter)

    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
            # Не блокируем, если очередь полна — пропускаем старые
            try:
                self.log_queue.put_nowait(msg)
            except queue.Full:
                # Удаляем старую запись и добавляем новую
                try:
                    self.log_queue.get_nowait()
                    self.log_queue.put_nowait(msg)
                except queue.Empty:
                    pass
        except Exception:
            self.handleError(record)


class LogViewer(ctk.CTkToplevel):
    """Окно для просмотра логов в реальном времени."""
    def __init__(
        self, master, title: str = "Логи приложения",
        max_lines: int = 500, update_ms: int = 100
    ):
        super().__init__(master)
        self.title(title)
        self.geometry("900x700")
        self.minsize(400, 200)

        self.max_lines = max_lines
        self.update_ms = update_ms
        self._closed = False
        # 🔹 UI
        self._setup_ui()

        # 🔹 Получаем очередь логов
        self.log_queue = get_log_queue()
        if not self.log_queue:
            self.text_log.insert(
                "end", "⚠️ Очередь логов не инициализирована!\n"
            )
            return

        # 🔹 Запускаем периодическое обновление (в главном потоке!)
        self.after(self.update_ms, self._poll_logs)

        # 🔹 Обработка закрытия окна
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        logger.info("Окно логов открыто")

    def _setup_ui(self):
        """Создаёт интерфейс окна."""
        # Панель кнопок
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=10, pady=5)

        self.btn_clear = ctk.CTkButton(
            self.btn_frame, text="Очистить", width=80,
            command=self._clear_logs, fg_color="gray"
        )
        self.btn_clear.pack(side="right")

        self.btn_copy = ctk.CTkButton(
            self.btn_frame, text="Копировать", width=80,
            command=self._copy_logs
        )
        self.btn_copy.pack(side="right", padx=5)
        # Поле с логами
        self.text_log = ctk.CTkTextbox(
            self, font=("Consolas", 12), state="disabled",
            wrap="word", activate_scrollbars=True
        )
        # 🔹 Настройка цветовых тегов — ЧЕРЕЗ ._textbox!
        # 🔹 Настройка тегов для СВЕТЛОЙ темы
        textbox = self.text_log._textbox
        # Базовый стиль: чёрный текст, белый фон (для всех уровней)
        BASE_STYLE = {"foreground": "#000000", "background": "#ffffff"}
        # Цвета ТОЛЬКО для уровня лога (будут применяться к части строки)
        LEVEL_COLORS = {
            "DEBUG": "#0066cc",      # Синий
            "INFO": "#008800",       # Тёмно-зелёный
            "WARNING": "#cc6600",    # Оранжевый
            "ERROR": "#cc0000",      # Красный
            "CRITICAL": "#990099"    # Фиолетовый
        }
        # Создаём теги: базовый стиль + цвет для уровня
        for level, color in LEVEL_COLORS.items():
            textbox.tag_configure(
                level,
                foreground=color,      # 🔹 Цветной ТОЛЬКО уровень
                background="#ffffff",  # Белый фон
                font=("Consolas", 12)
            )
        # Метаданные (время, модуль) — тёмно-серые, но на белом фоне
        textbox.tag_configure(
            "TIME", foreground="#555555", background="#ffffff"
        )
        textbox.tag_configure(
            "MODULE", foreground="#333333", background="#ffffff"
        )
        # Выделение ключевых слов — жирный чёрный с лёгкой подсветкой
        textbox.tag_configure(
            "HIGHLIGHT",
            foreground="#000000",
            background="#e0e0e0",  # светло-серый фон для выделения
            font=("Consolas", 12, "bold")
        )
        # 🔹 Базовый стиль для не распознанных логов
        textbox.tag_configure("DEFAULT", **BASE_STYLE)

        self.text_log.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Статус
        self.lbl_status = ctk.CTkLabel(
            self, text="Ожидание логов...", text_color="gray",
            font=("Arial", 8)
        )
        self.lbl_status.pack(pady=(0, 5))

    def _poll_logs(self):
        """Опрашивает очередь и добавляет новые логи в UI с раскраской."""
        if self._closed:
            return

        textbox = self.text_log._textbox  # ← кэш для удобства
        count = 0

        while not self.log_queue.empty():
            try:
                msg = self.log_queue.get_nowait()
                textbox.configure(state="normal")

                self._insert_colored_log(msg, textbox)  # ← передаём textbox
                # Ограничиваем количество строк
                if self.max_lines > 0:
                    # ← index() тоже через _textbox!
                    lines = int(textbox.index("end-1c").split(".")[0])
                    if lines > self.max_lines:
                        textbox.delete("1.0", f"{lines - self.max_lines}.0")

                textbox.configure(state="disabled")
                textbox.see("end")  # ← see() через _textbox!
                count += 1
            except queue.Empty:
                break

        # Обновление статуса...
        if count > 0:
            self.lbl_status.configure(text=f"📥 Получено {count} записей")
        else:
            self.lbl_status.configure(text="⏳ Ожидание...")

        if not self._closed:
            self.after(self.update_ms, self._poll_logs)

    def _insert_colored_log(self, msg: str, textbox=None):
        """
        Вставляет лог с раскраской: вся строка чёрная на белом,
        только уровень (INFO/DEBUG) — цветной.
        """
        if textbox is None:
            textbox = self.text_log._textbox

        level_log = 'DEBUG|INFO|WARNING|ERROR|CRITICAL'
        pattern = (
            rf'^([\d:\- ]+)\s*\|\s*({level_log})\s*\|\s*([^|]+)\s*\|\s*(.*)$'
        )
        match = re.match(pattern, msg.strip())

        if match:
            time_part, level, module_part, message = match.groups()
            # 1. Время — тёмно-серое
            textbox.insert("end", time_part.strip() + " ", "TIME")
            # 2. Разделитель — серый
            textbox.insert("end", "| ", "TIME")
            # 3. 🔹 УРОВЕНЬ — цветной (только эта часть!)
            # Используем тег с именем уровня, который мы настроили выше
            textbox.insert("end", f"{level:8s}", level)
            # 4. Разделитель — серый
            textbox.insert("end", " | ", "TIME")
            # 5. Модуль:функция — чёрный
            textbox.insert("end", module_part.strip() + " | ", "MODULE")
            # 6. 🔹 Сообщение — чёрное на белом (базовый стиль)
            self._insert_message_with_highlights(message, textbox)
            # Перенос строки
            textbox.insert("end", "\n")
        else:
            # Не распознано — вставляем как есть, чёрным на белом
            textbox.insert("end", msg + "\n", "DEFAULT")

    def _insert_message_with_highlights(self, message: str, textbox=None):
        """Вставляет сообщение,
        выделяя ключевые слова (чёрные на светло-сером).
        """
        if textbox is None:
            textbox = self.text_log._textbox

        keywords = {
            '✅': True, '❌': True, '⚠️': True, '🔥': True,
            'Успех': True, 'Ошибка': True, 'Критическая': True,
            'Запуск': True, 'Завершено': True
        }

        last_pos = 0
        for keyword in keywords:
            start = message.find(keyword, last_pos)
            if start != -1:
                # Текст до ключа — обычный чёрный
                if start > last_pos:
                    textbox.insert("end", message[last_pos:start], "MODULE")
                # Ключевое слово — жирное, с подсветкой
                textbox.insert("end", keyword, "HIGHLIGHT")
                last_pos = start + len(keyword)

        # Остаток сообщения — обычный чёрный
        if last_pos < len(message):
            textbox.insert("end", message[last_pos:], "MODULE")
        elif last_pos == 0:
            # Если ключей не нашли — всё сообщение обычным стилем
            textbox.insert("end", message, "MODULE")

    def _clear_logs(self):
        """Очищает поле логов."""
        textbox = self.text_log._textbox
        textbox.configure(state="normal")
        textbox.delete("1.0", "end")  # ← delete через _textbox!
        textbox.configure(state="disabled")
        logger.debug("🧹 Логи очищены пользователем")

    def _copy_logs(self):
        """Копирует все логи в буфер обмена."""
        textbox = self.text_log._textbox
        logs = textbox.get("1.0", "end-1c")  # ← get через _textbox!
        if logs.strip():
            self.clipboard_clear()
            self.clipboard_append(logs)
            self.lbl_status.configure(
                text="📋 Скопировано!", text_color="green"
            )
            self.after(1500, lambda: self.lbl_status.configure(
                text="⏳ Ожидание...", text_color="gray"
            ))

    def _on_close(self):
        """Обработчик закрытия окна."""
        self._closed = True
        logger.info("🪟 Окно логов закрыто")
        self.destroy()
