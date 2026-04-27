import logging
import os
import sys
from logging.handlers import RotatingFileHandler


class ColoredFormatter(logging.Formatter):
    """Форматтер, добавляющий ANSI-цвета только в консольный вывод."""

    COLORS = {
        'DEBUG': '\033[94m',    # Синий
        'INFO': '\033[92m',     # Зелёный
        'WARNING': '\033[93m',  # Жёлтый
        'ERROR': '\033[91m',    # Красный
        'CRITICAL': '\033[95m'  # Фиолетовый
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        # Базовое форматирование через родительский класс
        msg = super().format(record)
        # Оборачиваем в цвет + сброс
        color = self.COLORS.get(record.levelname, '')
        return f"{color}{msg}{self.RESET}"


def setup_logging(
    log_file: str = "logs/app.log",
    level_console: int = logging.DEBUG,
    level_file: int = logging.INFO,
    max_bytes: int = 10_485_760,  # 10 MB
    backup_count: int = 5,
    fmt: str | None = None,
    datefmt: str = "%Y-%m-%d %H:%M:%S"
) -> None:
    """
    Настраивает глобальное логирование для всего проекта.
    Вызывается ОДИН раз в точке входа (обычно в main.py).
    """
    # Формат по умолчанию (можно переопределить при вызове)
    if fmt is None:
        fmt = (
            "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
        )

    # Создаём директорию для логов
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    # Корневой логгер
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)  # Ловим всё, фильтруют хендлеры

    # Очищаем старые хендлеры (безопасно для перезапусков/тестов)
    if root.handlers:
        root.handlers.clear()

    # 📄 Файловый хендлер (БЕЗ цветов)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    file_handler.setLevel(level_file)
    file_handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
    root.addHandler(file_handler)

    # 🖥️ Консольный хендлер (С ЦВЕТАМИ)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level_console)
    console_handler.setFormatter(ColoredFormatter(fmt, datefmt=datefmt))
    root.addHandler(console_handler)

    logging.debug("Логирование успешно инициализировано.")
