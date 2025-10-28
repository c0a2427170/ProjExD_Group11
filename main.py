import pygame
import sys
import random
import os # ファイル操作のために追加

pygame.init()

# ミキサー（音）の初期化
pygame.mixer.init()

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

# ハイスコア機能のための関数と設定
HIGHSCORE_FILE = "highscore.txt"

def load_highscore():
    """
    ハイスコアファイルを読み込み、スコアを返す。ファイルがなければ 0 を返す。
    """
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "r") as f:
            try:
                # ファイルから読み込んだ文字列を整数に変換
                return int(f.read())
            except ValueError: # ファイル内容が数字でなかった場合
                return 0
    return 0

def save_highscore(score):
    """
    新しいハイスコアをファイルに書き込む。
    """
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))
# ==================================

# 音声ファイルのロード
try:
    # BGM（メインループで再生）
    pygame.mixer.music.load("~~~.mp3")  #ここにメインbgmのファイル名を入れる
    # # 効果音
    jump_sound = pygame.mixer.Sound("---.mp3")  #ここにジャンプの効果音のファイル名を入れる
    game_over_sound = pygame.mixer.Sound("===.mp3")  #ここにゲームオーバー時に流すbgmファイル名を入れる
except pygame.error as e:
    print(f"音楽ファイルのロードに失敗しました: {e}")
    # ファイルが見つからない場合は、エラーを無視してゲームを続行
    jump_sound = None
    game_over_sound = None

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

# スコア
font = pygame.font.SysFont(None, 40)
score = 0
distance = 0
high_score = load_highscore() # <-- 起動時にハイスコアをロード

# ゲーム状態
game_over = False

# BGMの再生開始 (ループ再生: -1)
if pygame.mixer.music.get_busy() == False:
    pygame.mixer.music.play(-1)

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
    
    # BGMの再生再開
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.play(-1)

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
            # ジャンプ効果音の再生
            if jump_sound:
                jump_sound.play()

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

        # スコア・距離
        distance += bg_speed / 10
        score = int(distance)

        # 衝突判定
        player_rect = pygame.Rect(player_x, player_y, *player_size)
        for enemy in enemy_list:
            enemy_rect = pygame.Rect(enemy[0], enemy[1], *enemy_size)
            if player_rect.colliderect(enemy_rect):
                game_over = True
                
                # ==================================================
                # ハイスコア更新チェックと保存
                if score > high_score:
                    high_score = score
                    save_highscore(high_score)
                # ==================================================
                
                # ゲームオーバー時の処理
                # BGMの停止
                pygame.mixer.music.stop()
                # ゲームオーバー効果音の再生
                if game_over_sound:
                    game_over_sound.play()

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

    # ==================================================
    # ハイスコア表示
    highscore_text = font.render(f"High Score: {high_score}", True, BLACK)
    # 画面右上に表示
    screen.blit(highscore_text, (WIDTH - highscore_text.get_width() - 10, 10))
    # ==================================================

    # ゲームオーバー表示
    if game_over:
        over_text = font.render("GAME OVER - Press R to Restart", True, RED)
        screen.blit(over_text, (WIDTH//2 - 220, HEIGHT//2 - 20))
        
        # ゲームオーバー時にハイスコアを更新した場合は強調表示
        if score == high_score:
             new_record_text = font.render("NEW HIGH SCORE!", True, RED)
             screen.blit(new_record_text, (WIDTH//2 - new_record_text.get_width()//2, HEIGHT//2 + 30))

    pygame.display.update()