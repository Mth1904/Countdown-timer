# Hehehee, :))
import pygame
import math

pygame.init()
pygame.init(frequency=44100, size=-16, channels=2, buffer=512)

WIDTH, HEIGHT = 520, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("⏱️ Countdown Timer 5⭐")

clock = pygame.time.Clock()
font_big = pygame.font.SysFont("arial", 64, bold=True)
font_small = pygame.font.SysFont("arial", 28)
font_medium = pygame.font.SysFont("arial", 36)

try:
    alarm = pygame.mixer.Sound("alarm.wav")  # hoặc "alarm.mp3" nếu đúng định dạng
except pygame.error as e:
    print("Lỗi khi load âm thanh:", e)
    alarm = None

# Định nghĩa 2 theme: dark và light
themes = {
    "dark": {
        "BG_TOP": (10, 30, 80),
        "BG_BOTTOM": (30, 200, 180),
        "TEXT_COLOR": (255, 255, 255),
        "CIRCLE_COLOR": (255, 255, 255),
        "BORDER_COLOR": (255, 255, 255),
        "BUTTONS": {
            "add_min": ((76, 175, 80), (0, 255, 255)),
            "sub_min": ((244, 67, 54), (255, 152, 0)),
            "add_sec": ((76, 175, 80), (0, 255, 255)),
            "sub_sec": ((244, 67, 54), (255, 152, 0)),
            "start":   ((33, 150, 243), (0, 255, 255)),
            "pause":   ((255, 152, 0), (255, 235, 59)),
            "reset":   ((244, 67, 54), (255, 152, 0)),
            "theme":   ((100, 100, 100), (50, 50, 50)),
        },
    },
    "light": {
        "BG_TOP": (230, 230, 250),
        "BG_BOTTOM": (135, 206, 250),
        "TEXT_COLOR": (30, 30, 30),
        "CIRCLE_COLOR": (30, 30, 30),
        "BORDER_COLOR": (30, 30, 30),
        "BUTTONS": {
            "add_min": ((80, 180, 120), (120, 230, 200)),
            "sub_min": ((230, 90, 80), (255, 170, 130)),
            "add_sec": ((80, 180, 120), (120, 230, 200)),
            "sub_sec": ((230, 90, 80), (255, 170, 130)),
            "start":   ((60, 180, 230), (120, 230, 250)),
            "pause":   ((255, 200, 90), (255, 255, 130)),
            "reset":   ((230, 90, 80), (255, 170, 130)),
            "theme":   ((180, 180, 180), (130, 130, 130)),
        },
    }
}

current_theme = "dark"

def draw_gradient():
    BG_TOP = themes[current_theme]["BG_TOP"]
    BG_BOTTOM = themes[current_theme]["BG_BOTTOM"]
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(BG_TOP[0] * (1 - ratio) + BG_BOTTOM[0] * ratio)
        g = int(BG_TOP[1] * (1 - ratio) + BG_BOTTOM[1] * ratio)
        b = int(BG_TOP[2] * (1 - ratio) + BG_BOTTOM[2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

def draw_rounded_button(rect, c1, c2, text, text_color):
    button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    for y in range(rect.height):
        ratio = y / rect.height
        r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
        g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
        b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
        pygame.draw.line(button_surface, (r, g, b), (0, y), (rect.width, y))
    pygame.draw.rect(button_surface, (255, 255, 255, 180), button_surface.get_rect(), border_radius=16)
    mask = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, rect.width, rect.height), border_radius=16)
    button_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    screen.blit(button_surface, (rect.x, rect.y))
    text_surf = font_small.render(text, True, text_color)
    screen.blit(text_surf, text_surf.get_rect(center=rect.center))

