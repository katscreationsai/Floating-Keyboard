import tkinter as tk
from tkinter import ttk
import sys
import ctypes

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
    pyautogui.FAILSAFE = False
except ImportError:
    PYAUTOGUI_AVAILABLE = False

class BrightPinkLightKeyboardApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Bright Pink Light Floating Keyboard")
        self.geometry("820x400")
        
        # Window configuration for floating overlay
        self.overrideredirect(True)      # Remove standard OS title bar
        self.attributes("-topmost", True)  # Stay on top of other windows
        self.attributes("-alpha", 0.90)    # Transparency slider base value (90%)

        # State tracking variables
        self.is_shift = False
        self.is_caps = False
        self.is_ctrl_active = False        # State tracking for Ctrl shortcuts
        self.drag_x = 0
        self.drag_y = 0

        # Symbol Map matching standard QWERTY shift numbers
        self.shift_symbols = {
            '1': '!', '2': '@', '3': '#', '4': '$', '5': '%',
            '6': '^', '7': '&', '8': '*', '9': '(', '0': ')',
            '-': '_', '=': '+', '`': '~', '[': '{', ']': '}',
            '\\': '|', ';': ':', "'": '"', ',': '<', '.': '>', '/': '?'
        }

        # Bright Pink & White Light Theme Styling Palette
        self.bg_color = "#fff0f5"          # Lavender Blush / Soft light pink outer canvas
        self.panel_color = "#ffb6c1"       # Light pink header/title bar
        self.key_bg = "#ffffff"            # Crisp white keycaps
        self.key_fg = "#d14770"            # Deep hot pink text color for readability
        self.key_active = "#ff69b4"        # Hot Pink when pressed
        self.key_active_fg = "#ffffff"     # White text when key is pressed active
        self.ctrl_active_bg = "#ff1493"    # Deep vibrant pink when Ctrl is engaged
        self.modifier_active_bg = "#ff69b4"# Bright pink for active Shift/Caps
        
        self.configure(bg=self.bg_color)

        # Build UI Structure
        self.create_title_bar()
        self.create_keyboard_layout()

        # Apply OS-level style to PREVENT focus-stealing on Windows
        self.after(100, self.apply_no_activate_style)

    def apply_no_activate_style(self):
        """Forces Windows API to assign WS_EX_NOACTIVATE so clicks never steal text cursor focus."""
        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            if not hwnd:
                hwnd = self.winfo_id()
            GWL_EXSTYLE = -20
            WS_EX_NOACTIVATE = 0x08000000
            WS_EX_TOOLWINDOW = 0x00000080
            
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW)
        except Exception as e:
            print(f"Note: Could not apply native no-activate style: {e}")

    def create_title_bar(self):
        """Creates a custom draggable title bar with transparency slider and close utility."""
        title_bar = tk.Frame(self, bg=self.panel_color, relief="flat", height=35)
        title_bar.pack(fill="x", side="top")
        title_bar.pack_propagate(False)

        # Window Dragging Bindings
        title_bar.bind("<Button-1>", self.start_move)
        title_bar.bind("<B1-Motion>", self.on_move)

        title_label = tk.Label(
            title_bar, text=" 💖 Bright Pink Floating Keyboard", 
            bg=self.panel_color, fg="#8b0032", font=("Segoe UI", 10, "bold")
        )
        title_label.pack(side="left", padx=10)
        title_label.bind("<Button-1>", self.start_move)
        title_label.bind("<B1-Motion>", self.on_move)

        close_btn = tk.Button(
            title_bar, text="✕", bg=self.panel_color, fg="#8b0032", 
            bd=0, font=("Segoe UI", 10, "bold"), activebackground="#ff1493",
            activeforeground="#ffffff", command=self.destroy, width=4
        )
        close_btn.pack(side="right", fill="y")

        # Opacity Slider Frame
        slider_frame = tk.Frame(title_bar, bg=self.panel_color)
        slider_frame.pack(side="right", padx=15)

        trans_label = tk.Label(slider_frame, text="Opacity:", bg=self.panel_color, fg="#8b0032", font=("Segoe UI", 9))
        trans_label.pack(side="left", padx=2)

        self.opacity_var = tk.DoubleVar(value=0.90)
        self.trans_slider = ttk.Scale(
            slider_frame, from_=0.2, to=1.0, 
            variable=self.opacity_var,
            orient="horizontal", length=100, command=self.change_transparency
        )
        self.trans_slider.pack(side="left", padx=2)

    def create_keyboard_layout(self):
        """Generates full Function row, symbol row, and standard QWERTY layout matrix."""
        self.keyboard_frame = tk.Frame(self, bg=self.bg_color)
        self.keyboard_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.rows = [
            ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'],
            ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+'], # Dedicated easy-access symbol row
            ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
            ['Tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'],
            ['Caps', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", 'Enter'],
            ['Shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'Shift'],
            ['Ctrl', 'Space']
        ]

        self.key_buttons = {}

        for row in self.rows:
            row_frame = tk.Frame(self.keyboard_frame, bg=self.bg_color)
            row_frame.pack(fill="both", expand=True, pady=2)

            for key in row:
                width_val = 4
                if key in ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']:
                    width_val = 3
                elif key in ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+']:
                    width_val = 4
                elif key == 'Backspace': width_val = 8
                elif key == 'Tab': width_val = 5
                elif key == 'Caps': width_val = 6
                elif key == 'Enter': width_val = 7
                elif key == 'Shift': width_val = 7
                elif key == 'Ctrl': width_val = 5
                elif key == 'Space': width_val = 30

                btn = tk.Button(
                    row_frame, text=key, font=("Segoe UI", 9, "bold" if "F" in key or key in ["Ctrl", "Shift", "Caps"] else "normal"),
                    bg=self.key_bg, fg=self.key_fg, activebackground=self.key_active,
                    activeforeground=self.key_active_fg, bd=1, relief="raised",
                    width=width_val, takefocus=False,
                    command=lambda k=key: self.on_key_click(k)
                )
                btn.pack(side="left", fill="both", expand=True, padx=1, pady=1)
                
                if key == 'Ctrl':
                    self.ctrl_button = btn
                elif key == 'Shift':
                    if not hasattr(self, 'shift_buttons'):
                        self.shift_buttons = []
                    self.shift_buttons.append(btn)
                elif key == 'Caps':
                    self.caps_button = btn
                elif len(key) == 1 and key.isalpha():
                    self.key_buttons[key] = btn

    def change_transparency(self, val):
        self.attributes("-alpha", float(val))

    def start_move(self, event):
        self.drag_x = event.x
        self.drag_y = event.y

    def on_move(self, event):
        deltax = event.x - self.drag_x
        deltay = event.y - self.drag_y
        new_x = self.winfo_x() + deltax
        new_y = self.winfo_y() + deltay
        self.geometry(f"+{new_x}+{new_y}")

    def on_key_click(self, key):
        """Processes keystrokes, modifiers, and function commands directly into external windows."""
        if key == 'Ctrl':
            self.is_ctrl_active = not self.is_ctrl_active
            if self.is_ctrl_active:
                self.ctrl_button.config(bg=self.ctrl_active_bg, fg="#ffffff")
            else:
                self.ctrl_button.config(bg=self.key_bg, fg=self.key_fg)
            return

        elif key == 'Caps':
            self.is_caps = not self.is_caps
            if self.is_caps:
                self.caps_button.config(bg=self.modifier_active_bg, fg="#ffffff")
            else:
                self.caps_button.config(bg=self.key_bg, fg=self.key_fg)
            self.update_case()
            return
            
        elif key == 'Shift':
            self.is_shift = not self.is_shift
            shift_color = self.modifier_active_bg if self.is_shift else self.key_bg
            shift_fg = "#ffffff" if self.is_shift else self.key_fg
            for s_btn in getattr(self, 'shift_buttons', []):
                s_btn.config(bg=shift_color, fg=shift_fg)
            self.update_case()
            return

        # Handle characters based on Shift/Caps logic
        if key == 'Space':
            char_to_send = ' '
        elif key == 'Backspace':
            char_to_send = 'backspace'
        elif key == 'Enter':
            char_to_send = 'enter'
        elif key == 'Tab':
            char_to_send = 'tab'
        elif key.startswith('F') and key[1:].isdigit():
            char_to_send = key.lower()
        else:
            char_to_send = key
            # Check if Shift is active to map standard numbers/symbols to secondary characters
            if self.is_shift and key in self.shift_symbols:
                char_to_send = self.shift_symbols[key]
            elif self.is_shift ^ self.is_caps and len(key) == 1 and key.isalpha():
                char_to_send = char_to_send.upper()
            
            # Auto-reset Shift after one key press, matching physical keyboard behavior
            if self.is_shift:
                self.is_shift = False
                for s_btn in getattr(self, 'shift_buttons', []):
                    s_btn.config(bg=self.key_bg, fg=self.key_fg)
                self.update_case()

        if PYAUTOGUI_AVAILABLE:
            try:
                if self.is_ctrl_active:
                    pyautogui.hotkey('ctrl', char_to_send)
                    self.is_ctrl_active = False
                    self.ctrl_button.config(bg=self.key_bg, fg=self.key_fg)
                else:
                    pyautogui.press(char_to_send)
            except Exception as e:
                print(f"Injection Error: {e}")
        else:
            action = f"Ctrl+{char_to_send}" if self.is_ctrl_active else char_to_send
            print(f"[Simulated Shortcut/Key]: {action}")
            if self.is_ctrl_active:
                self.is_ctrl_active = False
                self.ctrl_button.config(bg=self.key_bg, fg=self.key_fg)

    def update_case(self):
        upper_active = self.is_caps or self.is_shift
        for char, btn in self.key_buttons.items():
            btn.config(text=char.upper() if upper_active else char.lower())

if __name__ == "__main__":
    app = BrightPinkLightKeyboardApp()
    app.mainloop()