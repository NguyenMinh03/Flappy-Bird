import pygame
from random import randint

pygame.init()
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Flappy Bird')
running = True

GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# Mario-style pipe colors
PIPE_DARK = (0, 155, 0)
PIPE_LIGHT = (80, 255, 80)
PIPE_LIP = (0, 200, 0)
PIPE_OUTLINE = (0, 110, 0)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


bird_angle = 0.0  # current visual angle (degrees)


def draw_mario_pipe(surface, x, y, w, h, lip_side="top"):
    """Draw a simple Mario-style pipe with a rim and shading.
    lip_side: 'top' or 'bottom' (where the opening/rim should be)
    Returns a rect for collision.
    """
    lip_h = 14
    body = pygame.Rect(int(x), int(y), int(w), int(h))

    # main body
    pygame.draw.rect(surface, PIPE_DARK, body)

    # highlight stripe
    stripe_w = max(4, int(w * 0.22))
    stripe_x = int(x + w * 0.15)
    stripe = pygame.Rect(stripe_x, int(y), stripe_w, int(h))
    pygame.draw.rect(surface, PIPE_LIGHT, stripe)

    # rim (lip) - a bit wider than the body
    if lip_side == "top":
        lip = pygame.Rect(int(x - 6), int(y), int(w + 12), lip_h)
    else:  # bottom
        lip = pygame.Rect(int(x - 6), int(y + h - lip_h), int(w + 12), lip_h)
    pygame.draw.rect(surface, PIPE_LIP, lip)

    # outlines
    pygame.draw.rect(surface, PIPE_OUTLINE, body, 2)
    pygame.draw.rect(surface, PIPE_OUTLINE, lip, 2)

    return body.union(lip)


clock = pygame.time.Clock()

TUBE_WIDTH = 50
TUBE_VELOCITY = 3
TUBE_GAP = 150

tube1_x = 600
tube2_x = 800
tube3_x = 1000

tube1_height = randint(100, 400)
tube2_height = randint(100, 400)
tube3_height = randint(100, 400)

BIRD_X = 50
bird_y = 400
BIRD_WIDTH = 35
BIRD_HEIGHT = 35

bird_drop_velocity = 0
GRAVITY = 0.5

score = 0
font = pygame.font.SysFont('sans', 20)

tube1_pass = False
tube2_pass = False
tube3_pass = False

pausing = False
background_image = pygame.image.load("background.png").convert()
bird_image_orig = pygame.image.load("bird.png").convert_alpha()
bird_image_orig = pygame.transform.scale(
    bird_image_orig, (BIRD_WIDTH, BIRD_HEIGHT))
floor_image = pygame.image.load("floor.png").convert()
floor_image = pygame.transform.scale(floor_image, (WIDTH, 50))
while running:
    clock.tick(60)
    screen.fill(GREEN)
    screen.blit(background_image, (0, 0))    # Draw Mario-style pipes
    # Top pipes (opening faces DOWN) => lip at BOTTOM
    tube1_rect = draw_mario_pipe(
        screen, tube1_x, 0, TUBE_WIDTH, tube1_height, lip_side="bottom")
    tube2_rect = draw_mario_pipe(
        screen, tube2_x, 0, TUBE_WIDTH, tube2_height, lip_side="bottom")
    tube3_rect = draw_mario_pipe(
        screen, tube3_x, 0, TUBE_WIDTH, tube3_height, lip_side="bottom")

    # Bottom pipes (opening faces UP) => lip at TOP
    tube1_rect_inv = draw_mario_pipe(
        screen, tube1_x, tube1_height + TUBE_GAP, TUBE_WIDTH,
        HEIGHT - tube1_height - TUBE_GAP, lip_side="top"
    )
    tube2_rect_inv = draw_mario_pipe(
        screen, tube2_x, tube2_height + TUBE_GAP, TUBE_WIDTH,
        HEIGHT - tube2_height - TUBE_GAP, lip_side="top"
    )
    tube3_rect_inv = draw_mario_pipe(
        screen, tube3_x, tube3_height + TUBE_GAP, TUBE_WIDTH,
        HEIGHT - tube3_height - TUBE_GAP, lip_side="top"
    )
    # move tube to the left
    tube1_x = tube1_x - TUBE_VELOCITY
    tube2_x = tube2_x - TUBE_VELOCITY
    tube3_x = tube3_x - TUBE_VELOCITY

    # draw floor - tile across full width
    # draw bird (tilt up when going up, bow down when falling)
    floor_tile_width = floor_image.get_width()
    x = 0
    while x < WIDTH:
        screen.blit(floor_image, (x, 550))
        x += floor_tile_width
    sand_rect = pygame.Rect(0, 550, WIDTH, 50)
    target_angle = clamp(-bird_drop_velocity * 6, -60, 30)
    bird_angle += (target_angle - bird_angle) * 0.2
    rotated_bird = pygame.transform.rotate(bird_image_orig, bird_angle)
    bird_center = (BIRD_X + BIRD_WIDTH // 2, int(bird_y) + BIRD_HEIGHT // 2)
    bird_rect = rotated_bird.get_rect(center=bird_center)
    screen.blit(rotated_bird, bird_rect)

    # bird falls
    bird_y += bird_drop_velocity
    bird_drop_velocity += GRAVITY

    # generate new tubes
    if tube1_x < -TUBE_WIDTH:
        tube1_x = 550
        tube1_height = randint(100, 400)
        tube1_pass = False
    if tube2_x < -TUBE_WIDTH:
        tube2_x = 550
        tube2_height = randint(100, 400)
        tube2_pass = False
    if tube3_x < -TUBE_WIDTH:
        tube3_x = 550
        tube3_height = randint(100, 400)
        tube3_pass = False

    score_txt = font.render("Score: " + str(score), True, BLACK)
    screen.blit(score_txt, (5, 5))

    # update score
    if tube1_x + TUBE_WIDTH <= BIRD_X and tube1_pass == False:
        score += 1
        tube1_pass = True
    if tube2_x + TUBE_WIDTH <= BIRD_X and tube2_pass == False:
        score += 1
        tube2_pass = True
    if tube3_x + TUBE_WIDTH <= BIRD_X and tube3_pass == False:
        score += 1
        tube3_pass = True

    # check collision
    for tube in [tube1_rect, tube2_rect, tube3_rect, tube1_rect_inv, tube2_rect_inv, tube3_rect_inv, sand_rect]:
        if bird_rect.colliderect(tube):
            pausing = True
            TUBE_VELOCITY = 0
            bird_drop_velocity = 0
            game_over_txt = font.render(
                "Game over, score: " + str(score), True, BLACK)
            screen.blit(game_over_txt, (200, 300))
            press_space_txt = font.render(
                "Press Space to Continue", True, BLACK)
            screen.blit(press_space_txt, (160, 400))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # reset
                if pausing:
                    bird_y = 400
                    TUBE_VELOCITY = 3
                    tube1_x = 600
                    tube2_x = 800
                    tube3_x = 1000
                    score = 0
                    pausing = False
                    bird_angle = 0.0
                bird_drop_velocity = 0
                bird_drop_velocity -= 7

    pygame.display.flip()

pygame.quit()
