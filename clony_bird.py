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
        
        # Bird selection
        self.bird_selected = False
        self.selected_bird_index = 0  # 0 = Easy, 1 = Medium, 2 = Hard
        self.difficulty_multiplier = 1.0  # Base speed multiplier
        self.bird_options = [
            {"char": "✈️", "name": "Easy", "difficulty": 1.0, "desc": "Normal speed"},
            {"char": "🛩️", "name": "Medium", "difficulty": 1.1, "desc": "10% faster"},
            {"char": "🚁", "name": "Hard", "difficulty": 1.2, "desc": "20% faster"},
        ]
        
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
            curses.use_default_colors()  # Better performance
            curses.init_pair(1, curses.COLOR_YELLOW, -1)  # Bird (transparent bg)
            curses.init_pair(2, curses.COLOR_GREEN, -1)   # Pipes (transparent bg)
            curses.init_pair(3, curses.COLOR_CYAN, -1)    # Sky (transparent bg)
            curses.init_pair(4, curses.COLOR_WHITE, -1)   # Text (transparent bg)
            curses.init_pair(5, curses.COLOR_RED, -1)     # Game Over (transparent bg)
            self.colors_enabled = True
        except:
            self.colors_enabled = False
        
        # Set background color for better performance
        try:
            if self.colors_enabled:
                self.stdscr.bkgd(' ', curses.color_pair(3))
        except:
            pass
        
        # Check if terminal supports emoji and set default bird
        try:
            self.stdscr.addstr(0, 0, "✈️")
            self.stdscr.refresh()
            self.bird_char = self.bird_options[0]["char"]  # Default to first bird
        except:
            # Fallback characters if emoji not supported
            self.bird_options = [
                {"char": "A", "name": "Easy", "difficulty": 1.0, "desc": "10% slower"},
                {"char": "B", "name": "Medium", "difficulty": 1.1, "desc": "Normal speed"},
                {"char": "C", "name": "Hard", "difficulty": 1.2, "desc": "10% faster"},
            ]
            self.bird_char = self.bird_options[0]["char"]
    
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
        """Get pipe speed based on current level and difficulty"""
        # Level 1: speed 1, Level 2: speed 1.5, Level 3: speed 2, Level 4: speed 2.5, Level 5: speed 3
        base_speed = PIPE_SPEED + (self.level - 1) * 0.5
        # Apply difficulty multiplier (10% increase per difficulty level)
        return base_speed * self.difficulty_multiplier
    
    def select_bird(self, index):
        """Select a bird and set difficulty"""
        if 0 <= index < len(self.bird_options):
            self.selected_bird_index = index
            self.bird_char = self.bird_options[index]["char"]
            self.difficulty_multiplier = self.bird_options[index]["difficulty"]
            self.bird_selected = True
    
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
    
    def draw_bird_selection_screen(self):
        """Draw the bird selection screen"""
        center_y = self.height // 2
        center_x = self.width // 2
        
        # Title
        title = "SELECT YOUR BIRD"
        title_x = center_x - len(title) // 2
        
        # Instructions
        instructions = [
            "Use LEFT/RIGHT arrows or 1/2/3 to select",
            "Press SPACE or ENTER to confirm",
        ]
        
        # Draw title
        try:
            if self.colors_enabled:
                self.stdscr.addstr(2, title_x, title, curses.color_pair(1) | curses.A_BOLD)
            else:
                self.stdscr.addstr(2, title_x, title, curses.A_BOLD)
        except:
            pass
        
        # Draw bird options
        start_y = center_y - 2
        spacing = max(15, self.width // 4)
        
        for i, bird in enumerate(self.bird_options):
            x = center_x - (spacing * len(self.bird_options)) // 2 + i * spacing + spacing // 2
            
            # Highlight selected bird
            is_selected = (i == self.selected_bird_index)
            attr = curses.A_BOLD if is_selected else curses.A_NORMAL
            color = curses.color_pair(1) if is_selected else curses.color_pair(4)
            
            # Draw selection indicator
            if is_selected:
                try:
                    indicator = ">>>"
                    self.stdscr.addstr(start_y - 1, x - len(indicator) // 2, indicator, color | attr)
                except:
                    pass
            
            # Draw bird character
            try:
                if self.colors_enabled:
                    self.stdscr.addstr(start_y, x - 1, bird["char"], color | attr)
                else:
                    self.stdscr.addstr(start_y, x - 1, bird["char"], attr)
            except:
                pass
            
            # Draw bird name
            name_x = x - len(bird["name"]) // 2
            try:
                if self.colors_enabled:
                    self.stdscr.addstr(start_y + 1, name_x, bird["name"], color | attr)
                else:
                    self.stdscr.addstr(start_y + 1, name_x, bird["name"], attr)
            except:
                pass
            
            # Draw difficulty description
            desc_x = x - len(bird["desc"]) // 2
            try:
                if self.colors_enabled:
                    self.stdscr.addstr(start_y + 2, desc_x, bird["desc"], curses.color_pair(4))
                else:
                    self.stdscr.addstr(start_y + 2, desc_x, bird["desc"])
            except:
                pass
        
        # Draw instructions
        inst_y = start_y + 5
        for i, line in enumerate(instructions):
            if inst_y + i < self.height - 1:
                x = center_x - len(line) // 2
                try:
                    if self.colors_enabled:
                        self.stdscr.addstr(inst_y + i, x, line, curses.color_pair(4))
                    else:
                        self.stdscr.addstr(inst_y + i, x, line)
                except:
                    pass
    
    def draw_welcome_screen(self):
        """Draw the welcome/start screen"""
        center_y = self.height // 2
        center_x = self.width // 2
        
        # ASCII art for "CLONY BIRD" - all lines padded to same length
        title_lines = [
            "  ____ _                    ____  _     _ _ ",
            " / ___| | ___  _ __   ___  | __ )(_) __| | |",
            "| |   | |/ _ \\| '_ \\ / _ \\ |  _ \\| |/ _` | |",
            "| |___| | (_) | | | |  __/ | |_) | | (_| |_|",
            " \\____|_|\\___/|_| |_|\\___| |____/|_|\\__,_(_)",
        ]
        
        # Find the longest line for proper centering
        max_line_length = max(len(line) for line in title_lines)
        
        # Welcome text
        welcome_text = "WELCOME!"
        
        # Instructions
        instructions = [
            "Press SPACE or W to start and jump",
            "",
            "Navigate through pipes and advance through 5 levels!",
            "Each level requires 30 points to complete.",
            "Speed increases with each level.",
            "",
            "Controls:",
            "  SPACE / W  - Jump",
            "  R          - Restart (after game over)",
            "  Q / ESC    - Quit",
        ]
        
        # Draw title - center based on longest line
        start_y = max(2, center_y - 8)
        for i, line in enumerate(title_lines):
            if start_y + i < self.height - 1:
                # Center based on max line length, then adjust for actual line
                x = center_x - max_line_length // 2
                if x >= 0 and x + len(line) < self.width:
                    try:
                        if self.colors_enabled:
                            self.stdscr.addstr(start_y + i, x, line, curses.color_pair(1) | curses.A_BOLD)
                        else:
                            self.stdscr.addstr(start_y + i, x, line, curses.A_BOLD)
                    except:
                        pass
        
        # Draw welcome text
        welcome_y = start_y + len(title_lines) + 1
        welcome_x = center_x - len(welcome_text) // 2
        if welcome_y < self.height - 1 and welcome_x >= 0:
            try:
                if self.colors_enabled:
                    self.stdscr.addstr(welcome_y, welcome_x, welcome_text, curses.color_pair(5) | curses.A_BOLD | curses.A_BLINK)
                else:
                    self.stdscr.addstr(welcome_y, welcome_x, welcome_text, curses.A_BOLD | curses.A_BLINK)
            except:
                pass
        
        # Draw instructions
        inst_start_y = welcome_y + 3
        for i, line in enumerate(instructions):
            if inst_start_y + i < self.height - 2:
                x = center_x - len(line) // 2
                if x >= 0 and x + len(line) < self.width:
                    try:
                        if self.colors_enabled:
                            self.stdscr.addstr(inst_start_y + i, x, line, curses.color_pair(4))
                        else:
                            self.stdscr.addstr(inst_start_y + i, x, line)
                    except:
                        pass
    
    def draw_game_over_screen(self):
        """Draw the game over screen"""
        center_y = self.height // 2
        center_x = self.width // 2
        
        # ASCII art for "GAME OVER" - find max length for alignment
        game_over_lines = [
            "   ____                        ___",
            "  / ___| __ _ _ __ ___   ___  / _ \\__   _____ _ __",
            " | |  _ / _` | '_ ` _ \\ / _ \\| | | \\ \\ / / _ \\ '__|",
            " | |_| | (_| | | | | | |  __/| |_| |\\ V /  __/ |",
            "  \\____|\\__,_|_| |_| |_|\\___|  \\___/  \\_/ \\___|_|",
        ]
        
        # Find the longest line for proper centering
        max_line_length = max(len(line) for line in game_over_lines)
        
        # Stats
        selected_bird = self.bird_options[self.selected_bird_index]
        stats = [
            f"Difficulty: {selected_bird['name']} ({selected_bird['desc']})",
            f"Level Reached: {self.level}",
            f"Total Score: {self.total_score}",
            f"Level Score: {self.level_score}/{self.points_per_level}",
        ]
        
        # Instructions
        instructions = [
            "",
            "Press R to restart",
            "Press Q to quit",
        ]
        
        # Draw game over title - center based on longest line
        start_y = max(2, center_y - 6)
        for i, line in enumerate(game_over_lines):
            if start_y + i < self.height - 1:
                # Center based on max line length
                x = center_x - max_line_length // 2
                if x >= 0 and x + len(line) < self.width:
                    try:
                        if self.colors_enabled:
                            self.stdscr.addstr(start_y + i, x, line, curses.color_pair(5) | curses.A_BOLD)
                        else:
                            self.stdscr.addstr(start_y + i, x, line, curses.A_BOLD)
                    except:
                        pass
        
        # Draw stats
        stats_start_y = start_y + len(game_over_lines) + 2
        for i, stat in enumerate(stats):
            if stats_start_y + i < self.height - 1:
                x = center_x - len(stat) // 2
                if x >= 0 and x + len(stat) < self.width:
                    try:
                        if self.colors_enabled:
                            self.stdscr.addstr(stats_start_y + i, x, stat, curses.color_pair(4) | curses.A_BOLD)
                        else:
                            self.stdscr.addstr(stats_start_y + i, x, stat, curses.A_BOLD)
                    except:
                        pass
        
        # Draw instructions
        inst_start_y = stats_start_y + len(stats) + 1
        for i, line in enumerate(instructions):
            if inst_start_y + i < self.height - 1:
                x = center_x - len(line) // 2
                if x >= 0 and x + len(line) < self.width:
                    try:
                        if self.colors_enabled:
                            self.stdscr.addstr(inst_start_y + i, x, line, curses.color_pair(4))
                        else:
                            self.stdscr.addstr(inst_start_y + i, x, line)
                    except:
                        pass
    
    def draw(self):
        """Draw everything on screen - optimized to reduce flickering"""
        # Use erase() instead of clear() for better performance
        self.stdscr.erase()
        
        # Draw ground (only one line, efficient)
        ground_y = self.height - 1
        ground_line = GROUND_CHAR * self.width
        try:
            if self.colors_enabled:
                self.stdscr.addstr(ground_y, 0, ground_line[:self.width], curses.color_pair(2))
            else:
                self.stdscr.addstr(ground_y, 0, ground_line[:self.width])
        except:
            pass
        
        # Only draw game elements if bird is selected, game is started and not over
        if self.bird_selected and self.game_started and not self.game_over:
            # Draw pipes (optimized - draw by lines instead of pixels)
            pipe_line = PIPE_CHAR * PIPE_WIDTH
            pipe_attr = curses.color_pair(2) if self.colors_enabled else 0
            
            for pipe in self.pipes:
                pipe_x = int(pipe['x'])
                gap_y = int(pipe['gap_y'])
                gap_top = gap_y - PIPE_GAP // 2
                gap_bottom = gap_y + PIPE_GAP // 2
                
                # Only draw if pipe is visible
                if -PIPE_WIDTH <= pipe_x < self.width:
                    # Calculate visible area
                    start_x = max(0, pipe_x)
                    end_x = min(self.width, pipe_x + PIPE_WIDTH)
                    visible_width = end_x - start_x
                    offset = start_x - pipe_x
                    
                    if visible_width > 0:
                        visible_pipe = pipe_line[offset:offset + visible_width]
                        
                        # Top pipe - draw line by line
                        for y in range(1, gap_top):
                            if 0 <= y < self.height - 1:
                                try:
                                    if self.colors_enabled:
                                        self.stdscr.addstr(y, start_x, visible_pipe, pipe_attr)
                                    else:
                                        self.stdscr.addstr(y, start_x, visible_pipe)
                                except:
                                    pass
                        
                        # Bottom pipe - draw line by line
                        for y in range(gap_bottom + 1, self.height - 1):
                            if 0 <= y < self.height - 1:
                                try:
                                    if self.colors_enabled:
                                        self.stdscr.addstr(y, start_x, visible_pipe, pipe_attr)
                                    else:
                                        self.stdscr.addstr(y, start_x, visible_pipe)
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
            
            # Draw score and level info (only during gameplay)
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
        
        # Draw level up message (only during active gameplay)
        if self.game_started and not self.game_over and self.level_up_message_time > 0:
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
        
        # Draw bird selection, welcome screen, or game over screen
        if not self.bird_selected:
            self.draw_bird_selection_screen()
        elif not self.game_started:
            self.draw_welcome_screen()
        elif self.game_over:
            self.draw_game_over_screen()
        
        # Use noutrefresh + doupdate for better performance (reduces flickering)
        self.stdscr.noutrefresh()
        curses.doupdate()
    
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
        self.bird_selected = False  # Reset bird selection
        self.selected_bird_index = 0  # Reset to first bird
        self.difficulty_multiplier = 1.0  # Reset difficulty
        self.bird_y = self.height // 2
        self.bird_velocity = 0
        self.pipes = []
        self.create_initial_pipes()
        # Reset bird character to default
        self.bird_char = self.bird_options[0]["char"]
    
    def handle_input(self):
        """Handle keyboard input"""
        try:
            key = self.stdscr.getch()
            
            # Bird selection phase
            if not self.bird_selected:
                if key == curses.KEY_LEFT or key == ord('a') or key == ord('A'):
                    # Move selection left
                    self.selected_bird_index = (self.selected_bird_index - 1) % len(self.bird_options)
                elif key == curses.KEY_RIGHT or key == ord('d') or key == ord('D'):
                    # Move selection right
                    self.selected_bird_index = (self.selected_bird_index + 1) % len(self.bird_options)
                elif key == ord('1'):
                    self.select_bird(0)
                elif key == ord('2'):
                    self.select_bird(1)
                elif key == ord('3'):
                    self.select_bird(2)
                elif key == ord(' ') or key == ord('\n') or key == ord('\r'):  # SPACE or ENTER
                    # Confirm selection
                    self.select_bird(self.selected_bird_index)
            # Quit functionality (works at any time)
            if key == ord('q') or key == ord('Q') or key == 27:  # ESC or Q
                return False
            
            # Game controls (only after bird is selected)
            if key == ord(' ') or key == ord('w') or key == ord('W'):
                if not self.game_started:
                    self.start_game()
                else:
                    self.jump()
            elif key == ord('r') or key == ord('R'):
                if self.game_over:
                    self.restart()
        except:
            pass
        
        return True
    
    def run(self):
        """Main game loop - optimized for smooth rendering"""
        while True:
            if not self.handle_input():
                break
            
            # Only update game logic if bird is selected
            if self.bird_selected:
                self.update_bird()
                self.update_pipes()
            
            self.draw()
            
            # Reduced sleep time for smoother gameplay (less flickering)
            time.sleep(0.03)  # 30ms for ~33 FPS

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
