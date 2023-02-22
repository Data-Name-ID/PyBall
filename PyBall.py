import sys
import json
import pygame
import colorsys

from math import atan2, cos, sin
from random import randint, choice
from os import path, makedirs
from dataclasses import dataclass
from typing import List, Tuple, Union
from cryptography.fernet import Fernet

pygame.mixer.pre_init()
pygame.init()
pygame.font.init()

pygame.display.set_caption('PyBall')

# КОНФИГУРАЦИЯ #
DEFAULT_FPS = 240

GRAVITY = 0.1

LEVEL_WIDTH = 9
LEVEL_HEIGHT = 10

PARTICLES_COLOR = (87, 104, 250)
PARTICLES_COUNT = 20

BLOCK_SIZE = 40
BLOCK_KILL_NUMBER = 0

BALL_RADIUS = 5
BALL_SPEED = 1
BALL_DAMAGE = 1
BALL_COLOR = 'white'

FONT_PATH = 'App/fonts/EpilepsySans.ttf'
FONT = pygame.font.Font(FONT_PATH, 26)
BIG_FONT = pygame.font.Font(FONT_PATH, 42)
FONT_COLOR = pygame.Color('white')

BACKGROUND_COLOR = (4, 0, 20)
BOTTOM_LINE_COLOR = (0, 102, 255)

BUTTON_HEIGHT = 50
BUTTON_COLOR = (117, 102, 179)
BUTTON_HOVER_COLOR = (143, 130, 196)

NEW_GAME_SETTINGS = {'score': 0, 'last_level': 1}

DATA_FOLDER = 'Data'
SECRET_KEY_PATH = 'Data/secret.key'
GAME_SAVE_PATH = 'Data/game_save.data'

MUSIC_VOLUME = 0.5

MAIN_THEME_SOUND = 'App/sounds/main_theme.mp3'

HIT_SOUND = pygame.mixer.Sound("App/sounds/hit.wav")
DESTRUCTION_SOUND = pygame.mixer.Sound("App/sounds/destruction.wav")
CLICK_SOUND = pygame.mixer.Sound("App/sounds/click.wav")
REBOUND_SOUND = pygame.mixer.Sound("App/sounds/rebound.wav")
GAME_OVER_SOUND = pygame.mixer.Sound("App/sounds/game_over.mp3")
WIN_SOUND = pygame.mixer.Sound("App/sounds/win.mp3")
SHOOT_SOUND = pygame.mixer.Sound("App/sounds/shoot.wav")
CONTINUE_SOUND = pygame.mixer.Sound("App/sounds/continue.wav")
ON_LINE_SOUND = pygame.mixer.Sound("App/sounds/on_line.wav")
# ============ #


@dataclass
class Point:
    x: Union[int, float]
    y: Union[int, float]


@dataclass
class GameCodes:
    win: int = 1
    game_over: int = 2
    play: int = 3
    main_menu: int = 4
    again: int = 5
    exit: int = -1


if not path.exists(DATA_FOLDER):
    makedirs(DATA_FOLDER)

if not path.exists(SECRET_KEY_PATH):
    key = Fernet.generate_key()
    with open(SECRET_KEY_PATH, 'wb') as f:
        f.write(key)
else:
    with open(SECRET_KEY_PATH, 'rb') as f:
        key = f.read()

fernet = Fernet(key)

if path.exists(GAME_SAVE_PATH):
    with open(GAME_SAVE_PATH, 'rb') as f:
        game_save = json.loads(fernet.decrypt(f.read()))
else:
    game_save = NEW_GAME_SETTINGS.copy()

clock = pygame.time.Clock()
fps = DEFAULT_FPS

screen = pygame.display.set_mode(
    (LEVEL_WIDTH * BLOCK_SIZE, LEVEL_HEIGHT * BLOCK_SIZE + 150)
)
screen_rect = (0, 0, screen.get_width(), screen.get_height())

pygame.mixer.music.load(MAIN_THEME_SOUND)
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(MUSIC_VOLUME)


