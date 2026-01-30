# import tkinter as tk
# from tkinter import filedialog, messagebox, simpledialog, Scale
# from PIL import Image, ImageTk, ImageOps

# # Colors
# C_BG = "#2b2b2b"
# C_PANEL = "#3c3f41"
# C_ACCENT = "#4a90e2"
# C_BTN = "#555555"

# class MainView:
#     def __init__(self, root, controller):
#         self.root = root
#         self.controller = controller
#         self.root.title("PyVision Pro - Pipeline Editor")
#         self.root.geometry("1300x850")
#         self.root.configure(bg=C_BG)

#         self.canvas_image_ref = None
#         self._setup_ui()

#     def _setup_ui(self):
#         # Menu
#         self.menu_bar = tk.Menu(self.root)
#         self.root.config(menu=self.menu_bar)
        
#         f_menu = tk.Menu(self.menu_bar, tearoff=0)
#         f_menu.add_command(label="Open", command=self.controller.open_image)
#         f_menu.add_command(label="Save", command=self.controller.save_image)
#         f_menu.add_command(label="Revert to Original", command=self.controller.revert_original) # Added to Menu
#         f_menu.add_separator()
#         f_menu.add_command(label="Exit", command=self.root.quit)
#         self.menu_bar.add_cascade(label="File", menu=f_menu)

#         # Layout
#         self.controls_frame = tk.Frame(self.root, width=320, bg=C_PANEL, padx=10, pady=10)
#         self.controls_frame.pack(side=tk.LEFT, fill=tk.Y)
#         self.controls_frame.pack_propagate(False)

#         self.display_frame = tk.Frame(self.root, bg=C_BG)
#         self.display_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

#         self.canvas = tk.Canvas(self.display_frame, bg="#101010", highlightthickness=0)
#         self.canvas.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

#         self.status_bar = tk.Label(self.root, text="Ready", bg=C_PANEL, fg="white", anchor=tk.W)
#         self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

#         self._create_controls()

#     def _create_controls(self):
#         def add_head(txt):
#             tk.Label(self.controls_frame, text=txt, font=("Arial", 11, "bold"), bg=C_PANEL, fg=C_ACCENT).pack(pady=(15,5), anchor="w")

#         def add_btn(txt, cmd, color=C_BTN):
#             tk.Button(self.controls_frame, text=txt, command=cmd, bg=color, fg="white", relief=tk.FLAT).pack(fill=tk.X, pady=2)

#         # 1. Main Actions
#         add_head("History / Reset")
        
#         # Undo / Redo Row
#         row1 = tk.Frame(self.controls_frame, bg=C_PANEL)
#         row1.pack(fill=tk.X)
#         tk.Button(row1, text="Undo", command=self.controller.undo_action, bg="#f0ad4e", fg="black").pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,2))
#         tk.Button(row1, text="Redo", command=self.controller.redo_action, bg=C_BTN, fg="white").pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(2,0))

#         # Revert Button
#         tk.Button(self.controls_frame, text="⚠ Revert to Original File", command=self.controller.revert_original, bg="#d9534f", fg="white", font=("Arial", 9, "bold")).pack(fill=tk.X, pady=(5,0))

#         # 2. Filters
#         add_head("Quick Filters")
#         add_btn("Grayscale", self.controller.apply_grayscale)
#         add_btn("Edge Detection", self.controller.apply_edge)

#         # 3. Pipeline Sliders
#         add_head("Adjustments (Pipeline)")
        
#         def mk_slide(lbl, cmd, v_min, v_max):
#             tk.Label(self.controls_frame, text=lbl, bg=C_PANEL, fg="silver").pack(anchor="w")
#             s = Scale(self.controls_frame, from_=v_min, to=v_max, orient=tk.HORIZONTAL, bg=C_PANEL, fg="white", highlightthickness=0, command=cmd)
#             s.pack(fill=tk.X)
#             return s

#         self.blur_s = mk_slide("Blur", self.controller.change_blur, 0, 20)
#         self.bright_s = mk_slide("Brightness", self.controller.change_brightness, -100, 100)
#         self.cont_s = mk_slide("Contrast", self.controller.change_contrast, -100, 100)

#         # Apply / Cancel Row
#         row2 = tk.Frame(self.controls_frame, bg=C_PANEL)
#         row2.pack(fill=tk.X, pady=10)
#         tk.Button(row2, text="✔ Apply Pipeline", command=self.controller.commit_sliders, bg="#5cb85c", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,2))
#         tk.Button(row2, text="✖ Reset Sliders", command=self.controller.reset_sliders, bg="#d9534f", fg="white").pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(2,0))

#         # 4. Geometry
#         add_head("Geometry")
#         add_btn("Rotate 90", lambda: self.controller.apply_geometry("rotate", 0))
#         add_btn("Flip H", lambda: self.controller.apply_geometry("flip", 1))
#         add_btn("Resize", lambda: self.controller.apply_geometry("resize", None))

