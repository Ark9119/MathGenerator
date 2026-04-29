import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional
from log_viewer import QueueHandler, get_log_queue


class ModuleFilter(logging.Filter):
    """Фильтр: пропускает только логи от указанного модуля."""
    def __init__(self, module_name: str):
        super().__init__()
        self.module_name = module_name

    def filter(self, record: logging.LogRecord) -> bool:
        # record.name — это __name__ модуля, откуда пришёл лог
        return (
            record.name == self.module_name or
            record.name.startswith(self.module_name + ".")
        )


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
        # Сначала форматируем базовое сообщение
        msg = super().format(record)
        # Находим levelname в строке и оборачиваем только его
        color = self.COLORS.get(record.levelname, '')
        # Заменяем levelname на цветную версию (один раз)
        msg = msg.replace(
            record.levelname,
            f"{color}{record.levelname}{self.RESET}",
            1  # только первое вхождение
        )
        return msg


def setup_logging(
    log_file: str = "logs/app.log",
    level_console: int = logging.DEBUG,
    level_file: int = logging.DEBUG,
    max_bytes: int = 10_485_760,  # 10 MB
    backup_count: int = 5,
    fmt: str | None = None,
    datefmt: str = "%Y-%m-%d %H:%M:%S",
    module_logs: Optional[dict[str, str]] = None
) -> None:
    """
    Настраивает глобальное логирование для всего проекта.
    Вызывается ОДИН раз в точке входа (обычно в main.py).
    """
    # Формат по умолчанию (можно переопределить при вызове)
    if fmt is None:
        fmt = (
            "%(asctime)s | %(levelname)-8s | "
            "%(name)s:%(funcName)s:%(lineno)d | "
            "%(message)s"
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

    # 📁 Отдельные хендлеры для указанных модулей
    if module_logs:
        for module_name, file_path in module_logs.items():
            # Создаём папку, если нужно
            dir_path = os.path.dirname(file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)

            # Хендлер для этого модуля
            handler = RotatingFileHandler(
                file_path,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8"
            )
            handler.setLevel(level_file)
            handler.setFormatter(logging.Formatter(fmt, datefmt=datefmt))
            handler.addFilter(ModuleFilter(module_name))
            root.addHandler(handler)

    # 🖥️ Консольный хендлер (С ЦВЕТАМИ)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level_console)
    console_handler.setFormatter(ColoredFormatter(fmt, datefmt=datefmt))
    root.addHandler(console_handler)

    # 📨 Хендлер для стриминга в UI (если очередь инициализирована)
    log_queue = get_log_queue()
    if log_queue is not None:
        # 🔹 Формат должен соответствовать паттерну в _insert_colored_log
        ui_fmt = (
            '%(asctime)s | %(levelname)-8s | '
            '%(name)s:%(funcName)s | %(message)s'
        )
        ui_formatter = logging.Formatter(ui_fmt, datefmt="%Y-%m-%d %H:%M:%S")

        queue_handler = QueueHandler(log_queue, ui_formatter)
        queue_handler.setLevel(logging.DEBUG)  # Ловим всё
        root.addHandler(queue_handler)

    logging.info(
        f'\n{"-"*20}\n'
        "Логирование успешно инициализировано."
    )
