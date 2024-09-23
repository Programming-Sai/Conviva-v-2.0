import sys
import tty
import termios

# ANSI color codes
GREEN = "\033[32m"
RESET = "\033[0m"

def colored_input(prompt, color=GREEN):
    # Display the prompt
    sys.stdout.write(prompt)
    sys.stdout.flush()

    # Save terminal settings
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    
    try:
        tty.setcbreak(sys.stdin.fileno())  # Set terminal to cbreak mode
        input_chars = []
        while True:
            char = sys.stdin.read(1)  # Read one character at a time
            if char == '\n':  # If the user presses Enter, stop input
                sys.stdout.write('\n')
                break
            elif char == '\x7f':  # Handle backspace
                if input_chars:
                    input_chars.pop()  # Remove last character from the list
                    sys.stdout.write('\b \b')  # Move cursor back and clear the character
            else:
                input_chars.append(char)  # Append valid character
                sys.stdout.write(f"{color}{char}{RESET}")  # Print character in color
            sys.stdout.flush()
        
        return ''.join(input_chars)  # Return the captured input
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)  # Restore terminal settings

# Example usage
name = colored_input("NAME: ", GREEN)
print(f"You entered: {name}")
