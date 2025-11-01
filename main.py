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
jump_enemy_list = []
jump_enemy_spawn_timer = 0
current_speed = bg_speed

class Enemy:
    """通常の地上敵。score に応じて一定確率で大きい敵になる。

    Attributes
    ----------
    x, y : int
        敵の左上座標
    size : tuple[int, int]
        (幅, 高さ)
    type : str
        "normal" または "big"
    """
    def __init__(self, x: int, y: int, score: int) -> None:
        """Enemy を初期化する。

        Parameters
        ----------
        x, y : int
            初期座標（通常は画面右外）
        score : int
            現在のスコア（大きい敵の出現判定に使用）
        """
        self.normal_size = (40, 40)  #通常サイズの敵も入れる
        self.big_size = (60, 60)  #大きいサイズの敵
        self.x = x
        self.y = y

        if score >= 1000 and random.random() < 0.3:  #score1000以上の時30%の確率で大きい敵が出現
            self.size = self.big_size
            self.type = "big"
            self.y = floor_y - self.size[1]  #敵の高さ
        else:
            self.size = self.normal_size
            self.type = "normal"
            self.y = floor_y - self.size[1]

    def get_rect(self) -> pygame.Rect:
        """衝突判定用の矩形を返す。"""
        return pygame.Rect(self.x, self.y, *self.size)  #衝突判定

    def draw(self, screen: pygame.Surface) -> None:
        """敵を描画する。"""
        color = RED if self.type == "normal" else (180, 0, 0)  #大きい敵なら濃い赤色に
        pygame.draw.rect(screen, color, (self.x, self.y, *self.size))  #四角の左上x,y座標を展開

class EnemyJump:
    """画面手前で光り、着地状態なら勝手にジャンプする敵。

    - 光る距離は固定（0 < x < 250）
    - ジャンプは on_ground が True のときに一回だけ発動し、着地で再度可能になる
    """
    def __init__(self, x: int, y: int) -> None:
        """EnemyJump を初期化する。

        Parameters
        ----------
        x, y : int
            初期座標
        """
        self.x = x
        self.y = y
        self.size = 40
        self.color = RED
        self.vel_y = 0
        self.on_ground = True
        self.glow = False

    def update(self, speed: float) -> None:
        """毎フレーム呼ぶ更新処理。

        - 横方向移動（speed）
        - 光る判定（手前に来たら glow = True）
        - on_ground のときのみジャンプを起こす
        - 空中時は重力で落下させ、着地で復帰
        """
        self.x -= speed  # 横移動

        # 光る条件
        if 0 < self.x < 250:  # 画面手前で光る

            self.glow = True
            # 光ったらジャンプ（1回だけ）
            if self.on_ground:
                self.vel_y = -23  #負の値が上方向なため大きいほどジャンプ力が大きくなる
                self.on_ground = False  #jumpしたため地面にいない状態
        else:
            self.glow = False  #画面手前にいないときは赤色のまま

        # 重力
        if not self.on_ground:  #空中にいるとき
            self.vel_y += 0.8   #重力を加算していく(下方向の加速度)
            self.y += self.vel_y  #位置更新
            if self.y + self.size >= floor_y:  #敵の下端が床の座標に到達したら
                self.y = floor_y - self.size  #床に接する位置に修正
                self.vel_y = 0  #重力リセット
                self.on_ground = True  #再度ジャンプ可能状態

    def draw(self, screen: pygame.Surface) -> None:
        """敵（四角）を描画する。光っているときは黄色で表示。"""
        color = (255, 255, 0) if self.glow else self.color  #光っているとき黄色
        pygame.draw.rect(screen, color, (self.x, self.y, self.size, self.size))  #四角形(画面描画,色,(左上の座標,幅と高さは正方形のため同じ))



# スコア
font = pygame.font.SysFont(None, 40)
score = 0
distance = 0

# ゲーム状態
game_over = False

def reset_game():
    global player_x, player_y, player_vel_y, on_ground, bg_scroll
    global enemy_list, jump_enemy_list, score, distance, game_over
    global enemy_spawn_timer, jump_enemy_spawn_timer,current_speed

    player_x = 100
    player_y = floor_y - player_size[1]
    player_vel_y = 0
    on_ground = True
    bg_scroll = 0
    enemy_list = []
    enemy_spawn_timer = 0
    jump_enemy_list = []
    jump_enemy_spawn_timer = 0
    score = 0
    distance = 0
    current_speed = bg_speed
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
        bg_scroll -= current_speed
        if bg_scroll <= -WIDTH:
            bg_scroll = 0

        # 敵生成
        enemy_spawn_timer += 1
        if enemy_spawn_timer > 100:
            enemy_x = WIDTH + random.randint(0, 300)
            enemy_y = floor_y - enemy_size[1]
            enemy_list.append(Enemy(enemy_x, enemy_y, score))  #敵が大きいか小さいかが自動で決まる
            enemy_spawn_timer = 0

        # EnemyJump 生成
        jump_enemy_spawn_timer += 1
        if score >= 500 and jump_enemy_spawn_timer > 500:  # 500フレームごとに出現
            enemy_x = WIDTH + random.randint(0, 200)
            enemy_y = floor_y - 40
            jump_enemy_list.append(EnemyJump(enemy_x, enemy_y))
            jump_enemy_spawn_timer = 0

        # スコア・距離
        distance += bg_speed / 10
        score = int(distance)

        #スピード上昇
        if score >= 1500:
            current_speed = bg_speed * 1.5

        # 敵移動
        for enemy in enemy_list:
            enemy.x -= current_speed

        #発光ジャンプ
        for enemy in jump_enemy_list:
            enemy.update(current_speed)  # 横移動＋ジャンプ＋重力

        # 敵削除
        enemy_list = [e for e in enemy_list if e.x > -e.size[0]]
        jump_enemy_list = [e for e in jump_enemy_list if e.x + e.size > 0]

        # 衝突判定
        player_rect = pygame.Rect(player_x, player_y, *player_size)
        for enemy in enemy_list:
            if player_rect.colliderect(enemy.get_rect()):
                game_over = True
        
        for enemy in jump_enemy_list:
            if player_rect.colliderect(pygame.Rect(enemy.x, enemy.y, enemy.size, enemy.size)):
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

    #ジャンプする敵
    for enemy in jump_enemy_list:
        enemy.draw(screen)  # 光る敵も描画

    # スコア表示
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    # ゲームオーバー表示
    if game_over:
        over_text = font.render("GAME OVER - Press R to Restart", True, RED)
        screen.blit(over_text, (WIDTH//2 - 220, HEIGHT//2 - 20))

    pygame.display.update()
