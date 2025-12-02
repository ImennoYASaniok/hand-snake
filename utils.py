"""
utils.py - модуль дополнительных утилит для упрощения работы с различными объектами

Содержит функции для преобразование цвета, обработку нажатий клавиш через cv2
"""

import cv2

# -------------------------------
# Цветовые утилиты
# -------------------------------

def hex_to_bgr(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (b, g, r)

HEX_COLOR_BASE = "#c6edbe"
BGR_COLOR_BASE = hex_to_bgr(HEX_COLOR_BASE)
HEX_COLOR_BACK = "#A1A1A1"
BGR_COLOR_BACK = hex_to_bgr(HEX_COLOR_BACK)

# -------------------------------
# Утилита для работы с клавишами
# -------------------------------

RANGE_DIGITS = [48, 58]
RANGE_CAPITAL_LETTERS = [65, 91]
RANGE_UPPERCASE_LETTERS = [97, 123]
key_codes = {
    "esc": 27,
    "enter": 13,
    "back_space": 8,
    "tab": 9,
    "space": 32,
    "delete": 27,
    "up": [82, 2490368],
    "down": [84, 2621440],
    "left": [81, 2424832],
    "right": [83, 2555904],
    **{chr(i): i for i in range(*RANGE_DIGITS)}, # 0–9
    **{chr(i): i for i in range(*RANGE_CAPITAL_LETTERS)}, # A–Z
    **{chr(i): i for i in range(*RANGE_UPPERCASE_LETTERS)}, # a–z
}


def check_in_range(val: int, range: [int, int]) -> bool:
    return range[0] <= val <= range[1]


def key_code_to_sym(key_code: int) -> str:
    if check_in_range(key_code, RANGE_DIGITS) or check_in_range(key_code, RANGE_CAPITAL_LETTERS) or check_in_range(key_code, RANGE_UPPERCASE_LETTERS):
        return key_codes[key_code]
    else:
        raise KeyError("Ошибка: Не существует символа с таким кодом")


def check_press_button(key: str, type_detect: str = "") -> bool:
    if key in key_codes:
        detect_key =  cv2.waitKey(1)

        val = key_codes[key]
        if type(val) == list:
            return detect_key in val
        else:
            if type_detect == "same":
                detect_key = key_code_to_sym(detect_key)
                detect_key = detect_key.lower()
                return detect_key == key
            else:
                return detect_key == val
    else:
        raise KeyError(f"Ошибка: обработчик не знает клавиши {key}")