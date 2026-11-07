
"""Типізовані дескриптори та __init_subclass__ для системи конфігурації."""


class ValidatedField:
    """Дескриптор із перевіркою типу та діапазону значень."""

    def __init__(self, expected_type: type, min_value=None, max_value=None):
        self.expected_type = expected_type
        self.min_value = min_value
        self.max_value = max_value

    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private_name, None)

    def __set__(self, obj, value):
        if type(value) is not self.expected_type:
            raise TypeError(
                f"Поле '{self.name}' повинно мати тип "
                f"{self.expected_type.__name__}"
            )

        if self.min_value is not None and value < self.min_value:
            raise ValueError(
                f"Поле '{self.name}' повинно бути не менше {self.min_value}"
            )

        if self.max_value is not None and value > self.max_value:
            raise ValueError(
                f"Поле '{self.name}' повинно бути не більше {self.max_value}"
            )

        setattr(obj, self.private_name, value)


class ConfigSection:
    """Базовий клас із автоматичною реєстрацією секцій."""

    _sections: dict[str, type] = {}

    def __init_subclass__(cls, section_name: str = "", **kwargs):
        super().__init_subclass__(**kwargs)

        if section_name:
            if section_name in ConfigSection._sections:
                raise ValueError(
                    f"Секція '{section_name}' вже зареєстрована"
                )
            ConfigSection._sections[section_name] = cls

    @classmethod
    def get_section(cls, name: str):
        return cls._sections.get(name)

    @classmethod
    def list_sections(cls) -> list[str]:
        return list(cls._sections.keys())


class DatabaseConfig(ConfigSection, section_name="database"):
    host = ValidatedField(str)
    port = ValidatedField(int, min_value=1, max_value=65535)
    max_connections = ValidatedField(int, min_value=1, max_value=1000)

    def __init__(self, host: str, port: int, max_connections: int):
        self.host = host
        self.port = port
        self.max_connections = max_connections


class LoggingConfig(ConfigSection, section_name="logging"):
    level = ValidatedField(str)
    max_file_size_mb = ValidatedField(int, min_value=1, max_value=1024)

    def __init__(self, level: str, max_file_size_mb: int):
        self.level = level
        self.max_file_size_mb = max_file_size_mb


def main():
    print("Зареєстровані секції:")
    print(ConfigSection.list_sections())

    print("\nПеревірка отримання класу секції:")
    print(ConfigSection.get_section("database").__name__)
    print(ConfigSection.get_section("logging").__name__)

    print("\nСтворення конфігурації бази даних:")
    database = DatabaseConfig("localhost", 5432, 100)
    print(f"Host: {database.host}")
    print(f"Port: {database.port}")
    print(f"Max connections: {database.max_connections}")

    print("\nСтворення конфігурації логування:")
    logging = LoggingConfig("INFO", 50)
    print(f"Level: {logging.level}")
    print(f"Max file size: {logging.max_file_size_mb} MB")

    print("\nПеревірка неправильного типу:")
    try:
        database.port = "5432"
    except TypeError as error:
        print(f"Очікувана помилка TypeError: {error}")

    print("\nПеревірка виходу за межі діапазону:")
    try:
        database.port = 70000
    except ValueError as error:
        print(f"Очікувана помилка ValueError: {error}")

    print("\nПеревірка нижньої межі:")
    try:
        logging.max_file_size_mb = 0
    except ValueError as error:
        print(f"Очікувана помилка ValueError: {error}")


if __name__ == "__main__":
    main()
