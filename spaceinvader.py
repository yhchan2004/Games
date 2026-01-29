import pygame
import random

img_path=r"C:\Users\user\ultralytics\python_project\Games\myane.png"
# 1. Setup Constants
WIDTH, HEIGHT = 800, 600
PLAYER_SIZE = 50
ENEMY_SIZE = 40
BULLET_WIDTH, BULLET_HEIGHT = 5, 10
FPS = 60

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invader")
clock = pygame.time.Clock()

# --- NEW: Font and Score Setup ---
font = pygame.font.SysFont("monospace", 35)
score = 0

# 2. Define Game Objects
player=pygame.Rect(WIDTH // 2 - PLAYER_SIZE // 2, HEIGHT - PLAYER_SIZE - 10, PLAYER_SIZE, PLAYER_SIZE)
enemies=[]
bullets=[]

enemy_img=pygame.image.load(img_path)  # Placeholder for enemy image
enemy_img = pygame.transform.scale(enemy_img, (ENEMY_SIZE, ENEMY_SIZE))
enemies_direction = 1
enemies_speed = 2

def create_enemies():
    for i in range(8):
        # Creates enemies in a row
        enemy = pygame.Rect(i * 80 + 100, 50, ENEMY_SIZE, ENEMY_SIZE)
        enemies.append(enemy)
create_enemies() # Initial wave

running=True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Fire a bullet from the center of the player
                new_bullet = pygame.Rect(player.centerx, player.top, BULLET_WIDTH, BULLET_HEIGHT)
                bullets.append(new_bullet)
    
    # Player Movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player.left > 0:
        player.x -= 5
    if keys[pygame.K_RIGHT] and player.right < WIDTH:
        player.x += 5


    # Enemy Movement
    move_down = False
    for enemy in enemies:
        enemy.x += enemies_speed * enemies_direction
        if enemy.right >= WIDTH or enemy.left <= 0:
            move_down = True

    if move_down:
        enemies_direction *= -1
        for enemy in enemies:
            enemy.y += 20 

    # --- NEW: Check for Game Over ---
    for enemy in enemies:
        if enemy.colliderect(player) or enemy.bottom >= HEIGHT:
            print(f"GAME OVER! Final Score: {score}")
            running = False

    # Bullet Movement & Collision
    for bullet in bullets[:]:
        bullet.y -= 7
        if bullet.bottom < 0:
            bullets.remove(bullet)
        
        # Check if bullet hits enemy
        for enemy in enemies[:]:
            if bullet.colliderect(enemy):
                enemies.remove(enemy)
                bullets.remove(bullet)
                break

    if len(enemies) == 0:
        enemies_speed += 0.5 # Make the next wave faster!
        create_enemies()
    # 4. Drawing
    pygame.draw.rect(screen, GREEN, player)
    for enemy in enemies:
        screen.blit(enemy_img, (enemy.x, enemy.y))
    for bullet in bullets:
        pygame.draw.rect(screen, YELLOW, bullet)

    pygame.display.flip()
    clock.tick(FPS)
pygame.quit()