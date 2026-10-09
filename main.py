import sys

from fdf.exceptions import FdfError
from fdf.gui import App
from fdf.parser import parse_map


def main() -> int:
    """Точка входа в программу. Обрабатывает аргументы командной строки и ошибки."""
    
    # Проверка количества аргументов
    if len(sys.argv) != 2:
        print("Использование: python main.py <файл.fdf>", file=sys.stderr)
        return 2

    filepath = sys.argv[1]

    try:
        # Пытаемся прочитать и распарсить карту
        parse_map(filepath)
    except OSError as file_error:
        # Ошибка, если файл не найден или нет прав на чтение
        print(f"Ошибка файла: {file_error}", file=sys.stderr)
        return 1
    except FdfError as format_error:
        # Ошибка формата карты (неверные числа, цвета, разная длина строк)
        print(f"Ошибка формата: {format_error}", file=sys.stderr)
        return 1

    # Если всё хорошо, запускаем графическое приложение
    application = App(filepath)
    return application.run()


if __name__ == "__main__":
    sys.exit(main())