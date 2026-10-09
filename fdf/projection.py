import math

from .model import Map, Point

# Константы для изометрической проекции (угол 30 градусов)
COS_30_DEGREES = math.cos(math.radians(30))
SIN_30_DEGREES = math.sin(math.radians(30))


class Camera:
    """Камера для проецирования 3D-точек на 2D-экран."""

    def __init__(self) -> None:
        self.scale: float = 1.0
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0
        self.z_scale: float = 1.0

    def project(self, point: Point) -> tuple[float, float]:
        """Проецирует 3D-точку на 2D-плоскость в изометрической проекции.

        Формулы:
            x_prime = (x - y) * cos(30°)
            y_prime = (x + y) * sin(30°) - z * z_scale
            X = x_prime * scale + offset_x
            Y = y_prime * scale + offset_y
        """
        x_coordinate = point.x
        y_coordinate = point.y
        z_coordinate = point.z

        x_prime = (x_coordinate - y_coordinate) * COS_30_DEGREES
        y_prime = (x_coordinate + y_coordinate) * SIN_30_DEGREES - z_coordinate * self.z_scale

        screen_x = x_prime * self.scale + self.offset_x
        screen_y = y_prime * self.scale + self.offset_y

        return screen_x, screen_y

    def fit(self, map_object: Map, window_width: int, window_height: int) -> None:
        """Автоматически масштабирует и центрирует карту в окне.

        Алгоритм:
        1. Проецируем все точки при scale=1 и нулевом смещении
        2. Находим min/max по каждой оси
        3. scale = min(window_width/map_width, window_height/map_height) * 0.9
        4. Смещение центрирует карту
        """

        # Сбрасываем параметры для расчёта границ
        self.scale = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0

        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')

        for point in map_object:
            screen_x, screen_y = self.project(point)
            min_x = min(min_x, screen_x)
            max_x = max(max_x, screen_x)
            min_y = min(min_y, screen_y)
            max_y = max(max_y, screen_y)

        map_width = max_x - min_x
        map_height = max_y - min_y

        # Вычисляем масштаб с отступом 0.9 от краёв окна
        if map_width > 0 and map_height > 0:
            scale_by_width = (window_width / map_width) * 0.9
            scale_by_height = (window_height / map_height) * 0.9
            self.scale = min(scale_by_width, scale_by_height)
        else:
            self.scale = 1.0

        # Вычисляем центр карты и центрируем её в окне
        center_map_x = (min_x + max_x) / 2.0
        center_map_y = (min_y + max_y) / 2.0

        self.offset_x = (window_width / 2.0) - (center_map_x * self.scale)
        self.offset_y = (window_height / 2.0) - (center_map_y * self.scale)