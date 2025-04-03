# game.py - Core game mechanics
import pygame
import random
from entities import PacMan, Ghost, Pellet, PowerPellet
from level import load_level

class Game:
    def __init__(self, screen, level_num, level_complete_callback, game_over_callback):
        self.screen = screen
        self.level_num = level_num
        self.level_complete_callback = level_complete_callback
        self.game_over_callback = game_over_callback
        
        # Game properties
        self.score = 0
        self.lives = 3
        self.paused = False
        
        # Define wall colors for each level
        self.wall_colors = [
            (0, 0, 255),    # Level 1 - Blue
            (255, 0, 0),    # Level 2 - Red
            (0, 255, 0),    # Level 3 - Green
            (255, 255, 0),  # Level 4 - Yellow
            (255, 0, 255),  # Level 5 - Magenta
            (0, 255, 255),  # Level 6 - Cyan
            (255, 165, 0),  # Level 7 - Orange
            (128, 0, 128),  # Level 8 - Purple
            (0, 128, 0),    # Level 9 - Dark Green
            (255, 192, 203) # Level 10 - Pink
        ]
        
        # Load level
        self.map_data, self.wall_rects = load_level(level_num)
        self.tile_size = 20  # Size of each tile in the map
        
        # Calculate map offset to center it on screen
        map_width = len(self.map_data[0]) * self.tile_size
        map_height = len(self.map_data) * self.tile_size
        self.map_offset_x = (screen.get_width() - map_width) // 2
        self.map_offset_y = (screen.get_height() - map_height) // 2
        
        # Create game entities
        self.create_entities()
        
        # Font for score display
        self.font = pygame.font.SysFont('Arial', 24)
        
        # Game state
        self.game_active = True
        self.power_pellet_active = False
        self.power_timer = 0
        
    def create_entities(self):
        # Create Pac-Man, ghosts, pellets based on the map data
        self.pacman = None
        self.ghosts = []
        self.pellets = []
        self.power_pellets = []
        
        # Parse the map_data to create entities
        for y, row in enumerate(self.map_data):
            for x, cell in enumerate(row):
                # Convert grid position to screen position
                screen_x = self.map_offset_x + x * self.tile_size
                screen_y = self.map_offset_y + y * self.tile_size
                
                if cell == 'P':  # Pac-Man
                    self.pacman = PacMan(screen_x, screen_y, self.tile_size)
                elif cell == 'G':  # Ghost
                    # Create ghosts with different colors and behaviors
                    ghost_colors = [(255, 0, 0), (255, 184, 255), (0, 255, 255), (255, 184, 82)]
                    color = ghost_colors[len(self.ghosts) % len(ghost_colors)]
                    self.ghosts.append(Ghost(screen_x, screen_y, self.tile_size, color))
                elif cell == '.':  # Pellet
                    self.pellets.append(Pellet(screen_x, screen_y, self.tile_size))
                elif cell == 'O':  # Power Pellet
                    self.power_pellets.append(PowerPellet(screen_x, screen_y, self.tile_size))
        
        # Create outer boundary walls with correct offsets
        map_width = len(self.map_data[0]) * self.tile_size
        map_height = len(self.map_data) * self.tile_size
        
        # Add outer walls to wall_rects with increased distance from maze
        boundary_offset = 30  # Increased distance from maze
        self.wall_rects = [
            pygame.Rect(self.map_offset_x - boundary_offset, self.map_offset_y - boundary_offset, 
                       map_width + (boundary_offset * 2), 15),  # Top
            pygame.Rect(self.map_offset_x - boundary_offset, self.map_offset_y + map_height + boundary_offset - 15, 
                       map_width + (boundary_offset * 2), 15),  # Bottom
            pygame.Rect(self.map_offset_x - boundary_offset, self.map_offset_y - boundary_offset, 
                       15, map_height + (boundary_offset * 2)),  # Left
            pygame.Rect(self.map_offset_x + map_width + boundary_offset - 15, self.map_offset_y - boundary_offset, 
                       15, map_height + (boundary_offset * 2))  # Right
        ]
        
        # Add maze walls with correct offsets
        for y, row in enumerate(self.map_data):
            for x, cell in enumerate(row):
                if cell == 'W':
                    wall_rect = pygame.Rect(
                        self.map_offset_x + x * self.tile_size + 2.5,  # Shift right by 2.5 pixels
                        self.map_offset_y + y * self.tile_size + 2.5,  # Shift down by 2.5 pixels
                        15,  # Width of 15
                        15   # Height of 15
                    )
                    self.wall_rects.append(wall_rect)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.paused = not self.paused
            elif self.pacman and not self.paused:
                # Handle arrow key controls for Pac-Man
                if event.key == pygame.K_LEFT:
                    self.pacman.set_direction(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.pacman.set_direction(1, 0)
                elif event.key == pygame.K_UP:
                    self.pacman.set_direction(0, -1)
                elif event.key == pygame.K_DOWN:
                    self.pacman.set_direction(0, 1)
        elif event.type == pygame.KEYUP and self.pacman and not self.paused:
            # Keep the current direction when key is released
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
                # Only stop if the released key matches the current direction
                if (event.key == pygame.K_LEFT and self.pacman.direction == (-1, 0)) or \
                   (event.key == pygame.K_RIGHT and self.pacman.direction == (1, 0)) or \
                   (event.key == pygame.K_UP and self.pacman.direction == (0, -1)) or \
                   (event.key == pygame.K_DOWN and self.pacman.direction == (0, 1)):
                    self.pacman.set_direction(0, 0)
                    self.pacman.moving = False
    
    def update(self):
        if self.paused or not self.game_active:
            return
            
        # Update Pac-Man
        if self.pacman:
            self.pacman.update(self.wall_rects)
            
            # Check for pellet collisions
            for pellet in self.pellets[:]:
                if self.pacman.rect.colliderect(pellet.rect):
                    self.pellets.remove(pellet)
                    self.score += 10
            
            # Check for power pellet collisions
            for power_pellet in self.power_pellets[:]:
                if self.pacman.rect.colliderect(power_pellet.rect):
                    self.power_pellets.remove(power_pellet)
                    self.score += 50
                    self.power_pellet_active = True
                    self.power_timer = 300  # 5 seconds at 60 FPS
            
            # Check for ghost collisions
            for ghost in self.ghosts:
                if self.pacman.rect.colliderect(ghost.rect):
                    if self.power_pellet_active:
                        # Eat the ghost
                        ghost.reset()
                        self.score += 200
                    else:
                        # Lose a life
                        self.lives -= 1
                        if self.lives <= 0:
                            self.game_active = False
                            self.game_over_callback(self.score)
                        else:
                            self.reset_positions()
        
        # Update ghosts
        for ghost in self.ghosts:
            # Adjust ghost behavior based on power pellet
            scared = self.power_pellet_active
            if scared and self.power_timer < 60:  # Flash during the last second
                scared = self.power_timer % 10 < 5
            
            ghost.update(self.wall_rects, self.pacman, scared)
        
        # Update power pellet timer
        if self.power_pellet_active:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.power_pellet_active = False
        
        # Check if level is complete (all pellets eaten)
        if len(self.pellets) == 0 and len(self.power_pellets) == 0:
            self.game_active = False
            self.level_complete_callback(self.score)
    
    def reset_positions(self):
        # Reset Pac-Man and ghosts to their starting positions
        if self.pacman:
            self.pacman.reset()
        for ghost in self.ghosts:
            ghost.reset()
    
    def draw(self):
        # Get the wall color for the current level
        wall_color = self.wall_colors[self.level_num - 1]
        
        # Draw maze walls
        for wall_rect in self.wall_rects:
            # Draw walls with the map offset and level-specific color
            pygame.draw.rect(self.screen, wall_color, wall_rect)
        
        # Draw pellets
        for pellet in self.pellets:
            pellet.draw(self.screen)
        
        # Draw power pellets
        for power_pellet in self.power_pellets:
            power_pellet.draw(self.screen)
        
        # Draw ghosts
        for ghost in self.ghosts:
            ghost.draw(self.screen, self.power_pellet_active)
        
        # Draw Pac-Man
        if self.pacman:
            self.pacman.draw(self.screen)
        
        # Draw score and lives
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        lives_text = self.font.render(f"Lives: {self.lives}", True, (255, 255, 255))
        level_text = self.font.render(f"Level: {self.level_num}", True, (255, 255, 255))
        
        self.screen.blit(score_text, (20, 20))
        self.screen.blit(lives_text, (20, 50))
        self.screen.blit(level_text, (20, 80))
        
        # Draw paused message if game is paused
        if self.paused:
            paused_font = pygame.font.SysFont('Arial', 48)
            paused_text = paused_font.render("PAUSED", True, (255, 255, 255))
            text_rect = paused_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
            self.screen.blit(paused_text, text_rect)