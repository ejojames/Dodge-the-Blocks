"""
Dodge the Blocks 
"""

import pygame
import pygame_gui
import random
import sys

# ---- Initialize pygame and window ----------------------------------------
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodge the Blocks")
clock = pygame.time.Clock()

# UI manager for all buttons and labels
manager = pygame_gui.UIManager((WIDTH, HEIGHT))
FONT = pygame.font.SysFont("calibri", 28)

# ---- Game states ----------------------------------------------------------
STATE_MAIN_MENU, STATE_PLAYING, STATE_PAUSED, STATE_GAME_OVER = range(4)
game_state = STATE_MAIN_MENU

# ---- Difficulty settings --------------------------------------------------
difficulty_settings = {
    "Easy": {"speed": 6, "increment": 0.3},
    "Medium": {"speed": 10, "increment": 0.8},
    "Hard": {"speed": 14, "increment": 1.2},
}
current_difficulty = "Medium"
STARTING_LIVES = 5

# ---- Game variables -------------------------------------------------------
player_rect = None
enemy_list = []
score = 0
enemy_speed = 0
lives = STARTING_LIVES

# ---- UI element references -----------------------------------------------
main_menu_buttons = []
in_game_buttons = []
pause_menu_buttons = []
game_over_buttons = []
confirmation_ui_elements = []
confirmation_callback = None
confirmation_active = False

# ---- Utility functions ----------------------------------------------------
def clear_all_ui():
    manager.clear_and_reset()
    main_menu_buttons.clear()
    in_game_buttons.clear()
    pause_menu_buttons.clear()
    game_over_buttons.clear()
    confirmation_ui_elements.clear()


def draw_text(surface, text, x, y, font=FONT, color=(220, 220, 220)):
    surf = font.render(text, True, color)
    surface.blit(surf, (x, y))


# ---- Game setup/reset -----------------------------------------------------
def start_new_game():
    global player_rect, enemy_list, score, enemy_speed, lives
    player_rect = pygame.Rect(WIDTH // 2 - 25, HEIGHT - 70, 50, 50)
    enemy_list = [pygame.Rect(random.randint(0, WIDTH - 40), -40, 40, 40)]
    score = 0
    lives = STARTING_LIVES
    enemy_speed = difficulty_settings[current_difficulty]["speed"]


# ---- UI setup functions ---------------------------------------------------
def build_main_menu():
    clear_all_ui()
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((WIDTH // 2 - 180, 80), (360, 50)),
        text="🚀 Dodge the Blocks!",
        manager=manager,
    )
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((WIDTH // 2 - 120, 150), (240, 30)),
        text=f"Starting Lives: {STARTING_LIVES}",
        manager=manager,
    )
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((WIDTH // 2 - 120, 190), (240, 24)),
        text=f"Difficulty: {current_difficulty}",
        manager=manager,
    )
    btn_play = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 100, 260), (200, 60)),
        text="Play",
        manager=manager,
    )
    btn_difficulty = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 100, 340), (200, 60)),
        text="Change Difficulty",
        manager=manager,
    )
    btn_quit = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 100, 420), (200, 60)),
        text="Quit",
        manager=manager,
    )
    main_menu_buttons.extend([btn_play, btn_difficulty, btn_quit])


def build_in_game_buttons():
    btn_pause = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH - 220, 8), (100, 36)),
        text="Pause",
        manager=manager,
    )
    btn_quit = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH - 110, 8), (100, 36)),
        text="Quit",
        manager=manager,
    )
    in_game_buttons.extend([btn_pause, btn_quit])


def build_pause_menu():
    clear_all_ui()
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((WIDTH // 2 - 120, 120), (240, 40)),
        text="Paused",
        manager=manager,
    )
    btn_resume = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 100, 200), (200, 60)),
        text="Resume",
        manager=manager,
    )
    btn_restart = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 100, 280), (200, 60)),
        text="Restart",
        manager=manager,
    )
    btn_quit_to_menu = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 100, 360), (200, 60)),
        text="Quit to Menu",
        manager=manager,
    )
    pause_menu_buttons.extend([btn_resume, btn_restart, btn_quit_to_menu])


def build_game_over_screen():
    clear_all_ui()
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((WIDTH // 2 - 160, 120), (320, 40)),
        text=f"Game Over! Score: {score}",
        manager=manager,
    )
    btn_restart = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 100, 220), (200, 60)),
        text="Restart",
        manager=manager,
    )
    btn_quit_to_menu = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 100, 300), (200, 60)),
        text="Quit to Menu",
        manager=manager,
    )
    game_over_buttons.extend([btn_restart, btn_quit_to_menu])