class TextRender:
    def __init__(self, screen: pygame.surface.Surface) -> None:
        self.screen = screen

    def bottom_left(self, text: str, font: pygame.font.Font = FONT) -> None:
        text_surface = font.render(text, False, FONT_COLOR)
        self.screen.blit(
            text_surface,
            (10, self.screen.get_height() - 10 - text_surface.get_height()),
        )

    def bottom_right(self, text: str, font: pygame.font.Font = FONT) -> None:
        text_surface = font.render(text, False, FONT_COLOR)
        self.screen.blit(
            text_surface,
            (
                self.screen.get_width() - 10 - text_surface.get_width(),
                screen.get_height() - 10 - text_surface.get_height(),
            ),
        )

    def center(
        self, text: str, pos_y: int, font: pygame.font.Font = FONT
    ) -> None:
        text_surface = font.render(text, False, FONT_COLOR)
        self.screen.blit(
            text_surface,
            (
                (self.screen.get_width() - text_surface.get_width()) / 2,
                pos_y,
            ),
        )


class GameMap:
    def __init__(self, level: List[List[str]], ball_count: int) -> None:
        self.width = len(level[0])
        self.height = len(level)

        self.map = [[None] * self.width for _ in range(self.height)]
        self.ball_count = ball_count

        self.score = 0
        self.bottom_line = BottomLine(
            self.height * BLOCK_SIZE + BLOCK_SIZE // 2
        )

        self.is_shoot = False
        self.previous_time = pygame.time.get_ticks()

        self.ball_stop_point = None

        self.departure_point = pygame.math.Vector2(
            screen.get_width() / 2, self.bottom_line.rect.top - BALL_RADIUS
        )

        for y in range(self.height):
            for x in range(self.width):
                symbol = level[y][x]

                if symbol.isdigit():
                    self.map[y][x] = Block(self, x, y, int(symbol))

    def get_score(self) -> int:
        return self.score

    def change_score(self, score: int) -> None:
        self.score += score

    def set_departure_point(self, new_point: pygame.math.Vector2) -> None:
        self.departure_point = new_point

    def set_ball_stop_point(
        self, new_point: Union[Point, None] = None
    ) -> None:
        self.ball_stop_point = new_point

    def shoot(self) -> None:
        if all(
            map(
                lambda x: x.speed == pygame.math.Vector2(0),
                balls_group.sprites(),
            )
        ):
            self.is_shoot = pygame.mouse.get_pos()

    def update(self) -> None:
        global fps, game_save

        text_render.bottom_left(f'Текущий счёт: {self.get_score()}')
        text_render.bottom_right(
            f'x{self.ball_count - len(balls_group.sprites())}'
        )

        if not self.is_shoot:
            draw_sight_line(self)

        if self.is_shoot and len(balls_group.sprites()) < self.ball_count:
            now = pygame.time.get_ticks()
            if now - self.previous_time > DEFAULT_FPS * 100 / fps:
                mouse = tuple(map(lambda x: x + BALL_RADIUS, self.is_shoot))

                if mouse[1] > self.bottom_line.rect.top - 20:
                    mouse = (mouse[0], self.bottom_line.rect.top - 20)
                distance = mouse - self.departure_point

                position = pygame.math.Vector2(
                    self.departure_point.x - BALL_RADIUS,
                    self.departure_point.y,
                )
                speed = distance.normalize() * BALL_SPEED

                SHOOT_SOUND.play()
                Ball(self, position, speed)
                self.previous_time = now

        if self.is_shoot and all(
            map(
                lambda ball: ball.speed == pygame.math.Vector2(0)
                and ball.rect.centerx == self.ball_stop_point.x,
                balls_group.sprites(),
            )
        ):
            if len(blocks_group) == 0:
                game_save['score'] += self.score
                game_save['last_level'] += 1
                fps = DEFAULT_FPS
                return GameCodes.win

            CONTINUE_SOUND.play()
            
            fps = DEFAULT_FPS
            self.is_shoot = False

            clear_sprites(balls_group)
            self.set_departure_point(
                pygame.math.Vector2(
                    self.ball_stop_point.x, self.ball_stop_point.y
                )
            )
            self.set_ball_stop_point()

            for block in blocks_group.sprites():
                block.move()

            if pygame.sprite.spritecollideany(self.bottom_line, blocks_group):
                return GameCodes.game_over


