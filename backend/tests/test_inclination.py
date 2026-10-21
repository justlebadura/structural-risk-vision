"""Pruebas de la inclinación aparente con Canny + Hough."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from services import inclination  # noqa: E402


def _image_with_line(p1: tuple[int, int], p2: tuple[int, int]) -> np.ndarray:
    image = np.full((400, 400, 3), 255, dtype=np.uint8)
    import cv2

    cv2.line(image, p1, p2, (0, 0, 0), 4)
    return image


class InclinationTests(unittest.TestCase):
    def test_vertical_column(self) -> None:
        result = inclination.detect_element_inclination(
            _image_with_line((200, 40), (200, 360)), element="columna"
        )
        self.assertTrue(result["detected"])
        self.assertEqual(result["reference"], "vertical")
        self.assertLess(abs(result["tilt_deg"]), 2.0)
        self.assertTrue(result["reliable"])

    def test_column_tilted_about_ten_degrees(self) -> None:
        result = inclination.detect_element_inclination(
            _image_with_line((170, 40), (230, 360)), element="columna"
        )
        self.assertTrue(result["detected"])
        self.assertEqual(result["reference"], "vertical")
        self.assertAlmostEqual(result["tilt_deg"], 10.9, delta=2.0)
        self.assertNotEqual(result["tilt_signed_deg"], 0.0)

    def test_horizontal_beam(self) -> None:
        result = inclination.detect_element_inclination(
            _image_with_line((40, 200), (360, 200)), element="viga"
        )
        self.assertTrue(result["detected"])
        self.assertEqual(result["reference"], "horizontal")
        self.assertLess(abs(result["tilt_deg"]), 2.0)

    def test_blank_image_is_not_detected(self) -> None:
        image = np.full((400, 400, 3), 255, dtype=np.uint8)
        result = inclination.detect_element_inclination(image, element="muro")
        self.assertFalse(result["detected"])
        self.assertIsNone(result["tilt_deg"])
        self.assertEqual(result["lines_count"], 0)


if __name__ == "__main__":
    unittest.main()
