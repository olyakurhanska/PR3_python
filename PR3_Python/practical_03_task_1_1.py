"""Система плагінів з автоматичною реєстрацією через метаклас."""

from abc import ABCMeta, abstractmethod
import hashlib


class PluginMeta(ABCMeta):
    """Метаклас для реєстрації та перевірки плагінів."""

    _registry: dict[str, type] = {}
    REQUIRED_ATTRS = ("name", "version")

    def __new__(mcs, cls_name: str, bases: tuple, namespace: dict):
        cls = super().__new__(mcs, cls_name, bases, namespace)

        if bases:
            for attr in mcs.REQUIRED_ATTRS:
                if attr not in namespace:
                    raise TypeError(
                        f"Клас {cls_name} повинен визначати атрибут '{attr}'"
                    )

            plugin_name = namespace["name"]

            if plugin_name in mcs._registry:
                raise ValueError(
                    f"Плагін з назвою '{plugin_name}' вже зареєстрований"
                )

            mcs._registry[plugin_name] = cls

        return cls

    @classmethod
    def get_registry(mcs) -> dict[str, type]:
        """Повертає копію реєстру плагінів."""
        return mcs._registry.copy()

    @classmethod
    def create_plugin(mcs, plugin_name: str):
        """Створює екземпляр зареєстрованого плагіна."""
        if plugin_name not in mcs._registry:
            raise ValueError(f"Невідомий плагін: {plugin_name}")

        return mcs._registry[plugin_name]()


class BasePlugin(metaclass=PluginMeta):
    """Базовий клас плагіна."""

    @abstractmethod
    def execute(self, data: str) -> str:
        """Обробляє вхідний текст."""


class UpperPlugin(BasePlugin):
    name = "upper"
    version = "1.0"

    def execute(self, data: str) -> str:
        return data.upper()


class ReversePlugin(BasePlugin):
    name = "reverse"
    version = "1.0"

    def execute(self, data: str) -> str:
        return data[::-1]


class CensorPlugin(BasePlugin):
    name = "censor"
    version = "1.1"

    def __init__(self):
        self.words = ["Світ"]

    def execute(self, data: str) -> str:
        result = data

        for word in self.words:
            result = result.replace(word, "***")

        return result


def hash_execute(self, data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


HashPlugin = type(
    "HashPlugin",
    (BasePlugin,),
    {
        "__module__": __name__,
        "name": "hash",
        "version": "2.0",
        "execute": hash_execute,
    },
)


def main():
    print("Зареєстровані плагіни:")

    for name, cls in PluginMeta.get_registry().items():
        print(f"  {name} (v{cls.version}): {cls.__name__}")

    print("\nРезультати роботи плагінів:")

    test_data = "Привіт Світ"

    for name in PluginMeta.get_registry():
        plugin = PluginMeta.create_plugin(name)
        print(f"  {name}: {plugin.execute(test_data)}")

    print("\nПеревірка обов'язкових атрибутів:")

    try:
        class InvalidPlugin(BasePlugin):
            name = "invalid"

            def execute(self, data: str) -> str:
                return data

    except TypeError as error:
        print(f"  Очікувана помилка: {error}")


if __name__ == "__main__":
    main()