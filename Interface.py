import pygame
import sys
import os
import random

pygame.init()

# =====================================================
# SCREEN
# =====================================================
WIDTH, HEIGHT = 1400, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shop System")
clock = pygame.time.Clock()
FPS = 60

# =====================================================
# COLORS
# =====================================================
WHITE = (255, 255, 255)
CARD = (55, 55, 75)
CARD_HOVER = (85, 85, 115)
OUTLINE = (200, 200, 200)
BUTTON = (70, 170, 90)
BUTTON_HOVER = (100, 220, 120)

# =====================================================
# FONTS
# =====================================================
font = pygame.font.SysFont("impact", 22)
big_font = pygame.font.SysFont("impact", 36)
sold_font = pygame.font.SysFont("arial", 60, bold=True)

# =====================================================
# DESCRIPTIONS
# =====================================================
DESCRIPTIONS = {
    1: "gives a second try",
    2: "choose next genre",
    3: "swap coins with the top half of players",
    4: "stops someones bid without them knowing",
    5: "forced to bet xx%",
    6: "reduce time by xx%",
    7: "adds x coins to bet",
    8: "doubles coins earned in round",
    9: "halves your coins earned in round",
    10: "grants 2 random buffs or debuffs",
    11: "causes an enemy to use a debuff on themselves"
}

# =====================================================
# IMAGE LOADER
# =====================================================
def load_image(path, size=None):
    if not path or not os.path.exists(path):
        return None
    img = pygame.image.load(path).convert_alpha()
    if size:
        img = pygame.transform.smoothscale(img, size)
    return img

# =====================================================
# TEXT WRAP
# =====================================================
def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    line = ""

    for w in words:
        test = line + w + " "
        if font.size(test)[0] < max_width:
            line = test
        else:
            lines.append(line)
            line = w + " "

    lines.append(line)
    return lines


# =====================================================
# ITEM
# =====================================================
class ShopItem:

    def __init__(self, x, y, w, h, item_id, cost, image_index):

        self.base_rect = pygame.Rect(x, y, w, h)

        self.item_id = item_id
        self.cost = cost
        self.image_index = image_index
        self.description = DESCRIPTIONS.get(image_index, "Unknown item...")

        self.image = load_image(f"assets/item_{image_index}.png", (w - 40, h - 80))

        self.bought = False

        self.flip = 0.0
        self.flip_dir = 0

        self.hovered = False
        self.hit_rect = self.base_rect.copy()

    # -------------------------------------------------
    def update(self, mouse):

        self.hovered = self.base_rect.collidepoint(mouse)

        if not self.bought:
            self.flip_dir = 1 if self.hovered else -1

        self.flip = max(0.0, min(1.0, self.flip + self.flip_dir * 0.12))

    # -------------------------------------------------
    def click(self):
        self.bought = True

    # -------------------------------------------------
    def draw(self, surface):

        scale_x = max(0.25, abs(1 - self.flip * 2))

        w = int(self.base_rect.width * scale_x)
        h = self.base_rect.height

        draw_rect = pygame.Rect(0, 0, w, h)
        draw_rect.center = self.base_rect.center

        self.hit_rect = self.base_rect

        pygame.draw.rect(
            surface,
            CARD_HOVER if self.hovered else CARD,
            draw_rect,
            border_radius=12
        )
        pygame.draw.rect(surface, OUTLINE, draw_rect, 2, border_radius=12)

        # FRONT
        if self.flip < 0.5:

            if self.image:
                img_w = max(1, draw_rect.width - 40)
                img_h = max(1, draw_rect.height - 80)

                img = pygame.transform.smoothscale(self.image, (img_w, img_h))
                surface.blit(img, (draw_rect.x + 20, draw_rect.y + 20))

            cost = font.render(f"Cost: {self.cost}", True, WHITE)
            surface.blit(cost, (draw_rect.x + 10, draw_rect.bottom - 40))

        # BACK
        else:

            surface.blit(font.render("DESCRIPTION:", True, WHITE),
                         (draw_rect.x + 10, draw_rect.y + 15))

            lines = wrap_text(self.description, font, draw_rect.width - 20)

            y = draw_rect.y + 60
            for line in lines[:6]:
                surface.blit(font.render(line, True, WHITE),
                             (draw_rect.x + 10, y))
                y += 22

        # SOLD
        if self.bought:

            overlay = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            surface.blit(overlay, draw_rect.topleft)

            stamp = sold_font.render("SOLD", True, (255, 40, 40))
            stamp = pygame.transform.rotate(stamp, -20)
            surface.blit(stamp, stamp.get_rect(center=draw_rect.center))


# =====================================================
# SHOP
# =====================================================
class Shop:

    def __init__(self):

        self.items = []
        self.selected = None

        self.background = load_image("assets/background.png", (WIDTH, HEIGHT))

        self.create_items()

    # -------------------------------------------------
    def create_items(self):

        w, h = 240, 240
        spacing = 60

        cols, rows = 3, 2

        grid_w = cols * w + (cols - 1) * spacing
        grid_h = rows * h + (rows - 1) * spacing

        start_x = (WIDTH - grid_w) // 2
        start_y = (HEIGHT - grid_h) // 2

        # 🔥 RANDOM ORDER
        indices = [1, 2, 3, 4, 5, 6]
        random.shuffle(indices)

        for i in range(6):

            r = i // cols
            c = i % cols

            x = start_x + c * (w + spacing)
            y = start_y + r * (h + spacing)

            self.items.append(
                ShopItem(
                    x, y, w, h,
                    f"ITEM_{i+1}",
                    100 + i * 50,
                    indices[i]
                )
            )

    # -------------------------------------------------
    def handle_events(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            mouse = pygame.mouse.get_pos()

            for item in self.items:
                if item.hit_rect.collidepoint(mouse):
                    self.selected = item
                    break

            if self.selected:

                popup_rect = pygame.Rect(
                    self.selected.base_rect.centerx - 60,
                    self.selected.base_rect.bottom + 10,
                    120,
                    40
                )

                if popup_rect.collidepoint(mouse):
                    self.selected.click()
                    self.selected = None

    # -------------------------------------------------
    def update(self):

        mouse = pygame.mouse.get_pos()

        for item in self.items:
            item.update(mouse)

    # -------------------------------------------------
    def draw(self, surface):

        if self.background:
            surface.blit(self.background, (0, 0))
        else:
            surface.fill((30, 30, 40))

        title = big_font.render("SHOP", True, WHITE)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

        for item in self.items:
            item.draw(surface)

        # POPUP UNDER ITEM
        if self.selected:

            popup_rect = pygame.Rect(
                self.selected.base_rect.centerx - 60,
                self.selected.base_rect.bottom + 10,
                120,
                40
            )

            mouse = pygame.mouse.get_pos()
            color = BUTTON_HOVER if popup_rect.collidepoint(mouse) else BUTTON

            pygame.draw.rect(surface, color, popup_rect, border_radius=8)
            pygame.draw.rect(surface, WHITE, popup_rect, 2, border_radius=8)

            text = font.render("BUY", True, WHITE)
            surface.blit(text, (popup_rect.x + 35, popup_rect.y + 8))


# =====================================================
# RUN
# =====================================================
shop = Shop()

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        shop.handle_events(event)

    shop.update()
    shop.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()