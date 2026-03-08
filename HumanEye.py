import tkinter as tk
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageOps
import os
import time

# =========================
# 1. CONFIGURE YOUR IMAGE
# =========================
IMAGE_PATH = "snellen_chart.png"

WINDOW_W = 1000
WINDOW_H = 800
DISPLAY_W = 600
DISPLAY_H = 700

# =========================
# 2. IMAGE PROCESSING
# =========================
def load_base_image(path):
    if not os.path.exists(path):
        canvas = Image.new("RGB", (DISPLAY_W, DISPLAY_H), "white")
        return canvas
    img = Image.open(path).convert("RGB")
    img = ImageOps.exif_transpose(img)
    img.thumbnail((DISPLAY_W, DISPLAY_H))
    canvas = Image.new("RGB", (DISPLAY_W, DISPLAY_H), "white")
    x = (DISPLAY_W - img.width) // 2
    y = (DISPLAY_H - img.height) // 2
    canvas.paste(img, (x, y))
    return canvas

def make_hyperopia_effect(img):
    blurred = img.filter(ImageFilter.GaussianBlur(radius=6))
    blurred = ImageEnhance.Contrast(blurred).enhance(0.9)
    return blurred

def make_corrected_effect(original, hyperopia):
    corrected = hyperopia.filter(ImageFilter.UnsharpMask(radius=3, percent=250, threshold=1))
    corrected = Image.blend(corrected, original, 0.9)
    corrected = ImageEnhance.Contrast(corrected).enhance(1.05)
    return corrected

# =========================
# 3. BUILD STATES
# =========================
if not os.path.exists(IMAGE_PATH):
    print(f"Warning: {IMAGE_PATH} not found. Using blank chart.")

base_img = load_base_image(IMAGE_PATH)
hyperopia_img = make_hyperopia_effect(base_img)
corrected_img = make_corrected_effect(base_img, hyperopia_img)

states = [
    {
        "tab_text": "Original image",
        "title": "Original image",
        "color": "#1c5ca0",
        "image": base_img,
    },
    {
        "tab_text": "Hyperopia effect",
        "title": "Hyperopia effect",
        "color": "#b43737",
        "image": hyperopia_img,
    },
    {
        "tab_text": "After convex lens correction",
        "title": "After convex lens correction",
        "color": "#238c5a",
        "image": corrected_img,
    },
]

# =========================
# 4. TKINTER APP
# =========================
class EyeReportApp:
    def __init__(self, root):
        self.root = root
        self.root.title(" Hyperopia Correction")
        self.root.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.root.configure(bg="#ffffff")
        self.current_index = 0
        self.animating = False
        
        # Prepare PhotoImages
        self.tk_images = [ImageTk.PhotoImage(s["image"]) for s in states]
        
        self._setup_ui()
        self.render_state(0)

    def _setup_ui(self):
        header_frame = tk.Frame(self.root, bg="white")
        header_frame.pack(pady=(30, 10), fill="x")

        title_container = tk.Frame(header_frame, bg="white")
        title_container.pack()
        
        
        tk.Label(title_container, text="Hyperopia", font=("Arial", 32, "bold"), fg="#b43737", bg="white").pack(side="left")
        tk.Label(title_container, text=" Correction", font=("Arial", 32, "bold"), fg="#333333", bg="white").pack(side="left")

        self.main_card = tk.Frame(self.root, bg="white", bd=0)
        self.main_card.pack(pady=20, padx=50, fill="both", expand=True)

        self.state_header = tk.Frame(self.main_card, height=50)
        self.state_header.pack(fill="x")
        self.state_header.pack_propagate(False)

        self.state_label = tk.Label(self.state_header, text="", font=("Arial", 16, "bold"), fg="white")
        self.state_label.pack(expand=True)

        # Use Canvas instead of Label for overlays/animations
        canvas_bg = tk.Frame(self.main_card, bg="#f8f9fa", bd=1, relief="solid")
        canvas_bg.pack(pady=0, fill="both", expand=True)
        
        self.canvas = tk.Canvas(canvas_bg, width=DISPLAY_W, height=DISPLAY_H, bg="white", highlightthickness=0)
        self.canvas.pack(expand=True, padx=20, pady=20)

        footer_nav = tk.Frame(self.root, bg="#eef5fb", height=60)
        footer_nav.pack(side="bottom", fill="x")
        
        self.indicator_label = tk.Label(footer_nav, text="Input image  →  optical defect  →  convex lens correction  →  improved output", font=("Arial", 18, "bold"), bg="#eef5fb", fg="#333333")
        self.indicator_label.pack(pady=15)

        self.prev_btn = tk.Button(self.root, text="❮", font=("Arial", 20, "bold"), bg="white", fg="#1c5ca0", bd=0, command=self.go_prev, cursor="hand2", activebackground="#f0f0f0")
        self.prev_btn.place(relx=0.05, rely=0.5, anchor="center")

        self.next_btn = tk.Button(self.root, text="❯", font=("Arial", 20, "bold"), bg="white", fg="#1c5ca0", bd=0, command=self.go_next, cursor="hand2", activebackground="#f0f0f0")
        self.next_btn.place(relx=0.95, rely=0.5, anchor="center")

    def render_state(self, index):
        if self.animating: return
        self.current_index = index
        state = states[index]

        self.state_header.config(bg=state["color"])
        self.state_label.config(text=state["tab_text"], bg=state["color"])
        
        # Draw base image
        self.canvas.delete("all")
        self.canvas.create_image(DISPLAY_W//2, DISPLAY_H//2, image=self.tk_images[index], anchor="center")

        # Trigger animation if entering corrected state
        if index == 2:
            self.animate_lens()

    def animate_lens(self):
        self.animating = True
        # Create Lens graphic (one side of glasses)
        # We'll use a semi-transparent looking oval
        lens_id = self.canvas.create_oval(-150, 100, -10, 340, outline="#1c5ca0", width=4, fill="")
        # Simple highlight to make it look like glass
        highlight_id = self.canvas.create_arc(-130, 120, -30, 320, start=120, extent=60, outline="white", width=2, style="arc")
        
        target_x = DISPLAY_W // 2
        current_x = -80
        step = 15
        
        def step_anim():
            nonlocal current_x
            if current_x < target_x:
                self.canvas.move(lens_id, step, 0)
                self.canvas.move(highlight_id, step, 0)
                current_x += step
                self.root.after(10, step_anim)
            else:
                self.animating = False
        
        step_anim()

    def go_next(self):
        self.render_state((self.current_index + 1) % len(states))

    def go_prev(self):
        self.render_state((self.current_index - 1) % len(states))

if __name__ == "__main__":
    root = tk.Tk()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    app = EyeReportApp(root)
    root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    # High DPI support
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    app = EyeReportApp(root)
    root.mainloop()
