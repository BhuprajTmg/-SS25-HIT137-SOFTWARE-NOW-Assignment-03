# from PIL import Image

# class AppController:
#     def __init__(self, root, model_cls, view_cls):
#         self.model = model_cls()
#         self.view = view_cls(root, self)
        
#         # Flag to prevent slider callbacks during reset
#         self.is_resetting = False
        
#         self.view.canvas.bind("<Configure>", lambda e: self._refresh())

#     # --- File ---
#     def open_image(self):
#         path = self.view.ask_open()
#         if path and self.model.load_image(path):
#             self.view.set_sliders(0, 0, 0)
#             self._refresh()
#             self.view.status_bar.config(text=f"Loaded: {path}")

#     def save_image(self):
#         if self.model.current_image is None: return
#         path = self.view.ask_save()
#         if path and self.model.save_image(path):
#             self.view.show_info("Saved!")

#     def revert_original(self):
#         """Restores the file as it was on disk."""
#         if self.model.revert_to_original():
#             self.is_resetting = True
#             self.view.set_sliders(0, 0, 0)
#             self.is_resetting = False
#             self._refresh()
#             self.view.status_bar.config(text="Reverted to Original File.")

#     def _refresh(self):
#         rgb = self.model.get_display_image()
#         if rgb is not None:
#             self.view.update_image(Image.fromarray(rgb))

#     def _chk(self):
#         if self.model.current_image is None:
#             self.view.show_err("Load image first")
#             return False
#         return True

#     # --- Pipeline Sliders ---
    
#     def change_blur(self, val):
#         if self.is_resetting or not self._chk(): return
#         self.model.update_pipeline_param("blur", int(val))
#         self._refresh()

#     def change_brightness(self, val):
#         if self.is_resetting or not self._chk(): return
#         self.model.update_pipeline_param("brightness", int(val))
#         self._refresh()

#     def change_contrast(self, val):
#         if self.is_resetting or not self._chk(): return
#         self.model.update_pipeline_param("contrast", int(val))
#         self._refresh()

#     def commit_sliders(self):
#         if not self._chk(): return
#         self.model.commit_pipeline()
        
#         # Reset sliders visually to 0, because effects are now baked in
#         self.is_resetting = True
#         self.view.set_sliders(0, 0, 0) 
#         self.is_resetting = False
        
#         self.view.status_bar.config(text="Pipeline Applied.")
#         self._refresh()

#     def reset_sliders(self):
#         if not self._chk(): return
        
#         self.is_resetting = True
#         self.view.set_sliders(0, 0, 0)
#         self.is_resetting = False
        
#         self.model.reset_pipeline_params()
#         self.model.preview_image = None # clear preview
#         self._refresh()
#         self.view.status_bar.config(text="Sliders Reset.")

#     # --- Instant ---
#     def apply_grayscale(self):
#         if self._chk():
#             self.model.apply_grayscale()
#             self._reset_ui_after_instant()

#     def apply_edge(self):
#         if self._chk():
#             self.model.apply_edge_detection()
#             self._reset_ui_after_instant()

#     def apply_geometry(self, op, p):
#         if self._chk():
#             if op == "resize":
#                 w, h = self.view.ask_res()
#                 if w and h: self.model.apply_geometry("resize", (w, h))
#             else:
#                 self.model.apply_geometry(op, p)
#             self._reset_ui_after_instant()

#     def _reset_ui_after_instant(self):
#         self.is_resetting = True
#         self.view.set_sliders(0, 0, 0)
#         self.is_resetting = False
#         self._refresh()

#     # --- Undo/Redo ---
#     def undo_action(self):
#         if self.model.undo():
#             self.is_resetting = True
#             self.view.set_sliders(0, 0, 0)
#             self.is_resetting = False
#             self._refresh()
#             self.view.status_bar.config(text="Undone.")

#     def redo_action(self):
#         if self.model.redo():
#             self.is_resetting = True
#             self.view.set_sliders(0, 0, 0)
#             self.is_resetting = False
#             self._refresh()
#             self.view.status_bar.config(text="Redone.")


#-------------new code------------------
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

    def revert_original(self):
        if self.model.revert_original():
            self.reset_ui_sliders()
            self.refresh_view()
            self.view.status_bar.config(text="Reverted to original.")

    def refresh_view(self):
        rgb = self.model.get_rgb_display()
        if rgb is not None:
            self.view.update_image(Image.fromarray(rgb))

    def _has_img(self):
        if self.model.curr_img is None:
            self.view.show_err("Please load an image first.")
            return False
        return True

    # --- Sliders ---

    def change_blur(self, val):
        if self.resetting or not self._has_img(): return
        self.model.update_param("blur", int(val))
        self.refresh_view()

    def change_brightness(self, val):
        if self.resetting or not self._has_img(): return
        self.model.update_param("bright", int(val))
        self.refresh_view()

    def change_contrast(self, val):
        if self.resetting or not self._has_img(): return
        self.model.update_param("contrast", int(val))
        self.refresh_view()

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
        """Helper to zero out sliders without triggering callbacks"""
        self.resetting = True
        self.view.set_sliders(0, 0, 0)
        self.resetting = False

    # --- Actions ---

    def apply_grayscale(self):
        if self._has_img():
            self.model.apply_gray()
            self._post_action_reset()

    def apply_edge(self):
        if self._has_img():
            self.model.apply_edges()
            self._post_action_reset()

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

    # --- History ---

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