import pygame
import random
import math

# =====================
# 基本配置
# =====================
SIZE = 4
CELL = 110
PADDING = 15
BOARD_TOP = 120

WIDTH = SIZE * CELL + PADDING * 2
HEIGHT = BOARD_TOP + SIZE * CELL + PADDING + 20
FPS = 60

# 颜色
COLOR_BG = (187, 173, 160)
COLOR_EMPTY = (205, 193, 180)
COLOR_TEXT_DARK = (119, 110, 101)
COLOR_TEXT_LIGHT = (249, 246, 242)

TILE_COLORS = {
    0: COLOR_EMPTY, 2: (238, 228, 218), 4: (237, 224, 200),
    8: (242, 177, 121), 16: (245, 149, 99), 32: (246, 124, 95),
    64: (246, 94, 59), 128: (237, 207, 114), 256: (237, 204, 97),
    512: (237, 200, 80), 1024: (237, 197, 63), 2048: (237, 194, 46),
}

# =====================
# 动画与特效类
# =====================
class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 1.0
        self.color = color
        self.size = random.randint(4, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3  # 重力
        self.life -= 0.04
        self.size *= 0.92

    def draw(self, screen, ox, oy):
        if self.life > 0:
            alpha = int(255 * max(0, self.life))
            s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            s.fill((*self.color, alpha))
            screen.blit(s, (int(self.x + ox), int(self.y + oy)))

class FloatingText:
    def __init__(self, text, x, y, color):
        self.text, self.x, self.y = text, x, y
        self.life = 1.0
        self.color = color

    def update(self):
        self.y -= 1.5
        self.life -= 0.025

    def draw(self, screen, font, ox, oy):
        if self.life > 0:
            alpha = int(255 * max(0, self.life))
            txt = font.render(self.text, True, self.color)
            s = pygame.Surface((txt.get_width(), txt.get_height()), pygame.SRCALPHA)
            s.blit(txt, (0, 0))
            s.set_alpha(alpha)
            screen.blit(s, (int(self.x - txt.get_width()//2 + ox), int(self.y + oy)))

class Tile:
    def __init__(self, value, row, col):
        self.value = value
        self.row, self.col = row, col
        self.x, self.y = get_pos(row, col)
        self.target_x, self.target_y = self.x, self.y

        self.scale = 0.1  # 出生缩放动画
        self.target_scale = 1.0
        self.merged = False # 防止单次滑动连续合并
        self.merged_into = None # 记录被合并到了哪个方块上

    def update(self):
        # 平滑移动 (Lerp) - 系数越大移动越快，打击感越强
        self.x += (self.target_x - self.x) * 0.25
        self.y += (self.target_y - self.y) * 0.25

        if abs(self.x - self.target_x) < 1: self.x = self.target_x
        if abs(self.y - self.target_y) < 1: self.y = self.target_y

        # 缩放弹跳动画
        self.scale += (self.target_scale - self.scale) * 0.2
        if abs(self.scale - self.target_scale) < 0.01:
            self.scale = self.target_scale
            if self.target_scale > 1.0:
                self.target_scale = 1.0 # 弹回原状

    def is_moving(self):
        return self.x != self.target_x or self.y != self.target_y

    def trigger_merge(self):
        self.target_scale = 1.25 # 触发放大弹跳

# =====================
# 辅助函数
# =====================
def get_pos(row, col):
    x = PADDING + col * CELL + CELL // 2
    y = BOARD_TOP + row * CELL + CELL // 2
    return x, y

grid = [[None for _ in range(SIZE)] for _ in range(SIZE)]
dying_tiles = [] # 存放正在滑动消失的“牺牲者”方块
particles = []
floating_texts = []
shake_intensity = 0
shake_duration = 0

def spawn_particles(x, y, color):
    for _ in range(10):
        particles.append(Particle(x, y, color))

def add_floating_text(text, x, y):
    floating_texts.append(FloatingText(text, x, y - 20, (255, 255, 255)))

def trigger_shake(intensity, duration):
    global shake_intensity, shake_duration
    shake_intensity = intensity
    shake_duration = duration

# =====================
# 核心游戏逻辑 (最终修复版)
# =====================
def process_move(direction):
    global dying_tiles
    moved = False
    total_score = 0

    # 清除上一轮的 merged 标记
    for r in range(SIZE):
        for c in range(SIZE):
            if grid[r][c]:
                grid[r][c].merged = False

    # 处理左右移动
    if direction in ['left', 'right']:
        for r in range(SIZE):
            # 获取该行的 tile
            tiles = [grid[r][c] for c in range(SIZE) if grid[r][c]]
            if direction == 'right':
                tiles.reverse() # 从右向左处理，保证右侧优先合并

            new_tiles = []
            for tile in tiles:
                if new_tiles and new_tiles[-1].value == tile.value and not new_tiles[-1].merged:
                    # 发生合并！
                    survivor = new_tiles[-1]
                    survivor.value *= 2
                    survivor.merged = True
                    total_score += survivor.value

                    # 牺牲者记录，稍后让它滑向幸存者的位置
                    tile.merged_into = survivor
                    dying_tiles.append(tile)
                else:
                    new_tiles.append(tile)
                    tile.merged_into = None

            # 【核心修复】：绝对不要反转 new_tiles！
            # 合并后的 new_tiles 已经是“从滑动边缘向内”排列的了

            # 清空当前行，准备重新分配
            for c in range(SIZE): grid[r][c] = None

            # 分配新坐标并检查是否发生移动
            for i, tile in enumerate(new_tiles):
                c = i if direction == 'left' else SIZE - 1 - i
                if tile.col != c: # 只要列号变了，就说明发生了移动
                    moved = True
                tile.target_x, tile.target_y = get_pos(r, c)
                tile.row, tile.col = r, c
                grid[r][c] = tile

            # 设置牺牲者的目标坐标（让它们滑向合并点）
            for tile in tiles:
                if hasattr(tile, 'merged_into') and tile.merged_into:
                    tile.target_x, tile.target_y = tile.merged_into.target_x, tile.merged_into.target_y

            # 触发合并特效
            for tile in new_tiles:
                if tile.merged:
                    tile.trigger_merge()
                    spawn_particles(tile.target_x, tile.target_y, TILE_COLORS.get(tile.value, (255,255,255)))
                    add_floating_text(f"+{tile.value}", tile.target_x, tile.target_y)
                    if tile.value >= 128: trigger_shake(4, 6)

    # 处理上下移动
    elif direction in ['up', 'down']:
        for c in range(SIZE):
            tiles = [grid[r][c] for r in range(SIZE) if grid[r][c]]
            if direction == 'down':
                tiles.reverse() # 从下向上处理，保证下侧优先合并

            new_tiles = []
            for tile in tiles:
                if new_tiles and new_tiles[-1].value == tile.value and not new_tiles[-1].merged:
                    survivor = new_tiles[-1]
                    survivor.value *= 2
                    survivor.merged = True
                    total_score += survivor.value

                    tile.merged_into = survivor
                    dying_tiles.append(tile)
                else:
                    new_tiles.append(tile)
                    tile.merged_into = None

            # 【核心修复】：绝对不要反转 new_tiles！

            for r in range(SIZE): grid[r][c] = None

            for i, tile in enumerate(new_tiles):
                r = i if direction == 'up' else SIZE - 1 - i
                if tile.row != r:
                    moved = True
                tile.target_x, tile.target_y = get_pos(r, c)
                tile.row, tile.col = r, c
                grid[r][c] = tile

            for tile in tiles:
                if hasattr(tile, 'merged_into') and tile.merged_into:
                    tile.target_x, tile.target_y = tile.merged_into.target_x, tile.merged_into.target_y

            for tile in new_tiles:
                if tile.merged:
                    tile.trigger_merge()
                    spawn_particles(tile.target_x, tile.target_y, TILE_COLORS.get(tile.value, (255,255,255)))
                    add_floating_text(f"+{tile.value}", tile.target_x, tile.target_y)
                    if tile.value >= 128: trigger_shake(4, 6)

    # 只要发生了合并，必然算作一次有效移动（即使方块看起来没动）
    if total_score > 0:
        moved = True

    return moved, total_score

def add_tile():
    empty = [(r, c) for r in range(SIZE) for c in range(SIZE) if not grid[r][c]]
    if empty:
        r, c = random.choice(empty)
        val = 4 if random.random() < 0.1 else 2
        grid[r][c] = Tile(val, r, c)

def check_game_over():
    for r in range(SIZE):
        for c in range(SIZE):
            if not grid[r][c]: return False
            if c + 1 < SIZE and grid[r][c+1] and grid[r][c].value == grid[r][c+1].value: return False
            if r + 1 < SIZE and grid[r+1][c] and grid[r][c].value == grid[r+1][c].value: return False
    return True

# =====================
# 渲染
# =====================
def draw_tile(screen, tile, ox, oy, fonts):
    # 阴影 (增加立体感)
    shadow_rect = pygame.Rect(tile.x - CELL//2 + 4 + ox, tile.y - CELL//2 + 6 + oy, CELL - 8, CELL - 8)
    pygame.draw.rect(screen, (140, 130, 120), shadow_rect, border_radius=12)

    # 主体 (带缩放)
    size = int((CELL - 8) * tile.scale)
    rect = pygame.Rect(tile.x - size//2 + ox, tile.y - size//2 + oy, size, size)
    color = TILE_COLORS.get(tile.value, (60, 58, 54))
    pygame.draw.rect(screen, color, rect, border_radius=12)

    # 文字
    if tile.value > 0:
        if tile.value < 100: f = fonts["tile_1"]
        elif tile.value < 1000: f = fonts["tile_2"]
        else: f = fonts["tile_3"]

        text_color = COLOR_TEXT_DARK if tile.value <= 4 else COLOR_TEXT_LIGHT
        text = f.render(str(tile.value), True, text_color)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

def draw_game(screen, score, won, over, fonts):
    global shake_intensity, shake_duration

    # 屏幕震动偏移
    ox, oy = 0, 0
    if shake_duration > 0:
        ox = random.uniform(-shake_intensity, shake_intensity)
        oy = random.uniform(-shake_intensity, shake_intensity)
        shake_duration -= 1

    screen.fill(COLOR_BG)

    # UI
    screen.blit(fonts["ui"].render(f"Score: {score}", True, COLOR_TEXT_DARK), (PADDING + ox, 20 + oy))
    screen.blit(fonts["ui_small"].render("Arrows: Move | R: Restart", True, COLOR_TEXT_DARK),
                (WIDTH - 220 + ox, 30 + oy))

    # 棋盘背景
    board_rect = pygame.Rect(PADDING - 5 + ox, BOARD_TOP - 5 + oy, SIZE * CELL + 10, SIZE * CELL + 10)
    pygame.draw.rect(screen, (167, 157, 144), board_rect, border_radius=15)

    # 空格子
    for r in range(SIZE):
        for c in range(SIZE):
            x, y = get_pos(r, c)
            rect = pygame.Rect(x - CELL//2 + 4 + ox, y - CELL//2 + 4 + oy, CELL - 8, CELL - 8)
            pygame.draw.rect(screen, COLOR_EMPTY, rect, border_radius=12)

    # 绘制牺牲者（在底层）
    for tile in dying_tiles:
        draw_tile(screen, tile, ox, oy, fonts)

    # 绘制存活方块（在顶层）
    for r in range(SIZE):
        for c in range(SIZE):
            if grid[r][c]:
                draw_tile(screen, grid[r][c], ox, oy, fonts)

    # 绘制特效
    for p in particles: p.draw(screen, ox, oy)
    for ft in floating_texts: ft.draw(screen, fonts["ui"], ox, oy)

    # 游戏结束/胜利遮罩
    if over or won:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((240, 240, 240, 180))
        screen.blit(overlay, (0, 0))

        msg = "Game Over!" if over else "You Win! (Keep Going)"
        text = fonts["ui_large"].render(msg, True, COLOR_TEXT_DARK)
        screen.blit(text, text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    pygame.display.flip()

# =====================
# 主程序
# =====================
def main():
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("2048 - Juice Edition (Final)")
    clock = pygame.time.Clock()

    fonts = {
        "ui_large": pygame.font.Font(None, 72),
        "ui": pygame.font.Font(None, 40),
        "ui_small": pygame.font.Font(None, 24),
        "tile_1": pygame.font.Font(None, 56),
        "tile_2": pygame.font.Font(None, 44),
        "tile_3": pygame.font.Font(None, 32),
    }

    global grid, dying_tiles, particles, floating_texts
    can_input = True
    score = 0
    won = False
    over = False

    # 初始化
    add_tile()
    add_tile()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                elif event.key == pygame.K_r:
                    grid = [[None for _ in range(SIZE)] for _ in range(SIZE)]
                    dying_tiles = []
                    score, won, over = 0, False, False
                    add_tile(); add_tile()
                    can_input = True
                elif can_input and not over:
                    direction = None
                    if event.key == pygame.K_LEFT: direction = "left"
                    elif event.key == pygame.K_RIGHT: direction = "right"
                    elif event.key == pygame.K_UP: direction = "up"
                    elif event.key == pygame.K_DOWN: direction = "down"

                    if direction:
                        moved, gain = process_move(direction)
                        if moved:
                            score += gain
                            can_input = False # 锁定输入，等待动画完成

        # 更新逻辑
        if not can_input:
            all_stopped = True
            for r in range(SIZE):
                for c in range(SIZE):
                    if grid[r][c] and grid[r][c].is_moving():
                        all_stopped = False
                        break
                if not all_stopped: break

            for tile in dying_tiles:
                if tile.is_moving():
                    all_stopped = False
                    break

            if all_stopped:
                add_tile()
                can_input = True
                if not won and any(grid[r][c] and grid[r][c].value == 2048 for r in range(SIZE) for c in range(SIZE)):
                    won = True
                if check_game_over():
                    over = True

        # 更新动画
        for r in range(SIZE):
            for c in range(SIZE):
                if grid[r][c]: grid[r][c].update()

        for tile in dying_tiles[:]:
            tile.update()
            if not tile.is_moving():
                dying_tiles.remove(tile) # 到达目标后移除牺牲者

        for p in particles[:]:
            p.update()
            if p.life <= 0: particles.remove(p)

        for ft in floating_texts[:]:
            ft.update()
            if ft.life <= 0: floating_texts.remove(ft)

        draw_game(screen, score, won, over, fonts)
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
