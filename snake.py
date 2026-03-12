import pygame
import random
from typing import List, Tuple, Set, Optional

# Константы
CELL_SIZE = 20
GRID_WIDTH = 32
GRID_HEIGHT = 24
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT
CENTER_X = (GRID_WIDTH // 2) * CELL_SIZE
CENTER_Y = (GRID_HEIGHT // 2) * CELL_SIZE

# Цвета в формате RGB
BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
PINK = (255, 150, 150)
BLUE = (0, 100, 255)

# Направления движения
DIRECTIONS = {
    pygame.K_UP: (0, -CELL_SIZE),
    pygame.K_DOWN: (0, CELL_SIZE),
    pygame.K_LEFT: (-CELL_SIZE, 0),
    pygame.K_RIGHT: (CELL_SIZE, 0)
}

# Все возможные клетки игрового поля
ALL_CELLS = {(x * CELL_SIZE, y * CELL_SIZE)
             for x in range(GRID_WIDTH)
             for y in range(GRID_HEIGHT)}


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, position: Tuple[int, int], color: Tuple[int, int, int]):
        """
        Инициализация игрового объекта.

        Args:
            position: Начальная позиция объекта (x, y)
            color: Цвет объекта в формате RGB
        """
        self.position = position
        self.color = color

    def draw_cell(self, surface: pygame.Surface, position: Tuple[int, int],
                  color: Tuple[int, int, int]) -> None:
        """
        Рисует одну ячейку на игровом поле.

        Args:
            surface: Поверхность для отрисовки
            position: Позиция ячейки (x, y)
            color: Цвет ячейки
        """
        rect = pygame.Rect(position[0], position[1], CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, color, rect)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Абстрактный метод для отрисовки объекта.
        Должен быть переопределен в дочерних классах.

        Args:
            surface: Поверхность для отрисовки
        """
        pass


class Apple(GameObject):
    """Класс, представляющий яблоко на игровом поле."""

    def __init__(self):
        """Инициализация яблока со случайной позицией."""
        super().__init__((0, 0), RED)
        self.randomize_position(set())

    def randomize_position(self, occupied_cells: Set[Tuple[int, int]]) -> None:
        """
        Устанавливает случайную позицию яблока, не занятую змейкой.

        Args:
            occupied_cells: Множество занятых клеток
        """
        available_cells = ALL_CELLS - occupied_cells
        if available_cells:
            self.position = random.choice(tuple(available_cells))

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает яблоко на игровой поверхности."""
        self.draw_cell(surface, self.position, self.color)


class Snake(GameObject):
    """Класс, представляющий змейку."""

    def __init__(self):
        """Инициализация змейки в начальном состоянии."""
        super().__init__((CENTER_X, CENTER_Y), GREEN)

        self.positions: List[Tuple[int, int]] = [(CENTER_X, CENTER_Y)]
        self.direction = DIRECTIONS[pygame.K_RIGHT]
        self.next_direction: Optional[Tuple[int, int]] = None
        self.length = 1
        self.last_position: Optional[Tuple[int, int]] = None
        self.grew = False

    def update_direction(self, new_direction: Tuple[int, int]) -> None:
        """
        Обновляет направление движения змейки.
        Запрещает движение в противоположном направлении.

        Args:
            new_direction: Новое направление движения (dx, dy)
        """
        opposite_direction = (new_direction[0] * -1, new_direction[1] * -1)
        if opposite_direction != self.direction:
            self.next_direction = new_direction

    def move(self) -> None:
        """
        Обновляет позицию змейки:
        - Добавляет новую голову
        - Удаляет хвост, если длина не увеличилась
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

        head_x, head_y = self.get_head_position()
        new_head = (
            (head_x + self.direction[0]) % SCREEN_WIDTH,
            (head_y + self.direction[1]) % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_head)
        self.grew = False

        if len(self.positions) > self.length:
            self.last_position = self.positions.pop()
        else:
            self.last_position = None
            self.grew = True

    def draw(self, surface: pygame.Surface) -> None:
        """
        Отрисовывает змейку на игровой поверхности.

        Args:
            surface: Поверхность для отрисовки
        """
        if self.positions:
            self._draw_head(surface, self.positions[0])

            for position in self.positions[1:]:
                self.draw_cell(surface, position, self.color)

        if self.last_position and not self.grew:
            self.draw_cell(surface, self.last_position, BLACK)

    def _draw_head(self, surface: pygame.Surface, position: Tuple[int, int]) -> None:
        """
        Рисует голову змейки с глазами и языком.

        Args:
            surface: Поверхность для отрисовки
            position: Позиция головы
        """
        head_x, head_y = position

        self.draw_cell(surface, position, DARK_GREEN)

        eye1_pos, eye2_pos, tongue_points = self._get_head_features(head_x, head_y)

        self._draw_eyes(surface, eye1_pos, eye2_pos)
        pygame.draw.polygon(surface, PINK, tongue_points)

    def _get_head_features(self, head_x: int, head_y: int) -> Tuple[
            Tuple[int, int], Tuple[int, int], List[Tuple[int, int]]]:
        """
        Возвращает позиции глаз и точки языка в зависимости от направления.

        Args:
            head_x: X координата головы
            head_y: Y координата головы

        Returns:
            Кортеж с позициями глаз и списком точек языка
        """
        if self.direction == DIRECTIONS[pygame.K_RIGHT]:
            eye1 = (head_x + 12, head_y + 5)
            eye2 = (head_x + 12, head_y + 15)
            tongue = [
                (head_x + 18, head_y + 8),
                (head_x + 22, head_y + 10),
                (head_x + 18, head_y + 12)
            ]
        elif self.direction == DIRECTIONS[pygame.K_LEFT]:
            eye1 = (head_x + 8, head_y + 5)
            eye2 = (head_x + 8, head_y + 15)
            tongue = [
                (head_x + 2, head_y + 8),
                (head_x - 2, head_y + 10),
                (head_x + 2, head_y + 12)
            ]
        elif self.direction == DIRECTIONS[pygame.K_UP]:
            eye1 = (head_x + 5, head_y + 8)
            eye2 = (head_x + 15, head_y + 8)
            tongue = [
                (head_x + 8, head_y + 2),
                (head_x + 12, head_y + 2),
                (head_x + 10, head_y - 2)
            ]
        else:
            eye1 = (head_x + 5, head_y + 12)
            eye2 = (head_x + 15, head_y + 12)
            tongue = [
                (head_x + 8, head_y + 18),
                (head_x + 12, head_y + 18),
                (head_x + 10, head_y + 22)
            ]

        return eye1, eye2, tongue

    def _draw_eyes(self, surface: pygame.Surface,
                   eye1_pos: Tuple[int, int],
                   eye2_pos: Tuple[int, int]) -> None:
        """
        Рисует глаза змейки.

        Args:
            surface: Поверхность для отрисовки
            eye1_pos: Позиция первого глаза
            eye2_pos: Позиция второго глаза
        """
        pygame.draw.circle(surface, WHITE, eye1_pos, 3)
        pygame.draw.circle(surface, WHITE, eye2_pos, 3)
        pygame.draw.circle(surface, BLUE, eye1_pos, 2)
        pygame.draw.circle(surface, BLUE, eye2_pos, 2)
        pygame.draw.circle(surface, BLACK, eye1_pos, 1)
        pygame.draw.circle(surface, BLACK, eye2_pos, 1)

    def get_head_position(self) -> Tuple[int, int]:
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def get_occupied_cells(self) -> Set[Tuple[int, int]]:
        """Возвращает множество клеток, занятых змейкой."""
        return set(self.positions)

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        self.positions = [(CENTER_X, CENTER_Y)]
        self.direction = DIRECTIONS[pygame.K_RIGHT]
        self.next_direction = None
        self.length = 1
        self.last_position = None

    def check_self_collision(self) -> bool:
        """
        Проверяет, не столкнулась ли змейка сама с собой.

        Returns:
            True, если голова столкнулась с телом, иначе False
        """
        if len(self.positions) < 3:
            return False

        head = self.get_head_position()
        return head in self.positions[1:]


def handle_keys(snake: Snake) -> bool:
    """
    Обрабатывает нажатия клавиш для управления змейкой.

    Args:
        snake: Объект змейки для изменения направления

    Returns:
        False, если игра должна завершиться, иначе True
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            elif event.key in DIRECTIONS:
                snake.update_direction(DIRECTIONS[event.key])
    return True


def main() -> None:
    """Основной игровой цикл."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Змейка")
    clock = pygame.time.Clock()

    snake = Snake()
    apple = Apple()
    record_length = 1

    running = True
    while running:
        clock.tick(7)

        running = handle_keys(snake)
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            if snake.length > record_length:
                record_length = snake.length
                pygame.display.set_caption(f"Змейка (Рекорд: {record_length})")

            apple.randomize_position(snake.get_occupied_cells())

        if snake.check_self_collision():
            snake.reset()
            apple.randomize_position(snake.get_occupied_cells())

        screen.fill(BLACK)
        snake.draw(screen)
        apple.draw(screen)

        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
