import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import pygame
import sys
import random
import math

pygame.init()

# === 定数 ===
WIDTH, HEIGHT = 800, 400
WHITE = (255, 255, 255)
BLUE = (50, 100, 255)
RED = (255, 80, 80)
BLACK = (0, 0, 0)
GREEN = (80, 180, 80)
YELLOW = (255, 230, 0)
CYAN = (0, 255, 255)
FPS = 60


# === プレイヤークラス ===
class Player:
    def __init__(self, x, y, w, h, floor_y):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = BLUE
        self.vel_y = 0
        self.gravity = 0.8
        self.jump_power = -15
        self.double_jump_power = -12
        self.jump_count = 0
        self.max_jumps = 1
        self.on_ground = True
        self.floor_y = floor_y

        # 画像設定
        self.img = pygame.image.load("fig/5.png").convert_alpha()
        self.img = pygame.transform.flip(self.img, True, False)
        self.img = pygame.transform.scale(self.img, (w, h))

        # パワーアップ管理
        self.powerup_active = False
        self.powerup_timer = 0

    def handle_input(self):
        if self.jump_count < self.max_jumps:
            if self.jump_count == 0:
                self.vel_y = self.jump_power
            else:
                self.vel_y = self.double_jump_power
            self.jump_count += 1
            self.on_ground = False

    def activate_powerup(self, duration=600):
        self.powerup_active = True
        self.max_jumps = 2
        self.powerup_timer = duration
        self.color = CYAN

    def update(self):
        self.rect.y += self.vel_y
        self.vel_y += self.gravity

        # 地面に接地
        if self.rect.bottom >= self.floor_y:
            self.rect.bottom = self.floor_y
            self.vel_y = 0
            self.jump_count = 0
            self.on_ground = True

        # パワーアップ時間
        if self.powerup_active:
            self.powerup_timer -= 1
            if self.powerup_timer <= 0:
                self.powerup_active = False
                self.max_jumps = 1
                self.color = BLUE

    def draw(self, screen):
        screen.blit(self.img, self.rect.topleft)

    def get_rect(self):
        return self.rect

# === 敵クラス ===
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
    def __init__(self, x, y, w, h, speed, enemy_type="normal"):
        self.rect = pygame.Rect(x, y, w, h)
        self.type = enemy_type  # "normal" or "big"
        self.color = RED if self.type == "normal" else (180, 0, 0) #normalじゃない敵の色を濃くする
        self.speed = speed

    def update(self, current_speed):
        self.rect.x -= int(current_speed)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def get_rect(self) -> pygame.Rect:
        """衝突判定用の矩形を返す。"""
        return self.rect #衝突判定

