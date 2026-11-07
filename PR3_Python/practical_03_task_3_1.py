
"""Паттерни Singleton та Factory Method."""

from abc import ABC, abstractmethod
from datetime import datetime
import json


class SingletonMeta(type):
    """Метаклас для реалізації патерну Singleton."""

    _instances: dict[type, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class LogFormatter(ABC):
    """Абстрактний базовий клас форматера логів."""

    @abstractmethod
    def format(
        self, level: str, message: str, timestamp: datetime
    ) -> str:
        """Форматує повідомлення логу."""


class PlainFormatter(LogFormatter):
    """Простий текстовий формат."""

    def format(
        self, level: str, message: str, timestamp: datetime
    ) -> str:
        formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"[{level}] {formatted_time} - {message}"


class JSONFormatter(LogFormatter):
    """Форматування повідомлень у JSON."""

    def format(
        self, level: str, message: str, timestamp: datetime
    ) -> str:
        data = {
            "level": level,
            "time": timestamp.isoformat(timespec="seconds"),
            "message": message
        }
        return json.dumps(data, ensure_ascii=False)


class ColorFormatter(LogFormatter):
    """Кольоровий формат для терміналу."""

    COLORS = {
        "DEBUG": "\033[90m",
        "INFO": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
    }
    RESET = "\033[0m"

    def format(
        self, level: str, message: str, timestamp: datetime
    ) -> str:
        formatted_time = timestamp.strftime("%H:%M:%S")
        color = self.COLORS.get(level, "")
        text = f"[{level}] {formatted_time} - {message}"
        return f"{color}{text}{self.RESET}"


class FormatterFactory:
    """Фабрика форматерів із реєстрацією нових типів."""

    _formatters: dict[str, type[LogFormatter]] = {
        "plain": PlainFormatter,
        "json": JSONFormatter,
        "color": ColorFormatter,
    }

    @classmethod
    def register(
        cls, name: str, formatter_cls: type[LogFormatter]
    ):
        if not issubclass(formatter_cls, LogFormatter):
            raise TypeError(
                "Форматер повинен успадковувати LogFormatter"
            )
        cls._formatters[name] = formatter_cls

    @classmethod
    def create(cls, name: str) -> LogFormatter:
        if name not in cls._formatters:
            raise ValueError(f"Невідомий форматер: {name}")
        return cls._formatters[name]()

    @classmethod
    def available(cls) -> list[str]:
        return list(cls._formatters.keys())


class Logger(metaclass=SingletonMeta):
    """Логер із підтримкою рівнів та різних форматерів."""

    LEVELS = {
        "DEBUG": 0,
        "INFO": 1,
        "WARNING": 2,
        "ERROR": 3
    }

    def __init__(
        self,
        formatter_name: str = "plain",
        min_level: str = "DEBUG"
    ):
        if min_level not in self.LEVELS:
            raise ValueError(f"Невідомий рівень: {min_level}")

        self._formatter = FormatterFactory.create(formatter_name)
        self._min_level = min_level
        self._log_history: list[str] = []

    def set_formatter(self, name: str):
        self._formatter = FormatterFactory.create(name)

    def log(self, level: str, message: str):
        if level not in self.LEVELS:
            raise ValueError(f"Невідомий рівень: {level}")

        if self.LEVELS[level] < self.LEVELS[self._min_level]:
            return

        timestamp = datetime.now()
        formatted = self._formatter.format(
            level, message, timestamp
        )

        print(formatted)
        self._log_history.append(formatted)

    def debug(self, msg: str):
        self.log("DEBUG", msg)

    def info(self, msg: str):
        self.log("INFO", msg)

    def warning(self, msg: str):
        self.log("WARNING", msg)

    def error(self, msg: str):
        self.log("ERROR", msg)

    def get_history(self) -> list[str]:
        return self._log_history[:]


def main():
    print("=== 1. Перевірка Singleton ===")

    logger1 = Logger("plain", "DEBUG")
    logger2 = Logger("json", "INFO")

    print(f"Singleton: {logger1 is logger2}")
    print(f"ID першого логера: {id(logger1)}")
    print(f"ID другого логера: {id(logger2)}")

    print("\n=== 2. Звичайне логування ===")
    logger1.debug("Початок діагностики")
    logger1.info("Система запущена")
    logger1.warning("Мало пам'яті")
    logger1.error("Помилка з'єднання")

    print("\n=== 3. JSON-формат ===")
    logger1.set_formatter("json")
    logger1.info("Форматування у JSON")

    print("\n=== 4. Кольоровий формат ===")
    logger1.set_formatter("color")
    logger1.warning("Попередження у кольоровому форматі")

    print("\n=== 5. Перевірка фабрики ===")
    print(f"Форматери: {FormatterFactory.available()}")

    print("\n=== 6. Реєстрація нового форматера ===")

    class ShortFormatter(LogFormatter):
        def format(
            self, level: str, message: str, timestamp: datetime
        ) -> str:
            return f"{level}: {message}"

    FormatterFactory.register("short", ShortFormatter)
    logger1.set_formatter("short")
    logger1.info("Новий форматер працює")

    print(f"Доступні форматери: {FormatterFactory.available()}")

    print("\n=== 7. Перевірка невідомого форматера ===")
    try:
        logger1.set_formatter("unknown")
    except ValueError as error:
        print(f"Очікувана помилка: {error}")

    print("\n=== 8. Історія повідомлень ===")
    history = logger1.get_history()

    for entry in history:
        print(entry)

    print(f"\nВсього записів: {len(history)}")


if __name__ == "__main__":
    main()
