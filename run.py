#!/usr/bin/env python3
"""Точка входа в приложение. Запуск: python run.py"""

from interface.log_window import init_log_queue  # 🔹 Импортируем
from algoritm.logging_config import setup_logging
from interface.main_window import App
import logging


if __name__ == "__main__":
    # 🔹 Инициализируем очередь логов ДО настройки логгера
    init_log_queue(max_size=2000)  # Храним последние 2000 записей

    # 🔧 Настраиваем логирование ДО импорта модулей с логгерами
    setup_logging(
        log_file="logs/main.log",
        level_console=logging.DEBUG,
        level_file=logging.DEBUG,
        module_logs={
            "main": "logs/generate_algoritm.log",  # логи алгоритма отдельно
            "interface_for_main": "logs/interface.log",  # логи UI отдельно
        }
    )

    logger = logging.getLogger(__name__)
    logger.info("🚀 Запуск приложения")
    app = App()
    app.mainloop()
