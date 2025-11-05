import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
import pygame
import sys
import random
import math

pygame.init()
# ミキサー（音）の初期化
pygame.mixer.init()

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

# === ハイスコア機能 ===
HIGHSCORE_FILE = "highscore.txt"

def load_highscore():
    """
    ハイスコアファイルを読み込み、スコアを返す。ファイルがなければ 0 を返す。
    """
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "r") as f:
            try:
                return int(f.read())
            except ValueError:
                return 0
    return 0

def save_highscore(score):
    """
    新しいハイスコアをファイルに書き込む。
    """
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))
# ==================================


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
        try:
            self.img = pygame.image.load("fig/5.png").convert_alpha()
            self.img = pygame.transform.flip(self.img, True, False)
            self.img = pygame.transform.scale(self.img, (w, h))
        except pygame.error as e:
            print(f"プレイヤー画像のロードに失敗: {e}")
            self.img = None # 画像がなくても四角形で描画するフォールバック

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
            return True # ジャンプ音を鳴らすために成功したことを返す
        return False

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
        if self.img:
            screen.blit(self.img, self.rect.topleft)
        else:
            # 画像ロード失敗時のフォールバック
            pygame.draw.rect(screen, self.color, self.rect)

    def get_rect(self):
        return self.rect

# === 敵クラス ===
class Enemy:
    """通常の地上敵。"""
    def __init__(self, x, y, w, h, speed, enemy_type="normal"):
        self.rect = pygame.Rect(x, y, w, h)
        self.type = enemy_type
        self.color = RED if self.type == "normal" else (180, 0, 0)
        self.speed = speed

    def update(self, current_speed):
        self.rect.x -= int(current_speed)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def get_rect(self) -> pygame.Rect:
        return self.rect

# === コインクラス（回転アニメーション付き）===
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

