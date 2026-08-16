"""
Image preprocessing pipeline for document scans.

Applies a sequence of OpenCV operations to improve OCR accuracy:
  1. deskew   — corrects document tilt via Hough line detection
  2. crop     — detects the largest rectangular contour and applies a perspective warp
  3. denoise  — reduces noise using Non-Local Means denoising

Each function is intentionally kept minimal for the scaffold phase.
TODO markers indicate where parameters should be tuned when real document
data is available.
"""

from __future__ import annotations

import cv2
import numpy as np


def _to_grayscale(image: np.ndarray) -> np.ndarray:
    """Convert BGR image to grayscale if it isn't already."""
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image


def deskew(image: np.ndarray) -> np.ndarray:
    """
    Detect and correct document skew using Hough line transform.

    The algorithm:
    1. Converts to grayscale and applies Canny edge detection.
    2. Detects dominant lines via probabilistic Hough transform.
    3. Computes the median line angle and rotates the image to compensate.

    # TODO: tune Canny thresholds and Hough parameters against real scan data.

    Args:
        image: Input image (BGR or grayscale, uint8).

    Returns:
        Deskewed image with same dimensions as input.
    """
    gray = _to_grayscale(image)

    # TODO: tune Canny thresholds (currently: 50, 150)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # TODO: tune Hough parameters (rho, theta, threshold, minLineLength, maxLineGap)
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=80,
        minLineLength=100,
        maxLineGap=10,
    )

    if lines is None:
        return image  # No lines detected; return as-is

    angles: list[float] = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        # Only consider near-horizontal lines (±30°)
        if -30 < angle < 30:
            angles.append(angle)

    if not angles:
        return image

    median_angle = float(np.median(angles))

    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
    deskewed = cv2.warpAffine(
        image,
        rotation_matrix,
        (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,
    )
    return deskewed


def crop_document(image: np.ndarray) -> np.ndarray:
    """
    Detect the largest rectangular document contour and apply a perspective warp.

    Falls back to the original image if no suitable quadrilateral is found.

    # TODO: tune contour area threshold and approximation epsilon for real scans.

    Args:
        image: Input image (BGR or grayscale, uint8).

    Returns:
        Cropped and perspective-corrected image, or original if crop fails.
    """
    gray = _to_grayscale(image)

    # TODO: tune blur kernel size and Canny thresholds
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 30, 120)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return image

    largest = max(contours, key=cv2.contourArea)
    image_area = image.shape[0] * image.shape[1]

    # TODO: tune minimum area ratio (currently 10% of image)
    if cv2.contourArea(largest) < 0.10 * image_area:
        return image

    # Approximate the contour to a polygon
    peri = cv2.arcLength(largest, True)
    approx = cv2.approxPolyDP(largest, 0.02 * peri, True)

    if len(approx) != 4:
        return image  # Not a clean quadrilateral; skip crop

    # Order points: top-left, top-right, bottom-right, bottom-left
    pts = approx.reshape(4, 2).astype("float32")
    rect = _order_points(pts)
    warped = _four_point_transform(image, rect)
    return warped


def denoise(image: np.ndarray) -> np.ndarray:
    """
    Apply Non-Local Means denoising to reduce scan noise.

    # TODO: tune h (filter strength) against real scan data.
        Higher h removes more noise but can blur text edges.

    Args:
        image: Input image (BGR or grayscale, uint8).

    Returns:
        Denoised image.
    """
    if len(image.shape) == 3:
        # TODO: tune h=10, hColor=10, templateWindowSize=7, searchWindowSize=21
        return cv2.fastNlMeansDenoisingColored(
            image, None, h=10, hColor=10, templateWindowSize=7, searchWindowSize=21
        )
    else:
        # TODO: tune h=10, templateWindowSize=7, searchWindowSize=21
        return cv2.fastNlMeansDenoising(
            image, None, h=10, templateWindowSize=7, searchWindowSize=21
        )


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Full preprocessing pipeline: decode → deskew → crop → denoise.

    This is the primary entry point called by the extraction module.

    Args:
        image_bytes: Raw bytes of the uploaded image file.

    Returns:
        Preprocessed image as a numpy array (BGR, uint8), ready for OCR.

    Raises:
        ValueError: If the bytes cannot be decoded as a valid image.
    """
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Could not decode image — unsupported format or corrupted file.")

    image = deskew(image)
    image = crop_document(image)
    image = denoise(image)

    return image


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def _order_points(pts: np.ndarray) -> np.ndarray:
    """Order four corner points as: top-left, top-right, bottom-right, bottom-left."""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]    # top-left  (smallest sum)
    rect[2] = pts[np.argmax(s)]    # bottom-right (largest sum)
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)] # top-right  (smallest diff)
    rect[3] = pts[np.argmax(diff)] # bottom-left (largest diff)
    return rect


def _four_point_transform(image: np.ndarray, rect: np.ndarray) -> np.ndarray:
    """Apply a perspective warp using four ordered corner points."""
    (tl, tr, br, bl) = rect

    width_a = np.linalg.norm(br - bl)
    width_b = np.linalg.norm(tr - tl)
    max_width = max(int(width_a), int(width_b))

    height_a = np.linalg.norm(tr - br)
    height_b = np.linalg.norm(tl - bl)
    max_height = max(int(height_a), int(height_b))

    dst = np.array(
        [[0, 0], [max_width - 1, 0], [max_width - 1, max_height - 1], [0, max_height - 1]],
        dtype="float32",
    )

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (max_width, max_height))
    return warped
