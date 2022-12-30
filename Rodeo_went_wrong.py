import pygame
from sys import exit
from os import path

pygame.init()
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()
FPS = 60


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
        self.dx = -(target.rect.x + target.rect.w // 2 - 600 // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - 600 // 2)


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

    fon = pygame.transform.scale(load_image('start_screen.webp'), (600, 600))
    screen.blit(fon, (0, 0))
    pygame.draw.rect(screen, 'black', (108, 10, 390, 90))
    pygame.draw.rect(screen, (205, 155, 29), (108, 10, 390, 90), 5)

    font = pygame.font.Font(None, 50)
    text_coord = 25

    string_rendered = font.render(title, 1, pygame.Color((205, 155, 29)))
    intro_rect = string_rendered.get_rect()
    text_coord += 10
    intro_rect.top = text_coord
    intro_rect.x = 10
    text_coord += intro_rect.height
    screen.blit(string_rendered, intro_rect)


def terminate():  # if event.type == pygame.QUIT:
    pygame.quit()
    exit()


def move_up():
    pass


def move_down():
    pass


def move_right():
    pass


def move_left():
    pass


def main():
    camera = Camera()
    start_screen()
    while True:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                terminate()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP:  # ВВЕРХ
                    move_up()

                elif event.key == pygame.K_DOWN:  # ВНИЗ
                    move_down()

                elif event.key == pygame.K_RIGHT:  # ВПРАВО
                    move_right()

                elif event.key == pygame.K_LEFT:  # ВЛЕВО
                    move_left()

                """""
                # изменяем ракурс камеры
                camera.update(player)
                # обновляем положение всех спрайтов
                for sprite in all_sprites:
                    camera.apply(sprite)
                """""

                screen.fill('black')
                # drawing of sprites
                clock.tick(FPS)
            pygame.display.flip()


if __name__ == '__main__':
    main()