#     def update_image(self, pil_image):
#         if not pil_image: return
#         # Logic to fit image in canvas (Aspect Ratio)
#         cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
#         if cw < 10: cw, ch = 800, 600
        
#         img = ImageOps.contain(pil_image.copy(), (cw, ch), Image.Resampling.LANCZOS)
#         self.canvas_image_ref = ImageTk.PhotoImage(img)
#         self.canvas.delete("all")
#         self.canvas.create_image(cw//2, ch//2, anchor=tk.CENTER, image=self.canvas_image_ref)

#     def set_sliders(self, b, br, c):
#         # We need to block callbacks to prevent "double firing" during reset
#         # But simple .set() is usually fine if controller handles logic efficiently
#         self.blur_s.set(b)
#         self.bright_s.set(br)
#         self.cont_s.set(c)

#     def ask_open(self): return filedialog.askopenfilename(filetypes=[("Img", "*.jpg *.png *.jpeg *.bmp")])
#     def ask_save(self): return filedialog.asksaveasfilename(defaultextension=".png")
#     def show_err(self, m): messagebox.showerror("Error", m)
#     def show_info(self, m): messagebox.showinfo("Info", m)
#     def ask_res(self):
#         w = simpledialog.askinteger("Resize", "Width:", minvalue=1)
#         h = simpledialog.askinteger("Resize", "Height:", minvalue=1)
#         return w, h


# ---------------------New code

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Scale
from PIL import Image, ImageTk, ImageOps

class UI:
    def __init__(self, root, app):
        self.root = root
        self.app = app
        self.root.title("PyVision Editor")
        self.root.geometry("1300x850")
        
        # Theme Settings
        self.bg_col = "#2b2b2b"
        self.panel_col = "#3c3f41"
        self.root.configure(bg=self.bg_col)

        self.img_cache = None 
        self.setup_gui()

    def setup_gui(self):
        # Menu Bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open", command=self.app.open_image)
        file_menu.add_command(label="Save", command=self.app.save_image)
        file_menu.add_command(label="Revert Original", command=self.app.revert_original)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Layout Frames
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
        # Helper for headers
        def header(txt):
            tk.Label(self.sidebar, text=txt, font=("Arial", 11, "bold"), 
                     bg=self.panel_col, fg="#4a90e2").pack(pady=(15,5), anchor="w")

        # Helper for buttons
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

        # Geometry
        header("Geometry")
        btn("Rotate 90", lambda: self.app.apply_geometry("rotate", 0))
        btn("Flip H", lambda: self.app.apply_geometry("flip", 1))
        btn("Resize", lambda: self.app.apply_geometry("resize", None))

    # def update_image(self, pil_img):
    #     if not pil_img: return
        
    #     # Fit aspect ratio
    #     w = self.canvas.winfo_width()
    #     h = self.canvas.winfo_height()
        
    #     # Fallback if window isn't rendered yet
    #     if w < 10: w, h = 1500, 800
        
    #     img = ImageOps.contain(pil_img.copy(), (w, h), Image.Resampling.LANCZOS)
    #     self.img_cache = ImageTk.PhotoImage(img)
        
    #     self.canvas.delete("all")
    #     self.canvas.create_image(w//2, h//2, anchor="center", image=self.img_cache)
    def update_image(self, pil_img):
        if not pil_img: return
        
        # FIX: Force the canvas to update its geometry before we measure it
        self.canvas.update_idletasks()
        
        # Get the actual visible dimensions of the canvas
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # Fallback only if the window is somehow minimized or not mapped
        # We update these to match your window size (1300 - 300 sidebar = 1000)
        if w < 10: w, h = 1000, 800
        
        # Resize image to fit inside the canvas (Aspect Ratio preserved)
        img = ImageOps.contain(pil_img.copy(), (w, h), Image.Resampling.LANCZOS)
        self.img_cache = ImageTk.PhotoImage(img)
        
        # Clear previous drawing
        self.canvas.delete("all")
        
        # DRAW IMAGE AT TRUE CENTER
        # w//2 and h//2 are the center points
        # anchor=tk.CENTER ensures the image's center sits on that point
        self.canvas.create_image(w//2, h//2, anchor=tk.CENTER, image=self.img_cache)

    def set_sliders(self, v1, v2, v3):
        self.s_blur.set(v1)
        self.s_bright.set(v2)
        self.s_cont.set(v3)

    # Wrappers for dialogs
    def ask_open(self): 
        return filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.png *.jpeg *.bmp")])
    
    def ask_save(self): 
        return filedialog.asksaveasfilename(defaultextension=".png")
    
    def show_err(self, msg): 
        messagebox.showerror("Error", msg)
    
    def show_info(self, msg): 
        messagebox.showinfo("Info", msg)
        
    def ask_res(self):
        w = simpledialog.askinteger("Resize", "Width:", minvalue=1)
        h = simpledialog.askinteger("Resize", "Height:", minvalue=1)
        return w, h