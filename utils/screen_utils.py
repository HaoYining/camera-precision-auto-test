"""
screen_utils.py - 屏幕截取与OCR识别工具模块

提供屏幕区域截图和文字识别功能，用于读取软件界面上显示的帧数等信息。
"""

import re

import pyautogui
from PIL import Image

try:
    import pytesseract
except ImportError:
    pytesseract = None


def configure_tesseract(tesseract_cmd: str) -> None:
    """配置 Tesseract OCR 引擎路径。"""
    if pytesseract is not None:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


def capture_region(region: dict) -> Image.Image:
    """
    截取屏幕指定区域的图像。

    Args:
        region: 包含 x, y, width, height 的字典，定义截取区域。

    Returns:
        截取的 PIL Image 对象。
    """
    screenshot = pyautogui.screenshot(
        region=(region["x"], region["y"], region["width"], region["height"])
    )
    return screenshot


def recognize_number(image: Image.Image) -> int | None:
    """
    对图像进行 OCR 识别，提取其中的数字。

    Args:
        image: PIL Image 对象。

    Returns:
        识别出的整数，如果无法识别则返回 None。
    """
    if pytesseract is None:
        print("[错误] pytesseract 未安装，无法进行OCR识别。")
        return None

    # 转为灰度图，提高识别率
    gray = image.convert("L")

    # 二值化处理
    threshold = 128
    binary = gray.point(lambda p: 255 if p > threshold else 0)

    # 使用 Tesseract 识别，限定只识别数字
    text = pytesseract.image_to_string(
        binary, config="--psm 7 -c tessedit_char_whitelist=0123456789"
    )

    # 提取纯数字
    digits = re.sub(r"\D", "", text.strip())
    if digits:
        return int(digits)
    return None