class Button:
    def __init__(self, x, y, w, h, key, text, text_color=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.key = key
        self.text = text
        self.text_color = text_color if text_color else themes[current_theme]["TEXT_COLOR"]

    def draw(self):
        c1, c2 = themes[current_theme]["BUTTONS"][self.key]
        draw_rounded_button(self.rect, c1, c2, self.text, self.text_color)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

buttons = {
    "add_min": Button(50, 60, 60, 50, "add_min", "+"),
    "sub_min": Button(50, 130, 60, 50, "sub_min", "-"),
    "add_sec": Button(140, 60, 60, 50, "add_sec", "+"),
    "sub_sec": Button(140, 130, 60, 50, "sub_sec", "-"),
    "start":   Button(230, 60, 210, 50, "start", "START", (255, 255, 255)),
    "pause":   Button(230, 130, 210, 50, "pause", "PAUSE", (255, 255, 255)),
    "reset":   Button(150, 200, 200, 50, "reset", "RESET", (255, 255, 255)),
    "theme":   Button(410, 10, 80, 30, "theme", "Sáng", (255, 255, 255)),
}

running = True
start = False
paused = False
total_seconds = 0
start_ticks = 0
paused_time = 0
pause_start = 0
alarm_played = False

def draw_clock_hand(center, length, angle_deg, color, thickness):
    angle_rad = math.radians(angle_deg - 90)
    end_x = center[0] + length * math.cos(angle_rad)
    end_y = center[1] + length * math.sin(angle_rad)
    pygame.draw.line(screen, color, center, (end_x, end_y), thickness)
    radius = thickness // 2 + 1
    pygame.draw.circle(screen, color, (int(end_x), int(end_y)), radius)

def draw_clock(center, seconds_left):
    radius = 140
    pygame.draw.circle(screen, themes[current_theme]["CIRCLE_COLOR"], center, radius)
    pygame.draw.circle(screen, themes[current_theme]["BORDER_COLOR"], center, radius, 5)

    second_angle = (seconds_left % 60) * 6
    minute_angle = ((seconds_left // 60) % 60) * 6

    # 🔥 Màu kim phút theo theme
    minute_color = (255, 0, 0)  # Luôn luôn đỏ
    second_color = (0, 0, 0) if current_theme == "dark" else (255, 255, 255)

    draw_clock_hand(center, radius * 0.65, minute_angle, minute_color, 8)
    draw_clock_hand(center, radius * 0.9, second_angle, second_color, 6)


    pygame.draw.circle(screen, (0, 0, 0), center, 12)

def draw_time_text(seconds_left):
    mins = int(seconds_left) // 60
    secs = int(seconds_left) % 60
    time_str = f"{mins:02}:{secs:02}"
    text_surf = font_big.render(time_str, True, themes[current_theme]["TEXT_COLOR"])
    rect = text_surf.get_rect(center=(WIDTH // 2, 620))
    screen.blit(text_surf, rect)

def toggle_theme():
    global current_theme
    if current_theme == "dark":
        current_theme = "light"
        buttons["theme"].text = "Tối"
        for btn in buttons.values():
            btn.text_color = themes[current_theme]["TEXT_COLOR"]
    else:
        current_theme = "dark"
        buttons["theme"].text = "Sáng"
        for btn in buttons.values():
            btn.text_color = themes[current_theme]["TEXT_COLOR"]

while running:
    draw_gradient()

    for btn in buttons.values():
        btn.draw()

    if start and not paused:
        elapsed_ms = pygame.time.get_ticks() - start_ticks - paused_time
        seconds_left = max(0, total_seconds - elapsed_ms / 1000)
        if seconds_left <= 0:
            seconds_left = 0
            if alarm and not alarm_played:
                alarm.play()
                alarm_played = True
            start = False
            paused = False

    else:
        seconds_left = total_seconds

    draw_clock((WIDTH // 2, 450), seconds_left)
    draw_time_text(seconds_left)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if buttons["add_min"].is_clicked(event) and not start:
                total_seconds += 60
                if total_seconds > 3599:
                    total_seconds = 3599
                alarm_played = False

            elif buttons["sub_min"].is_clicked(event) and not start:
                total_seconds -= 60
                if total_seconds < 0:
                    total_seconds = 0
                alarm_played = False

            elif buttons["add_sec"].is_clicked(event) and not start:
                total_seconds += 1
                if total_seconds > 3599:
                    total_seconds = 3599
                alarm_played = False

            elif buttons["sub_sec"].is_clicked(event) and not start:
                total_seconds -= 1
                if total_seconds < 0:
                    total_seconds = 0
                alarm_played = False

            elif buttons["start"].is_clicked(event) and total_seconds > 0:
                start = True
                paused = False
                paused_time = 0
                start_ticks = pygame.time.get_ticks()
                alarm_played = False

            elif buttons["pause"].is_clicked(event) and start:
                paused = not paused
                if paused:
                    pause_start = pygame.time.get_ticks()
                else:
                    paused_time += pygame.time.get_ticks() - pause_start

            elif buttons["reset"].is_clicked(event):
                start = False
                paused = False
                total_seconds = 0
                paused_time = 0
                alarm_played = False

            elif buttons["theme"].is_clicked(event):
                toggle_theme()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()


