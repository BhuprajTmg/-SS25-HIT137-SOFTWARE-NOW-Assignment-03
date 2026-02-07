import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Scale
from PIL import Image, ImageTk, ImageOps

# Used OOP Concept: Main UI class for managing graphical interface
class UI:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.root.title("PyVision Editor")
        self.root.geometry("1300x850")
        
        # This is configured for theme settings
        self.bg_col = "#2b2b2b"
        self.panel_col = "#3c3f41"
        self.root.configure(bg=self.bg_col)

        self.img_cache = None 
        self.setup_gui()

    def setup_gui(self):
        #This gives us the configuration of Menu Bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.app.open_image)
        file_menu.add_command(label="Save", command=self.app.save_image)
        file_menu.add_command(label="Revert Original", command=self.app.revert_original)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Tihs gives entire layout of the Frames
        self.sidebar = tk.Frame(self.root, width=300, bg=self.panel_col, padx=10, pady=10)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.main_area = tk.Frame(self.root, bg=self.bg_col)
        self.main_area.pack(side="right", expand=True, fill="both")

        self.canvas = tk.Canvas(self.main_area, bg="#101010", highlightthickness=0)
        self.canvas.pack(expand=True, fill="both", padx=20, pady=20)

        self.status_bar = tk.Label(self.root, text="Ready", bg=self.panel_col, fg="white", anchor="w")
        self.status_bar.pack(side="bottom", fill="x")

        self.load_controls()

    def load_controls(self):
        # configures the header 
        def header(txt):
            tk.Label(self.sidebar, text=txt, font=("Arial", 11, "bold"), 
                     bg=self.panel_col, fg="#4a90e2").pack(pady=(15,5), anchor="w")

        # confgiures for buttons
        def btn(txt, cmd, col="#555555"):
            tk.Button(self.sidebar, text=txt, command=cmd, bg=col, fg="white", 
                      relief="flat").pack(fill="x", pady=2)

        # History Section
        header("History")
        row = tk.Frame(self.sidebar, bg=self.panel_col)
        row.pack(fill="x")
        tk.Button(row, text="Undo", command=self.app.undo_action, bg="#f0ad4e", fg="black").pack(side="left", expand=True, fill="x", padx=1)
        tk.Button(row, text="Redo", command=self.app.redo_action, bg="#555555", fg="white").pack(side="right", expand=True, fill="x", padx=1)
        
        btn("⚠ Revert All", self.app.revert_original, "#d9534f")

        # Filters
        header("Filters")
        btn("Grayscale", self.app.apply_grayscale)
        btn("Edge Detection", self.app.apply_edge)

        # Sliders
        header("Adjustments")
        
        def slider(lbl, cmd, min_v, max_v):
            tk.Label(self.sidebar, text=lbl, bg=self.panel_col, fg="silver").pack(anchor="w")
            s = Scale(self.sidebar, from_=min_v, to=max_v, orient="horizontal", 
                      bg=self.panel_col, fg="white", highlightthickness=0, command=cmd)
            s.pack(fill="x")
            return s

        self.s_blur = slider("Blur", self.app.change_blur, 0, 20)
        self.s_bright = slider("Brightness", self.app.change_brightness, -100, 100)
        self.s_cont = slider("Contrast", self.app.change_contrast, -100, 100)

        # Commit/Reset Buttons
        box = tk.Frame(self.sidebar, bg=self.panel_col)
        box.pack(fill="x", pady=10)
        tk.Button(box, text="✔ Apply", command=self.app.commit_sliders, bg="#5cb85c", fg="white").pack(side="left", expand=True, fill="x", padx=1)
        tk.Button(box, text="✖ Reset", command=self.app.reset_sliders, bg="#d9534f", fg="white").pack(side="right", expand=True, fill="x", padx=1)

        # Geometry of the image
        header("Geometry")
        btn("Rotate 90", lambda: self.app.apply_geometry("rotate", 0))
        btn("Flip H", lambda: self.app.apply_geometry("flip", 1))
        btn("Resize", lambda: self.app.apply_geometry("resize", None))

    def update_image(self, pil_img):
        if not pil_img: return
        
        self.canvas.update_idletasks()
        
        # This helps generate and set picture graphic.
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()

        if w < 10: w, h = 1000, 800
        
        # Resize image according (Aspect Ratio preserved)
        img = ImageOps.contain(pil_img.copy(), (w, h), Image.Resampling.LANCZOS)
        self.img_cache = ImageTk.PhotoImage(img)
        
        # Clear previous drawing
        self.canvas.delete("all")
        
        # DRAW IMAGE AT CENTER
        self.canvas.create_image(w//2, h//2, anchor=tk.CENTER, image=self.img_cache)

    def set_sliders(self, v1, v2, v3):
        self.s_blur.set(v1)
        self.s_bright.set(v2)
        self.s_cont.set(v3)

    # It will help in Wrapping for dialogs
    def ask_open(self): 
        return filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg *.bmp")])
    
    def ask_save(self): 
        return filedialog.asksaveasfilename(defaultextension=".png")
    #It display error message dialog to user
    def show_err(self, msg): 
        messagebox.showerror("Error", msg)
    
    #Simillarly this gives us the information
    def show_info(self, msg): 
        messagebox.showinfo("Info", msg)
        
    def ask_res(self):
        w = simpledialog.askinteger("Resize", "Width:", minvalue=1)
        h = simpledialog.askinteger("Resize", "Height:", minvalue=1)
        return w, h