# ---- Confirmation popup ---------------------------------------------------
def show_confirmation(message, yes_callback):
    global confirmation_ui_elements, confirmation_active, confirmation_callback
    if confirmation_active:
        return
    confirmation_active = True
    confirmation_callback = yes_callback
    lbl = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((WIDTH // 2 - 180, HEIGHT // 2 - 80), (360, 40)),
        text=message,
        manager=manager,
    )
    btn_yes = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 - 90, HEIGHT // 2 - 10), (80, 50)),
        text="Yes",
        manager=manager,
    )
    btn_no = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((WIDTH // 2 + 10, HEIGHT // 2 - 10), (80, 50)),
        text="No",
        manager=manager,
    )
    confirmation_ui_elements.extend([lbl, btn_yes, btn_no])


def hide_confirmation():
    global confirmation_active, confirmation_callback
    for elem in confirmation_ui_elements[:]:
        try:
            elem.kill()
        except Exception:
            pass
    confirmation_ui_elements.clear()
    confirmation_active = False
    confirmation_callback = None


# ---- Game logic -----------------------------------------------------------
def move_enemies_and_check_lives():
    global enemy_list, score, enemy_speed, lives
    for enemy in enemy_list[:]:
        enemy.y += enemy_speed
        if enemy.y > HEIGHT:
            enemy_list.remove(enemy)
            enemy_list.append(pygame.Rect(random.randint(0, WIDTH - 40), -40, 40, 40))
            score += 1
            if score % 5 == 0:
                enemy_speed += difficulty_settings[current_difficulty]["increment"]
        if player_rect.colliderect(enemy):
            enemy_list.remove(enemy)
            enemy_list.append(pygame.Rect(random.randint(0, WIDTH - 40), -40, 40, 40))
            lives -= 1
            if lives <= 0:
                return True
    return False


def draw_gameplay():
    """Draw player, enemies, and HUD, avoiding overlap with buttons."""
    screen.fill((24, 28, 50))
    pygame.draw.rect(screen, (51, 204, 204), player_rect)
    for enemy in enemy_list:
        pygame.draw.rect(screen, (220, 70, 80), enemy)

    # Move all HUD to top-left to avoid pause button area
    draw_text(screen, f"Score: {score}", 18, 18)
    draw_text(screen, f"Lives: {lives}", 18, 52)
    draw_text(screen, "Press Q to Quit", 18, 86, FONT, color=(180, 180, 180))


# ---- Start main menu ------------------------------------------------------
build_main_menu()


# ---- Main loop ------------------------------------------------------------
running = True
while running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        manager.process_events(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and game_state == STATE_PLAYING and not confirmation_active:
                game_state = STATE_PAUSED
                build_pause_menu()
            elif event.key == pygame.K_q and game_state == STATE_PLAYING and not confirmation_active:
                show_confirmation(
                    "Quit to main menu? Progress will be lost.",
                    lambda: [clear_all_ui(), build_main_menu(), globals().update({'game_state': STATE_MAIN_MENU})]
                )

        # ---- UI Button Handling ----
        if game_state == STATE_MAIN_MENU:
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == main_menu_buttons[0]:
                    start_new_game()
                    game_state = STATE_PLAYING
                    clear_all_ui()
                    build_in_game_buttons()
                elif event.ui_element == main_menu_buttons[1]:
                    keys = list(difficulty_settings.keys())
                    idx = keys.index(current_difficulty)
                    current_difficulty = keys[(idx + 1) % len(keys)]
                    build_main_menu()
                elif event.ui_element == main_menu_buttons[2]:
                    running = False

        elif game_state == STATE_PLAYING:
            if event.type == pygame_gui.UI_BUTTON_PRESSED and not confirmation_active:
                txt = getattr(event.ui_element, "text", "")
                if txt == "Pause":
                    game_state = STATE_PAUSED
                    build_pause_menu()
                elif txt == "Quit":
                    show_confirmation(
                        "Quit to main menu? Progress will be lost.",
                        lambda: [clear_all_ui(), build_main_menu(), globals().update({'game_state': STATE_MAIN_MENU})]
                    )

        elif game_state == STATE_PAUSED:
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                txt = getattr(event.ui_element, "text", "")
                if txt == "Resume":
                    game_state = STATE_PLAYING
                    clear_all_ui()
                    build_in_game_buttons()
                elif txt == "Restart":
                    start_new_game()
                    game_state = STATE_PLAYING
                    clear_all_ui()
                    build_in_game_buttons()
                elif txt == "Quit to Menu":
                    show_confirmation(
                        "Quit to main menu from Pause?",
                        lambda: [clear_all_ui(), build_main_menu(), globals().update({'game_state': STATE_MAIN_MENU})]
                    )

        elif game_state == STATE_GAME_OVER:
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                txt = getattr(event.ui_element, "text", "")
                if txt == "Restart":
                    start_new_game()
                    game_state = STATE_PLAYING
                    clear_all_ui()
                    build_in_game_buttons()
                elif txt == "Quit to Menu":
                    clear_all_ui()
                    build_main_menu()
                    game_state = STATE_MAIN_MENU

        # ---- Confirmation overlay ----
        if confirmation_active and event.type == pygame_gui.UI_BUTTON_PRESSED:
            txt = getattr(event.ui_element, "text", "")
            if txt == "Yes":
                if confirmation_callback:
                    confirmation_callback()
                hide_confirmation()
            elif txt == "No":
                hide_confirmation()
                if game_state == STATE_MAIN_MENU:
                    build_main_menu()
                elif game_state == STATE_PLAYING:
                    clear_all_ui()
                    build_in_game_buttons()
                elif game_state == STATE_PAUSED:
                    build_pause_menu()
                elif game_state == STATE_GAME_OVER:
                    build_game_over_screen()

    # ---- Game updates outside event loop ----
    if game_state == STATE_PLAYING and not confirmation_active:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_rect.x -= 12
        if keys[pygame.K_RIGHT]:
            player_rect.x += 12
        player_rect.x = max(0, min(WIDTH - player_rect.width, player_rect.x))

        if move_enemies_and_check_lives():
            game_state = STATE_GAME_OVER
            build_game_over_screen()

    # ---- Rendering ----
    if game_state in (STATE_MAIN_MENU, STATE_PAUSED, STATE_GAME_OVER):
        screen.fill((42, 43, 55))
        manager.update(time_delta)
        manager.draw_ui(screen)
    elif game_state == STATE_PLAYING:
        draw_gameplay()
        manager.update(time_delta)
        manager.draw_ui(screen)
    else:
        screen.fill((0, 0, 0))

    pygame.display.update()

pygame.quit()
sys.exit()
