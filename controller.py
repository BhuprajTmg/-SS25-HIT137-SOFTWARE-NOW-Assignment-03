from PIL import Image

class AppController:
    def __init__(self, root, Model, View):
        self.model = Model()
        self.view = View(root, self)
        
        # Flag to prevent sliders from going crazy during resets
        self.resetting = False
        
        # Make sure canvas updates when window gets resized
        self.view.canvas.bind("<Configure>", lambda e: self.refresh_view())

    def open_image(self):
        path = self.view.ask_open()
        if not path: 
            return  # User cancelled, no biggie

        if self.model.load_image(path):
            self.reset_ui_sliders()
            self.refresh_view()
            # Show which file we just opened
            self.view.status_bar.config(text=f"Loaded: {path}")

    def save_image(self):
        # Can't save if there's nothing loaded yet
        if self.model.curr_img is None: 
            return
        
        path = self.view.ask_save()
        if path and self.model.save_image(path):
            self.view.show_info("Image Saved!")

    def revert_original(self):
        # Go back to the original image, undoing everything
        if self.model.revert_original():
            self.reset_ui_sliders()
            self.refresh_view()
            self.view.status_bar.config(text="Reverted to original.")

    def refresh_view(self):
        # Get the current image data and update display
        rgb = self.model.get_rgb_display()
        if rgb is not None:
            self.view.update_image(Image.fromarray(rgb))

    def _has_img(self):
        # Quick check to make sure an image is loaded
        if self.model.curr_img is None:
            self.view.show_err("Please load an image first.")
            return False
        return True

    # Slider change handlers below
    # Note: these get called A LOT when dragging sliders

    def change_blur(self, val):
        if self.resetting or not self._has_img(): 
            return
        self.model.update_param("blur", int(val))
        self.refresh_view()

    def change_brightness(self, val):
        if self.resetting or not self._has_img(): 
            return
        # Convert to int since slider gives us float sometimes
        self.model.update_param("bright", int(val))
        self.refresh_view()

    def change_contrast(self, val):
        if self.resetting or not self._has_img(): 
            return
        self.model.update_param("contrast", int(val))
        self.refresh_view()

    def commit_sliders(self):
        # Actually apply the slider adjustments permanently
        if not self._has_img(): 
            return
        
        self.model.commit()
        self.reset_ui_sliders()
        self.view.status_bar.config(text="Adjustments applied.")
        self.refresh_view()

    def reset_sliders(self):
        # Discard any slider changes and go back to committed state
        if not self._has_img(): 
            return
        
        self.reset_ui_sliders()
        self.model.reset_params()
        self.model.preview = None  # Clear preview
        self.refresh_view()
        self.view.status_bar.config(text="Sliders reset.")

    def reset_ui_sliders(self):
        """Sets all sliders back to zero without triggering their callbacks"""
        self.resetting = True  # Temporary flag to block callbacks
        self.view.set_sliders(0, 0, 0)
        self.resetting = False

    # Filter and effect functions

    def apply_grayscale(self):
        if self._has_img():
            self.model.apply_gray()
            self._post_action_reset()

    def apply_edge(self):
        # Edge detection filter
        if self._has_img():
            self.model.apply_edges()
            self._post_action_reset()

    def apply_geometry(self, op, p):
        if not self._has_img(): 
            return

        # Handle resize specially since it needs user input
        if op == "resize":
            w, h = self.view.ask_res()
            if w and h: 
                self.model.apply_geo("resize", (w, h))
        else:
            # Other operations like rotate, flip, etc.
            self.model.apply_geo(op, p)
            
        self._post_action_reset()

    def _post_action_reset(self):
        # Common cleanup after applying effects
        self.reset_ui_sliders()
        self.refresh_view()

    # Undo/Redo functionality

    def undo_action(self):
        if self.model.undo():
            self.reset_ui_sliders()
            self.refresh_view()
            self.view.status_bar.config(text="Undo.")

    def redo_action(self):
        if self.model.redo():
            self.reset_ui_sliders()
            self.refresh_view()
            self.view.status_bar.config(text="Redo.")