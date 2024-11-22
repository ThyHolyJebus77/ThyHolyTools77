import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import win32api
import win32gui
import win32con
import pywintypes
import threading
import ctypes
import subprocess
import json
import os

user32 = ctypes.windll.user32

# Constants for SetDisplayConfig
SDC_TOPOLOGY_INTERNAL = 0x00000001
SDC_TOPOLOGY_CLONE = 0x00000002
SDC_TOPOLOGY_EXTEND = 0x00000004
SDC_TOPOLOGY_EXTERNAL = 0x00000008
SDC_APPLY = 0x00000080

# Default configurations with categories
DEFAULT_RESOLUTIONS = {
    "Normal": [
        (3840, 2160, "4K"),
        (2560, 1440, "1440p"),
        (1920, 1080, "1080p"),
        (1360, 768, "768p"),
    ],
    "Tablet": [
        (3000, 2000, "Tablet 100%"),
        (2250, 1500, "Tablet 75%"),
        (1500, 1000, "Tablet 50%"),
        (750, 500, "Tablet 25%"),
    ],
    "Phone": [
        (3120, 1440, "Phone 100%"),
        (2340, 1080, "Phone 75%"),
        (1560, 720, "Phone 50%"),
        (780, 360, "Phone 25%"),
    ]
}
CONFIG_FILE = "resolutions.json"
SETTINGS_FILE = "settings.json"

def get_current_resolution():
    return (win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1))

def get_monitor_count():
    return user32.GetSystemMetrics(win32con.SM_CMONITORS)

original_resolution = get_current_resolution()
monitor_count = get_monitor_count()

# Load settings
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    else:
        return {"revert_time": 30}

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

settings = load_settings()

def change_resolution(width, height):
    try:
        devmode = pywintypes.DEVMODEType()
        devmode.PelsWidth = width
        devmode.PelsHeight = height
        devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT

        win32api.ChangeDisplaySettings(devmode, 0)

        # Update current resolution display
        current_resolution_label.config(text=f"Current Resolution: {width}x{height}")
        return True
    except Exception as e:
        show_temporary_message(f"Failed to change resolution: {str(e)}", "Error", duration=3000)
        return False

def revert_resolution():
    global timer_running
    timer_running = False
    change_resolution(*original_resolution)
    show_temporary_message(f"Resolution reverted to {original_resolution[0]}x{original_resolution[1]}", "Reverted", duration=3000)
    countdown_label.config(text="")

def confirm_resolution():
    global timer_running
    timer_running = False
    show_temporary_message("Resolution change confirmed", "Confirmed", duration=3000)
    if timer_thread and timer_thread.is_alive():
        timer_thread.join(timeout=0)
    countdown_label.config(text="")

def change_resolution_with_revert(width, height):
    if change_resolution(width, height):
        global timer_running
        timer_running = True

        # Update the countdown timer display
        start_countdown(settings["revert_time"])

        show_temporary_message(
            f"Resolution changed to {width}x{height}\n"
            f"It will revert in {settings['revert_time']} seconds if not confirmed.\n"
            "Click 'Confirm' to keep this resolution.",
            "Resolution Changed",
            duration=5000
        )

def show_temporary_message(message, title="Info", duration=3000):
    temp_win = tk.Toplevel(root)
    temp_win.title(title)
    temp_win.geometry("350x150")
    temp_win.resizable(False, False)
    temp_win.attributes("-topmost", True)
    label = tk.Label(temp_win, text=message, wraplength=330)
    label.pack(expand=True, fill='both', padx=10, pady=10)
    temp_win.after(duration, temp_win.destroy)

def create_resolution_button(parent_frame, width, height, text, category):
    btn_text = f"{text} ({width}x{height})"
    btn = tk.Button(parent_frame, text=btn_text, command=lambda: change_resolution_with_revert(width, height))
    btn.bind("<Button-3>", lambda e: show_context_menu(e, btn, width, height, text, category))
    create_tooltip(btn, f"Change resolution to {width}x{height}")
    return btn

def show_context_menu(event, button, width, height, text, category):
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="Remove", command=lambda: remove_resolution(button, width, height, text, category))
    menu.post(event.x_root, event.y_root)

def remove_resolution(button, width, height, text, category):
    global resolutions
    resolutions[category] = [res for res in resolutions[category] if not (res[0]==width and res[1]==height and res[2]==text)]
    save_resolutions()
    refresh_resolution_buttons()

