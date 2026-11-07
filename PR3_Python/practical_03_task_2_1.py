
"""Декоратори функцій з параметрами."""

import functools
import time


def cache(max_size: int = 128):
    """Декоратор кешування результатів (LRU-кеш)."""

    if max_size < 1:
        raise ValueError("Розмір кешу повинен бути додатним")

    def decorator(func):
        _cache = {}
        _call_order = []

        @functools.wraps(func)
        def wrapper(*args):
            if args in _cache:
                print(f"cache hit: {func.__name__}{args}")
                _call_order.remove(args)
                _call_order.append(args)
                return _cache[args]

            print(f"cache miss: {func.__name__}{args}")
            result = func(*args)

            if len(_cache) >= max_size:
                oldest = _call_order.pop(0)
                del _cache[oldest]

            _cache[args] = result
            _call_order.append(args)
            return result

        wrapper.cache_info = lambda: {
            "size": len(_cache),
            "max_size": max_size
        }

        def cache_clear():
            _cache.clear()
            _call_order.clear()

        wrapper.cache_clear = cache_clear

        return wrapper

    return decorator


def rate_limit(max_calls: int, period: float = 60.0):
    """Обмеження кількості викликів за період часу."""

    if max_calls < 1 or period <= 0:
        raise ValueError("Параметри обмеження повинні бути додатними")

    def decorator(func):
        call_times = []

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.monotonic()

            call_times[:] = [
                t for t in call_times
                if current_time - t < period
            ]

            if len(call_times) >= max_calls:
                raise RuntimeError(
                    f"Перевищено ліміт: {max_calls} викликів "
                    f"за {period} секунд"
                )

            call_times.append(current_time)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log(level: str = "INFO"):
    """Логування викликів, результатів та помилок."""

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(
                f"[{level}] Виклик "
                f"{func.__name__}(args={args}, kwargs={kwargs})"
            )

            start_time = time.perf_counter()

            try:
                result = func(*args, **kwargs)

                elapsed = time.perf_counter() - start_time

                print(
                    f"[{level}] {func.__name__} -> {result} "
                    f"(час: {elapsed:.4f}с)"
                )

                return result

            except Exception as error:
                elapsed = time.perf_counter() - start_time

                print(
                    f"[ERROR] {func.__name__}: {error} "
                    f"(час: {elapsed:.4f}с)"
                )
                raise

        return wrapper

    return decorator


@cache(max_size=64)
def fibonacci(n: int) -> int:
    """Обчислює n-е число Фібоначчі рекурсивно."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


@rate_limit(max_calls=5, period=10.0)
def send_notification(message: str) -> str:
    """Імітує відправку сповіщення."""
    return f"Надіслано: {message}"


@log(level="DEBUG")
def divide(a: float, b: float) -> float:
    """Ділення з можливим ZeroDivisionError."""
    return a / b


def main():
    print("=== 1. Декоратор cache ===")

    result = fibonacci(30)
    print(f"fibonacci(30) = {result}")
    print(f"Інформація про кеш: {fibonacci.cache_info()}")

    print("\nПовторний виклик fibonacci(30):")
    result = fibonacci(30)
    print(f"Результат: {result}")
    print(f"Інформація про кеш: {fibonacci.cache_info()}")

    print("\n=== 2. Декоратор rate_limit ===")

    for i in range(1, 7):
        try:
            result = send_notification(f"Повідомлення {i}")
            print(f"Виклик {i}: {result}")
        except RuntimeError as error:
            print(f"Виклик {i}: {error}")

    print("\n=== 3. Декоратор log ===")

    print("\nКоректне ділення:")
    divide(10, 3)

    print("\nДілення на нуль:")
    try:
        divide(10, 0)
    except ZeroDivisionError:
        print("Помилку ZeroDivisionError успішно оброблено")

    print("\n=== Перевірка functools.wraps ===")
    print(f"Назва функції: {fibonacci.__name__}")
    print(f"Документація: {fibonacci.__doc__}")


if __name__ == "__main__":
    main()
