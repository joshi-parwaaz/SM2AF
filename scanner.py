import cv2
import numpy as np

def enhance_scanned_image(input_path, output_path="scanned_output.png"):
    img = cv2.imread(input_path)
    orig = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blur, 75, 200)

    # Find contours
    contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            doc_cnt = approx
            break
    else:
        print("⚠️ Document edges not found, using original image.")
        doc_cnt = np.array([[[0,0]], [[img.shape[1],0]], [[img.shape[1], img.shape[0]]], [[0, img.shape[0]]]])

    # Reorder points and apply perspective transform
    def reorder(pts):
        pts = pts.reshape(4, 2)
        new_pts = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)
        new_pts[0] = pts[np.argmin(s)]
        new_pts[2] = pts[np.argmax(s)]
        new_pts[1] = pts[np.argmin(diff)]
        new_pts[3] = pts[np.argmax(diff)]
        return new_pts

    pts1 = reorder(doc_cnt)
    (tl, tr, br, bl) = pts1
    width = max(np.linalg.norm(br - bl), np.linalg.norm(tr - tl))
    height = max(np.linalg.norm(tr - br), np.linalg.norm(tl - bl))

    pts2 = np.array([[0,0], [width-1,0], [width-1,height-1], [0,height-1]], dtype="float32")
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    scanned = cv2.warpPerspective(orig, matrix, (int(width), int(height)))

    # Convert to grayscale and apply adaptive threshold for whitening
    scanned_gray = cv2.cvtColor(scanned, cv2.COLOR_BGR2GRAY)
    scanned_clean = cv2.adaptiveThreshold(scanned_gray, 255,
                                          cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 11, 10)

    cv2.imwrite(output_path, scanned_clean)
    print(f"✅ Scanned image saved as {output_path}")
    return output_path
