import pygame
from sys import exit
from os import path
from random import sample
from time import perf_counter

pygame.init()
screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()

# переменные, значения которых изменятся в функциях
tile_images, guy_image, bull_image, tile_width, \
    tile_height, guy, bull, all_sprites, tiles_group, \
    characters_group, level_x, level_y, directions, bull_doings, lvl_map = [None for _ in range(15)]


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
            four_random_box_places_on_line = sample(a, len(a))[:3]
            for ind in four_random_box_places_on_line:
                line[ind] = '#'
            line += '\n'
            if i == 5:
                line[5] = '@'
            elif i in [4, 3, 6, 7]:
                line[5] = '.'
            elif i == 8:
                line[5] = '*'
            line = ''.join(line)
            map_file.write(line)


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
    fon = pygame.transform.scale(load_image('game over.jpg'), (500, 500))
    screen.blit(fon, (0, 0))

    pygame.display.flip()


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

    # вернем игрока и быка, а также размер поля в клетках
    return the_guy, the_bull, x, y


def terminate():  # if event.type == pygame.QUIT:
    pygame.quit()
    exit()


def main_generation():
    global tile_height, tile_images, tile_width, \
        guy_image, guy, bull, bull_doings, bull_image, \
        all_sprites, level_x, level_y, directions, characters_group, tiles_group, lvl_map
    generate_map()

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

    lvl_map = load_level('map.txt')
    guy, bull, level_x, level_y = generate_level(lvl_map)

    '''belongs to main'''
    directions = ['up', 'up']  # для того чтобы определить, в какую сторону скользить

    # список действий быка
    # запас хода быка по вертикали в две клетки (100 пикселей), т.к в начале игры между игроком и быком это расстояние
    bull_doings = ['bull.rect.y - 1' for _ in range(150)]


def writing_round(n):
    font = pygame.font.Font(None, 80)

    string_rendered = font.render(f'Round {n}', 1, pygame.Color((194, 24, 7)))
    screen.blit(string_rendered, (140, 210))


