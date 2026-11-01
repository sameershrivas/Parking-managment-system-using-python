import tkinter as tk
import math
from tkinter import messagebox, ttk, simpledialog
import sqlite3
from datetime import datetime
from reportlab.pdfgen import canvas
import hashlib
import os
import subprocess
import platform

# ---- Cross-Platform Configuration ----
def get_system_font():
    """Get appropriate font for the current platform"""
    system = platform.system()
    if system == "Windows":
        return "Segoe UI"
    elif system == "Darwin":  # macOS
        return "SF Pro Display"
    else:  # Linux and others
        return "DejaVu Sans"

def get_fallback_font():
    """Get fallback font that works on all platforms"""
    return "Arial"

# Set platform-appropriate fonts
SYSTEM_FONT = get_system_font()
FALLBACK_FONT = get_fallback_font()

def safe_font(size=10, weight="normal"):
    """Get a font that works across platforms"""
    try:
        # Try system font first
        return (SYSTEM_FONT, size, weight)
    except:
        # Fall back to Arial if system font fails
        return (FALLBACK_FONT, size, weight)

# ---- Database Setup ----
# Create database directory if it doesn't exist
DB_DIR = "parking_data"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# Create database filename with proper path handling
DB_NAME = "parking_system.db"
DB_PATH = os.path.join(DB_DIR, DB_NAME)

# Ensure proper file permissions on Unix-like systems
if platform.system() != "Windows":
    try:
        os.chmod(DB_DIR, 0o755)
    except:
        pass

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Parking Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS parking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_number TEXT NOT NULL,
        vehicle_type TEXT NOT NULL,
        entry_time TEXT NOT NULL,
        exit_time TEXT,
        fee REAL
    )
''')

# Parking Spaces Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS parking_spaces (
        vehicle_type TEXT PRIMARY KEY,
        total_spaces INTEGER NOT NULL,
        occupied_spaces INTEGER DEFAULT 0
    )
''')

# Insert default parking spaces if table is empty
cursor.execute('SELECT COUNT(*) FROM parking_spaces')
if cursor.fetchone()[0] == 0:
    cursor.execute('INSERT INTO parking_spaces (vehicle_type, total_spaces, occupied_spaces) VALUES (?, ?, ?)', ('Car', 30, 0))
    cursor.execute('INSERT INTO parking_spaces (vehicle_type, total_spaces, occupied_spaces) VALUES (?, ?, ?)', ('Bike', 50, 0))
    cursor.execute('INSERT INTO parking_spaces (vehicle_type, total_spaces, occupied_spaces) VALUES (?, ?, ?)', ('Truck', 10, 0))
    cursor.execute('INSERT INTO parking_spaces (vehicle_type, total_spaces, occupied_spaces) VALUES (?, ?, ?)', ('Bus', 5, 0))

# Add vehicle_type column to existing parking table if it doesn't exist
try:
    cursor.execute('ALTER TABLE parking ADD COLUMN vehicle_type TEXT DEFAULT "Car"')
    # Update existing records to have a default vehicle type
    cursor.execute('UPDATE parking SET vehicle_type = "Car" WHERE vehicle_type IS NULL')
except sqlite3.OperationalError:
    # Column already exists, but let's make sure NULL values are updated
    cursor.execute('UPDATE parking SET vehicle_type = "Car" WHERE vehicle_type IS NULL')
    pass

# Admin Table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS admin (
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        security_question TEXT,
        security_answer TEXT
    )
