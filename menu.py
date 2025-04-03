# menu.py - Game menu implementation
import pygame
import random
import math

class AnimatedBackground:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Create a list of animated dots
        self.dots = []
        self.num_dots = 50
        self.dot_size = 4
        self.dot_speed = 2
        self.dot_color = (0, 0, 255)  # Blue dots
        
        # Initialize dots with random positions and directions
        for _ in range(self.num_dots):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            dx = random.choice([-self.dot_speed, self.dot_speed])
            dy = random.choice([-self.dot_speed, self.dot_speed])
            self.dots.append({
                'x': x,
                'y': y,
                'dx': dx,
                'dy': dy,
                'alpha': random.randint(50, 255)  # Random transparency
            })
    
    def update(self):
        # Update dot positions
        for dot in self.dots:
            dot['x'] += dot['dx']
            dot['y'] += dot['dy']
            
            # Bounce off screen edges
            if dot['x'] <= 0 or dot['x'] >= self.width:
                dot['dx'] *= -1
            if dot['y'] <= 0 or dot['y'] >= self.height:
                dot['dy'] *= -1
            
            # Update transparency for a pulsing effect
            dot['alpha'] = (dot['alpha'] + 5) % 255
    
    def draw(self):
        # Create a surface for the background
        background = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        background.fill((0, 0, 0, 180))  # Semi-transparent black background
        
        # Draw dots
        for dot in self.dots:
            color = (*self.dot_color, dot['alpha'])
            pygame.draw.circle(background, color, (int(dot['x']), int(dot['y'])), self.dot_size)
        
        # Draw the background
        self.screen.blit(background, (0, 0))

class Button:
    def __init__(self, screen, text, pos, size, callback=None, param=None):
        self.screen = screen
        self.text = text
        self.x, self.y = pos
        self.width, self.height = size
        self.callback = callback
        self.param = param
        self.hovered = False
        
        # Colors
        self.normal_color = (255, 255, 0)  # Pac-Man yellow
        self.hover_color = (255, 165, 0)   # Orange
        self.text_color = (0, 0, 0)        # Black
        
        # Font
        self.font = pygame.font.SysFont('Arial', 36)  # Increased font size
        self.text_surf = self.font.render(text, True, self.text_color)
        self.text_rect = self.text_surf.get_rect(center=(self.x + self.width//2, self.y + self.height//2))
        
    def draw(self):
        color = self.hover_color if self.hovered else self.normal_color
        pygame.draw.rect(self.screen, color, (self.x, self.y, self.width, self.height), 0, 10)
        pygame.draw.rect(self.screen, (0, 0, 255), (self.x, self.y, self.width, self.height), 2, 10)
        self.screen.blit(self.text_surf, self.text_rect)
    
    def check_hover(self, pos):
        prev_hover = self.hovered
        self.hovered = (self.x <= pos[0] <= self.x + self.width and 
                        self.y <= pos[1] <= self.y + self.height)
        return self.hovered != prev_hover  # Return True if state changed
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.check_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hovered:
            if self.callback:
                if self.param is not None:
                    self.callback(self.param)
                else:
                    self.callback()
            return True
        return False

class Menu:
    def __init__(self, screen, start_game_callback):
        self.screen = screen
        self.start_game_callback = start_game_callback
        self.buttons = []
        self.logo_font = pygame.font.SysFont('Arial', 96, bold=True)
        self.info_font = pygame.font.SysFont('Arial', 32)
        
        # Create animated background
        self.background = AnimatedBackground(screen)
        
        # Create level selection buttons
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        button_width = 250
        button_height = 50
        button_spacing = 20
        
        # Title position
        self.title_y = screen_height // 4 - 50
        
        # Description position
        self.desc_y = self.title_y + 100
        
        # Instructions position
        self.instructions_y = screen_height - 100
        
        # Calculate starting y-position for the grid of level buttons
        start_y = self.desc_y + 100
        
        # Create a grid of level buttons (2 rows x 5 columns)
        for row in range(2):
            for col in range(5):
                level = row * 5 + col + 1
                x = (screen_width - (button_width * 5 + button_spacing * 4)) // 2 + col * (button_width + button_spacing)
                y = start_y + row * (button_height + button_spacing)
                
                self.buttons.append(
                    Button(
                        screen, 
                        f"Level {level}",
                        (x, y),
                        (button_width, button_height),
                        self.start_game_callback,
                        level
                    )
                )
    
    def update(self):
        # Update background animation
        self.background.update()
        
        # Check for button hover
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.check_hover(mouse_pos)
    
    def handle_event(self, event):
        for button in self.buttons:
            if button.handle_event(event):
                return
    
    def draw(self):
        # Draw animated background
        self.background.draw()
        
        # Draw title
        title_surf = self.logo_font.render("PAC-MAN ADVENTURE", True, (255, 255, 0))
        title_rect = title_surf.get_rect(center=(self.screen.get_width()//2, self.title_y))
        self.screen.blit(title_surf, title_rect)
        
        # Draw description
        description = "Navigate through mazes, eat dots, and avoid ghosts!"
        desc_surf = self.info_font.render(description, True, (255, 255, 255))
        desc_rect = desc_surf.get_rect(center=(self.screen.get_width()//2, self.desc_y))
        self.screen.blit(desc_surf, desc_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw()
        
        # Draw instructions
        instructions = "Use arrow keys to control Pac-Man. Press ESC to return to menu."
        inst_surf = self.info_font.render(instructions, True, (200, 200, 200))
        inst_rect = inst_surf.get_rect(center=(self.screen.get_width()//2, self.instructions_y))
        self.screen.blit(inst_surf, inst_rect)