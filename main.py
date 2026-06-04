import pygame
from os.path import join
from random import randint, uniform

score = 0
player_lives = 3

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load('images/player2.png').convert_alpha()
        self.rect = self.image.get_frect(center=(window_width / 2, window_height / 2))
        self.direction = pygame.Vector2()
        self.speed = 300

        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])

        self.direction = self.direction.normalize() if self.direction else self.direction

        self.rect.center += self.direction * self.speed * dt

        # Keep player inside screen
        self.rect.clamp_ip(screen.get_rect())

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()

        self.laser_timer()


class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(
            center=(randint(0, window_width), randint(0, window_height))
        )

    def update(self, dt):
        self.rect.y += 50 * dt

        if self.rect.top > window_height:
            self.rect.bottom = 0
            self.rect.x = randint(0, window_width)


class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom=pos)

    def update(self, dt):
        self.rect.centery -= 400 * dt

        if self.rect.bottom < 0:
            self.kill()


class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)

        scale = uniform(0.6, 1.4)
        self.image = pygame.transform.rotozoom(surf, 0, scale)

        self.rect = self.image.get_frect(center=pos)

        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1).normalize()
        self.speed = randint(400, 500)

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt

        if self.rect.top > window_height:
            self.kill()


def collisions():
    global running, player_lives, score

    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True)

    if collision_sprites:
        player_lives -= 1

        if player_lives <= 0:
            running = False

    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(
            laser, meteor_sprites, True
        )

        if collided_sprites:
            score += len(collided_sprites)
            laser.kill()


def display_score():
    text = f"Score: {score}   Lives: {player_lives}"
    text_surf = font.render(text, True, (240, 240, 240))
    text_rect = text_surf.get_frect(midtop=(window_width / 2, 20))

    bg_rect = text_rect.inflate(20, 10)
    pygame.draw.rect(screen, (60, 60, 60), bg_rect, border_radius=8)

    screen.blit(text_surf, text_rect)


pygame.init()

window_width = 1280
window_height = 720

screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Space Shooter Improved')

running = True

clock = pygame.time.Clock()

star_surf = pygame.image.load('images/star.png').convert_alpha()
meteor_surf = pygame.image.load('images/meteor.png').convert_alpha()
laser_surf = pygame.image.load('images/laser.png').convert_alpha()

font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)

all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()

for _ in range(50):
    Star(all_sprites, star_surf)

player = Player(all_sprites)

meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)

while running:

    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == meteor_event:
            x = randint(0, window_width)
            y = randint(-200, -100)

            Meteor(
                meteor_surf,
                (x, y),
                (all_sprites, meteor_sprites)
            )

    all_sprites.update(dt)

    collisions()

    screen.fill('black')

    all_sprites.draw(screen)

    display_score()

    pygame.display.flip()

pygame.quit()