''')

# Add security columns to existing admin table if they don't exist
try:
    cursor.execute('ALTER TABLE admin ADD COLUMN security_question TEXT')
    cursor.execute('ALTER TABLE admin ADD COLUMN security_answer TEXT')
except sqlite3.OperationalError:
    # Columns already exist
    pass

conn.commit()

# ---- Modern Dialog Functions ----
def show_modern_info(title, message, icon="ℹ️"):
    """Show modern info dialog with futuristic styling"""
    dialog = tk.Toplevel()
    dialog.title(title)
    dialog.geometry("400x200")
    dialog.resizable(False, False)
    dialog.configure(bg="#2c3e50")
    dialog.transient()
    dialog.grab_set()
    
    # Center the dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
    y = (dialog.winfo_screenheight() // 2) - (200 // 2)
    dialog.geometry(f"+{x}+{y}")
    
    # Main frame with gradient effect
    main_frame = tk.Frame(dialog, bg="#34495e", relief="flat", bd=0)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
    
    # Header
    header_frame = tk.Frame(main_frame, bg="#2c3e50", height=50)
    header_frame.pack(fill=tk.X, pady=(0, 10))
    header_frame.pack_propagate(False)
    
    title_label = tk.Label(header_frame, text=f"{icon} {title}", 
                          font=safe_font(14, "bold"), 
                          bg="#2c3e50", fg="#ecf0f1")
    title_label.pack(expand=True)
    
    # Message area
    message_frame = tk.Frame(main_frame, bg="#34495e")
    message_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    message_label = tk.Label(message_frame, text=message, 
                           font=safe_font(11), 
                           bg="#34495e", fg="#ecf0f1",
                           wraplength=350, justify=tk.CENTER)
    message_label.pack(expand=True)
    
    # Button frame
    button_frame = tk.Frame(main_frame, bg="#34495e")
    button_frame.pack(fill=tk.X, pady=(0, 20))
    
    # Create a centered container for button
    button_container = tk.Frame(button_frame, bg="#34495e")
    button_container.pack(expand=True)
    
    ok_button = tk.Button(button_container, text="✓ OK", 
                         font=safe_font(10, "bold"), 
                         bg="#3498db", fg="white",
                         relief="flat", bd=0, padx=30, pady=8,
                         cursor="hand2", command=dialog.destroy)
    ok_button.pack()
    
    # Bind Enter key
    dialog.bind('<Return>', lambda e: dialog.destroy())
    dialog.focus_set()
    
    dialog.wait_window()

def show_modern_warning(title, message, icon="⚠️"):
    """Show modern warning dialog with futuristic styling"""
    dialog = tk.Toplevel()
    dialog.title(title)
    dialog.geometry("400x200")
    dialog.resizable(False, False)
    dialog.configure(bg="#e67e22")
    dialog.transient()
    dialog.grab_set()
    
    # Center the dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
    y = (dialog.winfo_screenheight() // 2) - (200 // 2)
    dialog.geometry(f"+{x}+{y}")
    
    # Main frame
    main_frame = tk.Frame(dialog, bg="#f39c12", relief="flat", bd=0)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
    
    # Header
    header_frame = tk.Frame(main_frame, bg="#e67e22", height=50)
    header_frame.pack(fill=tk.X, pady=(0, 10))
    header_frame.pack_propagate(False)
    
    title_label = tk.Label(header_frame, text=f"{icon} {title}", 
                          font=safe_font(14, "bold"), 
                          bg="#e67e22", fg="white")
    title_label.pack(expand=True)
    
    # Message area
    message_frame = tk.Frame(main_frame, bg="#f39c12")
    message_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    message_label = tk.Label(message_frame, text=message, 
                           font=safe_font(11), 
                           bg="#f39c12", fg="white",
                           wraplength=350, justify=tk.CENTER)
    message_label.pack(expand=True)
    
    # Button frame
    button_frame = tk.Frame(main_frame, bg="#f39c12")
    button_frame.pack(fill=tk.X, pady=(0, 20))
    
    ok_button = tk.Button(button_frame, text="✓ OK", 
                         font=safe_font(10, "bold"), 
                         bg="#d35400", fg="white",
                         relief="flat", bd=0, padx=30, pady=8,
                         cursor="hand2", command=dialog.destroy)
    ok_button.pack()
    
    # Bind Enter key
    dialog.bind('<Return>', lambda e: dialog.destroy())
    dialog.focus_set()
    
    dialog.wait_window()

def show_modern_error(title, message, icon="❌"):
    """Show modern error dialog with futuristic styling"""
    dialog = tk.Toplevel()
    dialog.title(title)
    dialog.geometry("400x200")
    dialog.resizable(False, False)
    dialog.configure(bg="#c0392b")
    dialog.transient()
    dialog.grab_set()
    
    # Center the dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
    y = (dialog.winfo_screenheight() // 2) - (200 // 2)
    dialog.geometry(f"+{x}+{y}")
    
    # Main frame
    main_frame = tk.Frame(dialog, bg="#e74c3c", relief="flat", bd=0)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
    
    # Header
    header_frame = tk.Frame(main_frame, bg="#c0392b", height=50)
    header_frame.pack(fill=tk.X, pady=(0, 10))
    header_frame.pack_propagate(False)
    
    title_label = tk.Label(header_frame, text=f"{icon} {title}", 
                          font=safe_font(14, "bold"), 
                          bg="#c0392b", fg="white")
    title_label.pack(expand=True)
    
    # Message area
    message_frame = tk.Frame(main_frame, bg="#e74c3c")
    message_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    message_label = tk.Label(message_frame, text=message, 
                           font=safe_font(11), 
                           bg="#e74c3c", fg="white",
                           wraplength=350, justify=tk.CENTER)
    message_label.pack(expand=True)
    
    # Button frame
    button_frame = tk.Frame(main_frame, bg="#e74c3c")
    button_frame.pack(fill=tk.X, pady=(0, 20))
    
    ok_button = tk.Button(button_frame, text="✓ OK", 
                         font=safe_font(10, "bold"), 
                         bg="#a93226", fg="white",
                         relief="flat", bd=0, padx=30, pady=8,
                         cursor="hand2", command=dialog.destroy)
    ok_button.pack()
    
    # Bind Enter key
    dialog.bind('<Return>', lambda e: dialog.destroy())
    dialog.focus_set()
    
    dialog.wait_window()

def show_modern_input(title, prompt, show_char=None, icon="💬"):
    """Show modern input dialog with futuristic styling"""
    result = [None]
    
    dialog = tk.Toplevel()
    dialog.title(title)
    dialog.geometry("450x250")
    dialog.resizable(False, False)
    dialog.configure(bg="#2c3e50")
    dialog.transient()
    dialog.grab_set()
    
    # Center the dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
    y = (dialog.winfo_screenheight() // 2) - (250 // 2)
    dialog.geometry(f"+{x}+{y}")
    
    # Main frame
    main_frame = tk.Frame(dialog, bg="#34495e", relief="flat", bd=0)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
    
    # Header
    header_frame = tk.Frame(main_frame, bg="#2c3e50", height=50)
    header_frame.pack(fill=tk.X, pady=(0, 15))
    header_frame.pack_propagate(False)
    
    title_label = tk.Label(header_frame, text=f"{icon} {title}", 
                          font=safe_font(14, "bold"), 
                          bg="#2c3e50", fg="#ecf0f1")
    title_label.pack(expand=True)
    
    # Prompt area
    prompt_frame = tk.Frame(main_frame, bg="#34495e")
    prompt_frame.pack(fill=tk.X, padx=20, pady=10)
    
    prompt_label = tk.Label(prompt_frame, text=prompt, 
                           font=safe_font(11), 
                           bg="#34495e", fg="#ecf0f1",
                           wraplength=400, justify=tk.LEFT)
    prompt_label.pack(anchor=tk.W)
    
    # Entry field
    entry_frame = tk.Frame(main_frame, bg="#34495e")
    entry_frame.pack(fill=tk.X, padx=20, pady=10)
    
    entry_var = tk.StringVar()
    entry = tk.Entry(entry_frame, textvariable=entry_var,
                    font=safe_font(12), 
                    bg="#2c3e50", fg="#ecf0f1",
                    relief="flat", bd=0, 
                    insertbackground="#ecf0f1",
                    show=show_char)
    entry.pack(fill=tk.X, ipady=8)
    entry.focus_set()
    
    # Button frame
    button_frame = tk.Frame(main_frame, bg="#34495e")
    button_frame.pack(fill=tk.X, pady=(10, 20))
    
    def on_ok():
        result[0] = entry_var.get()
        dialog.destroy()
    
    def on_cancel():
        result[0] = None
        dialog.destroy()
    
    # Create a centered container for buttons
    button_container = tk.Frame(button_frame, bg="#34495e")
    button_container.pack(expand=True)
    
    ok_button = tk.Button(button_container, text="✓ OK", 
                         font=safe_font(10, "bold"), 
                         bg="#27ae60", fg="white",
                         relief="flat", bd=0, padx=25, pady=8,
                         cursor="hand2", command=on_ok)
    ok_button.pack(side=tk.LEFT, padx=(0, 10))
    
    cancel_button = tk.Button(button_container, text="✗ Cancel", 
                            font=safe_font(10, "bold"), 
                            bg="#e74c3c", fg="white",
                            relief="flat", bd=0, padx=25, pady=8,
                            cursor="hand2", command=on_cancel)
    cancel_button.pack(side=tk.LEFT)
    
    # Bind Enter key
    dialog.bind('<Return>', lambda e: on_ok())
    dialog.bind('<Escape>', lambda e: on_cancel())
    
    dialog.wait_window()
    return result[0]

def show_vehicle_type_selector(title, prompt):
    """Show a dialog to select vehicle type"""
    vehicle_types = ["Car", "Bike", "Truck", "Bus"]
    result = [None]
    
    dialog = tk.Toplevel()
    dialog.title(title)
    dialog.geometry("500x400")
    dialog.resizable(False, False)
    dialog.configure(bg="#2c3e50")
    dialog.transient()
    dialog.grab_set()
    
    # Center the dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
    y = (dialog.winfo_screenheight() // 2) - (400 // 2)
    dialog.geometry(f"+{x}+{y}")
    
    # Main frame
    main_frame = tk.Frame(dialog, bg="#34495e", relief="flat", bd=0)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
    
    # Header
    header_frame = tk.Frame(main_frame, bg="#2c3e50", height=50)
    header_frame.pack(fill=tk.X, pady=(0, 15))
    header_frame.pack_propagate(False)
    
    title_label = tk.Label(header_frame, text=f"🚗 {title}", 
                          font=safe_font(14, "bold"), 
                          bg="#2c3e50", fg="#ecf0f1")
    title_label.pack(expand=True)
    
    # Prompt
    prompt_frame = tk.Frame(main_frame, bg="#34495e")
    prompt_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
    
    prompt_label = tk.Label(prompt_frame, text=prompt, 
                           font=safe_font(11), 
                           bg="#34495e", fg="#ecf0f1")
    prompt_label.pack(anchor=tk.W)
    
    # Vehicle types with availability
    list_frame = tk.Frame(main_frame, bg="#34495e")
    list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    # Get parking spaces info
    spaces_info = get_parking_spaces()
    spaces_dict = {vtype: (total, occupied) for vtype, total, occupied in spaces_info}
    
    # Create custom listbox-like interface
    selected_type = tk.StringVar()
    
    for i, vtype in enumerate(vehicle_types):
        total, occupied = spaces_dict.get(vtype, (0, 0))
        available = total - occupied
        
        # Frame for each vehicle type
        type_frame = tk.Frame(list_frame, bg="#2c3e50", relief="solid", bd=1)
        type_frame.pack(fill=tk.X, pady=2)
        
        # Radio button
        radio = tk.Radiobutton(type_frame, text="", variable=selected_type, value=vtype,
                              bg="#2c3e50", fg="#ecf0f1", selectcolor="#3498db",
                              activebackground="#34495e", activeforeground="#ecf0f1")
        radio.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Vehicle type info
        info_frame = tk.Frame(type_frame, bg="#2c3e50")
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)
        
        # Vehicle type name
        name_label = tk.Label(info_frame, text=vtype, 
                            font=safe_font(12, "bold"), 
                            bg="#2c3e50", fg="#ecf0f1")
        name_label.pack(anchor=tk.W)
        
        # Space availability
        status_color = "#27ae60" if available > 0 else "#e74c3c"
        status_text = f"Available: {available}/{total}"
        
        status_label = tk.Label(info_frame, text=status_text, 
                              font=safe_font(10), 
                              bg="#2c3e50", fg=status_color)
        status_label.pack(anchor=tk.W)
        
        # Disable if no space available
        if available <= 0:
            radio.config(state=tk.DISABLED)
            type_frame.config(bg="#7f8c8d")
            info_frame.config(bg="#7f8c8d")
            name_label.config(bg="#7f8c8d", fg="#bdc3c7")
            status_label.config(bg="#7f8c8d", fg="#e74c3c")
    
    # Button frame
    button_frame = tk.Frame(main_frame, bg="#34495e")
    button_frame.pack(fill=tk.X, pady=(10, 20))
    
    def on_select():
        if selected_type.get():
            result[0] = selected_type.get()
            dialog.destroy()
        else:
            show_modern_warning("No Selection", "Please select a vehicle type.", "⚠️")
    
    def on_cancel():
        result[0] = None
        dialog.destroy()
    
    # Create a centered container for buttons
    button_container = tk.Frame(button_frame, bg="#34495e")
    button_container.pack(expand=True)
    
    select_button = tk.Button(button_container, text="✓ Select", 
                             font=safe_font(10, "bold"), 
                             bg="#27ae60", fg="white",
                             relief="flat", bd=0, padx=25, pady=8,
                             cursor="hand2", command=on_select)
    select_button.pack(side=tk.LEFT, padx=(0, 10))
    
    cancel_button = tk.Button(button_container, text="✗ Cancel", 
                            font=safe_font(10, "bold"), 
                            bg="#e74c3c", fg="white",
                            relief="flat", bd=0, padx=25, pady=8,
                            cursor="hand2", command=on_cancel)
    cancel_button.pack(side=tk.LEFT)
    
    # Bind Enter key
    dialog.bind('<Return>', lambda e: on_select())
    dialog.bind('<Escape>', lambda e: on_cancel())
    
    dialog.focus_set()
    dialog.wait_window()
    return result[0]

def show_question_selector(title, prompt, questions):
    """Show a dialog to select from predefined security questions"""
    result = [None]
    
    dialog = tk.Toplevel()
    dialog.title(title)
    dialog.geometry("500x400")
    dialog.resizable(False, False)
    dialog.configure(bg="#2c3e50")
    dialog.transient()
    dialog.grab_set()
    
    # Center the dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
    y = (dialog.winfo_screenheight() // 2) - (400 // 2)
    dialog.geometry(f"+{x}+{y}")
    
    # Main frame
    main_frame = tk.Frame(dialog, bg="#34495e", relief="flat", bd=0)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
    
    # Header
    header_frame = tk.Frame(main_frame, bg="#2c3e50", height=50)
    header_frame.pack(fill=tk.X, pady=(0, 15))
    header_frame.pack_propagate(False)
    
    title_label = tk.Label(header_frame, text=f"❓ {title}", 
                          font=safe_font(14, "bold"), 
                          bg="#2c3e50", fg="#ecf0f1")
    title_label.pack(expand=True)
    
    # Prompt
    prompt_frame = tk.Frame(main_frame, bg="#34495e")
    prompt_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
    
    prompt_label = tk.Label(prompt_frame, text=prompt, 
                           font=safe_font(11), 
                           bg="#34495e", fg="#ecf0f1")
    prompt_label.pack(anchor=tk.W)
    
    # Questions list
    list_frame = tk.Frame(main_frame, bg="#34495e")
    list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    # Create listbox with scrollbar
    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                        font=safe_font(10), 
                        bg="#2c3e50", fg="#ecf0f1",
                        selectbackground="#3498db",
                        relief="flat", bd=0,
                        height=8)
    
    for question in questions:
        listbox.insert(tk.END, question)
    
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=listbox.yview)
    
    # Button frame
    button_frame = tk.Frame(main_frame, bg="#34495e")
    button_frame.pack(fill=tk.X, pady=(10, 20))
    
    def on_select():
        selection = listbox.curselection()
        if selection:
            result[0] = questions[selection[0]]
            dialog.destroy()
        else:
            show_modern_warning("No Selection", "Please select a security question.", "⚠️")
    
    def on_cancel():
        result[0] = None
        dialog.destroy()
    
    # Create a centered container for buttons
    button_container = tk.Frame(button_frame, bg="#34495e")
    button_container.pack(expand=True)
    
    select_button = tk.Button(button_container, text="✓ Select", 
                             font=safe_font(10, "bold"), 
                             bg="#27ae60", fg="white",
                             relief="flat", bd=0, padx=25, pady=8,
                             cursor="hand2", command=on_select)
    select_button.pack(side=tk.LEFT, padx=(0, 10))
    
    cancel_button = tk.Button(button_container, text="✗ Cancel", 
                            font=safe_font(10, "bold"), 
                            bg="#e74c3c", fg="white",
                            relief="flat", bd=0, padx=25, pady=8,
                            cursor="hand2", command=on_cancel)
    cancel_button.pack(side=tk.LEFT)
    
    # Double-click to select
    listbox.bind('<Double-1>', lambda e: on_select())
    
    # Bind Enter key
    dialog.bind('<Return>', lambda e: on_select())
    dialog.bind('<Escape>', lambda e: on_cancel())
    
    listbox.focus_set()
    dialog.wait_window()
    return result[0]

# ---- Helpers ----
def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def update_parking_spaces(vehicle_type, action):
    """Update parking spaces count (action: 'enter' or 'exit')"""
    if action == 'enter':
        cursor.execute('UPDATE parking_spaces SET occupied_spaces = occupied_spaces + 1 WHERE vehicle_type = ?', (vehicle_type,))
    elif action == 'exit':
        cursor.execute('UPDATE parking_spaces SET occupied_spaces = occupied_spaces - 1 WHERE vehicle_type = ?', (vehicle_type,))
    conn.commit()

def get_parking_spaces():
    """Get all parking spaces information"""
    cursor.execute('SELECT vehicle_type, total_spaces, occupied_spaces FROM parking_spaces')
    return cursor.fetchall()

def check_space_availability(vehicle_type):
    """Check if space is available for the vehicle type"""
    cursor.execute('SELECT total_spaces, occupied_spaces FROM parking_spaces WHERE vehicle_type = ?', (vehicle_type,))
    result = cursor.fetchone()
    if result:
        total, occupied = result
        return occupied < total
    return False

def sync_parking_spaces():
    """Sync parking spaces with actual database records"""
    try:
        # First, ensure all existing parking records have proper vehicle_type
        cursor.execute('UPDATE parking SET vehicle_type = "Car" WHERE vehicle_type IS NULL OR vehicle_type = ""')
        
        # Get actual counts of currently parked vehicles by type
        cursor.execute('''
            SELECT vehicle_type, COUNT(*) 
            FROM parking 
            WHERE exit_time IS NULL 
            GROUP BY vehicle_type
        ''')
        actual_counts = dict(cursor.fetchall())
        
        # Get all vehicle types from parking_spaces table
        cursor.execute('SELECT vehicle_type FROM parking_spaces')
        vehicle_types = [row[0] for row in cursor.fetchall()]
        
        # Update occupied_spaces for each vehicle type
        for vehicle_type in vehicle_types:
            actual_count = actual_counts.get(vehicle_type, 0)
            cursor.execute('''
                UPDATE parking_spaces 
                SET occupied_spaces = ? 
                WHERE vehicle_type = ?
            ''', (actual_count, vehicle_type))
        
        conn.commit()
        
    except Exception as e:
        print(f"ERROR: Failed to sync parking spaces: {e}")
        conn.rollback()

def refresh_all_data():
    """Comprehensive refresh function that updates all data and UI elements"""
    try:
        # Sync parking spaces with actual database records
        sync_parking_spaces()
        
        # Refresh the records table
        refresh_treeview()
        
        # Update parking status display
        update_parking_status()
        
        # Clear search if any (will be handled in the main window)
        # search_entry.delete(0, tk.END)  # This will be done where search_entry is accessible
        
        print("All data refreshed successfully")
        
    except Exception as e:
        show_modern_error("Refresh Error", f"Error refreshing data: {str(e)}", "❌")
        print(f"ERROR: Refresh failed - {e}")

def validate_vehicle_number(char):
    """Validate and format vehicle number input - only allow alphanumeric characters"""
    return char.isalnum() or char == ""

def format_vehicle_number(event):
    """Format vehicle number input in real-time"""
    current_text = event.widget.get()
    # Remove spaces and convert to uppercase
    formatted_text = current_text.replace(" ", "").upper()
    if formatted_text != current_text:
        event.widget.delete(0, tk.END)
        event.widget.insert(0, formatted_text)

def open_file_cross_platform(file_path):
    """Open a file using the default application across platforms"""
    try:
        system = platform.system()
        if system == "Linux":
            # Try multiple options for Linux
            try:
                subprocess.run(["xdg-open", file_path], check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                try:
                    subprocess.run(["gnome-open", file_path], check=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    subprocess.run(["kde-open", file_path], check=True)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", file_path], check=True)
        elif system == "Windows":
            os.startfile(file_path)  # More reliable than subprocess on Windows
        else:
            # Fallback for other systems
            subprocess.run(["xdg-open", file_path], check=True)
        return True
    except Exception as e:
        print(f"Error opening file: {e}")
        return False

def generate_ticket_pdf(filename, vehicle_number, entry_time, exit_time=None, fee=None, vehicle_type="Car"):
    # Create tickets directory if it doesn't exist
    TICKETS_DIR = "parking_tickets"
    if not os.path.exists(TICKETS_DIR):
        os.makedirs(TICKETS_DIR)
    
    # Save ticket in tickets directory
    ticket_path = os.path.join(TICKETS_DIR, filename)
    
    c = canvas.Canvas(ticket_path)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 800, "Parking Ticket")
    c.setFont("Helvetica", 12)
    c.drawString(50, 750, f"Vehicle Number: {vehicle_number}")
    c.drawString(50, 730, f"Vehicle Type: {vehicle_type}")
    c.drawString(50, 710, f"Entry Time: {entry_time}")
    if exit_time:
        c.drawString(50, 690, f"Exit Time: {exit_time}")
        c.drawString(50, 670, f"Total Fee: ₹{fee}")
    c.drawString(50, 630, "Thank you for using our service!")
    c.save()
    
    return ticket_path

# ---- Admin Functions ----
def admin_update_spaces():
    """Open admin interface to update parking spaces"""
    admin_window = tk.Toplevel()
    admin_window.title("Admin - Update Parking Spaces")
    admin_window.geometry("600x500")
    admin_window.resizable(False, False)
    admin_window.configure(bg="#2c3e50")
    admin_window.transient()
    admin_window.grab_set()
    
    # Center the window
    admin_window.update_idletasks()
    x = (admin_window.winfo_screenwidth() // 2) - (600 // 2)
    y = (admin_window.winfo_screenheight() // 2) - (500 // 2)
    admin_window.geometry(f"600x500+{x}+{y}")
    
    # Main frame
    main_frame = tk.Frame(admin_window, bg="#34495e", relief="flat", bd=0)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
    
    # Header
    header_frame = tk.Frame(main_frame, bg="#2c3e50", height=60)
    header_frame.pack(fill=tk.X, pady=(0, 20))
    header_frame.pack_propagate(False)
    
    title_label = tk.Label(header_frame, text="⚙️ Admin - Update Parking Spaces", 
                          font=safe_font(16, "bold"), bg="#2c3e50", fg="#ecf0f1")
    title_label.pack(expand=True)
    
    # Get current parking spaces
    spaces_info = get_parking_spaces()
    
    # Create input fields for each vehicle type
    entries = {}
    for vehicle_type, total_spaces, occupied_spaces in spaces_info:
        # Frame for each vehicle type
        type_frame = tk.Frame(main_frame, bg="#2c3e50", relief="flat", bd=1)
        type_frame.pack(fill=tk.X, padx=20, pady=8)
        
        # Inner frame for content
        inner_frame = tk.Frame(type_frame, bg="#34495e")
        inner_frame.pack(fill=tk.X, padx=2, pady=2)
        
        # Vehicle type label
        type_label = tk.Label(inner_frame, text=f"{vehicle_type}:", 
                             font=safe_font(12, "bold"), bg="#34495e", fg="#ecf0f1")
        type_label.pack(side=tk.LEFT, padx=(10, 0), pady=10)
        
        # Current spaces info
        status_color = "#27ae60" if (total_spaces - occupied_spaces) > 0 else "#e74c3c"
        info_text = f"Currently: {total_spaces} total, {occupied_spaces} occupied"
        info_label = tk.Label(inner_frame, text=info_text, 
                             font=safe_font(9), bg="#34495e", fg="#bdc3c7")
        info_label.pack(side=tk.LEFT, padx=(20, 0), pady=10)
        
        # Entry field
        entry_var = tk.StringVar(value=str(total_spaces))
        entry = tk.Entry(inner_frame, textvariable=entry_var, font=safe_font(11), 
                        relief="flat", bd=0, bg="#ecf0f1", fg="#2c3e50",
                        width=6, justify=tk.CENTER)
        entry.pack(side=tk.RIGHT, padx=(0, 10), pady=10)
        
        entries[vehicle_type] = entry_var
    
    # Button frame
    button_frame = tk.Frame(main_frame, bg="#34495e")
    button_frame.pack(fill=tk.X, pady=20)
    
    def save_changes():
        try:
            for vehicle_type, entry_var in entries.items():
                new_total = int(entry_var.get())
                if new_total < 0:
                    show_modern_warning("Invalid Input", f"Total spaces for {vehicle_type} cannot be negative.", "⚠️")
                    return
                
                # Get current occupied spaces
                cursor.execute('SELECT occupied_spaces FROM parking_spaces WHERE vehicle_type = ?', (vehicle_type,))
                result = cursor.fetchone()
                occupied_spaces = result[0] if result else 0
                
                if new_total < occupied_spaces:
                    show_modern_warning("Invalid Input", 
                                      f"Total spaces for {vehicle_type} ({new_total}) cannot be less than currently occupied spaces ({occupied_spaces}).", "⚠️")
                    return
                
                # Update the database
                cursor.execute('UPDATE parking_spaces SET total_spaces = ? WHERE vehicle_type = ?', 
                             (new_total, vehicle_type))
            
            conn.commit()
            show_modern_info("Success", "Parking spaces updated successfully!", "✅")
            admin_window.destroy()
            
            # Auto-refresh everything after admin update
            sync_parking_spaces()
            update_parking_status()
            refresh_treeview()
            
        except ValueError:
            show_modern_warning("Invalid Input", "Please enter valid numbers for all vehicle types.", "⚠️")
        except Exception as e:
            show_modern_warning("Error", f"Failed to update parking spaces: {str(e)}", "❌")
    
    # Create a centered container for buttons
    button_container = tk.Frame(button_frame, bg="#34495e")
    button_container.pack(expand=True)
    
    # Save button
    save_button = tk.Button(button_container, text="💾 Save Changes", 
                           font=safe_font(11, "bold"), bg="#27ae60", fg="white",
                           relief="flat", bd=0, padx=25, pady=10, cursor="hand2",
                           command=save_changes)
    save_button.pack(side=tk.LEFT, padx=(0, 15))
    
    # Cancel button
    cancel_button = tk.Button(button_container, text="✗ Cancel", 
                             font=safe_font(11, "bold"), bg="#e74c3c", fg="white",
                             relief="flat", bd=0, padx=25, pady=10, cursor="hand2",
                             command=admin_window.destroy)
    cancel_button.pack(side=tk.LEFT)
    
    # Bind keys
    admin_window.bind('<Escape>', lambda e: admin_window.destroy())
    admin_window.focus_set()

# ---- Functions ----
def vehicle_entry():
    global vehicle_type_var, vehicle_type_dropdown
    
    # Get vehicle number and remove ALL spaces, then convert to uppercase
    number = vehicle_number_entry.get().replace(" ", "").strip().upper()
    if not number:
        show_modern_warning("Input Error", "Please enter a vehicle number.", "⚠️")
        return
    
    # Check if vehicle is already parked
    cursor.execute('SELECT * FROM parking WHERE vehicle_number=? AND exit_time IS NULL', (number,))
    if cursor.fetchone():
        show_modern_warning("Already Parked", f"Vehicle {number} is already in the parking lot!", "🚫")
        vehicle_number_entry.delete(0, tk.END)
        return
    
    # Get vehicle type directly from dropdown widget - more reliable
    vehicle_type = vehicle_type_dropdown.get()  # Get directly from widget
    
    if not vehicle_type or vehicle_type.strip() == "":
        show_modern_warning("Input Error", "Please select a vehicle type.", "⚠️")
        return
    
    # Check space availability BEFORE allowing entry
    if not check_space_availability(vehicle_type):
        # Get current status for better error message
        cursor.execute('SELECT total_spaces, occupied_spaces FROM parking_spaces WHERE vehicle_type = ?', (vehicle_type,))
        result = cursor.fetchone()
        if result:
            total, occupied = result
            show_modern_warning("No Space Available", 
                               f"No parking space available for {vehicle_type}!\n\nCurrent Status:\nTotal: {total}\nOccupied: {occupied}\nAvailable: {total - occupied}\n\nPlease try another vehicle type.", "🚫")
        else:
            show_modern_warning("No Space Available", f"No parking space available for {vehicle_type}!\nPlease try another vehicle type.", "🚫")
        # Clear form and refresh displays when parking is full
        vehicle_number_entry.delete(0, tk.END)
        refresh_treeview()
        update_parking_status()
        return
    
    # Get current time with proper formatting
    now = datetime.now()
    entry_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    
    # Insert into database ONLY if space is available
    cursor.execute('INSERT INTO parking (vehicle_number, vehicle_type, entry_time) VALUES (?, ?, ?)', 
                   (number, vehicle_type, entry_time_str))
    conn.commit()
    
    # Update parking spaces
    update_parking_spaces(vehicle_type, 'enter')
    
    # Show success message
    show_modern_info("Success", f"{vehicle_type} {number} entered at {entry_time_str}", "✅")

    # Generate Entry Ticket ONLY after successful database entry
    filename = f"Parking_Ticket_{number}_ENTRY.pdf"
    ticket_path = generate_ticket_pdf(filename, number, entry_time_str, vehicle_type=vehicle_type)
    show_modern_info("Ticket Generated", f"Entry ticket saved as {ticket_path}", "🎫")

    # Clear form and refresh displays
    vehicle_number_entry.delete(0, tk.END)
    # DON'T reset dropdown - let user keep their selection
    
    # Auto-refresh everything after successful entry
    refresh_treeview()
    update_parking_status()  # Real-time update

def vehicle_exit():
    selected = tree.selection()
    if not selected:
        show_modern_warning("Selection Error", "Please select a vehicle to check out.", "⚠️")
        return
    
    item = tree.item(selected)
    record_id = item['values'][0]
    number = item['values'][1]
    vehicle_type = item['values'][2]
    entry_time_str = item['values'][3]
    
    try:
        entry_time = datetime.strptime(entry_time_str, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        exit_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
        hours_parked = (now - entry_time).total_seconds() / 3600
        
        # Fee calculation based on vehicle type
             # Real-life parking fee calculation
        total_minutes = max(1, math.ceil(
            (now - entry_time).total_seconds() / 60
        ))

        if vehicle_type == "Bike":
            if total_minutes <= 30:
                fee = 10
            elif total_minutes <= 120:
                fee = 15
            else:
                fee = 15 + math.ceil((total_minutes - 120) / 60) * 10

        elif vehicle_type == "Car":
            if total_minutes <= 30:
                fee = 20
            elif total_minutes <= 120:
                fee = 35
            else:
                fee = 35 + math.ceil((total_minutes - 120) / 60) * 20

        elif vehicle_type in ["Bus", "Truck"]:
            if total_minutes <= 120:
                fee = 80
            elif total_minutes <= 300:
                fee = 120
            elif total_minutes <= 600:
                fee = 300
            else:
                fee = 300 + math.ceil((total_minutes - 600) / 1440) * 500

        else:
            fee = 20

        # Update database
        cursor.execute(
            'UPDATE parking SET exit_time=?, fee=? WHERE id=?',
            (exit_time_str, fee, record_id)
        )
        conn.commit()

        # Update parking spaces
        update_parking_spaces(vehicle_type, 'exit')

        # Show success message
        show_modern_info(
            "Success",
            f"{vehicle_type} {number} checked out. Fee: ₹{fee}",
            "💰"
        )

        # Generate Exit Ticket
        filename = f"Parking_Ticket_{number}_EXIT.pdf"
        ticket_path = generate_ticket_pdf(
            filename, number, entry_time_str,
            exit_time_str, fee, vehicle_type
        )
        show_modern_info(
            "Ticket Generated",
            f"Exit ticket saved as {ticket_path}",
            "🎫"
        )

        # Auto-refresh everything
        refresh_treeview()
        update_parking_status()
        
    except Exception as e:
        show_modern_error("Error", f"Failed to process vehicle exit: {str(e)}", "❌")

def refresh_treeview():
    for row in tree.get_children():
        tree.delete(row)
    
    # Get search criteria and remove spaces for flexible searching
    search_text = search_entry.get().replace(" ", "").strip().upper()
    
    # Build query with explicit column order to match treeview
    query = '''SELECT id, vehicle_number, vehicle_type, entry_time, exit_time, fee 
               FROM parking WHERE 1=1'''
    params = []
    
    if search_text:
        query += ' AND UPPER(REPLACE(vehicle_number, " ", "")) LIKE ?'
        params.append(f'%{search_text}%')
    
    query += ' ORDER BY entry_time DESC'
    
    cursor.execute(query, params)
    for row in cursor.fetchall():
        # Ensure vehicle_type is not None
        row_list = list(row)
        if row_list[2] is None:  # vehicle_type column
            row_list[2] = "Car"  # Default value
        tree.insert('', tk.END, values=row_list)

def search_vehicle():
    """Search for a specific vehicle - auto-refresh results"""
    refresh_treeview()

def clear_filters():
    """Clear search field and refresh results"""
    search_entry.delete(0, tk.END)
    refresh_treeview()

def print_receipt():
    """Show print interface for selected vehicle"""
    selected = tree.selection()
    if not selected:
        show_modern_warning("Selection Error", "Please select a vehicle to print receipt.", "⚠️")
        return
    
    item = tree.item(selected)
    record_id = item['values'][0]
    number = item['values'][1]
    vehicle_type = item['values'][2]
    entry_time = item['values'][3]
    exit_time = item['values'][4] if item['values'][4] else None
    fee = item['values'][5] if item['values'][5] else None
    
    show_print_interface(number, entry_time, exit_time, fee, vehicle_type)

def update_parking_status():
    """Update parking status display in real-time"""
    # Sync parking spaces with actual database first
    sync_parking_spaces()
    
    # Update the status labels if they exist
    try:
        if 'status_labels' in globals() and status_labels:
            # Get updated parking spaces info
            spaces_info = get_parking_spaces()
            
            for vehicle_type, total_spaces, occupied_spaces in spaces_info:
                if vehicle_type in status_labels:
                    available_spaces = total_spaces - occupied_spaces
                    
                    # Update status label
                    status_color = "#27ae60" if available_spaces > 0 else "#e74c3c"
                    status_text = f"{occupied_spaces}/{total_spaces} occupied"
                    status_labels[vehicle_type]['status_label'].config(text=status_text, fg=status_color)
                    
                    # Update available label
                    status_labels[vehicle_type]['available_label'].config(text=f"Available: {available_spaces}")
                    
                    # Force widget update
                    status_labels[vehicle_type]['status_label'].update()
                    status_labels[vehicle_type]['available_label'].update()
    except Exception as e:
        print(f"Error updating parking status: {e}")
        # Force refresh the treeview as fallback
        try:
            refresh_treeview()
        except:
            pass

def show_print_interface(vehicle_number, entry_time, exit_time=None, fee=None, vehicle_type="Car"):
    """Show print preview and print interface"""
    dialog = tk.Toplevel()
    dialog.title("Print Receipt")
    dialog.geometry("600x700")
    dialog.resizable(False, False)
    dialog.configure(bg="#2c3e50")
    dialog.transient()
    dialog.grab_set()
    
    # Center the dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
    y = (dialog.winfo_screenheight() // 2) - (700 // 2)
    dialog.geometry(f"+{x}+{y}")
    
    # Main frame
    main_frame = tk.Frame(dialog, bg="#34495e", relief="flat", bd=0)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
    
    # Header
    header_frame = tk.Frame(main_frame, bg="#2c3e50", height=50)
    header_frame.pack(fill=tk.X, pady=(0, 10))
    header_frame.pack_propagate(False)
    
    title_label = tk.Label(header_frame, text="🖨️ Print Receipt", 
                          font=safe_font(16, "bold"), 
                          bg="#2c3e50", fg="#ecf0f1")
    title_label.pack(expand=True)
    
    # Receipt Preview Frame
    preview_frame = tk.Frame(main_frame, bg="white", relief="solid", bd=2)
    preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    # Receipt Content
    receipt_content = tk.Frame(preview_frame, bg="white")
    receipt_content.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
    
    # Receipt Header
    header_label = tk.Label(receipt_content, text="🚗 PARKING RECEIPT", 
                           font=safe_font(20, "bold"), 
                           bg="white", fg="#2c3e50")
    header_label.pack(pady=(0, 20))
    
    # Divider
    divider = tk.Frame(receipt_content, bg="#34495e", height=2)
    divider.pack(fill=tk.X, pady=(0, 20))
    
    # Receipt Details
    details_frame = tk.Frame(receipt_content, bg="white")
    details_frame.pack(fill=tk.X, pady=10)
    
    # Vehicle Number
    vehicle_frame = tk.Frame(details_frame, bg="white")
    vehicle_frame.pack(fill=tk.X, pady=8)
    
    tk.Label(vehicle_frame, text="Vehicle Number:", 
            font=safe_font(12, "bold"), 
            bg="white", fg="#2c3e50").pack(side=tk.LEFT)
    
    tk.Label(vehicle_frame, text=vehicle_number, 
            font=safe_font(14, "bold"), 
            bg="white", fg="#e74c3c").pack(side=tk.RIGHT)
    
    # Vehicle Type
    type_frame = tk.Frame(details_frame, bg="white")
    type_frame.pack(fill=tk.X, pady=8)
    
    tk.Label(type_frame, text="Vehicle Type:", 
            font=safe_font(12, "bold"), 
            bg="white", fg="#2c3e50").pack(side=tk.LEFT)
    
    tk.Label(type_frame, text=vehicle_type, 
            font=safe_font(12, "bold"), 
            bg="white", fg="#3498db").pack(side=tk.RIGHT)
    
    # Entry Time
    entry_frame = tk.Frame(details_frame, bg="white")
    entry_frame.pack(fill=tk.X, pady=8)
    
    tk.Label(entry_frame, text="Entry Time:", 
            font=safe_font(12), 
            bg="white", fg="#2c3e50").pack(side=tk.LEFT)
    
    tk.Label(entry_frame, text=entry_time, 
            font=safe_font(12), 
            bg="white", fg="#34495e").pack(side=tk.RIGHT)
    
    # Exit Time (if exists)
    if exit_time:
        exit_frame = tk.Frame(details_frame, bg="white")
        exit_frame.pack(fill=tk.X, pady=8)
        
        tk.Label(exit_frame, text="Exit Time:", 
                font=safe_font(12), 
                bg="white", fg="#2c3e50").pack(side=tk.LEFT)
        
        tk.Label(exit_frame, text=exit_time, 
                font=safe_font(12), 
                bg="white", fg="#34495e").pack(side=tk.RIGHT)
        
        # Duration calculation
        from datetime import datetime
        entry_dt = datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S")
        exit_dt = datetime.strptime(exit_time, "%Y-%m-%d %H:%M:%S")
        duration = exit_dt - entry_dt
        hours = duration.total_seconds() / 3600
        
        duration_frame = tk.Frame(details_frame, bg="white")
        duration_frame.pack(fill=tk.X, pady=8)
        
        tk.Label(duration_frame, text="Duration:", 
                font=safe_font(12), 
                bg="white", fg="#2c3e50").pack(side=tk.LEFT)
        
        tk.Label(duration_frame, text=f"{hours:.2f} hours", 
                font=safe_font(12), 
                bg="white", fg="#34495e").pack(side=tk.RIGHT)
    
    # Fee (if exists)
    if fee:
        fee_divider = tk.Frame(details_frame, bg="#34495e", height=1)
        fee_divider.pack(fill=tk.X, pady=15)
        
        fee_frame = tk.Frame(details_frame, bg="white")
        fee_frame.pack(fill=tk.X, pady=8)
        
        tk.Label(fee_frame, text="Total Fee:", 
                font=safe_font(14, "bold"), 
                bg="white", fg="#2c3e50").pack(side=tk.LEFT)
        
        tk.Label(fee_frame, text=f"₹{fee}", 
                font=safe_font(18, "bold"), 
                bg="white", fg="#27ae60").pack(side=tk.RIGHT)
    
    # Status
    status_frame = tk.Frame(details_frame, bg="white")
    status_frame.pack(fill=tk.X, pady=20)
    
    status_text = "PARKED" if not exit_time else "COMPLETED"
    status_color = "#f39c12" if not exit_time else "#27ae60"
    
    tk.Label(status_frame, text=f"Status: {status_text}", 
            font=safe_font(12, "bold"), 
            bg="white", fg=status_color).pack()
    
    # Footer
    footer_frame = tk.Frame(receipt_content, bg="white")
    footer_frame.pack(fill=tk.X, pady=20)
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tk.Label(footer_frame, text=f"Generated on: {current_time}", 
            font=safe_font(9), 
            bg="white", fg="#7f8c8d").pack()
    
    tk.Label(footer_frame, text="Thank you for using our parking service!", 
            font=safe_font(11, "italic"), 
            bg="white", fg="#34495e").pack(pady=(10, 0))
    
    # Button frame
    button_frame = tk.Frame(main_frame, bg="#34495e")
    button_frame.pack(fill=tk.X, pady=20)
    
    def on_print():
        """Handle print action"""
        # Generate PDF for printing
        status = "RECEIPT"
        if exit_time:
            status = "FINAL_RECEIPT"
        
        filename = f"Parking_Receipt_{vehicle_number}_{status}.pdf"
        ticket_path = generate_ticket_pdf(filename, vehicle_number, entry_time, exit_time, fee, vehicle_type)
        
        # Try to open with default PDF viewer for printing
        try:
            if open_file_cross_platform(ticket_path):
                show_modern_info("Print Ready", f"Receipt opened in PDF viewer!\n\nFile: {ticket_path}\n\nUse Ctrl+P to print from the PDF viewer.", "🖨️")
            else:
                show_modern_info("Receipt Saved", f"Receipt saved as:\n{ticket_path}\n\nOpen this file and print using your PDF viewer.", "�")
        except Exception as e:
            show_modern_info("Receipt Saved", f"Receipt saved as:\n{ticket_path}\n\nOpen this file and print using your PDF viewer.", "📄")
        
        dialog.destroy()
    
    def on_save_only():
        """Save receipt without printing"""
        status = "RECEIPT"
        if exit_time:
            status = "FINAL_RECEIPT"
        
        filename = f"Parking_Receipt_{vehicle_number}_{status}.pdf"
        ticket_path = generate_ticket_pdf(filename, vehicle_number, entry_time, exit_time, fee, vehicle_type)
        
        show_modern_info("Receipt Saved", f"Receipt saved as:\n{ticket_path}", "💾")
        dialog.destroy()
    
    def on_close():
        dialog.destroy()
    
    # Create a centered container for buttons
    button_container = tk.Frame(button_frame, bg="#34495e")
    button_container.pack(expand=True)
    
    print_button = tk.Button(button_container, text="🖨️ Print Receipt", 
                           font=safe_font(12, "bold"), 
                           bg="#27ae60", fg="white",
                           relief="flat", bd=0, padx=30, pady=12,
                           cursor="hand2", command=on_print)
    print_button.pack(side=tk.LEFT, padx=(0, 15))
    
    save_button = tk.Button(button_container, text="💾 Save Only", 
                          font=safe_font(12, "bold"), 
                          bg="#3498db", fg="white",
                          relief="flat", bd=0, padx=30, pady=12,
                          cursor="hand2", command=on_save_only)
    save_button.pack(side=tk.LEFT, padx=(0, 15))
    
    close_button = tk.Button(button_container, text="✗ Close", 
                           font=safe_font(12, "bold"), 
                           bg="#95a5a6", fg="white",
                           relief="flat", bd=0, padx=30, pady=12,
                           cursor="hand2", command=on_close)
    close_button.pack(side=tk.LEFT)
    
    # Bind keys
    dialog.bind('<Return>', lambda e: on_print())
    dialog.bind('<Escape>', lambda e: on_close())
    
    dialog.focus_set()
    dialog.wait_window()

def change_password():
    old_password = show_modern_input("Change Password", "Enter current password:", show_char="*", icon="🔒")
    if not old_password:
        return
    
    cursor.execute('SELECT password FROM admin')
    stored_password = cursor.fetchone()[0]
    if hash_password(old_password) != stored_password:
        show_modern_error("Error", "Current password incorrect!", "❌")
        return
    
    new_password = show_modern_input("Change Password", "Enter new password:", show_char="*", icon="🔑")
    if not new_password:
        return
    
    confirm_password = show_modern_input("Change Password", "Confirm new password:", show_char="*", icon="🔑")
    if not confirm_password:
        return
    
    if new_password != confirm_password:
        show_modern_error("Error", "Passwords do not match!", "❌")
        return
    
    cursor.execute('UPDATE admin SET password=?', (hash_password(new_password),))
    conn.commit()
    show_modern_info("Success", "Password changed successfully!", "✅")

def forgot_password():
    """Handle password recovery using security question"""
    username = show_modern_input("Password Recovery", "Enter your username:", icon="🔑")
    if not username:
        return
    
    # Check if user exists and has security question
    cursor.execute('SELECT security_question, security_answer FROM admin WHERE username=?', (username,))
    result = cursor.fetchone()
    
    if not result:
        show_modern_error("User Not Found", "Username not found in the system!", "❌")
        return
    
    security_question, correct_answer = result
    
    if not security_question:
        show_modern_error("Recovery Not Available", 
                         "No security question set for this account.\nPlease contact administrator.", "🔒")
        return
    
    # Ask security question
    user_answer = show_modern_input("Security Question", 
                                  f"Answer this security question:\n\n{security_question}", 
                                  icon="❓")
    if not user_answer:
        return
    
    # Check answer (case-insensitive)
    if user_answer.lower().strip() != correct_answer.lower().strip():
        show_modern_error("Incorrect Answer", "Security answer is incorrect!", "❌")
        return
    
    # Allow password reset
    new_password = show_modern_input("Reset Password", "Enter new password:", show_char="*", icon="🔑")
    if not new_password:
        return
    
    confirm_password = show_modern_input("Reset Password", "Confirm new password:", show_char="*", icon="🔑")
    if not confirm_password:
        return
    
    if new_password != confirm_password:
        show_modern_error("Error", "Passwords do not match!", "❌")
        return
    
    # Update password
    cursor.execute('UPDATE admin SET password=? WHERE username=?', (hash_password(new_password), username))
    conn.commit()
    
    show_modern_info("Success", "Password reset successfully!\nYou can now login with your new password.", "✅")

def show_login_failed_dialog():
    """Show login failed dialog with option to recover password"""
    result = [None]
    
    dialog = tk.Toplevel()
    dialog.title("Login Failed")
    dialog.geometry("450x350")
    dialog.resizable(False, False)
    dialog.configure(bg="#c0392b")
    dialog.transient()
    dialog.grab_set()
    
    # Center the dialog
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
    y = (dialog.winfo_screenheight() // 2) - (350 // 2)
    dialog.geometry(f"+{x}+{y}")
    
    # Main frame
    main_frame = tk.Frame(dialog, bg="#e74c3c", relief="flat", bd=0)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
    
    # Header
    header_frame = tk.Frame(main_frame, bg="#c0392b", height=50)
    header_frame.pack(fill=tk.X, pady=(0, 15))
    header_frame.pack_propagate(False)
    
    title_label = tk.Label(header_frame, text="❌ Login Failed", 
                          font=safe_font(14, "bold"), 
                          bg="#c0392b", fg="white")
    title_label.pack(expand=True)
    
    # Message area
    message_frame = tk.Frame(main_frame, bg="#e74c3c")
    message_frame.pack(fill=tk.X, padx=20, pady=15)
    
    message_label = tk.Label(message_frame, text="Invalid username or password!\n\nWhat would you like to do?", 
                           font=safe_font(12), 
                           bg="#e74c3c", fg="white",
                           wraplength=400, justify=tk.CENTER)
    message_label.pack()
    
    # Button frame
    button_frame = tk.Frame(main_frame, bg="#e74c3c")
    button_frame.pack(fill=tk.X, padx=20, pady=20)
    
    def on_try_again():
        result[0] = "retry"
        dialog.destroy()
    
    def on_forgot_password():
        result[0] = "forgot"
        dialog.destroy()
    
    def on_exit():
        result[0] = "exit"
        dialog.destroy()
    
    # Create a centered container for buttons
    button_container = tk.Frame(button_frame, bg="#e74c3c")
    button_container.pack(expand=True)
    
    retry_button = tk.Button(button_container, text="🔄 Try Again", 
                           font=safe_font(10, "bold"), 
                           bg="#27ae60", fg="white",
                           relief="flat", bd=0, padx=25, pady=10,
                           cursor="hand2", command=on_try_again)
    retry_button.pack(pady=(0, 12))
    
    forgot_button = tk.Button(button_container, text="🔑 Forgot Password", 
                            font=safe_font(10, "bold"), 
                            bg="#f39c12", fg="white",
                            relief="flat", bd=0, padx=25, pady=10,
                            cursor="hand2", command=on_forgot_password)
    forgot_button.pack(pady=(0, 12))
    
    exit_button = tk.Button(button_container, text="✗ Exit", 
                          font=safe_font(10, "bold"), 
                          bg="#95a5a6", fg="white",
                          relief="flat", bd=0, padx=25, pady=10,
                          cursor="hand2", command=on_exit)
    exit_button.pack()
    
    # Bind keys
    dialog.bind('<Return>', lambda e: on_try_again())
    dialog.bind('<Escape>', lambda e: on_exit())
    
    dialog.focus_set()
    dialog.wait_window()
    
    # Handle the result
    if result[0] == "retry":
        login()  # Try login again
    elif result[0] == "forgot":
        forgot_password()  # Start password recovery
        if root.winfo_exists():  # If recovery was successful, try login again
            login()
    else:
        root.destroy()  # Exit application

# ---- GUI Setup ----
def open_main_window():
    global vehicle_number_entry, tree, search_entry, vehicle_type_var, vehicle_type_dropdown, status_labels
    
    # Sync parking spaces with database at startup
    sync_parking_spaces()
    
    main_window = tk.Tk()
    main_window.title("Parking Management System")
    main_window.geometry("750x550")
    main_window.resizable(True, True)
    main_window.configure(bg="#f5f5f5")

    # Title Frame
    title_frame = tk.Frame(main_window, bg="#2c3e50", height=45)
    title_frame.pack(fill=tk.X, pady=(0, 10))
    title_frame.pack_propagate(False)

    title_label = tk.Label(title_frame, text="🚗 Parking Management System", 
                          font=safe_font(14, "bold"), bg="#2c3e50", fg="white")
    title_label.pack(expand=True)

    # Main Container
    main_container = tk.Frame(main_window, bg="#f5f5f5")
    main_container.pack(fill=tk.BOTH, expand=True, padx=10)

    # Parking Status Section
    status_section = tk.LabelFrame(main_container, text=" Parking Status ", 
                                  font=safe_font(10, "bold"), bg="white", 
                                  fg="#2c3e50", relief="flat", bd=2)
    status_section.pack(fill=tk.X, pady=(0, 8))

    status_inner = tk.Frame(status_section, bg="white")
    status_inner.pack(fill=tk.X, padx=8, pady=8)

    # Get parking spaces info and create status labels
    spaces_info = get_parking_spaces()
    status_labels = {}  # Store references to labels for real-time updates
    
    for i, (vehicle_type, total_spaces, occupied_spaces) in enumerate(spaces_info):
        available_spaces = total_spaces - occupied_spaces
        
        # Create status frame for each vehicle type
        type_frame = tk.Frame(status_inner, bg="white")
        type_frame.grid(row=0, column=i, padx=8, pady=4, sticky="ew")
        
        # Vehicle type icon and name
        type_label = tk.Label(type_frame, text=f"{vehicle_type}:", 
                             font=safe_font(9, "bold"), 
                             bg="white", fg="#2c3e50")
        type_label.pack(anchor=tk.W)
        
        # Status with color coding
        status_color = "#27ae60" if available_spaces > 0 else "#e74c3c"
        status_text = f"{occupied_spaces}/{total_spaces} occupied"
        
        status_label = tk.Label(type_frame, text=status_text, 
                               font=safe_font(8), 
                               bg="white", fg=status_color)
        status_label.pack(anchor=tk.W)
        
        # Available spaces
        available_label = tk.Label(type_frame, text=f"Available: {available_spaces}", 
                                  font=safe_font(8), 
                                  bg="white", fg="#34495e")
        available_label.pack(anchor=tk.W)
        
        # Store label references for real-time updates
        status_labels[vehicle_type] = {
            'status_label': status_label,
            'available_label': available_label
        }
    
    # Configure grid weights
    for i in range(len(spaces_info)):
        status_inner.grid_columnconfigure(i, weight=1)

    # Vehicle Entry Section
    entry_section = tk.LabelFrame(main_container, text=" Vehicle Entry ", 
                                 font=safe_font(10, "bold"), bg="white", 
                                 fg="#2c3e50", relief="flat", bd=2)
    entry_section.pack(fill=tk.X, pady=(0, 8))

    entry_inner = tk.Frame(entry_section, bg="white")
    entry_inner.pack(fill=tk.X, padx=8, pady=8)

    vehicle_number_label = tk.Label(entry_inner, text="Vehicle Number:", 
                                   font=safe_font(9), bg="white", fg="#34495e")
    vehicle_number_label.grid(row=0, column=0, sticky="w", padx=(0, 6))

    # Register validation function
    vcmd = (main_window.register(validate_vehicle_number), '%S')
    
    vehicle_number_entry = tk.Entry(entry_inner, font=safe_font(9), 
                                   relief="flat", bd=5, bg="#ecf0f1", width=16,
                                   validate='key', validatecommand=vcmd)
    vehicle_number_entry.grid(row=0, column=1, padx=(0, 8))
    
    # Bind KeyRelease event for real-time formatting
    vehicle_number_entry.bind('<KeyRelease>', format_vehicle_number)

    # Vehicle Type Dropdown
    vehicle_type_label = tk.Label(entry_inner, text="Vehicle Type:", 
                                 font=safe_font(9), bg="white", fg="#34495e")
    vehicle_type_label.grid(row=0, column=2, sticky="w", padx=(0, 6))

    vehicle_type_var = tk.StringVar(value="Car")
    vehicle_type_dropdown = ttk.Combobox(entry_inner, textvariable=vehicle_type_var,
                                        values=["Car", "Bike", "Truck", "Bus"],
                                        state="readonly", font=safe_font(9), width=10)
    vehicle_type_dropdown.grid(row=0, column=3, padx=(0, 8))
    
    # Force the dropdown to update properly
    vehicle_type_dropdown.current(0)  # Set to first item (Car)
    
    # Add a callback to handle dropdown selection
    def on_vehicle_type_change(event):
        selected = vehicle_type_dropdown.get()
        vehicle_type_var.set(selected)  # Explicitly set the variable
    
    vehicle_type_dropdown.bind('<<ComboboxSelected>>', on_vehicle_type_change)

    entry_button = tk.Button(entry_inner, text="✓ Vehicle Entry", 
                           font=safe_font(9, "bold"), bg="#27ae60", fg="white",
                           relief="flat", bd=0, padx=15, pady=6, cursor="hand2",
                           command=vehicle_entry)
    entry_button.grid(row=0, column=4, padx=(0, 8))

    exit_button = tk.Button(entry_inner, text="✗ Vehicle Exit", 
                          font=safe_font(9, "bold"), bg="#e74c3c", fg="white",
                          relief="flat", bd=0, padx=15, pady=6, cursor="hand2",
                          command=vehicle_exit)
    exit_button.grid(row=0, column=5)

    # Search Section
    search_section = tk.LabelFrame(main_container, text=" Search & Filter ", 
                                  font=safe_font(10, "bold"), bg="white", 
                                  fg="#2c3e50", relief="flat", bd=2)
    search_section.pack(fill=tk.X, pady=(0, 8))

    search_inner = tk.Frame(search_section, bg="white")
    search_inner.pack(fill=tk.X, padx=8, pady=8)

    search_label = tk.Label(search_inner, text="Search Vehicle:", 
                           font=safe_font(9), bg="white", fg="#34495e")
    search_label.grid(row=0, column=0, sticky="w", padx=(0, 6))

    # Register validation function for search
    search_vcmd = (main_window.register(validate_vehicle_number), '%S')
    
    search_entry = tk.Entry(search_inner, font=safe_font(9), 
                           relief="flat", bd=5, bg="#ecf0f1", width=16,
                           validate='key', validatecommand=search_vcmd)
    search_entry.grid(row=0, column=1, padx=(0, 8))
    
    # Bind KeyRelease event for real-time formatting and search
    def format_and_search(event):
        format_vehicle_number(event)
        refresh_treeview()  # Auto-search as user types
    
    search_entry.bind('<KeyRelease>', format_and_search)

    search_button = tk.Button(search_inner, text="🔍 Search", 
                            font=safe_font(9, "bold"), bg="#9b59b6", fg="white",
                            relief="flat", bd=0, padx=15, pady=6, cursor="hand2",
                            command=search_vehicle)
    search_button.grid(row=0, column=2, padx=(0, 8))

    clear_search_button = tk.Button(search_inner, text="🗑 Clear", 
                                  font=safe_font(9, "bold"), bg="#95a5a6", fg="white",
                                  relief="flat", bd=0, padx=15, pady=6, cursor="hand2",
                                  command=clear_filters)
    clear_search_button.grid(row=0, column=3)

    # Records Section
    records_section = tk.LabelFrame(main_container, text=" Parking Records ", 
                                   font=safe_font(10, "bold"), bg="white", 
                                   fg="#2c3e50", relief="flat", bd=2)
    records_section.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

    # Treeview Frame
    tree_frame = tk.Frame(records_section, bg="white")
    tree_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    # Style for Treeview
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", 
                   background="#ffffff",
                   foreground="#2c3e50",
                   rowheight=20,
                   fieldbackground="#ffffff",
                   font=safe_font(8))
    style.configure("Treeview.Heading", 
                   background="#34495e",
                   foreground="white",
                   font=safe_font(9, "bold"))
    style.map("Treeview", background=[('selected', '#3498db')])

    columns = ("ID", "Vehicle Number", "Vehicle Type", "Entry Time", "Exit Time", "Fee")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)

    # Configure columns with optimized widths
    tree.column("ID", width=40, anchor=tk.CENTER)
    tree.column("Vehicle Number", width=100, anchor=tk.CENTER)
    tree.column("Vehicle Type", width=80, anchor=tk.CENTER)
    tree.column("Entry Time", width=120, anchor=tk.CENTER)
    tree.column("Exit Time", width=120, anchor=tk.CENTER)
    tree.column("Fee", width=70, anchor=tk.CENTER)

    for col in columns:
        tree.heading(col, text=col)

    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Scrollbar
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Action Buttons Section - Keep only essential buttons
    button_section = tk.Frame(main_container, bg="#f5f5f5")
    button_section.pack(fill=tk.X, pady=(8, 8))

    change_pass_button = tk.Button(button_section, text="🔑 Change Password", 
                                 font=safe_font(9, "bold"), bg="#f39c12", fg="white",
                                 relief="flat", bd=0, padx=18, pady=8, cursor="hand2",
                                 command=change_password)
    change_pass_button.pack(side=tk.LEFT, padx=(0, 10))

    print_receipt_button = tk.Button(button_section, text="🖨️ Print Receipt", 
                                   font=safe_font(9, "bold"), bg="#8e44ad", fg="white",
                                   relief="flat", bd=0, padx=18, pady=8, cursor="hand2",
                                   command=print_receipt)
    print_receipt_button.pack(side=tk.LEFT, padx=(0, 10))

    admin_button = tk.Button(button_section, text="⚙️ Admin", 
                           font=safe_font(9, "bold"), bg="#e67e22", fg="white",
                           relief="flat", bd=0, padx=18, pady=8, cursor="hand2",
                           command=admin_update_spaces)
    admin_button.pack(side=tk.LEFT, padx=(0, 10))

    # Status Bar
    status_bar = tk.Frame(main_window, bg="#34495e", height=22)
    status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    status_bar.pack_propagate(False)

    status_label = tk.Label(status_bar, text="Ready | Modern Parking System", 
                           font=safe_font(8), bg="#34495e", fg="white")
    status_label.pack(side=tk.LEFT, padx=6, pady=2)

    # Initialize Treeview and sync parking spaces
    sync_parking_spaces()
    refresh_treeview()
    update_parking_status()  # Initialize parking status display

    main_window.mainloop()

# ---- Auth Screens ----
def signup():
    username = show_modern_input("Sign Up", "Create admin username:", icon="👤")
    if not username:
        root.destroy()
        return
    
    password = show_modern_input("Sign Up", "Create admin password:", show_char="*", icon="🔒")
    if not password:
        root.destroy()
        return
    
    confirm_password = show_modern_input("Sign Up", "Confirm admin password:", show_char="*", icon="🔒")
    if not confirm_password:
        root.destroy()
        return
    
    if password != confirm_password:
        show_modern_error("Error", "Passwords do not match!", "❌")
        root.destroy()
        return
    
    # Ask for security question
    security_question = show_question_selector("Sign Up", "Select a security question:", 
                                              ["What is your pet's name?", 
                                               "What is your mother's maiden name?", 
                                               "What was the name of your first school?"])
    if not security_question:
        root.destroy()
        return
    
    # Ask for security answer
    security_answer = show_modern_input("Sign Up", "Enter the answer to your security question:", icon="🔑")
    if not security_answer:
        root.destroy()
        return
    
    cursor.execute('INSERT INTO admin (username, password, security_question, security_answer) VALUES (?, ?, ?, ?)', 
                   (username, hash_password(password), security_question, security_answer))
    conn.commit()
    show_modern_info("Success", "Admin account created successfully!", "✅")
    open_main_window()

def login():
    username = show_modern_input("Login", "Enter admin username:", icon="👤")
    if not username:
        root.destroy()
        return
    
    password = show_modern_input("Login", "Enter admin password:", show_char="*", icon="🔒")
    if not password:
        root.destroy()
        return
    
    cursor.execute('SELECT * FROM admin WHERE username=? AND password=?', (username, hash_password(password)))
    if cursor.fetchone():
        show_modern_info("Login Success", "Welcome Admin!", "🎉")
        open_main_window()
    else:
        # Show login failed with recovery option
        show_login_failed_dialog()

# ---- Start App ----
root = tk.Tk()
root.withdraw()  # Hide root window

# Check if admin exists
cursor.execute('SELECT COUNT(*) FROM admin')
if cursor.fetchone()[0] == 0:
    signup()  # First time: Sign Up
else:
    login()   # Subsequent times: Login

conn.close()
