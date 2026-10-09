class FdfError(Exception):
    """Базовое исключение для FdF."""


class MapFormatError(FdfError):
    def __init__(self, line: int, col: int, message: str):
        self.line = line
        self.col = col
        super().__init__(f"строка {line}, колонка {col}: {message}")