import pygame
import sys
import random

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

# 床
floor_y = HEIGHT - 40

# プレイヤー設定
player_size = (40, 60)
player_x = 100
player_y = floor_y - player_size[1]
player_vel_y = 0
gravity = 0.8
jump_power = -15 # 通常ジャンプの力
double_jump_power = -10 # 2段目ジャンプの力(弱ジャンプ)
on_ground = True

# 2段ジャンプ用
jump_count = 0          # 現在のジャンプ回数
max_jumps = 2           # 最大ジャンプ回数（2段ジャンプ）

# 背景スクロール
bg_scroll = 0
bg_speed = 4

# 敵設定
enemy_size = (40, 40)
enemy_list = []
enemy_spawn_timer = 0

# スコア
font = pygame.font.SysFont(None, 40)
score = 0
distance = 0

# ゲーム状態
game_over = False

def reset_game():
    global player_x, player_y, player_vel_y, on_ground, bg_scroll, enemy_list, score, distance, game_over
    player_x = 100
    player_y = floor_y - player_size[1]
    player_vel_y = 0
    on_ground = True
    bg_scroll = 0
    enemy_list = []
    score = 0
    distance = 0
    game_over = False
    jump_count = 0

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
        
        if not game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if jump_count < max_jumps:
                    # 1段目 or 2段目を区別
                    if jump_count == 0:
                        player_vel_y = jump_power
                    else:
                        player_vel_y = double_jump_power
                    jump_count += 1
                    on_ground = False

    keys = pygame.key.get_pressed()
    if not game_over:
        # # ジャンプ
        # if keys[pygame.K_SPACE]:
        #     if jump_count < max_jumps:
        #         if jump_count == 0:
        #             player_vel_y = jump_power  # 1段目
        #         else:
        #             player_vel_y = double_jump_power  # 2段目(弱ジャンプ)
        #         jump_count += 1
        #         on_ground = False

        # 重力
        player_y += player_vel_y
        player_vel_y += gravity

        # 着地判定
        if player_y + player_size[1] >= floor_y:
            player_y = floor_y - player_size[1]
            player_vel_y = 0
            on_ground = True
            jump_count = 0 # 地面に着いたらジャンプ回数をリセット


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

        # スコア・距離
        distance += bg_speed / 10
        score = int(distance)

        # 衝突判定
        player_rect = pygame.Rect(player_x, player_y, *player_size)
        for enemy in enemy_list:
            enemy_rect = pygame.Rect(enemy[0], enemy[1], *enemy_size)
            if player_rect.colliderect(enemy_rect):
                game_over = True

    # ===== 描画 =====
    # 背景（床のスクロール）
    pygame.draw.rect(screen, GREEN, (bg_scroll, floor_y, WIDTH, 50))
    pygame.draw.rect(screen, GREEN, (bg_scroll + WIDTH, floor_y, WIDTH, 50))

    # プレイヤー
    pygame.draw.rect(screen, BLUE, (player_x, player_y, *player_size))

    # 敵
    for enemy in enemy_list:
        pygame.draw.rect(screen, RED, (enemy[0], enemy[1], *enemy_size))

    # スコア表示
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    # ゲームオーバー表示
    if game_over:
        over_text = font.render("GAME OVER - Press R to Restart", True, RED)
        screen.blit(over_text, (WIDTH//2 - 220, HEIGHT//2 - 20))

    pygame.display.update()