class Block(pygame.sprite.Sprite):
    def __init__(
        self, game_map: GameMap, pos_x: int, pos_y: int, number: int
    ) -> None:
        super().__init__(blocks_group, all_sprites)
        self.rect: pygame.Rect

        self.game_map = game_map

        self.pos_x = pos_x
        self.pos_y = pos_y
        self.number = number

        self._update()

    def move(self) -> None:
        self.pos_y += 1
        self._update()

    def deal_damage(self, damage: int) -> None:
        self.number -= damage
        self.game_map.change_score(damage * 2)

        if self.number <= BLOCK_KILL_NUMBER:
            DESTRUCTION_SOUND.play()
            self.game_map.change_score(damage * 10)

            self.kill()
            create_particles(self.rect.center)

        self._update()

    def _update(self) -> None:
        self.image = get_block_image(self.number)
        textsurface = FONT.render(str(self.number), True, FONT_COLOR)

        textrect = textsurface.get_rect(center=self.image.get_rect().center)
        self.image.blit(textsurface, textrect)

        self.rect = pygame.Rect(
            BLOCK_SIZE * self.pos_x,
            BLOCK_SIZE * self.pos_y,
            BLOCK_SIZE,
            BLOCK_SIZE,
        )

        self.sides = dict(
            left=pygame.Rect(
                self.rect.left - 1, self.rect.top, 1, self.rect.height
            ),
            right=pygame.Rect(
                self.rect.right, self.rect.top, 1, self.rect.height
            ),
            top=pygame.Rect(
                self.rect.left, self.rect.top - 1, self.rect.width, 1
            ),
            bottom=pygame.Rect(
                self.rect.left, self.rect.bottom, self.rect.width, 1
            ),
        )


class Ball(pygame.sprite.Sprite):
    def __init__(
        self,
        game_map: GameMap,
        position: pygame.math.Vector2,
        speed: pygame.math.Vector2,
        damage: int = BALL_DAMAGE,
    ) -> None:
        super().__init__(balls_group, all_sprites)
        self.rect: pygame.Rect

        self.game_map = game_map

        self.position = position
        self.speed = speed

        self.damage = damage

        self.image = pygame.Surface(
            (2 * BALL_RADIUS, 2 * BALL_RADIUS), pygame.SRCALPHA, 32
        )
        pygame.draw.circle(
            self.image,
            pygame.Color(BALL_COLOR),
            (BALL_RADIUS, BALL_RADIUS),
            BALL_RADIUS,
        )
        self.rect = pygame.Rect(
            self.position.x - BALL_RADIUS,
            self.position.y - BALL_RADIUS,
            2 * BALL_RADIUS,
            2 * BALL_RADIUS,
        )

    def move(self) -> None:
        self.position += self.speed

        self.rect.centerx = self.position.x
        self.rect.centery = self.position.y

    def update(self) -> None:
        if self.speed != pygame.math.Vector2(0):
            self.move()

        if self.rect.bottom >= self.game_map.bottom_line.rect.top:
            if self.speed != pygame.math.Vector2(0):
                ON_LINE_SOUND.play()

                self.speed = pygame.math.Vector2(0)
                self.rect.bottom = self.game_map.bottom_line.rect.top

                if self.game_map.ball_stop_point is None:
                    self.game_map.set_ball_stop_point(Point(*self.rect.center))

            if self.rect.centerx != self.game_map.ball_stop_point.x:
                if self.rect.centerx < self.game_map.ball_stop_point.x:
                    self.rect.x += 1
                else:
                    self.rect.x -= 1

            return None

        if self.rect.left <= 0 or self.rect.right >= screen.get_width():
            self.speed.x = -self.speed.x

        if self.rect.top <= 0:
            self.speed.y = -self.speed.y

        block = pygame.sprite.spritecollideany(self, blocks_group)

        if not block:
            return None

        block.deal_damage(self.damage)
        HIT_SOUND.play()

        collisions = set(
            side
            for side, rect in block.sides.items()
            if self.rect.colliderect(rect)
        )

        if (
            {'left', 'right'} & collisions
            and 'bottom' in collisions
            and self.rect.centery > block.rect.bottom
        ):
            if self.speed.y <= 0:
                self.speed.y = -self.speed.y
            else:
                self.speed.x = -self.speed.x

        elif (
            {'left', 'right'} & collisions
            and 'top' in collisions
            and self.rect.centery < block.rect.top
        ):
            if self.speed.y >= 0:
                self.speed.y = -self.speed.y
            else:
                self.speed.x = -self.speed.x

        elif (
            {'top', 'bottom'} & collisions
            and 'left' in collisions
            and self.rect.centerx < block.rect.left
        ):
            if self.speed.x >= 0:
                self.speed.x = -self.speed.x
            else:
                self.speed.y = -self.speed.y

        elif (
            {'top', 'bottom'} & collisions
            and 'right' in collisions
            and self.rect.centery > block.rect.right
        ):
            if self.speed.x <= 0:
                self.speed.x = -self.speed.x
            else:
                self.speed.y = -self.speed.y

        elif {'top', 'bottom'} & collisions:
            self.speed.y = -self.speed.y

        else:
            self.speed.x = -self.speed.x