def add_resolution():
    add_win = tk.Toplevel(root)
    add_win.title("Add Resolution")
    add_win.geometry("250x250")
    add_win.resizable(False, False)
    add_win.attributes("-topmost", True)

    tk.Label(add_win, text="Width:").pack(pady=5)
    width_entry = tk.Entry(add_win)
    width_entry.pack()

    tk.Label(add_win, text="Height:").pack(pady=5)
    height_entry = tk.Entry(add_win)
    height_entry.pack()

    tk.Label(add_win, text="Label:").pack(pady=5)
    label_entry = tk.Entry(add_win)
    label_entry.pack()

    tk.Label(add_win, text="Category:").pack(pady=5)
    category_var = tk.StringVar(value="Normal")
    category_options = list(resolutions.keys())
    category_menu = ttk.OptionMenu(add_win, category_var, category_var.get(), *category_options)
    category_menu.pack()

    def confirm_add():
        try:
            width = int(width_entry.get())
            height = int(height_entry.get())
            label = label_entry.get() or f"{width}x{height}"
            category = category_var.get()
            if category not in resolutions:
                resolutions[category] = []
            resolutions[category].append((width, height, label))
            save_resolutions()
            refresh_resolution_buttons()
            add_win.destroy()
        except ValueError:
            show_temporary_message("Please enter valid numeric values for width and height.", "Input Error", duration=3000)

    tk.Button(add_win, text="Add", command=confirm_add).pack(pady=10)

def refresh_resolution_buttons():
    for widget in resolution_buttons_frame.winfo_children():
        widget.destroy()

    for category, res_list in resolutions.items():
        # Create a label for the category
        category_label = tk.Label(resolution_buttons_frame, text=category + " Resolutions", font=('Arial', 12, 'bold'))
        category_label.pack(pady=(10, 5))

        # Create a frame for the buttons
        button_frame = tk.Frame(resolution_buttons_frame)
        button_frame.pack()

        # Create buttons for each resolution in the category
        for i, (width, height, text) in enumerate(res_list):
            button = create_resolution_button(button_frame, width, height, text, category)
            button.grid(row=i // 2, column=i % 2, padx=5, pady=5, sticky="nsew")

        # Adjust grid weights
        num_rows = (len(res_list) + 1) // 2
        for i in range(num_rows):
            button_frame.rowconfigure(i, weight=1)
        for j in range(2):
            button_frame.columnconfigure(j, weight=1)

def toggle_display_mode():
    try:
        # Get current display settings
        current_mode = user32.GetSystemMetrics(win32con.SM_CMONITORS)

        if current_mode > 1:
            # Currently in extended mode, switch to internal display only
            subprocess.run(["DisplaySwitch.exe", "/internal"], check=True)
            new_mode = "Single Screen (Internal Only)"
        else:
            # Currently in single screen mode, switch to extended mode
            subprocess.run(["DisplaySwitch.exe", "/extend"], check=True)
            new_mode = "Extended Screens"

        show_temporary_message(f"Switched to {new_mode} mode", "Display Mode Changed", duration=3000)
        # Update monitor count display
        monitor_count = get_monitor_count()
        monitor_count_label.config(text=f"Connected Monitors: {monitor_count}")
    except subprocess.CalledProcessError as e:
        show_temporary_message(f"Failed to change display mode. Error: {e}", "Error", duration=3000)
    except Exception as e:
        show_temporary_message(f"Failed to change display mode: {str(e)}", "Error", duration=3000)

def create_control_buttons(parent_frame):
    # Add Resolution button
    add_button = tk.Button(parent_frame, text="Add Resolution", command=add_resolution)
    add_button.pack(side='left', padx=5)
    create_tooltip(add_button, "Add a new custom resolution")

    # Confirm Resolution button
    confirm_button = tk.Button(parent_frame, text="Confirm Resolution", command=confirm_resolution)
    confirm_button.pack(side='left', padx=5)
    create_tooltip(confirm_button, "Confirm the current resolution")

    # Revert to Original button
    revert_button = tk.Button(parent_frame, text="Revert to Original", command=revert_resolution)
    revert_button.pack(side='left', padx=5)
    create_tooltip(revert_button, "Revert to the original resolution")

    # Toggle Screen Mode button
    toggle_button = tk.Button(parent_frame, text="Toggle Screen Mode", command=toggle_display_mode)
    toggle_button.pack(side='left', padx=5)
    create_tooltip(toggle_button, "Toggle between single and extended screen modes")

    # Settings button
    settings_button = tk.Button(parent_frame, text="Settings", command=open_settings)
    settings_button.pack(side='left', padx=5)
    create_tooltip(settings_button, "Adjust application settings")

def create_tooltip(widget, text):
    tooltip = ToolTip(widget, text)
    return tooltip

class ToolTip(object):
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     # milliseconds
        self.wraplength = 180   # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.id = None
        self.top = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hide_tip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.show_tip)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def show_tip(self):
        x = y = 0
        x = self.widget.winfo_pointerx() + 10
        y = self.widget.winfo_pointery() + 10
        self.top = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         wraplength=self.wraplength)
        label.pack(ipadx=1)

    def hide_tip(self):
        tw = self.top
        self.top = None
        if tw:
            tw.destroy()