# === コインクラス（回転アニメーション付き） ===
class Coin:
    def __init__(self, x, y, radius, speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.frame = random.randint(0, 60)
        self.speed = speed

    def update(self):
        self.x -= self.speed
        self.frame += 1

    def draw(self, screen):
        angle = (self.frame % 60) / 60 * math.pi * 2
        scale_x = abs(math.sin(angle))
        width = max(2, int(self.radius * 2 * scale_x))
        height = self.radius * 2
        pygame.draw.ellipse(screen, YELLOW, (self.x - width // 2, self.y - height // 2, width, height))

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

class EnemyJump:
    """画面手前で光り、着地状態なら勝手にジャンプする敵。

    - 光る距離は固定（0 < x < 250）
    - ジャンプは on_ground が True のときに一回だけ発動し、着地で再度可能になる
    """
    def __init__(self, x: int, y: int, floor_y: int) -> None:
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
        self.floor_y = floor_y

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
            if self.y + self.size >= self.floor_y:  #敵の下端が床の座標に到達したら
                self.y = self.floor_y - self.size  #床に接する位置に修正
                self.vel_y = 0  #重力リセット
                self.on_ground = True  #再度ジャンプ可能状態

    def draw(self, screen: pygame.Surface) -> None:
        """敵（四角）を描画する。光っているときは黄色で表示。"""
        color = (255, 255, 0) if self.glow else self.color  #光っているとき黄色
        pygame.draw.rect(screen, color, (self.x, self.y, self.size, self.size))  #四角形(画面描画,色,(左上の座標,幅と高さは正方形のため同じ))

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.size, self.size)

# === アイテムクラス ===
class Item:
    def __init__(self, x, y, w, h, speed, color=CYAN):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.speed = speed 

    def update(self, current_speed):
        self.rect.x -= int(current_speed)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

# === ゲーム管理クラス ===
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("ジャンプ強化アクション")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 40)

        self.floor_y = HEIGHT - 40
        self.bg_scroll = 0
        self.bg_speed = 4

        self.player = Player(100, self.floor_y - 60, 40, 60, self.floor_y)

        self.enemies = []
        self.jump_enemies = []
        self.items = []
        self.coins = []

        self.enemy_timer = 0
        self.item_timer = 0
        self.jump_enemy_timer = 0
        self.coin_timer = 0

        self.score = 0
        self.distance = 0
        self.coin_score = 0
        self.game_over = False

    def reset(self):
        self.__init__()

    def spawn_enemy(self):
        if self.enemy_timer > 90:
            x = WIDTH + random.randint(0, 300)
            if self.score >= 1000 and random.random() < 0.3:
                w, h = 60, 60
                enemy_type = "big"
            else:
                w, h = 40, 40
                enemy_type = "normal"
            y = self.floor_y - h
            self.enemies.append(Enemy(x, y, w, h, self.bg_speed, enemy_type))
            self.enemy_timer = 0

    def spawn_jump_enemy(self):
        # スコアが一定以上でジャンプ敵が出るようにする
        if self.score >= 500 and self.jump_enemy_timer > 500:
            x = WIDTH + random.randint(0, 200)
            y = self.floor_y - 40
            self.jump_enemies.append(EnemyJump(x, y, self.floor_y))
            self.jump_enemy_timer = 0

    def spawn_item(self):
        if self.item_timer > 600:
            x = WIDTH + random.randint(0, 300)
            y = self.floor_y - random.randint(80, 150)
            self.items.append(Item(x, y, 30, 30, self.bg_speed + 1))
            self.item_timer = 0

    def spawn_coins(self):
        """3連続・波型コインを生成"""
        if self.coin_timer > 300:
            base_y = random.randint(self.floor_y - 150, self.floor_y - 60)
            base_x = WIDTH + random.randint(0, 200)
            offset_y = [0, -20, +20]
            offset_x = [0, 40, 80]
            for i in range(3):
                cx = base_x + offset_x[i]
                cy = base_y + offset_y[i]
                self.coins.append(Coin(cx, cy, 10, self.bg_speed))
            self.coin_timer = 0

    def update(self):
        keys = pygame.key.get_pressed()

        if self.game_over:
            return

        if not self.game_over:
            self.player.update()
            self.bg_scroll -= self.bg_speed
            if self.bg_scroll <= -WIDTH:
                self.bg_scroll = 0

            self.enemy_timer += 1
            self.item_timer += 1
            self.jump_enemy_timer += 1
            self.coin_timer += 1

            self.spawn_enemy()
            self.spawn_item()
            self.spawn_jump_enemy()
            self.spawn_coins()

        current_speed = self.bg_speed
        if self.score >= 1500:
            current_speed = self.bg_speed * 1.5

         # 敵更新
        for enemy in self.enemies:
            enemy.update(current_speed)

        for jenemy in self.jump_enemies:
            jenemy.update(current_speed)

        # アイテム更新
        for item in self.items:
            item.update(current_speed)

        #コイン更新
        for coin in self.coins:
            coin.speed = current_speed
            coin.update()
            
        # 敵削除
        self.enemies = [e for e in self.enemies if e.get_rect().right > 0]
        self.jump_enemies = [j for j in self.jump_enemies if j.get_rect().right > 0]
        self.items = [i for i in self.items if i.rect.right > 0]
        self.coins = [c for c in self.coins if c.x > -c.radius * 2]

        self.distance += self.bg_speed / 10
        self.score = int(self.distance) + self.coin_score

        # === 敵との接触判定（踏んだ場合は足場として扱う） ===
        player_on_enemy = False
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                # 上から接触した場合
                if self.player.vel_y > 0 and self.player.rect.bottom - enemy.rect.top < 20:
                    self.player.rect.bottom = enemy.rect.top
                    self.player.vel_y = 0
                    self.player.jump_count = 0
                    player_on_enemy = True
                else:
                    # 横または下から接触 → ゲームオーバー
                    self.game_over = True

        #ジャンプ敵との衝突（どの方向でも即ゲームオーバー）
        for jenemy in self.jump_enemies:
            if self.player.rect.colliderect(jenemy.get_rect()):
                self.game_over = True
        
        # 敵の上にいない＆地面にもいないときは重力で落下
        if not player_on_enemy and self.player.rect.bottom < self.floor_y:
            self.player.on_ground = False

        # === アイテム取得判定 ===
        for item in self.items[:]:
            if self.player.rect.colliderect(item.rect):
                self.player.activate_powerup(duration=600)
                self.items.remove(item)

        player_rect = self.player.get_rect()
        for coin in self.coins[:]:
            if player_rect.colliderect(coin.get_rect()):
                self.coin_score += 50
                self.coins.remove(coin)

    def draw(self):
        self.screen.fill(WHITE)
        pygame.draw.rect(self.screen, GREEN, (self.bg_scroll, self.floor_y, WIDTH, 50))
        pygame.draw.rect(self.screen, GREEN, (self.bg_scroll + WIDTH, self.floor_y, WIDTH, 50))

        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for jenemy in self.jump_enemies:
            jenemy.draw(self.screen)
        for item in self.items:
            item.draw(self.screen)
        for coin in self.coins:
            coin.draw(self.screen)
            
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))

        jump_text = self.font.render(f"Max Jumps: {self.player.max_jumps}", True, BLACK)
        self.screen.blit(jump_text, (10, 50))

        if self.player.powerup_active:
            timer_text = self.font.render(f"Power Time: {self.player.powerup_timer // 60}", True, CYAN)
            self.screen.blit(timer_text, (10, 90))

        if self.game_over:
            over_text = self.font.render("GAME OVER - Press R to Restart", True, RED)
            self.screen.blit(over_text, (WIDTH // 2 - 220, HEIGHT // 2 - 20))

        pygame.display.update()

    def run(self):
        while True:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # KEYDOWN は常にチェックして内部で game_over を判定する
                if event.type == pygame.KEYDOWN:
                    if not self.game_over:
                        if event.key == pygame.K_SPACE:
                            # ジャンプ（押した瞬間）
                            self.player.handle_input()
                    else:
                        # game_over == True のときのみ R でリセット
                        if event.key == pygame.K_r:
                            self.reset()

            self.update()
            self.draw()


# === メイン処理 ===
if __name__ == "__main__":
    Game().run() 

