import cv2
import numpy as np

class ImageModel:
    def __init__(self):
        #keeping and managing Image data and also processing logic
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
