#!/usr/bin/env python3
"""
Clony Bird - Terminal Version
A terminal-based Flappy Bird clone using curses library (no display required)
"""
import curses
import random
import time
import sys

# Game constants (adjusted for terminal)
GRAVITY = 0.6  # Increased for faster falling
JUMP_STRENGTH = -0.8  # Further reduced for gentle, controlled jumps
PIPE_SPEED = 1
PIPE_GAP = 8  # Gap height in terminal rows
PIPE_WIDTH = 3  # Pipe width in terminal columns
PIPE_SPACING = 25  # Space between pipes
COLLISION_MARGIN = 0.3  # Small margin for collision detection (more forgiving on edges)
BIRD_CHAR = "🐦"  # Bird character (fallback to 'O' if emoji not supported)
PIPE_CHAR = "█"
GROUND_CHAR = "═"

class ClonyBird:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)  # Hide cursor
        self.stdscr.nodelay(1)  # Non-blocking input
        self.stdscr.timeout(50)  # 50ms timeout for input
        
        # Get terminal dimensions
        self.height, self.width = stdscr.getmaxyx()
        if self.height < 20 or self.width < 40:
            raise ValueError("Terminal too small! Need at least 40x20")
        
        # Game state
        self.level = 1
        self.max_level = 5
        self.level_score = 0  # Score within current level (0-30)
        self.total_score = 0  # Total score across all levels
        self.points_per_level = 30
        self.game_over = False
        self.game_started = False
        self.level_up_message_time = 0  # Track when to hide level up message
        
        # Bird position (relative to center)
        self.bird_x = self.width // 4
        self.bird_y = self.height // 2
        self.bird_velocity = 0
        
        # Create pipes list
        self.pipes = []
        self.create_initial_pipes()
        
        # Try to enable colors
        try:
            curses.start_color()
            curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Bird
            curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Pipes
            curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)   # Sky
            curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Text
            curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)    # Game Over
            self.colors_enabled = True
        except:
            self.colors_enabled = False
        
        # Check if terminal supports emoji
        try:
            self.stdscr.addstr(0, 0, "🐦")
            self.stdscr.refresh()
            self.bird_char = "🐦"
        except:
            self.bird_char = "O"
    
    def create_pipe(self, x):
        """Create a pipe pair data structure"""
        # Gap position (center of gap)
        gap_y = random.randint(self.height // 4, 3 * self.height // 4)
        return {
            'x': x,
            'gap_y': gap_y,
            'passed': False
        }
    
    def create_initial_pipes(self):
        """Create initial set of pipes"""
        start_x = self.width // 2
        for i in range(3):
            x = start_x + i * PIPE_SPACING
            self.pipes.append(self.create_pipe(x))
    
    def jump(self):
        """Make the bird jump"""
        if self.game_started and not self.game_over:
            self.bird_velocity = JUMP_STRENGTH
    
    def get_pipe_speed(self):
        """Get pipe speed based on current level"""
        # Level 1: speed 1, Level 2: speed 1.5, Level 3: speed 2, Level 4: speed 2.5, Level 5: speed 3
        return PIPE_SPEED + (self.level - 1) * 0.5
    
    def start_game(self):
        """Start the game"""
        if not self.game_started:
            self.game_started = True
    
    def update_bird(self):
        """Update bird position and velocity"""
        if not self.game_started or self.game_over:
            return
        
        # Apply gravity (increased rate for faster falling)
        self.bird_velocity += GRAVITY * 0.12
        
        # Cap maximum velocities to prevent too fast movement
        if self.bird_velocity > 3.0:  # Increased maximum downward velocity for faster falling
            self.bird_velocity = 3.0
        if self.bird_velocity < -1.5:  # Maximum upward velocity (prevent overshooting, matches reduced jump)
            self.bird_velocity = -1.5
        
        # Update position
        self.bird_y += self.bird_velocity
        
        # Check boundaries (with some margin from edges)
        if self.bird_y < 1 or self.bird_y >= self.height - 2:
            self.end_game()
    
    def update_pipes(self):
        """Update pipe positions"""
        if not self.game_started or self.game_over:
            return
        
        current_speed = self.get_pipe_speed()
        
        for pipe in self.pipes:
            # Move pipes at speed based on level
            pipe['x'] -= current_speed
            
            # Check if bird passed the pipe
            if not pipe['passed'] and pipe['x'] + PIPE_WIDTH < self.bird_x:
                pipe['passed'] = True
                self.level_score += 1
                self.total_score += 1
                
                # Check if level complete
                if self.level_score >= self.points_per_level:
                    self.level_up()
            
            # Check collision
            if self.check_collision(pipe):
                self.end_game()
                return
        
        # Remove pipes that are off screen and add new ones
        self.pipes = [p for p in self.pipes if p['x'] > -PIPE_WIDTH]
        
        # Add new pipe if needed
        if len(self.pipes) < 3:
            last_x = max([p['x'] for p in self.pipes]) if self.pipes else self.width // 2
            self.pipes.append(self.create_pipe(last_x + PIPE_SPACING))
    
    def level_up(self):
        """Advance to next level"""
        if self.level < self.max_level:
            self.level += 1
            self.level_score = 0
            self.level_up_message_time = 60  # Show message for ~3 seconds (60 frames at 50ms)
        else:
            # Max level reached, keep playing but don't advance further
            self.level_score = self.points_per_level  # Cap at max
    
    def check_collision(self, pipe):
        """Check if bird collides with pipe"""
        pipe_x = pipe['x']
        gap_y = pipe['gap_y']
        gap_top = gap_y - PIPE_GAP // 2
        gap_bottom = gap_y + PIPE_GAP // 2
        
        # Check if bird is within pipe's x range (with small margin for more forgiving horizontal collision)
        # This gives the bird a tiny bit of leeway when passing through
        if pipe_x - COLLISION_MARGIN <= self.bird_x < pipe_x + PIPE_WIDTH + COLLISION_MARGIN:
            # Check if bird is outside gap (strict vertical check - no margin for gap boundaries)
            # This ensures the bird must actually be in the gap
            if self.bird_y < gap_top or self.bird_y > gap_bottom:
                return True
        
        return False
    
    def draw(self):
        """Draw everything on screen"""
        self.stdscr.clear()
        
        # Draw sky background (optional, just for visual)
        if self.colors_enabled:
            for y in range(self.height - 1):
                for x in range(self.width):
                    try:
                        self.stdscr.addstr(y, x, " ", curses.color_pair(3))
                    except:
                        pass
        
        # Draw ground
        ground_y = self.height - 1
        for x in range(self.width):
            try:
                if self.colors_enabled:
                    self.stdscr.addstr(ground_y, x, GROUND_CHAR, curses.color_pair(2))
                else:
                    self.stdscr.addstr(ground_y, x, GROUND_CHAR)
            except:
                pass
        
        # Draw pipes
        for pipe in self.pipes:
            pipe_x = int(pipe['x'])
            gap_y = int(pipe['gap_y'])
            gap_top = gap_y - PIPE_GAP // 2
            gap_bottom = gap_y + PIPE_GAP // 2
            
            # Only draw if pipe is visible
            if -PIPE_WIDTH <= pipe_x < self.width:
                # Top pipe
                for y in range(1, gap_top):
                    for x_offset in range(PIPE_WIDTH):
                        x = pipe_x + x_offset
                        if 0 <= x < self.width and 0 <= y < self.height - 1:
                            try:
                                if self.colors_enabled:
                                    self.stdscr.addstr(y, x, PIPE_CHAR, curses.color_pair(2))
                                else:
                                    self.stdscr.addstr(y, x, PIPE_CHAR)
                            except:
                                pass
                
                # Bottom pipe
                for y in range(gap_bottom + 1, self.height - 1):
                    for x_offset in range(PIPE_WIDTH):
                        x = pipe_x + x_offset
                        if 0 <= x < self.width and 0 <= y < self.height - 1:
                            try:
                                if self.colors_enabled:
                                    self.stdscr.addstr(y, x, PIPE_CHAR, curses.color_pair(2))
                                else:
                                    self.stdscr.addstr(y, x, PIPE_CHAR)
                            except:
                                pass
        
        # Draw bird
        bird_x = int(self.bird_x)
        bird_y = int(self.bird_y)
        if 0 <= bird_x < self.width and 0 <= bird_y < self.height - 1:
            try:
                if self.colors_enabled:
                    self.stdscr.addstr(bird_y, bird_x, self.bird_char, curses.color_pair(1))
                else:
                    self.stdscr.addstr(bird_y, bird_x, self.bird_char)
            except:
                pass
        
        # Draw score and level info
        level_text = f"Level: {self.level}/{self.max_level}"
        score_text = f"Level Score: {self.level_score}/{self.points_per_level} | Total: {self.total_score}"
        try:
            if self.colors_enabled:
                self.stdscr.addstr(0, 2, level_text, curses.color_pair(4) | curses.A_BOLD)
                self.stdscr.addstr(1, 2, score_text, curses.color_pair(4))
            else:
                self.stdscr.addstr(0, 2, level_text, curses.A_BOLD)
                self.stdscr.addstr(1, 2, score_text)
        except:
            pass
        
        # Draw level up message
        if self.level_up_message_time > 0:
            msg = f"LEVEL {self.level}!"
            msg_x = (self.width - len(msg)) // 2
            msg_y = self.height // 2
            try:
                if self.colors_enabled:
                    self.stdscr.addstr(msg_y, msg_x, msg, curses.color_pair(5) | curses.A_BOLD | curses.A_BLINK)
                else:
                    self.stdscr.addstr(msg_y, msg_x, msg, curses.A_BOLD | curses.A_BLINK)
            except:
                pass
            self.level_up_message_time -= 1
        
        # Draw messages
        if not self.game_started:
            msg = "Press SPACE to start/jump"
            msg_x = (self.width - len(msg)) // 2
            msg_y = self.height // 2
            try:
                if self.colors_enabled:
                    self.stdscr.addstr(msg_y, msg_x, msg, curses.color_pair(4))
                else:
                    self.stdscr.addstr(msg_y, msg_x, msg)
            except:
                pass
        
        if self.game_over:
            msg1 = "GAME OVER!"
            msg2 = f"Reached Level: {self.level} | Total Score: {self.total_score}"
            msg3 = "Press R to restart, Q to quit"
            msg1_x = (self.width - len(msg1)) // 2
            msg2_x = (self.width - len(msg2)) // 2
            msg3_x = (self.width - len(msg3)) // 2
            msg_y = self.height // 2 - 1
            try:
                if self.colors_enabled:
                    self.stdscr.addstr(msg_y, msg1_x, msg1, curses.color_pair(5) | curses.A_BOLD)
                    self.stdscr.addstr(msg_y + 1, msg2_x, msg2, curses.color_pair(4))
                    self.stdscr.addstr(msg_y + 2, msg3_x, msg3, curses.color_pair(4))
                else:
                    self.stdscr.addstr(msg_y, msg1_x, msg1, curses.A_BOLD)
                    self.stdscr.addstr(msg_y + 1, msg2_x, msg2)
                    self.stdscr.addstr(msg_y + 2, msg3_x, msg3)
            except:
                pass
        
        self.stdscr.refresh()
    
    def end_game(self):
        """End the game"""
        if self.game_over:
            return
        self.game_over = True
    
    def restart(self):
        """Restart the game"""
        self.level = 1
        self.level_score = 0
        self.total_score = 0
        self.level_up_message_time = 0
        self.game_over = False
        self.game_started = False
        self.bird_y = self.height // 2
        self.bird_velocity = 0
        self.pipes = []
        self.create_initial_pipes()
    
    def handle_input(self):
        """Handle keyboard input"""
        try:
            key = self.stdscr.getch()
            
            if key == ord(' ') or key == ord('w') or key == ord('W'):
                if not self.game_started:
                    self.start_game()
                else:
                    self.jump()
            elif key == ord('r') or key == ord('R'):
                if self.game_over:
                    self.restart()
            elif key == ord('q') or key == ord('Q') or key == 27:  # ESC
                if self.game_over:
                    return False
        except:
            pass
        
        return True
    
    def run(self):
        """Main game loop"""
        while True:
            if not self.handle_input():
                break
            
            self.update_bird()
            self.update_pipes()
            self.draw()
            
            time.sleep(0.05)  # Control game speed

def main(stdscr):
    """Main function wrapper for curses"""
    try:
        game = ClonyBird(stdscr)
        game.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        # If curses fails, show error message
        curses.endwin()
        print(f"Error: {e}")
        print("Make sure your terminal is large enough (at least 40x20)")
        sys.exit(1)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\nGame interrupted. Goodbye!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