# === ジャンプ敵クラス ===
class EnemyJump:
    """画面手前で光り、着地状態なら勝手にジャンプする敵。"""
    def __init__(self, x: int, y: int, floor_y: int) -> None:
        self.x = x
        self.y = y
        self.size = 40
        self.color = RED
        self.vel_y = 0
        self.on_ground = True
        self.glow = False
        self.floor_y = floor_y

    def update(self, speed: float) -> None:
        self.x -= speed

        if 0 < self.x < 250:
            self.glow = True
            if self.on_ground:
                self.vel_y = -23
                self.on_ground = False
        else:
            self.glow = False

        if not self.on_ground:
            self.vel_y += 0.8
            self.y += self.vel_y
            if self.y + self.size >= self.floor_y:
                self.y = self.floor_y - self.size
                self.vel_y = 0
                self.on_ground = True

    def draw(self, screen: pygame.Surface) -> None:
        color = (255, 255, 0) if self.glow else self.color
        pygame.draw.rect(screen, color, (self.x, self.y, self.size, self.size))

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
        pygame.display.set_caption("ジャンプ強化アクション（音声・ハイスコア対応版）")
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
        
        # ハイスコア機能（統合）
        self.high_score = load_highscore()
        self.new_high_score_achieved = False # ハイスコア更新演出用

        # 音声ファイルのロード（統合）
        try:
            pygame.mixer.music.load("bgm1.mp3")
            self.jump_sound = pygame.mixer.Sound("bgm2.mp3")
            self.game_over_sound = pygame.mixer.Sound("bgm3.mp3")
            self.bgm_loaded = True
        except pygame.error as e:
            print(f"音楽ファイルのロードに失敗しました: {e}")
            self.jump_sound = None
            self.game_over_sound = None
            self.bgm_loaded = False

        # BGMの再生開始（統合）
        self.play_bgm()

    def play_bgm(self):
        if self.bgm_loaded and not pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.play(-1)
            except pygame.error as e:
                print(f"BGM再生失敗: {e}")

    def stop_bgm(self):
        if self.bgm_loaded:
            try:
                pygame.mixer.music.stop()
            except pygame.error:
                pass

    def reset(self):
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
        # self.high_score は維持
        self.new_high_score_achieved = False
        
        # BGMの再生再開（統合）
        self.play_bgm()


    def spawn_enemy(self):
        # (難易度調整：スコアが上がると敵の出現間隔を短くする)
        spawn_interval = max(45, 90 - (self.score // 100))
        if self.enemy_timer > spawn_interval:
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

    def handle_game_over(self):
        """ゲームオーバー処理（音声とハイスコア保存を統合）"""
        self.game_over = True
        self.stop_bgm()
        if self.game_over_sound:
            self.game_over_sound.play()
        
        # ハイスコア更新チェック（統合）
        if self.score > self.high_score:
            self.high_score = self.score
            save_highscore(self.high_score)
            self.new_high_score_achieved = True

    def update(self):
        if self.game_over:
            return

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

        for enemy in self.enemies:
            enemy.update(current_speed)
        for jenemy in self.jump_enemies:
            jenemy.update(current_speed)
        for item in self.items:
            item.update(current_speed)
        for coin in self.coins:
            coin.speed = current_speed
            coin.update()

        self.enemies = [e for e in self.enemies if e.get_rect().right > 0]
        self.jump_enemies = [j for j in self.jump_enemies if j.get_rect().right > 0]
        self.items = [i for i in self.items if i.rect.right > 0]
        self.coins = [c for c in self.coins if c.x > -c.radius * 2]

        self.distance += self.bg_speed / 10
        self.score = int(self.distance) + self.coin_score

        # === 衝突判定 ===
        player_on_enemy = False
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                if self.player.vel_y > 0 and self.player.rect.bottom - enemy.rect.top < 20:
                    self.player.rect.bottom = enemy.rect.top
                    self.player.vel_y = 0
                    self.player.jump_count = 0
                    player_on_enemy = True
                else:
                    self.handle_game_over() # ゲームオーバー処理

        for jenemy in self.jump_enemies:
            if self.player.rect.colliderect(jenemy.get_rect()):
                self.handle_game_over() # ゲームオーバー処理

        if not player_on_enemy and self.player.rect.bottom < self.floor_y:
            self.player.on_ground = False
        
        # (着地判定は Player.update() 内で行われる)

        # === アイテム・コイン取得 ===
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

        # スコア表示
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        self.screen.blit(score_text, (10, 10))

        # ハイスコア表示
        highscore_text = self.font.render(f"High Score: {self.high_score}", True, BLACK)
        self.screen.blit(highscore_text, (WIDTH - highscore_text.get_width() - 10, 10))

        # パワーアップ状態表示
        jump_text = self.font.render(f"Max Jumps: {self.player.max_jumps}", True, BLACK)
        self.screen.blit(jump_text, (10, 50))
        if self.player.powerup_active:
            timer_text = self.font.render(f"Power Time: {self.player.powerup_timer // 60}", True, CYAN)
            self.screen.blit(timer_text, (10, 90))

        # ゲームオーバー表示
        if self.game_over:
            over_text = self.font.render("GAME OVER - Press R to Restart", True, RED)
            over_rect = over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            self.screen.blit(over_text, over_rect)
            
            # ハイスコア更新演出
            if self.new_high_score_achieved:
                new_record_text = self.font.render("NEW HIGH SCORE!", True, RED)
                new_record_rect = new_record_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
                self.screen.blit(new_record_text, new_record_rect)

        pygame.display.update()

    def run(self):
        while True:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if not self.game_over:
                        if event.key == pygame.K_SPACE:
                            # ジャンプ
                            if self.player.handle_input():
                                if self.jump_sound:
                                    self.jump_sound.play()
                    else:
                        if event.key == pygame.K_r:
                            self.reset()

            self.update()
            self.draw()

# === メイン処理 ===
if __name__ == "__main__":
    Game().run()
