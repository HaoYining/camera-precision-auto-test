"""
calibration_ui.py - 交互式校准界面模块

提供图形化界面让用户通过鼠标点击和框选来标定软件中各按钮和区域的位置。
标定结果保存到 config/positions.json 供自动化流程使用。
"""

import json
import os
import sys
import tkinter as tk
from tkinter import messagebox

import pyautogui


class CalibrationUI:
    """
    交互式校准工具。

    引导用户依次：
    1. 点击"开始录制"按钮位置
    2. 点击"结束录制"按钮位置
    3. 点击"储存路径输入框"位置
    4. 点击"触发采集"按钮位置
    5. 框选"录制帧数显示区域"

    所有位置信息保存到 config/positions.json。
    """

    CLICK_TARGETS = [
        ("start_record", "开始录制按钮"),
        ("stop_record", "结束录制按钮"),
        ("storage_path", "储存路径输入框"),
        ("trigger_capture", "触发采集按钮"),
    ]

    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.positions: dict = {}
        self.root: tk.Tk | None = None
        self._region_start: tuple | None = None
        self._overlay: tk.Toplevel | None = None
        self._canvas: tk.Canvas | None = None

    def run(self) -> dict:
        """执行完整的校准流程，返回标定结果。"""
        print("=" * 60)
        print("  交互式校准工具 - 标定各按钮和区域位置")
        print("=" * 60)
        print()

        # 步骤1-4：依次点击各按钮位置
        for key, name in self.CLICK_TARGETS:
            self._calibrate_click_position(key, name)

        # 步骤5：框选帧数显示区域
        self._calibrate_frame_region()

        # 保存结果
        self._save_positions()

        print()
        print("=" * 60)
        print("  校准完成！所有位置已保存。")
        print("=" * 60)

        return self.positions

    def _calibrate_click_position(self, key: str, name: str) -> None:
        """引导用户点击一个按钮位置并记录坐标。"""
        print(f"\n>>> 请将鼠标移动到【{name}】的位置，然后按 Enter 键确认...")
        input(f"    （移动鼠标到 [{name}] 后按 Enter）")

        x, y = pyautogui.position()
        self.positions[key] = {"x": x, "y": y}
        print(f"    ✓ 已记录 [{name}] 位置: ({x}, {y})")

    def _calibrate_frame_region(self) -> None:
        """引导用户通过鼠标拖拽框选帧数显示区域。"""
        print("\n>>> 接下来请框选【录制帧数显示区域】")
        print("    将弹出一个半透明窗口覆盖整个屏幕，")
        print("    请用鼠标拖拽选择帧数显示的区域。")
        input("    准备好后按 Enter 开始框选...")

        self.root = tk.Tk()
        self.root.withdraw()

        # 创建全屏半透明覆盖层
        self._overlay = tk.Toplevel(self.root)
        self._overlay.attributes("-fullscreen", True)
        self._overlay.attributes("-alpha", 0.3)
        self._overlay.attributes("-topmost", True)
        self._overlay.configure(bg="gray")

        self._canvas = tk.Canvas(
            self._overlay, cursor="cross", bg="gray", highlightthickness=0
        )
        self._canvas.pack(fill=tk.BOTH, expand=True)

        self._rect_id = None
        self._canvas.bind("<ButtonPress-1>", self._on_region_press)
        self._canvas.bind("<B1-Motion>", self._on_region_drag)
        self._canvas.bind("<ButtonRelease-1>", self._on_region_release)

        # 在覆盖层上显示提示
        screen_w = self._overlay.winfo_screenwidth()
        self._canvas.create_text(
            screen_w // 2,
            30,
            text="请拖拽鼠标框选【录制帧数显示区域】，松开鼠标完成选择",
            fill="white",
            font=("Microsoft YaHei", 16, "bold"),
        )

        self.root.mainloop()

    def _on_region_press(self, event: tk.Event) -> None:
        """鼠标按下时记录起始坐标。"""
        self._region_start = (event.x, event.y)

    def _on_region_drag(self, event: tk.Event) -> None:
        """鼠标拖拽时绘制选区矩形。"""
        if self._region_start is None:
            return
        if self._rect_id is not None:
            self._canvas.delete(self._rect_id)
        x0, y0 = self._region_start
        self._rect_id = self._canvas.create_rectangle(
            x0, y0, event.x, event.y, outline="red", width=2
        )

    def _on_region_release(self, event: tk.Event) -> None:
        """鼠标释放时确认选区并保存。"""
        if self._region_start is None:
            return

        x0, y0 = self._region_start
        x1, y1 = event.x, event.y

        # 确保坐标正确排序
        left = min(x0, x1)
        top = min(y0, y1)
        right = max(x0, x1)
        bottom = max(y0, y1)

        width = right - left
        height = bottom - top

        if width < 5 or height < 5:
            print("    ⚠ 选区太小，请重新框选。")
            self._region_start = None
            return

        self.positions["frame_count_region"] = {
            "x": left,
            "y": top,
            "width": width,
            "height": height,
        }
        print(
            f"    ✓ 已记录 [录制帧数区域]: "
            f"({left}, {top}, {width}x{height})"
        )

        # 关闭覆盖层
        if self._overlay is not None:
            self._overlay.destroy()
        if self.root is not None:
            self.root.quit()
            self.root.destroy()
            self.root = None

    def _save_positions(self) -> None:
        """将标定结果保存到 JSON 文件。"""
        os.makedirs(self.config_dir, exist_ok=True)
        filepath = os.path.join(self.config_dir, "positions.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.positions, f, ensure_ascii=False, indent=4)
        print(f"\n    ✓ 位置信息已保存到: {filepath}")


def load_positions(config_dir: str = "config") -> dict | None:
    """
    从 config/positions.json 加载已保存的标定位置。

    Returns:
        标定位置字典，如果文件不存在则返回 None。
    """
    filepath = os.path.join(config_dir, "positions.json")
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
