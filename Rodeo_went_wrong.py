import pygame
from sys import exit
from os import path
from random import sample, choice
from time import perf_counter

pygame.init()
screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()

pygame.display.set_caption('Rodeo went wrong')
icon = pygame.image.load('data/icn.webp')
pygame.display.set_icon(icon)

# переменные, значения которых изменятся в функциях
tile_images, guy_image, horse_image, tile_width, \
    tile_height, guy, horse, all_sprites, tiles_group, \
    characters_group, level_x, level_y, directions, horse_doings, lvl_map = [None for _ in range(15)]


def generate_map():
    """''
    Условные обозначения карты:
    . - песок
    # - коробка
    @ - игрок
    * - лошадь
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
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites, characters_group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 4
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)

        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, what_line, sprites_in_a_row, guy_goes_up=False):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        #  it was working without this condition wtf
        if guy_goes_up:
            self.image = self.frames[self.cur_frame % sprites_in_a_row + sprites_in_a_row * (what_line - 1) + 1]
        else:
            self.image = self.frames[self.cur_frame % sprites_in_a_row + sprites_in_a_row * (what_line - 1)]


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

    # отрисовка заднего фона
    fon = pygame.transform.scale(load_image('start_screen_horse.webp'), (500, 500))
    screen.blit(fon, (0, 0))

    # отрисовка рамки
    pygame.draw.rect(screen, 'black', (78, 420, 350, 60))
    pygame.draw.rect(screen, (205, 155, 29), (78, 420, 350, 60), 5)

    # шрифт
    font = pygame.font.Font(None, 30)

    string_rendered = font.render(title, 1, pygame.Color((205, 155, 29)))
    screen.blit(string_rendered, (65, 440))


def final_screen(result):
    # отрисовка заднего фона
    fon = pygame.transform.scale(load_image('game over.jpg'), (500, 500))
    screen.blit(fon, (0, 0))

    # fetching record
    with open('data/record.txt', mode='r', encoding='utf-8') as file_with_record:
        record = file_with_record.readline().strip()

    font = pygame.font.Font(None, 20)
    string_rendered_result = font.render(f'Вы проиграли на {result}-ом раунде', 1, pygame.Color((205, 155, 29)))
    string_rendered_record = font.render(f'Ваш рекорд - на {record}-ом', 1, pygame.Color((205, 155, 29)))
    screen.blit(string_rendered_result, (10, 10))
    screen.blit(string_rendered_record, (10, 30))
    if result == int(record):
        string_rendered_congrats = font.render('Поздравляю!', 1, pygame.Color((205, 155, 29)))
        screen.blit(string_rendered_congrats, (10, 50))
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
                the_guy = Character(guy_image, 4, 4, x * 50, y * 50)
            elif level[y][x] == '*':
                Tile('empty', x, y)
                the_bull = Character(horse_image, 3, 4, x * 50, y * 50)

    # вернем игрока и лошадь, а также размер поля в клетках
    return the_guy, the_bull, x, y


def terminate():  # if event.type == pygame.QUIT:
    pygame.quit()
    exit()


def main_generation():
    global tile_height, tile_images, tile_width, \
        guy_image, guy, horse, horse_doings, horse_image, \
        all_sprites, level_x, level_y, directions, characters_group, tiles_group, lvl_map

    generate_map()

    texture_pack = choice([1, 2])
    if texture_pack == 1:
        tile_images = {
            'wall': pygame.transform.scale(load_image('box.png'), (50, 50)),
            'empty': pygame.transform.scale(load_image('sand.jpg'), (50, 50))
        }
    elif texture_pack == 2:
        tile_images = {
            'wall': pygame.transform.scale(load_image('old box.jpg'), (50, 50)),
            'empty': pygame.transform.scale(load_image('cracked sand.jpg'), (50, 50))
        }
    guy_image = pygame.transform.scale(load_image('guy_sprites.png'), (200, 200))
    horse_image = pygame.transform.scale(load_image('horse_sprites.jpg', (255, 255, 255)), (200, 200))

    tile_width = tile_height = 50

    # основные персонажи
    guy = None
    horse = None

    # группы спрайтов
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    characters_group = pygame.sprite.Group()

    lvl_map = load_level('map.txt')
    guy, horse, level_x, level_y = generate_level(lvl_map)

    '''belongs to main'''
    directions = ['up', 'up']  # для того чтобы определить, в какую сторону скользить

    # список действий лошади
    # запас хода быка по вертикали в две клетки (100 пикселей), т.к в начале игры между игроком и лошадью это расстояние
    horse_doings = ['horse.rect.y - 1' for _ in range(150)]


def writing_round(n):
    font = pygame.font.Font(None, 80)

    string_rendered = font.render(f'Round {n}', 1, pygame.Color((194, 24, 7)))
    screen.blit(string_rendered, (140, 210))


def main():
    main_generation()

    camera = Camera()
    start_screen()
    start_screen_ends = False

    # для правильной работы камеры
    guy_x = guy.rect.x
    guy_y = guy.rect.y

    # флаги направления игрока
    up, down, right, left = True, False, False, False

    sliding = False  # флаг скольжения

    c = 0  # счётчик

    write = False  # флаг на перезапись рекорда

    iterations = 0

    while True:
        iterations += 1
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

                            horse_doings.append('horse.rect.y - 1')
                            sliding = False

                        else:  # скольжение
                            sliding = True
                            if directions[-2] == 'right' or directions[-2] == 'down':
                                if guy_x < 500:
                                    if lvl_map[guy_y // tile_height][(guy_x + tile_width) // tile_width] != '#':
                                        guy.rect.x += 1
                                        guy_x += 1

                                        horse_doings.append('horse.rect.x + 1')
                            else:
                                if guy_x > 0:
                                    if lvl_map[guy_y // tile_height][(guy_x - 1) // tile_width] != '#':
                                        guy.rect.x -= 1
                                        guy_x -= 1

                                        horse_doings.append('horse.rect.x - 1')

                    else:
                        if lvl_map[(guy_y - 1) // tile_height][guy_x // tile_width] != '#' and \
                                lvl_map[(guy_y - 1) // tile_height][guy_x // tile_width + 1] != '#':
                            guy.rect.y -= 1
                            guy_y -= 1

                            horse_doings.append('horse.rect.y - 1')
                            sliding = False

                        else:  # скольжение
                            sliding = True
                            if directions[-2] == 'right' or directions[-2] == 'down':
                                if guy_x < 500:
                                    if lvl_map[guy_y // tile_height][(guy_x + tile_width) // tile_width] != '#':
                                        guy.rect.x += 1
                                        guy_x += 1

                                        horse_doings.append('horse.rect.x + 1')
                            else:
                                if guy_x > 0:
                                    if lvl_map[guy_y // tile_height][(guy_x - 1) // tile_width] != '#':
                                        guy.rect.x -= 1
                                        guy_x -= 1

                                        horse_doings.append('horse.rect.x - 1')

            elif down:  # ВНИЗ

                # действия игрока
                if guy_y < 500:
                    if guy_x % tile_width == 0:
                        if lvl_map[(guy_y + tile_height) // tile_height][guy_x // tile_width] != '#':
                            guy.rect.y += 1
                            guy_y += 1

                            horse_doings.append('horse.rect.y + 1')
                            sliding = False

                        else:  # скольжение
                            sliding = True
                            if directions[-2] == 'right' or directions[-2] == 'down':
                                if guy_x < 500:
                                    if lvl_map[guy_y // tile_height][(guy_x + tile_width) // tile_width] != '#':
                                        guy.rect.x += 1
                                        guy_x += 1

                                        horse_doings.append('horse.rect.x + 1')
                            else:
                                if guy_x > 0:
                                    if lvl_map[guy_y // tile_height][(guy_x - 1) // tile_width] != '#':
                                        guy.rect.x -= 1
                                        guy_x -= 1

                                        horse_doings.append('horse.rect.x - 1')

                    else:
                        if lvl_map[(guy_y + tile_height) // tile_height][guy_x // tile_width] != '#' and \
                                lvl_map[(guy_y + tile_height) // tile_height][guy_x // tile_width + 1] != '#':
                            guy.rect.y += 1
                            guy_y += 1

                            horse_doings.append('horse.rect.y + 1')
                            sliding = False

                        else:  # скольжение
                            sliding = True
                            if directions[-2] == 'right' or directions[-2] == 'down':
                                if guy_x < 500:
                                    if lvl_map[guy_y // tile_height][(guy_x + tile_width) // tile_width] != '#':
                                        guy.rect.x += 1
                                        guy_x += 1

                                        horse_doings.append('horse.rect.x + 1')
                            else:
                                if guy_x > 0:
                                    if lvl_map[guy_y // tile_height][(guy_x - 1) // tile_width] != '#':
                                        guy.rect.x -= 1
                                        guy_x -= 1

                                        horse_doings.append('horse.rect.x - 1')

            elif right:  # ВПРАВО

                # действия игрока
                if guy_x < 500:
                    if guy_y % tile_height == 0:
                        if lvl_map[guy_y // tile_height][(guy_x + tile_width) // tile_width] != '#':
                            guy.rect.x += 1
                            guy_x += 1

                            horse_doings.append('horse.rect.x + 1')
                            sliding = False

                        else:  # скольжение
                            sliding = True
                            if directions[-2] == 'up' or directions[-2] == 'left':
                                if guy_y > 0:
                                    if lvl_map[(guy_y - 1) // tile_height][guy_x // tile_width] != '#':
                                        guy.rect.y -= 1
                                        guy_y -= 1

                                        horse_doings.append('horse.rect.y - 1')
                            else:
                                if guy_y < 500:
                                    if lvl_map[(guy_y + tile_height) // tile_height][guy_x // tile_width] != '#':
                                        guy.rect.y += 1
                                        guy_y += 1

                                        horse_doings.append('horse.rect.y + 1')

                    else:
                        if lvl_map[guy_y // tile_height][(guy_x + tile_width) // tile_width] != '#' and \
                                lvl_map[guy_y // tile_height + 1][(guy_x + tile_width) // tile_width] != '#':
                            guy.rect.x += 1
                            guy_x += 1

                            horse_doings.append('horse.rect.x + 1')
                            sliding = False

                        else:  # скольжение
                            sliding = True
                            if directions[-2] == 'up' or directions[-2] == 'left':
                                if guy_y > 0:
                                    if lvl_map[(guy_y - 1) // tile_height][guy_x // tile_width] != '#':
                                        guy.rect.y -= 1
                                        guy_y -= 1

                                        horse_doings.append('horse.rect.y - 1')
                            else:
                                if guy_y < 500:
                                    if lvl_map[(guy_y + tile_height) // tile_height][guy_x // tile_width] != '#':
                                        guy.rect.y += 1
                                        guy_y += 1

                                        horse_doings.append('horse.rect.y + 1')

            elif left:  # ВЛЕВО

                # действия игрока
                if guy_x > 0:
                    if guy_y % tile_height == 0:
                        if lvl_map[guy_y // tile_height][(guy_x - 1) // tile_width] != '#':
                            guy.rect.x -= 1
                            guy_x -= 1

                            horse_doings.append('horse.rect.x - 1')
                            sliding = False

                        else:  # скольжение
                            sliding = True
                            if directions[-2] == 'up' or directions[-2] == 'left':
                                if guy_y > 0:
                                    if lvl_map[(guy_y - 1) // tile_height][guy_x // tile_width] != '#':
                                        guy.rect.y -= 1
                                        guy_y -= 1

                                        horse_doings.append('horse.rect.y - 1')
                            else:
                                if guy_y < 500:
                                    if lvl_map[(guy_y + tile_height) // tile_height][guy_x // tile_width] != '#':
                                        guy.rect.y += 1
                                        guy_y += 1

                                        horse_doings.append('horse.rect.y + 1')

                    else:
                        if lvl_map[guy_y // tile_height][(guy_x - 1) // tile_width] != '#' and \
                                lvl_map[guy_y // tile_height + 1][(guy_x - 1) // tile_width] != '#':
                            guy.rect.x -= 1
                            guy_x -= 1

                            horse_doings.append('horse.rect.x - 1')
                            sliding = False

                        else:  # скольжение
                            sliding = True
                            if directions[-2] == 'up' or directions[-2] == 'left':
                                if guy_y > 0:
                                    if lvl_map[(guy_y - 1) // tile_height][guy_x // tile_width] != '#':
                                        guy.rect.y -= 1
                                        guy_y -= 1

                                        horse_doings.append('horse.rect.y - 1')
                            else:
                                if guy_y < 500:
                                    if lvl_map[(guy_y + tile_height) // tile_height][guy_x // tile_width] != '#':
                                        guy.rect.y += 1
                                        guy_y += 1

                                        horse_doings.append('horse.rect.y + 1')

            # движение лошади
            # тут могла быть рекурсия
            if 'y' in horse_doings[0]:
                horse.rect.y = eval(horse_doings.pop(0))
                if sliding:
                    if 'y' in horse_doings[0]:
                        horse.rect.y = eval(horse_doings.pop(0))
                    else:
                        horse.rect.x = eval(horse_doings.pop(0))
                if '-' in horse_doings[0]:
                    horse_direction = 'up'
                else:
                    horse_direction = 'down'
            else:  # elif 'x' in horse_doings[0]
                horse.rect.x = eval(horse_doings.pop(0))
                if sliding:
                    if 'y' in horse_doings[0]:
                        horse.rect.y = eval(horse_doings.pop(0))
                    else:
                        horse.rect.x = eval(horse_doings.pop(0))
                if '-' in horse_doings[0]:
                    horse_direction = 'left'
                else:
                    horse_direction = 'right'

            # изменяем ракурс камеры
            camera.update(guy)
            # обновляем положение всех спрайтов
            for sprite in all_sprites:
                camera.apply(sprite)

            screen.fill('black')

            if iterations % 10 == 0:
                if up:
                    guy.update(2, 3, True)
                elif down:
                    guy.update(1, 4)
                elif right:
                    guy.update(4, 4)
                else:  # elif left
                    guy.update(3, 4)

                if horse_direction == 'up':
                    horse.update(4, 3)
                elif horse_direction == 'down':
                    horse.update(1, 3)
                elif horse_direction == 'right':
                    horse.update(3, 3)
                else:
                    horse.update(2, 3)

            elif iterations % 5 == 0 and sliding:
                if horse_direction == 'up':
                    horse.update(4, 3)
                elif horse_direction == 'down':
                    horse.update(1, 3)
                elif horse_direction == 'right':
                    horse.update(3, 3)
                else:
                    horse.update(2, 3)

            tiles_group.draw(screen)
            characters_group.draw(screen)
            if not sliding:  # normally
                clock.tick(150)
            else:
                clock.tick(75)

            # проверка на столконовение
            collide = horse.rect.colliderect(guy.rect)
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
                    final_screen(c)

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
    main()
