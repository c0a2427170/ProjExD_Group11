import pygame
import sys
import random
import os
import math

pygame.init()

# 画面サイズ
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("横スクロールアクションゲーム")

# FPS
clock = pygame.time.Clock()

# 色
WHITE = (255, 255, 255)
BLUE = (50, 100, 255)
RED = (255, 80, 80)
BLACK = (0, 0, 0)
GREEN = (80, 180, 80)
YELLOW = (255, 230, 0)

# 床
floor_y = HEIGHT - 40

# プレイヤー設定
player_size = (40, 60)
player_x = 100
player_y = floor_y - player_size[1]
player_vel_y = 0
gravity = 0.8
jump_power = -15
on_ground = True

# 背景スクロール
bg_scroll = 0
bg_speed = 4

# 敵設定
enemy_size = (40, 40)
enemy_list = []
enemy_spawn_timer = 0

# --- コイン設定 ---
coin_radius = 10
coin_list = []
coin_spawn_timer = 0  # コイン出現タイマー
COIN_INTERVAL = 100    # コインが出現する間隔（フレーム）
COIN_SPEED = bg_speed  # 背景と同じ速度で流れる

# スコア
font = pygame.font.SysFont(None, 40)
score = 0
coin_score = 0  # コインによる加算点
distance = 0

# ゲーム状態
game_over = False

def reset_game():
    global player_x, player_y, player_vel_y, on_ground
    global bg_scroll, enemy_list, coin_list
    global score, distance, coin_score, game_over
    player_x = 100
    player_y = floor_y - player_size[1]
    player_vel_y = 0
    on_ground = True
    bg_scroll = 0
    enemy_list = []
    coin_list = []
    score = 0
    distance = 0
    coin_score = 0
    game_over = False

# メインループ
while True:
    clock.tick(60)
    screen.fill(WHITE)

    # イベント処理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            reset_game()

    keys = pygame.key.get_pressed()
    if not game_over:
        # ジャンプ
        if keys[pygame.K_SPACE] and on_ground:
            player_vel_y = jump_power
            on_ground = False

        # 重力
        player_y += player_vel_y
        player_vel_y += gravity

        # 着地判定
        if player_y + player_size[1] >= floor_y:
            player_y = floor_y - player_size[1]
            player_vel_y = 0
            on_ground = True

        # 背景スクロール
        bg_scroll -= bg_speed
        if bg_scroll <= -WIDTH:
            bg_scroll = 0

        # 敵生成
        enemy_spawn_timer += 1
        if enemy_spawn_timer > 90:
            enemy_x = WIDTH + random.randint(0, 300)
            enemy_y = floor_y - enemy_size[1]
            enemy_list.append([enemy_x, enemy_y])
            enemy_spawn_timer = 0

        # 敵移動
        for enemy in enemy_list:
            enemy[0] -= bg_speed

        # 敵削除
        enemy_list = [e for e in enemy_list if e[0] > -enemy_size[0]]

         # --- コイン生成（3連続・波型）---
        coin_spawn_timer += 1
        if coin_spawn_timer > COIN_INTERVAL:
            base_y = random.randint(floor_y - 150, floor_y - 60)
            base_x = WIDTH + random.randint(0, 200)
            offset_y = [0, -20, +20]
            offset_x = [0, 40, 80]

            for i in range(3):
                cx = base_x + offset_x[i]
                cy = base_y + offset_y[i]
                coin_list.append([cx, cy, random.randint(0, 60)])  # frame値を追加

            coin_spawn_timer = 0

        # --- コイン移動＆回転アニメ更新 ---
        for coin in coin_list:
            coin[0] -= COIN_SPEED
            coin[2] += 1

        # --- コイン削除（画面外） ---
        coin_list = [c for c in coin_list if c[0] > -coin_radius * 2]

        # スコア・距離
        distance += bg_speed / 10
        score = int(distance) + coin_score

        # 衝突判定
        player_rect = pygame.Rect(player_x, player_y, *player_size)
        for enemy in enemy_list:
            enemy_rect = pygame.Rect(enemy[0], enemy[1], *enemy_size)
            if player_rect.colliderect(enemy_rect):
                game_over = True

        # --- コイン獲得判定 ---
        for coin in coin_list[:]:
            coin_rect = pygame.Rect(coin[0] - coin_radius, coin[1] - coin_radius, coin_radius * 2, coin_radius * 2)
            if player_rect.colliderect(coin_rect):
                coin_score += 50  # スコア加算
                coin_list.remove(coin)

    # ===== 描画 =====
    # 背景（床のスクロール）
    pygame.draw.rect(screen, GREEN, (bg_scroll, floor_y, WIDTH, 50))
    pygame.draw.rect(screen, GREEN, (bg_scroll + WIDTH, floor_y, WIDTH, 50))

    # プレイヤー
    pygame.draw.rect(screen, BLUE, (player_x, player_y, *player_size))

    # 敵
    for enemy in enemy_list:
        pygame.draw.rect(screen, RED, (enemy[0], enemy[1], *enemy_size))
    
    # --- コイン描画 ---
    for coin in coin_list:
        cx, cy, frame = coin
        angle = (frame % 60) / 60 * math.pi * 2
        scale_x = abs(math.sin(angle))  # 横幅を周期的に変化させる
        width = max(2, int(coin_radius * 2 * scale_x))  # 最小2px
        height = coin_radius * 2
        coin_surface = pygame.Surface((width, height))
        coin_surface.fill(YELLOW)
        pygame.draw.ellipse(screen, YELLOW, (cx - width//2, cy - height//2, width, height))

    # スコア表示 
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    # ゲームオーバー表示
    if game_over:
        over_text = font.render("GAME OVER - Press R to Restart", True, RED)
        screen.blit(over_text, (WIDTH//2 - 220, HEIGHT//2 - 20))

    pygame.display.update()

