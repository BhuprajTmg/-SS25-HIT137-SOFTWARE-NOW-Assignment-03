# import cv2
# import numpy as np

# class ImageModel:
#     def __init__(self):
#         self.original_image = None      # The absolute original loaded from disk
#         self.current_image = None       # The 'committed' state (history tip)
#         self.preview_image = None       # The live preview (with uncommitted slider effects)
#         self.edit_base_image = None     # The snapshot used as the starting point for sliders
        
#         # Pipeline Parameters
#         self.slider_values = {
#             "blur": 0,
#             "brightness": 0,
#             "contrast": 0
#         }
        
#         self.history = []
#         self.redo_stack = []
#         self.filepath = ""

#     def load_image(self, filepath):
#         image = cv2.imread(filepath)
#         if image is not None:
#             self.filepath = filepath
#             self.original_image = image
#             self.current_image = image.copy()
#             self.edit_base_image = image.copy()
#             self.preview_image = None # No active preview initially
            
#             # Reset history
#             self.history = []
#             self.redo_stack = []
#             self._save_to_history()
            
#             # Reset params
#             self.reset_pipeline_params()
#             return True
#         return False

#     def save_image(self, filepath):
#         if self.current_image is not None:
#             # Save what the user sees (preview if active, else current)
#             target = self.preview_image if self.preview_image is not None else self.current_image
#             cv2.imwrite(filepath, target)
#             return True
#         return False

#     def _save_to_history(self):
#         if self.current_image is not None:
#             self.history.append(self.current_image.copy())
#             if len(self.history) > 20:
#                 self.history.pop(0)

#     # --- Pipeline Management ---

#     def reset_pipeline_params(self):
#         self.slider_values = {"blur": 0, "brightness": 0, "contrast": 0}

#     def start_edit(self):
#         """Ensures we have a valid base for editing."""
#         if self.current_image is not None:
#             self.edit_base_image = self.current_image.copy()

#     def update_pipeline_param(self, param, value):
#         self.slider_values[param] = value
#         # Trigger the pipeline calculation
#         self.compute_composite_preview()

#     def compute_composite_preview(self):
#         """Applies ALL active slider parameters in order."""
#         if self.edit_base_image is None: return

#         # Start with the clean base
#         img = self.edit_base_image.copy()

#         # 1. Apply Blur
#         b_val = self.slider_values["blur"]
#         if b_val > 0:
#             k = b_val if b_val % 2 == 1 else b_val + 1
#             img = cv2.GaussianBlur(img, (k, k), 0)

#         # 2. Apply Brightness
#         br_val = self.slider_values["brightness"]
#         if br_val != 0:
#             hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
#             h, s, v = cv2.split(hsv)
#             v = cv2.add(v, br_val)
#             v[v > 255] = 255
#             v[v < 0] = 0
#             final_hsv = cv2.merge((h, s, v))
#             img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

#         # 3. Apply Contrast
#         c_val = self.slider_values["contrast"]
#         if c_val != 0:
#             alpha = float(131 * (c_val + 127)) / (127 * (131 - c_val))
#             gamma = 127 * (1 - alpha)
#             img = cv2.addWeighted(img, alpha, img, 0, gamma)

#         self.preview_image = img

#     def commit_pipeline(self):
#         """Bakes the preview into the current image."""
#         if self.preview_image is not None:
#             self._save_to_history()
#             self.current_image = self.preview_image.copy()
#             self.edit_base_image = self.current_image.copy() # Update base
#             self.redo_stack.clear()
#             # Reset pipeline params since they are now baked in
#             self.reset_pipeline_params()
#             self.preview_image = None

#     def revert_to_original(self):
#         """Restores the absolute original file."""
#         if self.original_image is not None:
#             self._save_to_history()
#             self.current_image = self.original_image.copy()
#             self.edit_base_image = self.original_image.copy()
#             self.reset_pipeline_params()
#             self.preview_image = None
#             self.redo_stack.clear()
#             return True
#         return False

#     # --- Instant Actions ---
#     # These bypass the pipeline sliders and act directly on the image

#     def apply_grayscale(self):
#         self._save_to_history()
#         # If there were pending slider changes, bake them first? 
#         # For simplicity, we act on the current committed image.
#         gray = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2GRAY)
#         self.current_image = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
#         self.edit_base_image = self.current_image.copy()
#         self.reset_pipeline_params()
#         self.preview_image = None

#     def apply_edge_detection(self):
#         self._save_to_history()
#         edges = cv2.Canny(self.current_image, 100, 200)
#         self.current_image = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
#         self.edit_base_image = self.current_image.copy()
#         self.reset_pipeline_params()
#         self.preview_image = None

#     def apply_geometry(self, op_type, param):
#         self._save_to_history()
#         img = self.current_image
#         if op_type == "rotate":
#             if param == 0: img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
#             elif param == 1: img = cv2.rotate(img, cv2.ROTATE_180)
#             elif param == 2: img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
#         elif op_type == "flip":
#             img = cv2.flip(img, param)
#         elif op_type == "resize":
#             img = cv2.resize(img, (param[0], param[1]), interpolation=cv2.INTER_AREA)
        
#         self.current_image = img
#         self.edit_base_image = self.current_image.copy()
#         self.reset_pipeline_params() # Geometry resets sliders usually
#         self.preview_image = None

#     # --- Undo/Redo ---