class SimpleBall(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__(balls_group, all_sprites)

        self.position = pygame.math.Vector2(
            randint(10, screen.get_width() - 10),
            randint(10, screen.get_height() - 10),
        )
        self.speed = pygame.math.Vector2(
            randint(20, 100) / 100, randint(20, 100) / 100
        )

        self.image = pygame.Surface(
            (2 * BALL_RADIUS, 2 * BALL_RADIUS), pygame.SRCALPHA, 32
        )
        pygame.draw.circle(
            self.image,
            pygame.Color(BALL_COLOR),
            (BALL_RADIUS, BALL_RADIUS),
            BALL_RADIUS,
        )
        self.rect = pygame.Rect(
            self.position.x - BALL_RADIUS,
            self.position.y - BALL_RADIUS,
            2 * BALL_RADIUS,
            2 * BALL_RADIUS,
        )

    def update(self) -> None:
        self.position += self.speed

        self.rect.x = self.position.x
        self.rect.y = self.position.y

        if self.rect.left <= 0 or self.rect.right >= screen.get_width():
            self.speed.x = -self.speed.x

        if self.rect.top <= 0 or self.rect.bottom >= screen.get_height():
            self.speed.y = -self.speed.y


class BottomLine(pygame.sprite.Sprite):
    def __init__(self, pos_y: int) -> None:
        super().__init__(all_sprites)
        self.rect: pygame.Rect

        self.image = pygame.Surface([screen.get_width(), 2])
        pygame.draw.rect(
            self.image,
            BOTTOM_LINE_COLOR,
            pygame.Rect(0, 0, self.image.get_width(), self.image.get_height()),
        )
        self.rect = pygame.Rect(
            0, pos_y, self.image.get_width(), self.image.get_height()
        )


class Button(pygame.sprite.Sprite):
    def __init__(self, pos_y: Tuple[int, int], text: str, code: int):
        super().__init__(buttons_group, all_sprites)

        self.code = code
        self.text = text

        self.image = pygame.Surface(
            (screen.get_width() / 3 * 2, BUTTON_HEIGHT)
        )

        self.rect = pygame.Rect(
            (screen.get_width() - self.image.get_width()) / 2,
            pos_y,
            self.image.get_width(),
            self.image.get_height(),
        )

        self.draw(BUTTON_COLOR)

    def draw(self, button_color):
        pygame.draw.rect(
            self.image,
            button_color,
            pygame.Rect(0, 0, self.image.get_width(), self.image.get_height()),
        )

        textsurface = FONT.render(self.text, True, FONT_COLOR)
        textrect = textsurface.get_rect(center=self.image.get_rect().center)

        self.image.blit(textsurface, textrect)

    def update(self) -> None:
        if self.rect.collidepoint(*pygame.mouse.get_pos()):
            self.draw(BUTTON_HOVER_COLOR)
        else:
            self.draw(BUTTON_COLOR)

    def check_click(self) -> Union[None, int]:
        if self.rect.collidepoint(*pygame.mouse.get_pos()):
            CLICK_SOUND.play()
            return self.code


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, center_x, bottom_y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(
            center_x - self.rect.width / 2, bottom_y - self.rect.height
        )
        self.time = pygame.time.get_ticks()

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(
            0, 0, sheet.get_width() // columns, sheet.get_height() // rows
        )
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(
                    sheet.subsurface(
                        pygame.Rect(frame_location, self.rect.size)
                    )
                )

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.time > 150:
            self.time = now
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[self.cur_frame]


class Particle(pygame.sprite.Sprite):
    def __init__(
        self,
        pos: Tuple[int, int],
        dx: int,
        dy: int,
        color: Tuple[int, int, int],
    ) -> None:
        super().__init__(all_sprites)

        image = pygame.Surface((BLOCK_SIZE // 2, BLOCK_SIZE // 2))
        pygame.draw.rect(
            image,
            pygame.Color(color),
            pygame.Rect(0, 0, BLOCK_SIZE, BLOCK_SIZE),
        )
        size = choice((5, 10, 20))
        self.image = pygame.transform.scale(image, (size, size))

        self.rect = self.image.get_rect()

        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos

        self.gravity = GRAVITY

    def update(self) -> None:
        self.velocity[1] += self.gravity

        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        if not self.rect.colliderect(screen_rect):
            self.kill()


class Image(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, image_name) -> None:
        super().__init__(balls_group, all_sprites)

        self.image = load_image(image_name)
        self.rect = self.image.get_rect()

        self.rect.x = pos_x - self.rect.width / 2
        self.rect.y = pos_y


def save_game_data() -> None:
    with open(GAME_SAVE_PATH, 'wb') as f:
        f.write(fernet.encrypt(json.dumps(game_save).encode()))


def terminate() -> None:
    save_game_data()

    pygame.quit()
    sys.exit()


def hsv_to_rgb(h: int, s: int, v: int) -> Tuple[int, int, int]:
    return tuple(
        round(i * 255) for i in colorsys.hsv_to_rgb(h / 100, s / 100, v / 100)
    )


def load_image(name: str) -> pygame.surface.Surface:
    image = pygame.image.load(f'App/img/{name}.png')
    image = image.convert_alpha()

    return image


def level_exist(number: int) -> bool:
    return path.exists(f'App/levels/level_{number}.txt')


def load_level(number: Union[int, str]) -> Tuple[List[List[str]], int]:
    file_name = f'App/levels/level_{number}.txt'

    with open(file_name, 'r') as map_file:
        lines = map_file.readlines()
        level_map = [
            [i for i in line.rstrip('\n').split('|')] for line in lines[:-1]
        ]

        return level_map, int(lines[-1])


def get_block_image(number: int) -> pygame.Surface:
    block_image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
    pygame.draw.rect(
        block_image,
        pygame.Color(hsv_to_rgb(number * 15 % 360, 56, 82)),
        pygame.Rect(1, 1, BLOCK_SIZE - 2, BLOCK_SIZE - 2),
    )
    pygame.draw.rect(
        block_image,
        pygame.Color(hsv_to_rgb(number * 15 % 360, 56, 46)),
        pygame.Rect(
            BLOCK_SIZE * 0.1,
            BLOCK_SIZE * 0.1,
            BLOCK_SIZE - BLOCK_SIZE * 0.2,
            BLOCK_SIZE - BLOCK_SIZE * 0.2,
        ),
    )

    return block_image


def create_particles(position: Tuple[int, int]) -> None:
    numbers = range(-5, 6)
    color = hsv_to_rgb(randint(0, 360), 75, 75)

    for _ in range(PARTICLES_COUNT):
        Particle(position, choice(numbers), choice(numbers), color)


def clear_sprites(group: pygame.sprite.Group):
    for sprite in group:
        sprite.kill()


def get_blackout(screen: pygame.surface.Surface) -> pygame.surface.Surface:
    blackout = pygame.Surface((screen.get_width(), screen.get_height()))
    blackout.fill('black')
    blackout.set_alpha(150)

    return blackout


def create_buttons(
    start_pos_y, *button_settings: Tuple[str, int]
) -> List[Button]:
    buttons = []

    for i in range(len(button_settings)):
        buttons.append(
            Button(
                start_pos_y + BUTTON_HEIGHT * i + BUTTON_HEIGHT / 3 * i,
                button_settings[i][0],
                button_settings[i][1],
            )
        )

    return buttons


def draw_sight_line(game_map: GameMap) -> None:
    mouse = Point(*pygame.mouse.get_pos())

    if mouse.y > game_map.bottom_line.rect.top - 20:
        mouse.y = game_map.bottom_line.rect.top - 20

    angle = atan2(
        mouse.y - game_map.departure_point.y,
        mouse.x - game_map.departure_point.x,
    )

    x = game_map.departure_point.x + screen.get_height() * cos(angle)
    y = game_map.departure_point.y + screen.get_height() * sin(angle)

    pygame.draw.line(
        screen,
        FONT_COLOR,
        (game_map.departure_point.x, game_map.departure_point.y),
        (x, y),
        1,
    )


text_render = TextRender(screen)

all_sprites = pygame.sprite.Group()
blocks_group = pygame.sprite.Group()
balls_group = pygame.sprite.Group()
buttons_group = pygame.sprite.Group()


def start_screen() -> int:
    for _ in range(randint(10, 30)):
        SimpleBall()

    Image(screen.get_width() / 2, 100, 'logo')

    AnimatedSprite(load_image('fox'), 14, 1, screen.get_width() / 2, 100)

    if game_save['last_level'] == 1:
        buttons = create_buttons(
            screen.get_height() / 4 * 2,
            ('Начать игру', GameCodes.play),
            ('Выход', GameCodes.exit),
        )

    elif level_exist(game_save['last_level']):
        buttons = create_buttons(
            screen.get_height() / 4 * 2,
            ('Продолжить', GameCodes.play),
            ('Выход', GameCodes.exit),
        )
    else:
        buttons = create_buttons(
            screen.get_height() / 4 * 2,
            ('Начать заново', GameCodes.again),
            ('Выход', GameCodes.exit),
        )

    while True:
        clock.tick(fps)
        screen.fill(pygame.Color(BACKGROUND_COLOR))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GameCodes.exit

            if event.type == pygame.MOUSEBUTTONUP:
                for button in buttons:
                    code = button.check_click()
                    if code:
                        return code

        text_render.bottom_left(f'Текущий счёт: {game_save["score"]}')
        text_render.bottom_right(f'Lvl: {game_save["last_level"]}')
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()


def game_screen(level: int) -> int:
    global fps

    game_map = GameMap(*load_level(level))

    while True:
        clock.tick(fps)
        screen.fill(pygame.Color(BACKGROUND_COLOR))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GameCodes.exit

            if event.type == pygame.MOUSEBUTTONUP:
                game_map.shoot()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_EQUALS and fps < DEFAULT_FPS * 2:
                    fps *= 2
                if event.key == pygame.K_MINUS and fps > DEFAULT_FPS:
                    fps /= 2

        code = game_map.update()
        all_sprites.update()
        all_sprites.draw(screen)

        pygame.display.flip()

        if code:
            return code


def end_screen(code: int):
    screen.blit(get_blackout(screen), (0, 0))

    if code == GameCodes.game_over:
        GAME_OVER_SOUND.play()
        buttons = [
            ('Переиграть', GameCodes.play),
            ('Главное меню', GameCodes.main_menu),
        ]
        text_render.center('Game Over', 110, BIG_FONT)

    elif code == GameCodes.win:
        WIN_SOUND.play()
        if level_exist(game_save['last_level']):
            buttons = [
                ('Следующий уровень', GameCodes.play),
                ('Главное меню', GameCodes.main_menu),
            ]
        else:
            buttons = [('Главное меню', GameCodes.main_menu)]

        text_render.center('Победа', 110, BIG_FONT)

    buttons = create_buttons(screen.get_height() / 3, *buttons)

    while True:
        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return GameCodes.exit

            if event.type == pygame.MOUSEBUTTONUP:
                for button in buttons:
                    code = button.check_click()
                    if code:
                        return code

        buttons_group.draw(screen)
        buttons_group.update()
        pygame.display.flip()


def main() -> None:
    global game_save
    code = start_screen()

    while True:
        if code == GameCodes.exit:
            terminate()

        if code == GameCodes.main_menu:
            clear_sprites(all_sprites)
            code = start_screen()

        if code == GameCodes.play:
            clear_sprites(all_sprites)
            code = game_screen(game_save['last_level'])

        if code in (GameCodes.win, GameCodes.game_over):
            code = end_screen(code)

        if code == GameCodes.again:
            game_save = NEW_GAME_SETTINGS.copy()
            save_game_data()
            clear_sprites(all_sprites)
            code = game_screen(game_save['last_level'])


main()