def main(ss):
    main_generation()

    camera = Camera()
    start_screen()
    start_screen_ends = ss

    # для правильной работы камеры
    guy_x = guy.rect.x
    guy_y = guy.rect.y

    # флаги направления игрока
    up, down, right, left = True, False, False, False

    sliding = False  # флаг скольжения

    c = 0  # счётчик

    write = False  # флаг на перезапись рекорда

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            if event.type == pygame.KEYDOWN:
                start_screen_ends = True
                if not c:
                    start_time = perf_counter()
                    c += 1

                    screen.fill('black')
                    writing_round(c)
                    pygame.display.flip()
                    pygame.time.wait(1000)

                    continue

                if len(directions) > 2:  # (or == 3) для меньшего расхода памяти (если, бы игра длилась долго...)
                    del directions[0]

                if event.key == pygame.K_UP:  # ВВЕРХ
                    up, down, right, left = True, False, False, False

                    directions.append('up')
                    if directions[-2] == 'up':
                        del directions[-2]

                elif event.key == pygame.K_DOWN:  # ВНИЗ
                    up, down, right, left = False, True, False, False

                    directions.append('down')
                    if directions[-2] == 'down':
                        del directions[-2]

                elif event.key == pygame.K_RIGHT:  # ВПРАВО
                    up, down, right, left = False, False, True, False

                    directions.append('right')
                    if directions[-2] == 'right':
                        del directions[-2]

                elif event.key == pygame.K_LEFT:  # ВЛЕВО
                    up, down, right, left = False, False, False, True

                    directions.append('left')
                    if directions[-2] == 'left':
                        del directions[-2]

        if start_screen_ends:
            if up:  # ВВЕРХ

                # действия игрока
                if guy_y > 0:
                    if guy_x % tile_width == 0:
                        if lvl_map[(guy_y - 1) // tile_height][guy_x // tile_width] != '#':
                            guy.rect.y -= 1
                            guy_y -= 1

                            bull_doings.append('bull.rect.y - 1')
                            sliding = False

                        else:  # скольжение
                            sliding = True
                            if directions[-2] == 'right' or directions[-2] == 'down':
                                if guy_x < 500:
                                    if lvl_map[guy_y // tile_height][(guy_x + tile_width) // tile_width] != '#':
                                        guy.rect.x += 1
                                        guy_x += 1

                                        bull_doings.append('bull.rect.x + 1')
                            else:
                                if guy_x > 0:
                                    if lvl_map[guy_y // tile_height][(guy_x - 1) // tile_width] != '#':
                                        guy.rect.x -= 1
                                        guy_x -= 1

                                        bull_doings.append('bull.rect.x - 1')

                    else:
                        if lvl_map[(guy_y - 1) // tile_height][guy_x // tile_width] != '#' and \
                                lvl_map[(guy_y - 1) // tile_height][guy_x // tile_width + 1] != '#':
                            guy.rect.y -= 1
                            guy_y -= 1

                            bull_doings.append('bull.rect.y - 1')
                            sliding = False

                        else:  # скольжение
                            sliding = True
                            if directions[-2] == 'right' or directions[-2] == 'down':
                                if guy_x < 500:
                                    if lvl_map[guy_y // tile_height][(guy_x + tile_width) // tile_width] != '#':
                                        guy.rect.x += 1
                                        guy_x += 1

                                        bull_doings.append('bull.rect.x + 1')
                            else:
                                if guy_x > 0:
                                    if lvl_map[guy_y // tile_height][(guy_x - 1) // tile_width] != '#':
                                        guy.rect.x -= 1
                                        guy_x -= 1

                                        bull_doings.append('bull.rect.x - 1')

            elif down:  # ВНИЗ

                # действия игрока
                if guy_y < 500:
                    if guy_x % tile_width == 0:
                        if lvl_map[(guy_y + tile_height) // tile_height][guy_x // tile_width] != '#':
                            guy.rect.y += 1
                            guy_y += 1

                            bull_doings.append('bull.rect.y + 1')
                            sliding = False

                        else:  # скольжение
                            sliding = True
                            if directions[-2] == 'right' or directions[-2] == 'down':
                                if guy_x < 500:
                                    if lvl_map[guy_y // tile_height][(guy_x + tile_width) // tile_width] != '#':
                                        guy.rect.x += 1
                                        guy_x += 1

                                        bull_doings.append('bull.rect.x + 1')
                            else:
                                if guy_x > 0:
                                    if lvl_map[guy_y // tile_height][(guy_x - 1) // tile_width] != '#':
                                        guy.rect.x -= 1
                                        guy_x -= 1

                                        bull_doings.append('bull.rect.x - 1')

                    else:
                        if lvl_map[(guy_y + tile_height) // tile_height][guy_x // tile_width] != '#' and \
                                lvl_map[(guy_y + tile_height) // tile_height][guy_x // tile_width + 1] != '#':
                            guy.rect.y += 1
                            guy_y += 1

                            bull_doings.append('bull.rect.y + 1')
                            sliding = False

                        else:  # скольжение
                            sliding = True
                            if directions[-2] == 'right' or directions[-2] == 'down':
                                if guy_x < 500:
                                    if lvl_map[guy_y // tile_height][(guy_x + tile_width) // tile_width] != '#':
                                        guy.rect.x += 1
                                        guy_x += 1

                                        bull_doings.append('bull.rect.x + 1')
                            else:
                                if guy_x > 0:
                                    if lvl_map[guy_y // tile_height][(guy_x - 1) // tile_width] != '#':
                                        guy.rect.x -= 1
                                        guy_x -= 1

                                        bull_doings.append('bull.rect.x - 1')

            elif right:  # ВПРАВО

                # действия игрока
                if guy_x < 500:
                    if guy_y % tile_height == 0:
                        if lvl_map[guy_y // tile_height][(guy_x + tile_width) // tile_width] != '#':
                            guy.rect.x += 1
                            guy_x += 1

                            bull_doings.append('bull.rect.x + 1')
                            sliding = False

                        else:  # скольжение
                            sliding = True
                            if directions[-2] == 'up' or directions[-2] == 'left':
                                if guy_y > 0:
                                    if lvl_map[(guy_y - 1) // tile_height][guy_x // tile_width] != '#':
                                        guy.rect.y -= 1
                                        guy_y -= 1

                                        bull_doings.append('bull.rect.y - 1')
                            else:
                                if guy_y < 500:
                                    if lvl_map[(guy_y + tile_height) // tile_height][guy_x // tile_width] != '#':
                                        guy.rect.y += 1
                                        guy_y += 1

                                        bull_doings.append('bull.rect.y + 1')

                    else:
                        if lvl_map[guy_y // tile_height][(guy_x + tile_width) // tile_width] != '#' and \
                                lvl_map[guy_y // tile_height + 1][(guy_x + tile_width) // tile_width] != '#':
                            guy.rect.x += 1
                            guy_x += 1

                            bull_doings.append('bull.rect.x + 1')
                            sliding = False

                        else:  # скольжение
                            sliding = True
                            if directions[-2] == 'up' or directions[-2] == 'left':
                                if guy_y > 0:
                                    if lvl_map[(guy_y - 1) // tile_height][guy_x // tile_width] != '#':
                                        guy.rect.y -= 1
                                        guy_y -= 1

                                        bull_doings.append('bull.rect.y - 1')
                            else:
                                if guy_y < 500:
                                    if lvl_map[(guy_y + tile_height) // tile_height][guy_x // tile_width] != '#':
                                        guy.rect.y += 1
                                        guy_y += 1

                                        bull_doings.append('bull.rect.y + 1')

            elif left:  # ВЛЕВО

                # действия игрока
                if guy_x > 0:
                    if guy_y % tile_height == 0:
                        if lvl_map[guy_y // tile_height][(guy_x - 1) // tile_width] != '#':
                            guy.rect.x -= 1
                            guy_x -= 1

                            bull_doings.append('bull.rect.x - 1')
                            sliding = False

                        else:  # скольжение
                            sliding = True
                            if directions[-2] == 'up' or directions[-2] == 'left':
                                if guy_y > 0:
                                    if lvl_map[(guy_y - 1) // tile_height][guy_x // tile_width] != '#':
                                        guy.rect.y -= 1
                                        guy_y -= 1

                                        bull_doings.append('bull.rect.y - 1')
                            else:
                                if guy_y < 500:
                                    if lvl_map[(guy_y + tile_height) // tile_height][guy_x // tile_width] != '#':
                                        guy.rect.y += 1
                                        guy_y += 1

                                        bull_doings.append('bull.rect.y + 1')

                    else:
                        if lvl_map[guy_y // tile_height][(guy_x - 1) // tile_width] != '#' and \
                                lvl_map[guy_y // tile_height + 1][(guy_x - 1) // tile_width] != '#':
                            guy.rect.x -= 1
                            guy_x -= 1

                            bull_doings.append('bull.rect.x - 1')
                            sliding = False

                        else:  # скольжение
                            sliding = True
                            if directions[-2] == 'up' or directions[-2] == 'left':
                                if guy_y > 0:
                                    if lvl_map[(guy_y - 1) // tile_height][guy_x // tile_width] != '#':
                                        guy.rect.y -= 1
                                        guy_y -= 1

                                        bull_doings.append('bull.rect.y - 1')
                            else:
                                if guy_y < 500:
                                    if lvl_map[(guy_y + tile_height) // tile_height][guy_x // tile_width] != '#':
                                        guy.rect.y += 1
                                        guy_y += 1

                                        bull_doings.append('bull.rect.y + 1')

            # движение быка
            # тут могла быть рекурсия
            if 'y' in bull_doings[0]:
                bull.rect.y = eval(bull_doings.pop(0))
                if sliding:
                    if 'y' in bull_doings[0]:
                        bull.rect.y = eval(bull_doings.pop(0))
                    else:
                        bull.rect.x = eval(bull_doings.pop(0))
            else:  # elif 'x' in bull_doings[0]
                bull.rect.x = eval(bull_doings.pop(0))
                if sliding:
                    if 'y' in bull_doings[0]:
                        bull.rect.y = eval(bull_doings.pop(0))
                    else:
                        bull.rect.x = eval(bull_doings.pop(0))

            # изменяем ракурс камеры
            camera.update(guy)
            # обновляем положение всех спрайтов
            for sprite in all_sprites:
                camera.apply(sprite)

            screen.fill('black')
            tiles_group.draw(screen)
            characters_group.draw(screen)
            if not sliding:  # normally
                clock.tick(150)
            else:
                clock.tick(75)

            # проверка на столконовение
            collide = bull.rect.colliderect(guy.rect)
            if collide:
                pygame.display.flip()
                # на счёт рекорда
                with open('data/record.txt', mode='r', encoding='utf-8') as file_with_record:
                    if c > int(file_with_record.readline().strip()):  # побит ли предыдущий рекорд
                        write = True
                if write:
                    with open('data/record.txt', mode='w', encoding='utf-8') as file_with_record:
                        file_with_record.write(str(c))

                while True:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            terminate()
                        # if event.type == pygame.KEYDOWN:
                        #    main(True)
                    final_screen()

            if (perf_counter() - start_time).__round__() == 15 * c:
                c += 1

                screen.fill('black')
                writing_round(c)
                pygame.display.flip()
                pygame.time.wait(1000)

                main_generation()
                # для правильной работы камеры
                guy_x = guy.rect.x
                guy_y = guy.rect.y

                # флаги направления игрока
                up, down, right, left = True, False, False, False

                sliding = False  # флаг скольжения
                continue

        pygame.display.flip()

    terminate()


if __name__ == '__main__':
    main(False)