#     def undo(self):
#         if len(self.history) > 1:
#             self.redo_stack.append(self.history.pop())
#             state = self.history[-1]
#             self.current_image = state.copy()
#             self.edit_base_image = state.copy()
#             self.reset_pipeline_params()
#             self.preview_image = None
#             return True
#         return False

#     def redo(self):
#         if self.redo_stack:
#             s = self.redo_stack.pop()
#             self.history.append(s)
#             self.current_image = s.copy()
#             self.edit_base_image = s.copy()
#             self.reset_pipeline_params()
#             self.preview_image = None
#             return True
#         return False

#     def get_display_image(self):
#         target = self.preview_image if self.preview_image is not None else self.current_image
#         if target is not None:
#             return cv2.cvtColor(target, cv2.COLOR_BGR2RGB)
#         return None


import cv2
import numpy as np

class ImageModel:
    def __init__(self):
        self.orig_img = None
        self.curr_img = None    # Committed state
        self.preview = None     # Temporary preview
        self.base_img = None    # Snapshot for sliders
        self.filepath = ""
        
        # Slider state
        self.params = {"blur": 0, "bright": 0, "contrast": 0}
        
        self.history = []
        self.redo_list = []

    def load_image(self, path):
        img = cv2.imread(path)
        if img is None:
            return False

        self.filepath = path
        self.orig_img = img
        self.curr_img = img.copy()
        self.base_img = img.copy()
        self.preview = None 
        
        # Reset stacks
        self.history = []
        self.redo_list = []
        self._push_history()
        self.reset_params()
        
        return True

    def save_image(self, path):
        if self.curr_img is None: return False
        
        # Save preview if it exists, otherwise current
        target = self.preview if self.preview is not None else self.curr_img
        cv2.imwrite(path, target)
        return True

    def _push_history(self):
        if self.curr_img is not None:
            self.history.append(self.curr_img.copy())
            if len(self.history) > 20:
                self.history.pop(0)

    # --- Processing Pipeline ---

    def reset_params(self):
        self.params = {"blur": 0, "bright": 0, "contrast": 0}

    def start_edit(self):
        if self.curr_img is not None:
            self.base_img = self.curr_img.copy()

    def update_param(self, key, val):
        self.params[key] = val
        self.run_pipeline()

    def run_pipeline(self):
        if self.base_img is None: return

        img = self.base_img.copy()
        p = self.params

        # Blur
        if p["blur"] > 0:
            k = p["blur"]
            if k % 2 == 0: k += 1
            img = cv2.GaussianBlur(img, (k, k), 0)

        # Brightness
        if p["bright"] != 0:
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            # cv2.add handles the clipping (0-255) automatically
            v = cv2.add(v, p["bright"]) 
            img = cv2.cvtColor(cv2.merge((h, s, v)), cv2.COLOR_HSV2BGR)

        # Contrast
        if p["contrast"] != 0:
            # Formula: alpha * img + beta
            f = 131 * (p["contrast"] + 127) / (127 * (131 - p["contrast"]))
            alpha = f
            gamma = 127 * (1 - f)
            img = cv2.addWeighted(img, alpha, img, 0, gamma)

        self.preview = img

    def commit(self):
        """Finalizes the preview into the main image"""
        if self.preview is not None:
            self._push_history()
            self.curr_img = self.preview.copy()
            self.base_img = self.curr_img.copy()
            self.redo_list.clear()
            self.reset_params()
            self.preview = None

    def revert_original(self):
        if self.orig_img is None: return False
        
        self._push_history()
        self.curr_img = self.orig_img.copy()
        self.base_img = self.orig_img.copy()
        self.reset_params()
        self.preview = None
        self.redo_list.clear()
        return True

    # --- Instant Effects ---

    def apply_gray(self):
        self._push_history()
        gray = cv2.cvtColor(self.curr_img, cv2.COLOR_BGR2GRAY)
        self.curr_img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        self.base_img = self.curr_img.copy()
        self.reset_params()
        self.preview = None

    def apply_edges(self):
        self._push_history()
        edges = cv2.Canny(self.curr_img, 100, 200)
        self.curr_img = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        self.base_img = self.curr_img.copy()
        self.reset_params()
        self.preview = None

    def apply_geo(self, mode, val):
        self._push_history()
        img = self.curr_img
        
        if mode == "rotate":
            code = [cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_180, cv2.ROTATE_90_COUNTERCLOCKWISE]
            img = cv2.rotate(img, code[val])
            
        elif mode == "flip":
            img = cv2.flip(img, val)
            
        elif mode == "resize":
            img = cv2.resize(img, (val[0], val[1]), interpolation=cv2.INTER_AREA)
        
        self.curr_img = img
        self.base_img = self.curr_img.copy()
        self.reset_params()
        self.preview = None

    # --- History ---

    def undo(self):
        if len(self.history) < 2: return False
        
        self.redo_list.append(self.history.pop())
        last = self.history[-1]
        
        self.curr_img = last.copy()
        self.base_img = last.copy()
        self.reset_params()
        self.preview = None
        return True

    def redo(self):
        if not self.redo_list: return False
        
        item = self.redo_list.pop()
        self.history.append(item)
        
        self.curr_img = item.copy()
        self.base_img = item.copy()
        self.reset_params()
        self.preview = None
        return True

    def get_rgb_display(self):
        target = self.preview if self.preview is not None else self.curr_img
        if target is None: return None
        return cv2.cvtColor(target, cv2.COLOR_BGR2RGB)