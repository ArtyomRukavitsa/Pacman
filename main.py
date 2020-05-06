import pygame
from random import randint
import os
from PyQt5.QtWidgets import QApplication, QInputDialog, QWidget, QTableWidgetItem
import sys

CHOOSE = ''  # Загрузить файл или новая генерация поля
COUNT = 0  # Счет игрока
all_sprites = pygame.sprite.Group()
banana = pygame.sprite.Group()


def lose():
    font = pygame.font.SysFont('Verdana', 60)
    text = font.render("Вы проиграли", 1, (100, 255, 100))
    screen.blit(text, (20, 30))


def win():
    font = pygame.font.SysFont('Verdana', 60)
    text = font.render("Вы выиграли", 1, (100, 255, 100))
    screen.blit(text, (20, 30))


def count():
    global COUNT
    font = pygame.font.SysFont('Verdana', 20)
    text = font.render(f"Счет: {COUNT}", 1, (100, 255, 100))
    screen.blit(text, (350, 10))


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


class Wall(SuperClass):
    def __init__(self, x, y):
        super().__init__(x, y)
        
    def draw(self):
        return '1'


class Empty(SuperClass):
    def __init__(self, x, y):
        super().__init__(x, y)

    def draw(self):
        return '0'


class Banana(SuperClass):
    def __init__(self, x, y):
        super().__init__(x, y)

    def draw(self):
        return '2'


class Creature(SuperClass):
    def __init__(self, x, y, v):
        super().__init__(x, y)
        self.v = v


class Pacman(Creature):
    def __init__(self, x, y, v):
        super().__init__(x, y, v)

    def move(self, board, x, y):
        new_x, new_y = self.x + x, self.y + y
        if 0 <= new_y <= board.width and 0 <= new_x <= board.height:
            if isinstance(board.board[new_y][new_x], Empty):
                board.board[new_y][new_x] = self
                board.board[self.y][self.x] = Empty(self.x, self.y)
                self.x, self.y = new_x, new_y
            elif isinstance(board.board[new_y][new_x], Banana):
                global COUNT
                board.board[new_y][new_x] = self
                board.board[self.y][self.x] = Empty(self.x, self.y)
                self.x, self.y = new_x, new_y
                COUNT += 100

    def draw(self):
        return 'P'


class Ghost(Creature):
    def __init__(self, x, y, v):
        super().__init__(x, y, v)

    def move(self, board):
        # 0 - вверх, 1 - вправо, 2 - вниз, 3 - влево
        while True:
            new_x, new_y = self.x, self.y
            direction = randint(0, 3)
            if direction == 0:
                new_y -= 1
            elif direction == 1:
                new_x += 1
            elif direction == 2:
                new_y += 1
            else:
                new_x -= 1
            if 0 <= new_y <= board.width and 0 <= new_x <= board.height:
                if isinstance(board.board[new_y][new_x], Empty):
                    board.board[new_y][new_x] = self
                    board.board[self.y][self.x] = Empty(self.x, self.y)
                    self.x, self.y = new_x, new_y
                    break

    def draw(self):
        return 'G'


class SmartGhost(Creature):
    def __init__(self, x, y, v):
        super().__init__(x, y, v)

    def move(self, board):
        new_x, new_y = self.x, self.y
        pacman = board.findPacman()
        if pacman.x > self.x:
            new_x += 1
        elif pacman.x == self.x:
            if pacman.y > self.y: new_y += 1
            else: new_y -= 1
        else:
            new_x -= 1
        if isinstance(board.board[new_y][new_x], Pacman):
            return True  # Съел Пакмана
        board.board[new_y][new_x] = self
        board.board[self.y][self.x] = Empty(self.x, self.y)
        self.x, self.y = new_x, new_y
        return False

    def draw(self):
        return 'S'


class CreatureSprite(pygame.sprite.Sprite):
    def __init__(self, board, image, x, y, v):
        super().__init__(all_sprites)
        self.x, self.y, self.v = x, y, v
        self.image = load_image(image)
        self.mw = self.image.get_width()
        self.mh = self.image.get_height()
        self.x = board.left + board.cell_size * x
        self.y = board.top + board.cell_size * y
        self.rect = self.image.get_rect().move(self.x, self.y)

    def moveSprite(self, x, y):
        self.x = board.left + board.cell_size * x
        self.y = board.top + board.cell_size * y
        self.rect = self.image.get_rect().move(self.x, self.y)


class BananaSprite(pygame.sprite.Sprite):
    def __init__(self, board, image, x, y):
        super().__init__(banana)
        self.x, self.y = x, y
        self.image = load_image(image)
        self.mw = self.image.get_width()
        self.mh = self.image.get_height()
        self.x = board.left + board.cell_size * x
        self.y = board.top + board.cell_size * y
        self.rect = self.image.get_rect().move(self.x, self.y)

    def update(self):
        if self.rect.colliderect(pacman_sprite.rect) or \
                self.rect.colliderect(ghost_sprite.rect) or \
                self.rect.colliderect(smartghost_sprite.rect):
            self.kill()


