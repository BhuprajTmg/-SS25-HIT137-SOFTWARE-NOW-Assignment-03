from PIL import Image

class AppController:
    def __init__(self, root, Model, View):
        self.model = Model()
        self.view = View(root, self)
        
        # Prevent sliders from firing events during programatic resets
        self.resetting = False
        
        # Redraw image on window resize
        self.view.canvas.bind("<Configure>", lambda e: self.refresh_view())

    def open_image(self):
        path = self.view.ask_open()
        if not path: return

        if self.model.load_image(path):
            self.reset_ui_sliders()
            self.refresh_view()
            self.view.status_bar.config(text=f"Loaded: {path}")

    def save_image(self):
        if self.model.curr_img is None: return
        
        path = self.view.ask_save()
        if path and self.model.save_image(path):
            self.view.show_info("Image Saved!")
    # Discharge all edits and restore the original loaded image
    def revert_original(self):
        if self.model.revert_original():
            self.reset_ui_sliders()
            self.refresh_view()
            self.view.status_bar.config(text="Reverted to original.")
    # Update display by converting numpy array to PIL Image
    def refresh_view(self):
        rgb = self.model.get_rgb_display()
        if rgb is not None:
            self.view.update_image(Image.fromarray(rgb))

    def _has_img(self):
        if self.model.curr_img is None:
            self.view.show_err("Please load an image first.")
            return False
        return True

    # --- This is the sliders portion of the project ---

    def change_blur(self, val):
        if self.resetting or not self._has_img(): return
        self.model.update_param("blur", int(val))
        self.refresh_view()
    # Update model parameter and refreshes preview in real-time
    def change_brightness(self, val):
        if self.resetting or not self._has_img(): return
        self.model.update_param("bright", int(val))
        self.refresh_view()

    # Update slider callback for contrast adjustment
    def change_contrast(self, val):
        if self.resetting or not self._has_img(): return
        self.model.update_param("contrast", int(val))
        self.refresh_view()
    
    # Apply current slider adjustments permanently.
    def commit_sliders(self):
        if not self._has_img(): return
        
        self.model.commit()
        self.reset_ui_sliders()
        self.view.status_bar.config(text="Adjustments applied.")
        self.refresh_view()

    def reset_sliders(self):
        if not self._has_img(): return
        
        self.reset_ui_sliders()
        self.model.reset_params()
        self.model.preview = None
        self.refresh_view()
        self.view.status_bar.config(text="Sliders reset.")

    def reset_ui_sliders(self):
        self.resetting = True
        self.view.set_sliders(0, 0, 0)
        self.resetting = False

    # Actions

    def apply_grayscale(self):
        if self._has_img():
            self.model.apply_gray()
            self._post_action_reset()
    
    # Applied dege detection filter current image state
    def apply_edge(self):
        if self._has_img():
            self.model.apply_edges()
            self._post_action_reset()
    
    # Apply geometric transfomation for special resizing dialogue
    def apply_geometry(self, op, p):
        if not self._has_img(): return

        if op == "resize":
            w, h = self.view.ask_res()
            if w and h: 
                self.model.apply_geo("resize", (w, h))
        else:
            self.model.apply_geo(op, p)
            
        self._post_action_reset()

    def _post_action_reset(self):
        self.reset_ui_sliders()
        self.refresh_view()

    #History buttons and actions

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
