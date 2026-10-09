from pathlib import Path

from .exceptions import MapFormatError
from .model import Map, Point


def _parse_color(color_str: str) -> str:
    """Парсит цвет из строки (например, 'FF0000' или 'ff') в формат '#RRGGBB'."""
    # Убираем '0x' или '0X', если они есть
    if color_str.lower().startswith('0x'):
        color_str = color_str[2:]
    
    try:
        val = int(color_str, 16)
    except ValueError:
        raise ValueError(f"некорректный цвет: {color_str}")
        
    # Форматируем в #RRGGBB в верхнем регистре
    return f"#{val:06X}"


def parse_map(filepath: str) -> Map:
    """Читает файл карты высот и возвращает объект Map."""
    path = Path(filepath)
    if not path.exists():
        raise OSError(f"Файл не найден: {filepath}")

    text = path.read_text(encoding='utf-8')

    lines = text.splitlines()
    
    # Игнорируем пустые строки в конце файла
    while lines and not lines[-1].strip():
        lines.pop()

    if not lines:
        raise MapFormatError(1, 1, "пустой файл")

    points: list[list[Point]] = []
    expected_width = -1

    for line_idx, line in enumerate(lines, start=1):
        tokens = line.split()
        if not tokens:
            # Пустая строка внутри карты — это ошибка формата
            raise MapFormatError(line_idx, 1, "пустая строка внутри карты")

        row: list[Point] = []
        for col_idx, token in enumerate(tokens, start=1):
            parts = token.split(',')
            if len(parts) > 2:
                raise MapFormatError(line_idx, col_idx, f"слишком много запятых в '{token}'")
            
            try:
                z = int(parts[0])
            except ValueError:
                raise MapFormatError(line_idx, col_idx, f"'{parts[0]}' — не целое число")
            
            color = None
            if len(parts) == 2:
                try:
                    color = _parse_color(parts[1])
                except ValueError:
                    raise MapFormatError(line_idx, col_idx, f"'{parts[1]}' — некорректный цвет")
            
            # x - это индекс колонки (с 0), y - индекс строки (с 0)
            row.append(Point(x=col_idx - 1, y=line_idx - 1, z=z, color=color))
        
        if expected_width == -1:
            expected_width = len(row)
        elif len(row) != expected_width:
            raise MapFormatError(line_idx, 1, f"строки разной длины: ожидалось {expected_width}, получено {len(row)}")
        
        points.append(row)

    return Map(points)