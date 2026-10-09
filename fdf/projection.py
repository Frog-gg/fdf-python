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
        # Углы вращения (в радианах)
        self.yaw: float = 0.0  # Поворот вокруг оси Y (влево/вправо)
        self.pitch: float = 0.0  # Наклон вокруг оси X (вперёд/назад)

    def project(self, point: Point) -> tuple[float, float]:
        """Проецирует 3D-точку на 2D-плоскость с вращением и изометрией."""
        x = point.x
        y = point.y
        z = point.z

        # Вращение вокруг оси Y (yaw)
        x_rot = x * math.cos(self.yaw) + z * math.sin(self.yaw)
        y_rot = y
        z_rot = -x * math.sin(self.yaw) + z * math.cos(self.yaw)

        # Вращение вокруг оси X (pitch)
        x_final = x_rot
        y_final = y_rot * math.cos(self.pitch) - z_rot * math.sin(self.pitch)
        z_final = y_rot * math.sin(self.pitch) + z_rot * math.cos(self.pitch)

        # Изометрическая проекция
        x_prime = (x_final - y_final) * COS_30_DEGREES
        y_prime = (x_final + y_final) * SIN_30_DEGREES - z_final * self.z_scale

        screen_x = x_prime * self.scale + self.offset_x
        screen_y = y_prime * self.scale + self.offset_y

        return screen_x, screen_y

    def fit(self, map_object: Map, window_width: int, window_height: int) -> None:
        """Автоматически масштабирует и центрирует карту в окне."""
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

        if map_width > 0 and map_height > 0:
            scale_by_width = (window_width / map_width) * 0.9
            scale_by_height = (window_height / map_height) * 0.9
            self.scale = min(scale_by_width, scale_by_height)
        else:
            self.scale = 1.0

        center_map_x = (min_x + max_x) / 2.0
        center_map_y = (min_y + max_y) / 2.0

        self.offset_x = (window_width / 2.0) - (center_map_x * self.scale)
        self.offset_y = (window_height / 2.0) - (center_map_y * self.scale)