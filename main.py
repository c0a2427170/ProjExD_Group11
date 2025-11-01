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
jump_power = -15
on_ground = True

# 背景スクロール
bg_scroll = 0
bg_speed = 4

# 敵設定
enemy_size = (40, 40)
enemy_list = []
enemy_spawn_timer = 0

class BigEnemy:
    def __init__(self, x, y, score):
        self.normal_size = (40, 40)
        self.big_size = (60, 60)
        self.x = x
        self.y = y

        if score >= 500 and random.random() < 0.3:
            self.size = self.big_size
            self.type = "big"
            self.y = floor_y - self.size[1]  #敵の高さ
        else:
            self.size = self.normal_size
            self.type = "normal"
            self.y = floor_y - self.size[1]

    def get_rect(self):
        return pygame.Rect(self.x, self.y, *self.size)  #衝突判定

    def draw(self, screen):
        color = RED if self.type == "normal" else (180, 0, 0)  #大きい敵なら濃い赤色に
        pygame.draw.rect(screen, color, (self.x, self.y, *self.size))  #四角の左上x,y座標を展開


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
            enemy_list.append(BigEnemy(enemy_x, enemy_y, score))  #敵が大きいか小さいかが自動で決まる
            enemy_spawn_timer = 0

        # 敵移動
        for enemy in enemy_list:
            enemy.x -= bg_speed

        # 敵削除
        enemy_list = [e for e in enemy_list if e.x > -e.size[0]]

        # スコア・距離
        distance += bg_speed / 10
        score = int(distance)

        # 衝突判定
        player_rect = pygame.Rect(player_x, player_y, *player_size)
        for enemy in enemy_list:
            if player_rect.colliderect(enemy.get_rect()):
                game_over = True

    # ===== 描画 =====
    # 背景（床のスクロール）
    pygame.draw.rect(screen, GREEN, (bg_scroll, floor_y, WIDTH, 50))
    pygame.draw.rect(screen, GREEN, (bg_scroll + WIDTH, floor_y, WIDTH, 50))

    # プレイヤー
    pygame.draw.rect(screen, BLUE, (player_x, player_y, *player_size))

    # 敵
    for enemy in enemy_list:
        enemy.draw(screen)

    # スコア表示
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    # ゲームオーバー表示
    if game_over:
        over_text = font.render("GAME OVER - Press R to Restart", True, RED)
        screen.blit(over_text, (WIDTH//2 - 220, HEIGHT//2 - 20))

    pygame.display.update()
