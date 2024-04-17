import pygame as p
import sys
from chess.main import Main


# Screen dimensions 
WIDTH = 800
HEIGHT = 800

class Menu():
    def __init__(self):
        p.init() 
        self.screen = p.display.set_mode((WIDTH, HEIGHT))
        
        # Set up the display
        self.screen.fill((0, 0, 0))
        p.display.set_caption("ChessItium Game")

        # Load the chessboard background image
        background_image = p.image.load("./chess/assets/chessboard-menu.png").convert()

        # Define colors
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        GRAY = (200, 200, 200)

        # Define button properties
        BUTTON_WIDTH, BUTTON_HEIGHT = 180, 70
        BUTTON_X = WIDTH // 2 - BUTTON_WIDTH // 2
        PLAY_BUTTON = HEIGHT // 2 - BUTTON_HEIGHT // 2

        # Create font object
        font = p.font.Font("./chess/assets/Merriweather-Bold.ttf", 40)

        running = True  # Variable to control the menu loop

        while running:
            for event in p.event.get():
                if event.type == p.QUIT:
                    p.quit()
                    sys.exit()

            # Blit the background image onto the screen
            self.screen.blit(background_image, (0, 0))

            # Draw the buttons
            main_btn = p.draw.rect(self.screen, BLACK, (BUTTON_X, PLAY_BUTTON, BUTTON_WIDTH, BUTTON_HEIGHT))

            # Draw button labels
            btn_play = font.render("Play", True, WHITE)
            btn_play_rect = btn_play.get_rect(center=(BUTTON_X + BUTTON_WIDTH // 2, PLAY_BUTTON + BUTTON_HEIGHT // 2))
            self.screen.blit(btn_play, btn_play_rect)

            # Draw the title
            title_text_shadow = font.render("Welcome To ChessItium", True, BLACK)
            title_text = font.render("Welcome To ChessItium", True, WHITE)
            self.screen.blit(title_text_shadow, (WIDTH // 2 - title_text.get_width() // 2 + 2, 52))
            self.screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

            # Check if buttons are clicked
            mouse_pos = p.mouse.get_pos()
            if p.mouse.get_pressed()[0]:
                if main_btn.collidepoint(mouse_pos):
                    print("Have Fun :D")
                    running = False  # Exit the menu loop

            # Update the display
            p.display.flip()

        # Close the menu and launch the game
        p.quit()
        main = Main()
        main.show_menu()

Menu()