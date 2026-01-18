import cv2
import os

# -------- CONFIG --------
IMAGE_FOLDER = "hand"
VALID_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")

# -------- LOAD IMAGES --------
image_files = sorted([
    f for f in os.listdir(IMAGE_FOLDER)
    if f.lower().endswith(VALID_EXTENSIONS)
])

if not image_files:
    raise FileNotFoundError("No images found in 'hand' folder")

current_index = 0
img = None

# -------- MOUSE CALLBACK --------
def click_event(event, x, y, flags, param):
    global img
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"[{image_files[current_index]}] -> X: {x}, Y: {y}")
        # Draw a small dot where clicked
        cv2.circle(img, (x, y), 4, (0, 0, 255, 255), -1)
        cv2.imshow("Image Viewer", img)

# -------- LOAD IMAGE FUNCTION --------
def load_image(index):
    global img
    path = os.path.join(IMAGE_FOLDER, image_files[index])
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)

    if img is None:
        raise ValueError(f"Could not load {image_files[index]}")

    h, w = img.shape[:2]
    print(f"\nViewing: {image_files[index]} | Size: {w}x{h}")

    cv2.imshow("Image Viewer", img)

# -------- MAIN --------
cv2.namedWindow("Image Viewer", cv2.WINDOW_NORMAL)
cv2.setMouseCallback("Image Viewer", click_event)

load_image(current_index)

print("\nControls:")
print("  Left Click  -> Get coordinate")
print("  N           -> Next image")
print("  P           -> Previous image")
print("  ESC         -> Exit")

while True:
    key = cv2.waitKey(0)

    if key == 27:  # ESC
        break

    elif key in [ord('n'), ord('N')]:
        current_index = (current_index + 1) % len(image_files)
        load_image(current_index)

    elif key in [ord('p'), ord('P')]:
        current_index = (current_index - 1) % len(image_files)
        load_image(current_index)

cv2.destroyAllWindows()
