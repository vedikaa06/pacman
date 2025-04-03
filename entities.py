# entities.py - Game entities such as Pac-Man, ghosts, and pellets
import pygame
import random
import math

class PacMan:
    def __init__(self, x, y, size):
        self.start_x = x
        self.start_y = y
        self.size = size
        self.reset()
        
        # Animation variables
        self.mouth_angle = 0
        self.mouth_opening = True
        self.animation_speed = 10
        
        # Movement variables
        self.speed = 3  # Movement speed
        self.grid_size = size  # Size of one grid cell
        self.moving = False
        self.direction = (0, 0)  # Current direction
        self.next_direction = (0, 0)  # Next direction to try
        self.position = [float(x), float(y)]  # Precise position for smooth movement
        self.last_position = [float(x), float(y)]  # Store last valid position
        self.grid_x = int(x / size)  # Current grid position
        self.grid_y = int(y / size)  # Current grid position
        self.last_direction = (0, 0)  # Store last direction for smoother movement
    
    def reset(self):
        self.rect = pygame.Rect(self.start_x, self.start_y, self.size, self.size)
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self.last_direction = (0, 0)
        self.moving = False
        self.position = [float(self.start_x), float(self.start_y)]
        self.last_position = [float(self.start_x), float(self.start_y)]
        self.grid_x = int(self.start_x / self.size)
        self.grid_y = int(self.start_y / self.size)
    
    def set_direction(self, dx, dy):
        # Store the new direction
        self.next_direction = (dx, dy)
        self.moving = True
    
    def update(self, walls):
        # Try to move in the next direction if it's different from current
        if self.next_direction != self.direction and self.moving:
            next_x = self.position[0] + self.next_direction[0] * self.speed
            next_y = self.position[1] + self.next_direction[1] * self.speed
            next_rect = pygame.Rect(next_x, next_y, self.size, self.size)
            
            can_move = True
            for wall in walls:
                if next_rect.colliderect(wall):
                    can_move = False
                    break
            
            if can_move:
                self.direction = self.next_direction
                self.last_direction = self.direction
        
        # Move in the current direction
        if self.direction != (0, 0) and self.moving:
            next_x = self.position[0] + self.direction[0] * self.speed
            next_y = self.position[1] + self.direction[1] * self.speed
            next_rect = pygame.Rect(next_x, next_y, self.size, self.size)
            
            can_move = True
            for wall in walls:
                if next_rect.colliderect(wall):
                    can_move = False
                    break
            
            if can_move:
                self.last_position = self.position.copy()  # Store last valid position
                self.position[0] = next_x
                self.position[1] = next_y
                self.rect.x = int(self.position[0])
                self.rect.y = int(self.position[1])
                self.grid_x = int(self.position[0] / self.grid_size)
                self.grid_y = int(self.position[1] / self.grid_size)
            else:
                # If we hit a wall, snap to the last valid position
                self.position = self.last_position.copy()
                self.rect.x = int(self.position[0])
                self.rect.y = int(self.position[1])
                self.grid_x = int(self.position[0] / self.grid_size)
                self.grid_y = int(self.position[1] / self.grid_size)
                self.moving = False
                self.direction = (0, 0)
                self.next_direction = (0, 0)
        
        # Update mouth animation
        if self.mouth_opening:
            self.mouth_angle += self.animation_speed
            if self.mouth_angle >= 45:
                self.mouth_opening = False
        else:
            self.mouth_angle -= self.animation_speed
            if self.mouth_angle <= 0:
                self.mouth_opening = True
    
    def draw(self, screen):
        # Calculate the center of the character
        center = (self.rect.x + self.rect.width//2, self.rect.y + self.rect.height//2)
        
        # Draw Pac-Man as a yellow circle with a mouth
        pygame.draw.circle(screen, (255, 255, 0), center, self.rect.width//2)
        
        # Calculate mouth angle based on direction
        angle = 0
        if self.direction == (1, 0):  # Right
            angle = 0
        elif self.direction == (0, 1):  # Down
            angle = 90
        elif self.direction == (-1, 0):  # Left
            angle = 180
        elif self.direction == (0, -1):  # Up
            angle = 270
        
        # Draw the mouth as a pie slice
        if self.direction != (0, 0):  # Only draw mouth if moving
            pygame.draw.polygon(screen, (0, 0, 0), [
                center,
                (center[0] + math.cos(math.radians(angle - self.mouth_angle)) * self.rect.width//2,
                 center[1] + math.sin(math.radians(angle - self.mouth_angle)) * self.rect.width//2),
                (center[0] + math.cos(math.radians(angle + self.mouth_angle)) * self.rect.width//2,
                 center[1] + math.sin(math.radians(angle + self.mouth_angle)) * self.rect.width//2)
            ])

class Ghost:
    def __init__(self, x, y, size, color):
        self.start_x = x
        self.start_y = y
        self.size = size
        self.color = color
        self.scared_color = (0, 0, 255)  # Blue when scared
        self.reset()
        
        # Ghost behavior type
        self.behavior_type = random.choice(["chase", "random", "patrol"])
        self.patrol_points = []
        self.current_patrol_point = 0
        
        # Create patrol points
        for _ in range(4):
            self.patrol_points.append((
                random.randint(100, 700),
                random.randint(100, 500)
            ))
    
    def reset(self):
        self.rect = pygame.Rect(self.start_x, self.start_y, self.size, self.size)
        self.direction = (0, 0)
        self.speed = 0.8  # Reduced from 1.5 to 0.8 for slower movement
    
    def update(self, walls, pacman, scared=False):
        # Adjust speed based on scared state
        actual_speed = self.speed * 0.3 if scared else self.speed  # Reduced scared speed from 0.5 to 0.3
        
        # Determine direction based on behavior type
        if scared:
            # Run away from Pac-Man when scared
            self.flee_from_pacman(pacman)
        else:
            if self.behavior_type == "chase":
                self.chase_pacman(pacman)
            elif self.behavior_type == "random":
                self.move_randomly()
            elif self.behavior_type == "patrol":
                self.patrol()
        
        # Try to move in the current direction
        next_rect = self.rect.copy()
        next_rect.x += self.direction[0] * actual_speed
        next_rect.y += self.direction[1] * actual_speed
        
        # Check for wall collisions
        collision = False
        for wall in walls:
            if next_rect.colliderect(wall):
                collision = True
                break
        
        if not collision:
            self.rect = next_rect
        else:
            # If we hit a wall, choose a new direction
            self.choose_new_direction(walls)
    
    def chase_pacman(self, pacman):
        # Find direction to Pac-Man
        dx = pacman.rect.centerx - self.rect.centerx
        dy = pacman.rect.centery - self.rect.centery
        
        # Normalize to get unit direction
        length = max(0.1, math.sqrt(dx*dx + dy*dy))
        dx /= length
        dy /= length
        
        # Simplify to cardinal directions
        if abs(dx) > abs(dy):
            self.direction = (1 if dx > 0 else -1, 0)
        else:
            self.direction = (0, 1 if dy > 0 else -1)
    
    def flee_from_pacman(self, pacman):
        # Find direction away from Pac-Man
        dx = self.rect.centerx - pacman.rect.centerx
        dy = self.rect.centery - pacman.rect.centery
        
        # Normalize to get unit direction
        length = max(0.1, math.sqrt(dx*dx + dy*dy))
        dx /= length
        dy /= length
        
        # Simplify to cardinal directions
        if abs(dx) > abs(dy):
            self.direction = (1 if dx > 0 else -1, 0)
        else:
            self.direction = (0, 1 if dy > 0 else -1)
    
    def move_randomly(self):
        if random.random() < 0.02:  # 2% chance to change direction each frame
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            self.direction = random.choice(directions)
    
    def patrol(self):
        if not self.patrol_points:
            return
            
        target = self.patrol_points[self.current_patrol_point]
        
        # Calculate direction to target
        dx = target[0] - self.rect.centerx
        dy = target[1] - self.rect.centery
        
        # Check if we're close to the target
        if abs(dx) < 10 and abs(dy) < 10:
            # Move to next patrol point
            self.current_patrol_point = (self.current_patrol_point + 1) % len(self.patrol_points)
            return
        
        # Normalize to get unit direction
        length = max(0.1, math.sqrt(dx*dx + dy*dy))
        dx /= length
        dy /= length
        
        # Simplify to cardinal directions
        if abs(dx) > abs(dy):
            self.direction = (1 if dx > 0 else -1, 0)
        else:
            self.direction = (0, 1 if dy > 0 else -1)
    
    def choose_new_direction(self, walls):
        # Try each direction until we find one that doesn't cause a collision
        possible_directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(possible_directions)
        
        for direction in possible_directions:
            next_rect = self.rect.copy()
            next_rect.x += direction[0] * self.speed
            next_rect.y += direction[1] * self.speed
            
            collision = False
            for wall in walls:
                if next_rect.colliderect(wall):
                    collision = True
                    break
            
            if not collision:
                self.direction = direction
                break
    
    def draw(self, screen, scared=False):
        color = self.scared_color if scared else self.color
        
        # Draw the main body (semi-circle)
        pygame.draw.circle(screen, color, (self.rect.centerx, self.rect.centery - self.size//4), self.size//2)
        
        # Draw the lower part (wavy bottom)
        wave_rect = pygame.Rect(
            self.rect.x,
            self.rect.centery - self.size//4,
            self.size,
            self.size//2
        )
        pygame.draw.rect(screen, color, wave_rect)
        
        # Draw the bottom waves
        wave_height = self.size//6
        wave_width = self.size//3
        
        for i in range(3):
            x_start = self.rect.x + i * wave_width
            pygame.draw.circle(
                screen,
                (0, 0, 0),  # Background color (for the gaps)
                (x_start + wave_width//2, self.rect.bottom),
                wave_height
            )
        
        # Draw eyes
        eye_size = self.size//5
        eye_y = self.rect.centery - self.size//4
        
        # Eye whites
        pygame.draw.circle(screen, (255, 255, 255), (self.rect.centerx - eye_size, eye_y), eye_size)
        pygame.draw.circle(screen, (255, 255, 255), (self.rect.centerx + eye_size, eye_y), eye_size)
        
        # Eye pupils - position based on direction
        pupil_offset_x = self.direction[0] * eye_size//2
        pupil_offset_y = self.direction[1] * eye_size//2
        
        if scared:
            pygame.draw.circle(screen, (0, 0, 0), (self.rect.centerx - eye_size, eye_y), eye_size//2)
            pygame.draw.circle(screen, (0, 0, 0), (self.rect.centerx + eye_size, eye_y), eye_size//2)
        else:
            # Normal pupil eyes
            pygame.draw.circle(
                screen, 
                (0, 0, 255), 
                (self.rect.centerx - eye_size + pupil_offset_x, eye_y + pupil_offset_y), 
                eye_size//2
            )
            pygame.draw.circle(
                screen, 
                (0, 0, 255), 
                (self.rect.centerx + eye_size + pupil_offset_x, eye_y + pupil_offset_y), 
                eye_size//2
            )

class Pellet:
    def __init__(self, x, y, tile_size):
        self.size = tile_size // 5
        self.rect = pygame.Rect(
            x + tile_size//2 - self.size//2,
            y + tile_size//2 - self.size//2,
            self.size,
            self.size
        )
    
    def draw(self, screen):
        pygame.draw.circle(
            screen,
            (255, 255, 255),
            self.rect.center,
            self.size // 2
        )

class PowerPellet:
    def __init__(self, x, y, tile_size):
        self.size = tile_size // 2
        self.rect = pygame.Rect(
            x + tile_size//2 - self.size//2,
            y + tile_size//2 - self.size//2,
            self.size,
            self.size
        )
        self.animation_counter = 0
        self.visible = True
    
    def draw(self, screen):
        # Make the power pellet flash
        self.animation_counter += 1
        if self.animation_counter >= 30:
            self.animation_counter = 0
            self.visible = not self.visible
        
        if self.visible:
            pygame.draw.circle(
                screen,
                (255, 255, 255),
                self.rect.center,
                self.size // 2
            )