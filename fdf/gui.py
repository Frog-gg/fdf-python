import pygame

from .model import Map
from .parser import parse_map
from .projection import Camera

# Цвета по умолчанию
BACKGROUND_COLOR = (30, 30, 30)  # Тёмно-серый фон
DEFAULT_LINE_COLOR = (255, 255, 255)  # Белый цвет для точек без цвета


def _parse_hex_color(hex_color: str) -> tuple[int, int, int]:
    """Преобразует строку цвета '#RRGGBB' в кортеж RGB для pygame."""
    # Убираем символ '#'
    hex_value = hex_color[1:]
    return (
        int(hex_value[0:2], 16),
        int(hex_value[2:4], 16),
        int(hex_value[4:6], 16),
    )


class App:
    """Главное приложение: инициализация окна, обработка событий и отрисовка."""

    def __init__(self, filepath: str) -> None:
        """Инициализирует pygame, парсит карту и создаёт камеру."""
        pygame.init()
        
        # Начальный размер окна
        self.window_width = 800
        self.window_height = 600
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
        pygame.display.set_caption("FdF — Каркасная 3D-модель")
        
        # Парсинг карты (исключение пробрасывается в main.py)
        self.map_object: Map = parse_map(filepath)
        
        # Создание камеры и автоматическое масштабирование
        self.camera = Camera()
        self.camera.fit(self.map_object, self.window_width, self.window_height)
        
        # Бонус: масштаб и сдвиг
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

    def run(self) -> int:
        """Главный цикл обработки событий. Возвращает код завершения."""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                        # Масштабирование (+ и -)
                    elif event.key == pygame.K_EQUALS:
                        self.scale *= 1.1
                    elif event.key == pygame.K_MINUS:
                        self.scale *= 0.9
                    # Сброс масштаба и сдвига (пробел)
                    elif event.key == pygame.K_SPACE:
                        self.scale = 1.0
                        self.offset_x = 0
                        self.offset_y = 0
                        self.camera.fit(self.map_object, self.window_width, self.window_height)
                    # Сдвиг карты (стрелки)
                    elif event.key == pygame.K_LEFT:
                        self.offset_x -= 20
                    elif event.key == pygame.K_RIGHT:
                        self.offset_x += 20
                    elif event.key == pygame.K_UP:
                        self.offset_y -= 20
                    elif event.key == pygame.K_DOWN:
                        self.offset_y += 20
                elif event.type == pygame.VIDEORESIZE:
                    # Перерисовка при изменении размера окна
                    self.window_width = event.w
                    self.window_height = event.h
                    self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
                    self.camera.fit(self.map_object, self.window_width, self.window_height)
            
            # Отрисовка
            self.screen.fill(BACKGROUND_COLOR)
            self.draw()
            pygame.display.flip()
        
        pygame.quit()
        return 0

    def draw(self) -> None:
        """Отрисовывает каркас: рёбра от каждой точки к соседней справа и снизу."""
        # Проходим по всем точкам карты
        for y_coordinate in range(self.map_object.height):
            for x_coordinate in range(self.map_object.width):
                current_point = self.map_object.get(x_coordinate, y_coordinate)
                
                # Проецируем текущую точку
                screen_x_current, screen_y_current = self.camera.project(current_point)
                screen_x_current = screen_x_current * self.scale + self.offset_x
                screen_y_current = screen_y_current * self.scale + self.offset_y
                
                # Определяем цвет текущей точки
                color_current = _parse_hex_color(current_point.color) if current_point.color else DEFAULT_LINE_COLOR
                
                # Рисуем ребро к соседней точке СПРАВА
                if x_coordinate + 1 < self.map_object.width:
                    right_point = self.map_object.get(x_coordinate + 1, y_coordinate)
                    screen_x_right, screen_y_right = self.camera.project(right_point)
                    screen_x_right = screen_x_right * self.scale + self.offset_x
                    screen_y_right = screen_y_right * self.scale + self.offset_y
                    
                    # Если цвета разные — можно сделать градиент (бонусное задание), 
                    # здесь рисуем цветом текущей точки
                    pygame.draw.line(
                        self.screen,
                        color_current,
                        (int(screen_x_current), int(screen_y_current)),
                        (int(screen_x_right), int(screen_y_right)),
                        1,
                    )
                
                # Рисуем ребро к соседней точке СНИЗУ
                if y_coordinate + 1 < self.map_object.height:
                    bottom_point = self.map_object.get(x_coordinate, y_coordinate + 1)
                    screen_x_bottom, screen_y_bottom = self.camera.project(bottom_point)
                    screen_x_bottom = screen_x_bottom * self.scale + self.offset_x
                    screen_y_bottom = screen_y_bottom * self.scale + self.offset_y
                    
                    pygame.draw.line(
                        self.screen,
                        color_current,
                        (int(screen_x_current), int(screen_y_current)),
                        (int(screen_x_bottom), int(screen_y_bottom)),
                        1,
                    )
