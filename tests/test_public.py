import os
import tempfile

import pytest

from fdf.model import Point
from fdf.parser import MapFormatError, parse_map
from fdf.projection import Camera


# Тест 1: размер карты 5x5
def test_elem_map_size():
    height_map = parse_map("maps/elem.fdf")
    assert height_map.width == 5
    assert height_map.height == 5


# Тест 2: высота центральной точки
def test_elem_center_height():
    height_map = parse_map("maps/elem.fdf")
    center_point = height_map.get(2, 2)
    assert center_point.z == 5


# Тест 3: координаты точек
def test_elem_point_coordinates():
    height_map = parse_map("maps/elem.fdf")
    top_left = height_map.get(0, 0)
    assert top_left.x == 0
    assert top_left.y == 0
    bottom_right = height_map.get(4, 4)
    assert bottom_right.x == 4
    assert bottom_right.y == 4


# Тест 4: ошибка формата - нечисловое значение
def test_invalid_number():
    with pytest.raises(MapFormatError):
        parse_map("maps/bad/invalid_number.fdf")


# Тест 5: ошибка формата - строки разной длины
def test_unequal_rows():
    with pytest.raises(MapFormatError):
        parse_map("maps/bad/unequal_rows.fdf")


# Тест 6: параметризация
@pytest.mark.parametrize("token,expected_z,expected_color", [
    ("7", 7, None),
    ("-3", -3, None),
    ("2,0xFF8800", 2, "#FF8800"),
    ("1,0xff", 1, "#0000FF"),
])
def test_parse_values(token, expected_z, expected_color):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.fdf', delete=False, encoding='utf-8') as tmp_file:
        tmp_file.write(token + "\n")
        tmp_path = tmp_file.name

    try:
        height_map = parse_map(tmp_path)
        point = height_map.get(0, 0)
        assert point.z == expected_z
        assert point.color == expected_color
    finally:
        os.unlink(tmp_path)


# Тест 7: проекция начала координат
def test_projection_origin():
    camera = Camera()
    point = Point(x=0, y=0, z=0)
    screen_x, screen_y = camera.project(point)
    assert screen_x == 0.0
    assert screen_y == 0.0


# Тест 8: проекция положительной высоты
def test_projection_positive_z():
    camera = Camera()
    point = Point(x=0, y=0, z=1)
    _, screen_y = camera.project(point)
    assert screen_y < 0


# Тест 9: fit помещает карту в окно
def test_camera_fit():
    height_map = parse_map("maps/elem.fdf")
    camera = Camera()
    camera.fit(height_map, 800, 600)

    for point in height_map:
        screen_x, screen_y = camera.project(point)
        assert 0 <= screen_x <= 800
        assert 0 <= screen_y <= 600


# Тест 10: методы модели
def test_model_methods():
    height_map = parse_map("maps/elem.fdf")
    assert len(height_map) == 25

    points_list = list(height_map)
    assert len(points_list) == 25

    neighbors = height_map.neighbors(0, 0)
    assert len(neighbors) == 2