def start_countdown(seconds):
    global countdown_thread
    countdown_thread = threading.Thread(target=countdown, args=(seconds,))
    countdown_thread.start()

def countdown(seconds):
    global timer_running
    while timer_running and seconds > 0:
        countdown_label.config(text=f"Time before revert: {seconds} seconds")
        time.sleep(1)
        seconds -= 1
    if timer_running and seconds == 0:
        revert_resolution()

def save_resolutions():
    with open(CONFIG_FILE, 'w') as f:
        json.dump(resolutions, f)

def load_resolutions():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict):
                # Data is already in the new format
                return data
            elif isinstance(data, list):
                # Data is in the old list format
                # Convert it to the new format under a default category
                return {"Custom": data}
    else:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_RESOLUTIONS, f)
        return DEFAULT_RESOLUTIONS

def open_settings():
    settings_win = tk.Toplevel(root)
    settings_win.title("Settings")
    settings_win.geometry("300x150")
    settings_win.resizable(False, False)
    settings_win.attributes("-topmost", True)

    tk.Label(settings_win, text="Revert Time (seconds):").pack(pady=10)
    revert_time_entry = tk.Entry(settings_win)
    revert_time_entry.insert(0, str(settings["revert_time"]))
    revert_time_entry.pack()

    def save_settings_action():
        try:
            revert_time = int(revert_time_entry.get())
            if revert_time <= 0:
                raise ValueError("Revert time must be positive.")
            settings["revert_time"] = revert_time
            save_settings(settings)
            settings_win.destroy()
            show_temporary_message("Settings saved.", "Settings", duration=2000)
        except ValueError as e:
            show_temporary_message(f"Invalid input: {str(e)}", "Error", duration=3000)

    tk.Button(settings_win, text="Save", command=save_settings_action).pack(pady=10)

import time

# Main application window
root = tk.Tk()
root.title("Display Settings")
root.geometry("500x700")
root.minsize(400, 600)

# Create a main frame
main_frame = tk.Frame(root)
main_frame.pack(fill='both', expand=True)

# Status labels frame
status_frame = tk.Frame(main_frame)
status_frame.pack(fill='x')

current_resolution_label = tk.Label(status_frame, text=f"Current Resolution: {original_resolution[0]}x{original_resolution[1]}")
current_resolution_label.pack(pady=5)

monitor_count_label = tk.Label(status_frame, text=f"Connected Monitors: {monitor_count}")
monitor_count_label.pack(pady=5)

# Countdown label
countdown_label = tk.Label(status_frame, text="")
countdown_label.pack(pady=5)

# Control buttons frame
control_frame = tk.Frame(main_frame)
control_frame.pack(fill='x', pady=10)

# Create control buttons
create_control_buttons(control_frame)

# Scrollable frame for resolution buttons
resolution_frame = tk.Frame(main_frame)
resolution_frame.pack(fill='both', expand=True)

canvas = tk.Canvas(resolution_frame)
scrollbar = ttk.Scrollbar(resolution_frame, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
canvas.configure(yscrollcommand=scrollbar.set)

# Limit the height of the canvas
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# The frame where resolution buttons will be added
resolution_buttons_frame = scrollable_frame

# Load resolutions
resolutions = load_resolutions()

# Create resolution buttons
refresh_resolution_buttons()

timer_running = False
timer_thread = None
countdown_thread = None

root.mainloop()
