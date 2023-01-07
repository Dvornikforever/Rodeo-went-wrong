import pygame
from sys import exit
from os import path
from random import sample

pygame.init()
screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()


def generate_map():

    """''
    Условные обозначения карты:
    . - песок
    # - коробка
    @ - игрок
    * - бык
    ''"""

    with open('data/map.txt', mode='w', encoding='utf-8') as map_file:
        for i in range(11):
            line = ['.' for _ in range(11)]
            a = [n for n in range(11)]
            four_random_box_places_on_line = sample(a, len(a))[:2]
            for ind in four_random_box_places_on_line:
                line[ind] = '#'
            line += '\n'
            if i == 5:
                line[5] = '@'
            elif i == 7:
                line[5] = '*'
            line = ''.join(line)
            map_file.write(line)


generate_map()  # then change to changing every 15 seconds


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    return level_map


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Character(pygame.sprite.Sprite):
    def __init__(self, img, pos_x, pos_y):
        super().__init__(characters_group, all_sprites)
        self.image = img
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - 500 // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - 500 // 2)


def load_image(img, color_key=None):
    fullname = path.join('data', img)
    if not path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        exit()
    img = pygame.image.load(fullname)
    if color_key is not None:
        img = img.convert()
        if color_key == -1:
            color_key = img.get_at((0, 0))
        img.set_colorkey(color_key)
    else:
        img = img.convert_alpha()
    return img


tile_images = {
    'wall': pygame.transform.scale(load_image('box.png'), (50, 50)),
    'empty': pygame.transform.scale(load_image('sand.jpg'), (50, 50))
}
guy_image = pygame.transform.scale(load_image('guy_sprites.png'), (50, 50))
bull_image = pygame.transform.scale(load_image('bull_sprites.png'), (50, 50))

tile_width = tile_height = 50


# основные персонажи
guy = None
bull = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
characters_group = pygame.sprite.Group()


def start_screen():
    title = "               Rodeo went wrong"

    fon = pygame.transform.scale(load_image('start_screen.webp'), (500, 500))
    screen.blit(fon, (0, 0))

    # отрисовка рамки
    pygame.draw.rect(screen, 'black', (78, 10, 350, 90))
    pygame.draw.rect(screen, (205, 155, 29), (78, 10, 350, 90), 5)

    # шрифт
    font = pygame.font.Font(None, 50)

    string_rendered = font.render(title, 1, pygame.Color((205, 155, 29)))
    screen.blit(string_rendered, (-37, 35))


def final_screen():
    pass


def generate_level(level):
    the_guy, the_bull, x, y = None, None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                the_guy = Character(guy_image, x, y)
            elif level[y][x] == '*':
                Tile('empty', x, y)
                the_bull = Character(bull_image, x, y)

    # вернем игрока, а также размер поля в клетках
    return the_guy, the_bull, x, y


def terminate():  # if event.type == pygame.QUIT:
    pygame.quit()
    exit()


lvl_map = load_level('map.txt')
guy, bull, level_x, level_y = generate_level(load_level('map.txt'))


def check_if_reversed():
    pass


def main():
    camera = Camera()
    start_screen()
    start_screen_ends = False

    # для правильной работы камеры
    guy_x = guy.rect.x
    guy_y = guy.rect.y
    bull_x = bull.rect.x
    bull_y = bull.rect.y

    # флаги направления игрока
    up = True
    down = False
    right = False
    left = False

    directions = ['up']  # для того чтобы определить, в какую сторону скользить

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            if event.type == pygame.KEYDOWN:
                start_screen_ends = True
                if event.key == pygame.K_UP:  # ВВЕРХ
                    up = True
                    down = False
                    right = False
                    left = False

                    directions.append('up')

                elif event.key == pygame.K_DOWN:  # ВНИЗ
                    down = True
                    right = False
                    left = False
                    up = False

                    directions.append('down')

                elif event.key == pygame.K_RIGHT:  # ВПРАВО
                    right = True
                    left = False
                    up = False
                    down = False

                    directions.append('right')

                elif event.key == pygame.K_LEFT:  # ВЛЕВО
                    left = True
                    up = False
                    down = False
                    right = False

                    directions.append('left')

        if start_screen_ends:

            if up:  # ВВЕРХ
                if guy_y > 0:
                    if guy_x % tile_width == 0:
                        if lvl_map[(guy_y - 1) // tile_height][guy_x // tile_width] != '#':
                            guy.rect.y -= 1
                            guy_y -= 1

                    else:
                        if lvl_map[(guy_y - 1) // tile_height][guy_x // tile_width] != '#' and \
                                lvl_map[(guy_y - 1) // tile_height][guy_x // tile_width + 1] != '#':
                            guy.rect.y -= 1
                            guy_y -= 1

            elif down:  # ВНИЗ
                if guy_y < 500:
                    if guy_x % tile_width == 0:
                        if lvl_map[(guy_y + tile_height) // tile_height][guy_x // tile_width] != '#':
                            guy.rect.y += 1
                            guy_y += 1

                    else:
                        if lvl_map[(guy_y + tile_height) // tile_height][guy_x // tile_width] != '#' and\
                                lvl_map[(guy_y + tile_height) // tile_height][guy_x // tile_width + 1] != '#':
                            guy.rect.y += 1
                            guy_y += 1

            elif right:  # ВПРАВО
                if guy_x < 500:
                    if guy_y % tile_height == 0:
                        if lvl_map[guy_y // tile_height][(guy_x + tile_width) // tile_width] != '#':
                            guy.rect.x += 1
                            guy_x += 1

                    else:
                        if lvl_map[guy_y // tile_height][(guy_x + tile_width) // tile_width] != '#' and \
                                lvl_map[guy_y // tile_height + 1][(guy_x + tile_width) // tile_width] != '#':
                            guy.rect.x += 1
                            guy_x += 1

            elif left:  # ВЛЕВО
                if guy_x > 0:
                    if guy_y % tile_height == 0:
                        if lvl_map[guy_y // tile_height][(guy_x - 1) // tile_width] != '#':
                            guy.rect.x -= 1
                            guy_x -= 1

                    else:
                        if lvl_map[guy_y // tile_height][(guy_x - 1) // tile_width] != '#' and\
                                lvl_map[guy_y // tile_height + 1][(guy_x - 1) // tile_width] != '#':
                            guy.rect.x -= 1
                            guy_x -= 1

            # изменяем ракурс камеры
            camera.update(guy)
            # обновляем положение всех спрайтов
            for sprite in all_sprites:
                camera.apply(sprite)

            screen.fill('black')
            tiles_group.draw(screen)
            characters_group.draw(screen)
            clock.tick(200)
        pygame.display.flip()


if __name__ == '__main__':
    main()