class Board:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[Empty(0, 0)] * width for _ in range(height)]
        self.left = 10
        self.top = 40
        self.cell_size = 30
        if CHOOSE == 'Новое поле':
            Board.generateBoard(self)
        else:
            Board.openBoard(self)

    # настройка внешнего вида
    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self):
        for i in range(self.width):
            for j in range(self.height):
                pygame.draw.rect(screen, (255, 255, 255),
                                 (self.left + i * self.cell_size,
                                  self.top + j * self.cell_size,
                                  self.cell_size, self.cell_size), 1)
                if isinstance(self.board[j][i], Wall):
                    pygame.draw.rect(screen, (255, 0, 255), (self.left + i * self.cell_size + 1,
                                                     self.top + j * self.cell_size + 1, self.cell_size - 2,
                                                     self.cell_size - 2), 0)

    def generateBoard(self):
        # Заполнение
        for i in range(self.width):
            for j in range(self.height):
                self.board[j][i] = Empty(i, j)

        x = randint(0, self.width - 1)
        y = randint(0, self.height - 1)
        self.board[y][x] = Pacman(x, y, 1)

        for i in range(30):
            while not isinstance(self.board[y][x], Empty):
                x = randint(0, self.width - 1)
                y = randint(0, self.height - 1)
            self.board[y][x] = Wall(x, y)

        while not isinstance(self.board[y][x], Empty):
            x = randint(0, self.width - 1)
            y = randint(0, self.height - 1)
        self.board[y][x] = Ghost(x, y, 1)

        while not isinstance(self.board[y][x], Empty):
            x = randint(0, self.width - 1)
            y = randint(0, self.height - 1)
        self.board[y][x] = SmartGhost(x, y, 1)

        for i in range(5):
            while not isinstance(self.board[y][x], Empty):
                x = randint(0, self.width - 1)
                y = randint(0, self.height - 1)
            self.board[y][x] = Banana(x, y)

    def findPacman(self):
        for i in range(self.width):
            for j in range(self.height):
                if isinstance(self.board[j][i], Pacman):
                    return self.board[j][i]

    def findGhost(self):
        for i in range(self.width):
            for j in range(self.height):
                if isinstance(self.board[j][i], Ghost):
                    return self.board[j][i]

    def findSmartGhost(self):
        for i in range(self.width):
            for j in range(self.height):
                if isinstance(self.board[j][i], SmartGhost):
                    return self.board[j][i]

    def findBanana(self):
        bananas = []
        for i in range(self.width):
            for j in range(self.height):
                if isinstance(self.board[j][i], Banana):
                    bananas.append(self.board[j][i])
        return bananas

    def openBoard(self):
        with open('game.txt', 'r', encoding='utf-8') as file:
            data = file.read().split('\n')
            for i in range(self.width):
                for j in range(self.height):
                    if data[j][i] == '0':
                        self.board[j][i] = Empty(i, j)
                    elif data[j][i] == '1':
                        self.board[j][i] = Wall(i, j)
                    elif data[j][i] == 'P':
                        self.board[j][i] = Pacman(i, j, 1)
                    elif data[j][i] == 'G':
                        self.board[j][i] = Ghost(i, j, 1)
                    elif data[j][i] == 'S':
                        self.board[j][i] = SmartGhost(i, j, 1)
                    elif data[j][i] == '2':
                        self.board[j][i] = Banana(i, j)
            global COUNT
            COUNT = int(data[-1])


# Диалоговое окно
class MyDialog(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        global CHOOSE
        CHOOSE, okBtnPressed = QInputDialog.getItem(self, "Новая игра",
                                               "Выберете поле",
                                               ("Последнее сохранение", "Новое поле"),
                                               1, False)
        if okBtnPressed:
            return


def move_all_creatures(board, x, y):
    global COUNT
    pacman.move(board, x, y)
    if COUNT == 200:
        return 'WIN'
    ghost.move(board)
    result = smartghost.move(board)
    if result:
        return 'LOSE'


def save(board):
    string = ''
    with open('game.txt', 'w', encoding='utf-8') as file:
        for line in board.board:
            for figure in line:
                string += figure.draw()
            string += '\n'
        file.write(string)
        global COUNT
        file.write(str(COUNT))


def cycle():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    res = move_all_creatures(board, -1, 0)
                    if res == 'LOSE':
                        return 'LOST'
                    elif res == 'WIN':
                        return 'WIN'
                elif event.key == pygame.K_RIGHT:
                    res = move_all_creatures(board, 1, 0)
                    if res == 'LOSE':
                        return 'LOST'
                    elif res == 'WIN':
                        return 'WIN'
                elif event.key == pygame.K_UP:
                    res = move_all_creatures(board, 0, -1)
                    if res == 'LOSE':
                        return 'LOST'
                    elif res == 'WIN':
                        return 'WIN'
                elif event.key == pygame.K_DOWN:
                    res = move_all_creatures(board, 0, 1)
                    if res == 'LOSE':
                        return 'LOST'
                    elif res == 'WIN':
                        return 'WIN'
                elif event.key == pygame.K_s:
                    save(board)
                pacman_sprite.moveSprite(pacman.x, pacman.y)
                ghost_sprite.moveSprite(ghost.x, ghost.y)
                smartghost_sprite.moveSprite(smartghost.x, smartghost.y)
        screen.fill((0, 0, 0))
        count()
        all_sprites.draw(screen)
        banana.update()
        banana.draw(screen)
        board.render()
        pygame.display.flip()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyDialog()

    pygame.init()
    size = width, height = 620, 650
    screen = pygame.display.set_mode(size)
    board = Board(20, 20)

    pacman = board.findPacman()
    ghost = board.findGhost()
    smartghost = board.findSmartGhost()
    bananas = board.findBanana()

    pacman_sprite = CreatureSprite(board, 'pacman.png', pacman.x, pacman.y, 1)
    ghost_sprite = CreatureSprite(board, 'ghost.png', ghost.x, ghost.y, 1)
    smartghost_sprite = CreatureSprite(board, 'smartghost.png', smartghost.x, smartghost.y, 1)
    for b in bananas:
        BananaSprite(board, 'food.jpg', b.x, b.y)
    result = cycle()
    if result == 'LOST':
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
            lose()
            pygame.display.flip()
    else:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
            win()
            pygame.display.flip()
    pygame.quit()