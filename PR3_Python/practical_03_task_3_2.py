
"""Паттерни Observer, Strategy та архітектурний шаблон MVC."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable


# --- Observer ---

class EventEmitter:
    """Базовий клас для системи подій."""

    def __init__(self):
        self._listeners: dict[str, list[Callable]] = {}

    def on(self, event: str, callback: Callable):
        """Підписатися на подію."""
        self._listeners.setdefault(event, []).append(callback)

    def off(self, event: str, callback: Callable):
        """Відписатися від події."""
        if event in self._listeners:
            if callback in self._listeners[event]:
                self._listeners[event].remove(callback)

    def emit(self, event: str, *args, **kwargs):
        """Повідомити всіх слухачів про подію."""
        for callback in self._listeners.get(event, [])[:]:
            callback(*args, **kwargs)


# --- Strategy ---

class SortStrategy(ABC):
    """Абстрактна стратегія сортування."""

    @abstractmethod
    def sort(self, tasks: list["Task"]) -> list["Task"]:
        """Повернути відсортований список завдань."""


class SortByPriority(SortStrategy):
    """Сортування за пріоритетом: 1 — найвищий."""

    def sort(self, tasks: list["Task"]) -> list["Task"]:
        return sorted(tasks, key=lambda task: task.priority)


class SortByDeadline(SortStrategy):
    """Сортування за найближчим терміном виконання."""

    def sort(self, tasks: list["Task"]) -> list["Task"]:
        return sorted(tasks, key=lambda task: task.deadline)


class SortByCreationDate(SortStrategy):
    """Сортування за датою створення, найновіші першими."""

    def sort(self, tasks: list["Task"]) -> list["Task"]:
        return sorted(
            tasks, key=lambda task: task.created_at, reverse=True
        )


# --- Model ---

@dataclass
class Task:
    """Модель окремого завдання."""

    title: str
    priority: int
    deadline: datetime
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)


class TaskModel(EventEmitter):
    """Model: зберігання завдань і бізнес-логіка."""

    def __init__(self):
        super().__init__()
        self._tasks: list[Task] = []

    def add_task(
        self, title: str, priority: int, deadline: datetime
    ):
        if not title.strip():
            raise ValueError("Назва завдання не може бути порожньою")

        if not 1 <= priority <= 5:
            raise ValueError("Пріоритет повинен бути від 1 до 5")

        task = Task(title, priority, deadline)
        self._tasks.append(task)
        self.emit("task_added", task)
        return task

    def complete_task(self, index: int):
        if not 0 <= index < len(self._tasks):
            raise IndexError("Неправильний індекс завдання")

        task = self._tasks[index]
        task.completed = True
        self.emit("task_completed", task)
        return task

    def remove_task(self, index: int):
        if not 0 <= index < len(self._tasks):
            raise IndexError("Неправильний індекс завдання")

        task = self._tasks.pop(index)
        self.emit("task_removed", task)
        return task

    def get_tasks(
        self, include_completed: bool = True
    ) -> list[Task]:
        if include_completed:
            return self._tasks.copy()

        return [
            task for task in self._tasks
            if not task.completed
        ]

    def get_statistics(self) -> dict:
        total = len(self._tasks)
        completed = sum(
            task.completed for task in self._tasks
        )

        return {
            "total": total,
            "completed": completed,
            "active": total - completed,
        }


# --- View ---

class TaskView:
    """View: відображення інформації в консолі."""

    def show_tasks(
        self, tasks: list[Task], title: str = "Завдання"
    ):
        print(f"\n{title}")
        print("-" * 80)
        print(
            f"{'№':<4} {'Назва':<25} "
            f"{'Пріоритет':<12} {'Дедлайн':<18} {'Статус'}"
        )
        print("-" * 80)

        if not tasks:
            print("Список завдань порожній")
            return

        for number, task in enumerate(tasks, start=1):
            status = "Виконано" if task.completed else "Активне"
            deadline = task.deadline.strftime("%d.%m.%Y")

            print(
                f"{number:<4} {task.title:<25} "
                f"{task.priority:<12} {deadline:<18} {status}"
            )

    def show_message(self, message: str):
        print(f"[INFO] {message}")

    def show_statistics(self, stats: dict):
        print("\nСтатистика завдань:")
        print(f"Всього: {stats['total']}")
        print(f"Виконано: {stats['completed']}")
        print(f"Активних: {stats['active']}")


# --- Controller ---

class TaskController:
    """Controller: координація Model, View та Strategy."""

    def __init__(self, model: TaskModel, view: TaskView):
        self._model = model
        self._view = view
        self._sort_strategy: SortStrategy = SortByPriority()

        self._model.on(
            "task_added",
            lambda task: self._view.show_message(
                f"Додано завдання: {task.title}"
            ),
        )

        self._model.on(
            "task_completed",
            lambda task: self._view.show_message(
                f"Виконано завдання: {task.title}"
            ),
        )

        self._model.on(
            "task_removed",
            lambda task: self._view.show_message(
                f"Видалено завдання: {task.title}"
            ),
        )

    def set_sort_strategy(self, strategy: SortStrategy):
        self._sort_strategy = strategy

    def add_task(
        self, title: str, priority: int, deadline: datetime
    ):
        return self._model.add_task(title, priority, deadline)

    def complete_task(self, index: int):
        return self._model.complete_task(index)

    def remove_task(self, index: int):
        return self._model.remove_task(index)

    def show_all(self):
        tasks = self._model.get_tasks()
        sorted_tasks = self._sort_strategy.sort(tasks)
        self._view.show_tasks(sorted_tasks)

    def show_active(self):
        tasks = self._model.get_tasks(include_completed=False)
        sorted_tasks = self._sort_strategy.sort(tasks)
        self._view.show_tasks(
            sorted_tasks, title="Активні завдання"
        )

    def show_stats(self):
        self._view.show_statistics(
            self._model.get_statistics()
        )


def main():
    model = TaskModel()
    view = TaskView()
    ctrl = TaskController(model, view)

    print("=== 1. Додавання завдань (Observer) ===")

    ctrl.add_task(
        "Написати звіт", 2, datetime(2026, 11, 15)
    )
    ctrl.add_task(
        "Підготувати презентацію", 4, datetime(2026, 11, 20)
    )
    ctrl.add_task(
        "Вивчити Python", 1, datetime(2026, 11, 18)
    )
    ctrl.add_task(
        "Перевірити код", 3, datetime(2026, 11, 12)
    )
    ctrl.add_task(
        "Завантажити на GitHub", 5, datetime(2026, 11, 10)
    )

    print("\n=== 2. Сортування за пріоритетом ===")
    ctrl.show_all()

    print("\n=== 3. Сортування за дедлайном ===")
    ctrl.set_sort_strategy(SortByDeadline())
    ctrl.show_all()

    print("\n=== 4. Сортування за датою створення ===")
    ctrl.set_sort_strategy(SortByCreationDate())
    ctrl.show_all()

    print("\n=== 5. Виконання завдання (Observer) ===")
    ctrl.complete_task(0)

    print("\n=== 6. Тільки активні завдання ===")
    ctrl.set_sort_strategy(SortByPriority())
    ctrl.show_active()

    print("\n=== 7. Статистика ===")
    ctrl.show_stats()

    print("\n=== 8. Видалення завдання (Observer) ===")
    ctrl.remove_task(1)
    ctrl.show_stats()

    print("\n=== 9. Перевірка методу off() ===")

    def temporary_listener(task):
        print(f"[TEST] Отримано подію: {task.title}")

    model.on("task_added", temporary_listener)
    model.off("task_added", temporary_listener)

    ctrl.add_task(
        "Перевірити Observer", 2, datetime(2026, 11, 25)
    )

    print("Тимчасового слухача успішно відписано")

    print("\n=== 10. Перевірка некоректного пріоритету ===")
    try:
        ctrl.add_task(
            "Некоректне завдання", 10, datetime(2026, 11, 30)
        )
    except ValueError as error:
        print(f"Очікувана помилка: {error}")

    print("\n=== Підсумкова статистика ===")
    ctrl.show_stats()


if __name__ == "__main__":
    main()
