import random
import shutil






class AsciiColors:
    """
    This class contains all text colors, background colors, and text formatting codes.
    """
    # Text colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright text colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    # Dark text colors
    DARK_GRAY = '\033[90m'
    DARK_RED = '\033[31m'
    DARK_GREEN = '\033[32m'
    DARK_YELLOW = '\033[33m'
    DARK_BLUE = '\033[34m'
    DARK_MAGENTA = '\033[35m'
    DARK_CYAN = '\033[36m'
    DARK_WHITE = '\033[37m'

    # Text styles
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    REVERSED = '\033[7m'
    DIM = '\033[2m'
    BLINK = '\033[5m'
    ITALIC = '\033[3m'  # Not all terminals support this

    # Strikethrough text style
    STRIKETHROUGH = '\033[9m'

    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

    # Bright background colors
    BG_BRIGHT_BLACK = '\033[100m'
    BG_BRIGHT_RED = '\033[101m'
    BG_BRIGHT_GREEN = '\033[102m'
    BG_BRIGHT_YELLOW = '\033[103m'
    BG_BRIGHT_BLUE = '\033[104m'
    BG_BRIGHT_MAGENTA = '\033[105m'
    BG_BRIGHT_CYAN = '\033[106m'
    BG_BRIGHT_WHITE = '\033[107m'

    # Reset
    RESET = '\033[0m'

    # Color and style lists
    text_colors = [
        BLACK, RED, GREEN, YELLOW,
        BLUE, MAGENTA, CYAN, WHITE,
        BRIGHT_BLACK, BRIGHT_RED, BRIGHT_GREEN,
        BRIGHT_YELLOW, BRIGHT_BLUE, BRIGHT_MAGENTA,
        BRIGHT_CYAN, BRIGHT_WHITE,
        DARK_GRAY, DARK_RED, DARK_GREEN,
        DARK_YELLOW, DARK_BLUE, DARK_MAGENTA,
        DARK_CYAN, DARK_WHITE
    ]

    background_colors = [
        BG_BLACK, BG_RED, BG_GREEN, BG_YELLOW,
        BG_BLUE, BG_MAGENTA, BG_CYAN, BG_WHITE,
        BG_BRIGHT_BLACK, BG_BRIGHT_RED, BG_BRIGHT_GREEN,
        BG_BRIGHT_YELLOW, BG_BRIGHT_BLUE, BG_BRIGHT_MAGENTA,
        BG_BRIGHT_CYAN, BG_BRIGHT_WHITE
    ]

    text_styles = [
        BOLD, UNDERLINE, REVERSED, DIM,
        BLINK, ITALIC, STRIKETHROUGH
    ]

    def color(self, text_to_color, color):
        return color + text_to_color + self.RESET
    
    def random_color(self, text_to_color):
        return random.choice([ random.choice(self.text_colors), random.choice(self.text_styles) ]) + text_to_color + self.RESET

    def center_text(self, text):
        return text.center(shutil.get_terminal_size().columns)
    
    def center_block_text(self, text):
        terminal_width = shutil.get_terminal_size().columns
        lines = text.splitlines()  # Split into individual lines
        centered_lines = [line.center(terminal_width) for line in lines]  # Center each line
        return "\n".join(centered_lines)  # Join centered lines back together




# x = AsciiColors()

# print(x.random_color("Hello"))
# print(x.center_block_text(x.color(title, x.RED)))
