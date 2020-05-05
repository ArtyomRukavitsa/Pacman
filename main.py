import pygame
from random import randint
import os

all_sprites = pygame.sprite.Group()


# Функция, отвечающая за загрузку изображения
def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    #image = image.convert_alpha()

    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


class SuperClass:
    def __init__(self, x, y):
        self.x, self.y = x, y

    def draw(self):
        pass


class Empty(SuperClass):
    def __init__(self, x, y):
        super().__init__(x, y)

    def draw(self):
        return '0'


class Creature(SuperClass):
    def __init__(self, x, y, v):
        super().__init__(x, y)
        self.v = v

    def draw(self):
        pass

    def move(self):
        pass


class Pacman(pygame.sprite.Sprite):
    def __init__(self, board, image, x, y, v):
        super().__init__(all_sprites)
        self.x, self.y, self.v = x, y, v
        self.image = load_image(image)
        self.mw = self.image.get_width()
        self.mh = self.image.get_height()
        self.x = board.top + board.cell_size * x
        self.y = board.left + board.cell_size * y
        self.rect = self.image.get_rect().move(self.x, self.y)

    def draw(self):
        return 'P'


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[Empty(0, 0)] * width for _ in range(height)]
        self.left = 10
        self.top = 10
        self.cell_size = 30
        Board.generateBoard(self)
        """По умолчанию пустые клетки """
        print(self.top)

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self):
        for i in range(self.width):
            for j in range(self.height):
                #arg = 0 if self.board[j][i].draw() == 'P' else 1
                pygame.draw.rect(screen, (255, 255, 255),
                                 (self.left + i * self.cell_size,
                                  self.top + j * self.cell_size,
                                  self.cell_size, self.cell_size), 1)

    def generateBoard(self):
        # Заполнение
        for i in range(self.width):
            for j in range(self.height):
                self.board[j][i] = Empty(i, j)

        x = randint(0, self.width - 1)
        y = randint(0, self.height - 1)
        self.board[y][x] = Pacman(self, 'pacman.png', x, y, 1)


pygame.init()
size = width, height = 470, 470
screen = pygame.display.set_mode(size)
board = Board(15, 15)
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    board.render()
    pygame.display.flip()
pygame.quit()