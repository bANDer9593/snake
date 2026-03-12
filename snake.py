import pygame
import random
from typing import List, Tuple, Optional

# Константы
CELL_SIZE = 20
GRID_WIDTH = 32
GRID_HEIGHT = 24
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT

# Цвета в формате RGB
BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 200, 0)
PINK = (255, 150, 150)
BLUE = (0, 100, 255)


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, position: Tuple[int, int],
                 color: Tuple[int, int, int]):
        self.position = position
        self.color = color

    def draw(self, surface: pygame.Surface) -> None:
        pass


class Apple(GameObject):
    """Класс, представляющий яблоко на игровом поле."""

    def __init__(self):
        super().__init__((0, 0), RED)
        self.randomize_position()

    def randomize_position(self) -> None:
        x = random.randint(0, GRID_WIDTH - 1) * CELL_SIZE
        y = random.randint(0, GRID_HEIGHT - 1) * CELL_SIZE
        self.position = (x, y)

    def draw(self, surface: pygame.Surface) -> None:
        rect = pygame.Rect(
            self.position[0],
            self.position[1],
            CELL_SIZE,
            CELL_SIZE
        )
        pygame.draw.rect(surface, self.color, rect)


class Snake(GameObject):
    """Класс, представляющий змейку."""

    def __init__(self):
        start_x = (GRID_WIDTH // 2) * CELL_SIZE
        start_y = (GRID_HEIGHT // 2) * CELL_SIZE
        super().__init__((start_x, start_y), GREEN)

        self.positions: List[Tuple[int, int]] = [(start_x, start_y)]
        self.direction = (CELL_SIZE, 0)
        self.next_direction: Optional[Tuple[int, int]] = None
        self.length = 1
        self.last_position: Optional[Tuple[int, int]] = None

    def update_direction(self, new_direction: Tuple[int, int]) -> None:
        opposite = (new_direction[0] * -1, new_direction[1] * -1)
        if opposite != self.direction:
            self.next_direction = new_direction

    def move(self) -> None:
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

        head_x, head_y = self.get_head_position()
        new_head = (
            (head_x + self.direction[0]) % SCREEN_WIDTH,
            (head_y + self.direction[1]) % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last_position = self.positions.pop()
        else:
            self.last_position = None

    def _draw_head(self, surface: pygame.Surface,
                   position: Tuple[int, int]) -> None:
        head_x, head_y = position
        head_rect = pygame.Rect(head_x, head_y, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, DARK_GREEN, head_rect)

        if self.direction == (CELL_SIZE, 0):
            eye1 = (head_x + 12, head_y + 5)
            eye2 = (head_x + 12, head_y + 15)
            tongue = [
                (head_x + 18, head_y + 8),
                (head_x + 22, head_y + 10),
                (head_x + 18, head_y + 12)
            ]
        elif self.direction == (-CELL_SIZE, 0):
            eye1 = (head_x + 8, head_y + 5)
            eye2 = (head_x + 8, head_y + 15)
            tongue = [
                (head_x + 2, head_y + 8),
                (head_x - 2, head_y + 10),
                (head_x + 2, head_y + 12)
            ]
        elif self.direction == (0, -CELL_SIZE):
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

        pygame.draw.circle(surface, WHITE, eye1, 3)
        pygame.draw.circle(surface, WHITE, eye2, 3)
        pygame.draw.circle(surface, BLUE, eye1, 2)
        pygame.draw.circle(surface, BLUE, eye2, 2)
        pygame.draw.circle(surface, BLACK, eye1, 1)
        pygame.draw.circle(surface, BLACK, eye2, 1)
        pygame.draw.polygon(surface, PINK, tongue)

    def draw(self, surface: pygame.Surface) -> None:
        for i, position in enumerate(self.positions):
            if i == 0:
                self._draw_head(surface, position)
            else:
                rect = pygame.Rect(
                    position[0],
                    position[1],
                    CELL_SIZE,
                    CELL_SIZE
                )
                pygame.draw.rect(surface, self.color, rect)

        if self.last_position:
            rect = pygame.Rect(
                self.last_position[0],
                self.last_position[1],
                CELL_SIZE,
                CELL_SIZE
            )
            pygame.draw.rect(surface, BLACK, rect)

    def get_head_position(self) -> Tuple[int, int]:
        return self.positions[0]

    def reset(self) -> None:
        start_x = (GRID_WIDTH // 2) * CELL_SIZE
        start_y = (GRID_HEIGHT // 2) * CELL_SIZE
        self.positions = [(start_x, start_y)]
        self.direction = (CELL_SIZE, 0)
        self.next_direction = None
        self.length = 1
        self.last_position = None

    def check_self_collision(self) -> bool:
        head = self.get_head_position()
        return head in self.positions[1:]


def handle_keys(snake: Snake) -> None:
    """Обрабатывает нажатия клавиш для управления змейкой."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                snake.update_direction((0, -CELL_SIZE))
            elif event.key == pygame.K_DOWN:
                snake.update_direction((0, CELL_SIZE))
            elif event.key == pygame.K_LEFT:
                snake.update_direction((-CELL_SIZE, 0))
            elif event.key == pygame.K_RIGHT:
                snake.update_direction((CELL_SIZE, 0))


def main() -> None:
    """Основной игровой цикл."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Змейка")
    clock = pygame.time.Clock()

    snake = Snake()
    apple = Apple()

    while True:
        clock.tick(5)

        handle_keys(snake)

        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position()
            while apple.position in snake.positions:
                apple.randomize_position()

        if snake.check_self_collision():
            snake.reset()
            apple.randomize_position()

        screen.fill(BLACK)
        snake.draw(screen)
        apple.draw(screen)

        pygame.display.update()


if __name__ == "__main__":
    main()