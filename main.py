# main.py - Main entry point for the game
import pygame
import sys
import os
from menu import Menu
from game import Game

# Initialize Pygame
pygame.init()
pygame.font.init()

# Game constants
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
TITLE = "Pac-Man Adventure"

# Create the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
LEVEL_COMPLETE = 3

class PacManGame:
    def __init__(self):
        self.screen = screen
        self.clock = clock
        self.state = MENU
        self.level = 1
        self.score = 0
        self.lives = 3
        
        # Create game components
        self.menu = Menu(self.screen, self.start_game)
        self.game = None
        
        # Load sounds
        self.load_sounds()
        
    def load_sounds(self):
        # Create sounds directory if it doesn't exist
        if not os.path.exists('sounds'):
            os.makedirs('sounds')
            
        # Sound effects would be loaded here
        # self.start_sound = pygame.mixer.Sound('sounds/start.wav')
        # etc.
        
    def start_game(self, level=1):
        self.level = level
        self.game = Game(self.screen, level, self.end_level, self.game_over)
        self.state = PLAYING
        # self.start_sound.play()
        
    def end_level(self, score):
        self.score += score
        self.level += 1
        if self.level > 10:
            self.level = 1
            self.state = MENU
        else:
            self.state = LEVEL_COMPLETE
    
    def game_over(self, score):
        self.score += score
        self.state = GAME_OVER
    
    def run(self):
        running = True
        
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if self.state == MENU:
                    self.menu.handle_event(event)
                elif self.state == PLAYING:
                    self.game.handle_event(event)
                elif self.state == GAME_OVER:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.state = MENU
                elif self.state == LEVEL_COMPLETE:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.start_game(self.level)
            
            # Update game state
            if self.state == MENU:
                self.menu.update()
            elif self.state == PLAYING:
                self.game.update()
            
            # Draw everything
            self.screen.fill((0, 0, 0))
            
            if self.state == MENU:
                self.menu.draw()
            elif self.state == PLAYING:
                self.game.draw()
            elif self.state == GAME_OVER:
                self.draw_game_over()
            elif self.state == LEVEL_COMPLETE:
                self.draw_level_complete()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def draw_game_over(self):
        font = pygame.font.SysFont('Arial', 48)
        game_over_text = font.render('GAME OVER', True, (255, 0, 0))
        score_text = font.render(f'Score: {self.score}', True, (255, 255, 255))
        continue_text = font.render('Press Enter to continue', True, (255, 255, 255))
        
        self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 100))
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2))
        self.screen.blit(continue_text, (SCREEN_WIDTH//2 - continue_text.get_width()//2, SCREEN_HEIGHT//2 + 100))
    
    def draw_level_complete(self):
        font = pygame.font.SysFont('Arial', 48)
        level_text = font.render(f'Level {self.level-1} Complete!', True, (255, 255, 0))
        score_text = font.render(f'Score: {self.score}', True, (255, 255, 255))
        continue_text = font.render('Press Enter to continue to next level', True, (255, 255, 255))
        
        self.screen.blit(level_text, (SCREEN_WIDTH//2 - level_text.get_width()//2, SCREEN_HEIGHT//2 - 100))
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2))
        self.screen.blit(continue_text, (SCREEN_WIDTH//2 - continue_text.get_width()//2, SCREEN_HEIGHT//2 + 100))

# Run the game
if __name__ == "__main__":
    game = PacManGame()
    game.run()