import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import pygame
import sys
import random

pygame.init()

# === 定数 ===
WIDTH, HEIGHT = 800, 400
WHITE = (255, 255, 255)
BLUE = (50, 100, 255)
RED = (255, 80, 80)
BLACK = (0, 0, 0)
GREEN = (80, 180, 80)
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

    def handle_input(self, keys):
        if keys[pygame.K_SPACE]:
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


# === 敵クラス ===
class Enemy:
    def __init__(self, x, y, w, h, speed):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = RED
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


# === アイテムクラス ===
class Item:
    def __init__(self, x, y, w, h, speed, color=CYAN):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed

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
        self.items = []
        self.enemy_timer = 0
        self.item_timer = 0
        self.score = 0
        self.distance = 0
        self.game_over = False

    def reset(self):
        self.__init__()

    def spawn_enemy(self):
        if self.enemy_timer > 90:
            x = WIDTH + random.randint(0, 300)
            y = self.floor_y - 40
            self.enemies.append(Enemy(x, y, 40, 40, self.bg_speed))
            self.enemy_timer = 0

    def spawn_item(self):
        if self.item_timer > 600:
            x = WIDTH + random.randint(0, 300)
            y = self.floor_y - random.randint(80, 150)
            self.items.append(Item(x, y, 30, 30, self.bg_speed + 1))
            self.item_timer = 0

    def update(self):
        keys = pygame.key.get_pressed()

        if not self.game_over:
            self.player.update()
            self.bg_scroll -= self.bg_speed
            if self.bg_scroll <= -WIDTH:
                self.bg_scroll = 0

            self.enemy_timer += 1
            self.item_timer += 1
            self.spawn_enemy()
            self.spawn_item()

            for enemy in self.enemies:
                enemy.update()
            for item in self.items:
                item.update()

            # 敵・アイテムが画面外に出たら削除
            self.enemies = [e for e in self.enemies if e.rect.right > 0]
            self.items = [i for i in self.items if i.rect.right > 0]

            self.distance += self.bg_speed / 10
            self.score = int(self.distance)

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

            # 敵の上にいない＆地面にもいないときは重力で落下
            if not player_on_enemy and self.player.rect.bottom < self.floor_y:
                self.player.on_ground = False

            # === アイテム取得判定 ===
            for item in self.items[:]:
                if self.player.rect.colliderect(item.rect):
                    self.player.activate_powerup(duration=600)
                    self.items.remove(item)

        else:
            if keys[pygame.K_r]:
                self.reset()

    def draw(self):
        self.screen.fill(WHITE)
        pygame.draw.rect(self.screen, GREEN, (self.bg_scroll, self.floor_y, WIDTH, 50))
        pygame.draw.rect(self.screen, GREEN, (self.bg_scroll + WIDTH, self.floor_y, WIDTH, 50))

        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for item in self.items:
            item.draw(self.screen)

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
                if not self.game_over and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player.handle_input(pygame.key.get_pressed())

            self.update()
            self.draw()


# === メイン処理 ===
if __name__ == "__main__":
    Game().run()
