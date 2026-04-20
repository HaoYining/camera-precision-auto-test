"""
controller.py - 自动化测试控制器

实现重复精度测试的完整自动化流程：
1. 设置储存路径
2. 开始录制
3. 触发采集
4. 等待录制完成
5. OCR识别帧数
6. 验证结果（帧数 == 54 为合格）
7. 不合格则清除数据并重试
8. 合格则进入下一组
9. 共采集30组合格数据
"""

import os
import shutil
import time

import pyautogui
import keyboard

from utils.screen_utils import capture_region, recognize_number

# 禁用 pyautogui 的安全暂停（可按需调整）
pyautogui.PAUSE = 0.3
pyautogui.FAILSAFE = True  # 鼠标移到左上角可紧急停止


class AutomationController:
    """
    自动化测试控制器。

    根据校准的按钮位置和配置参数，自动执行重复精度测试的
    30组数据采集流程。
    """

    # 剪贴板操作超时时间（秒）
    CLIPBOARD_TIMEOUT = 5

    def __init__(self, positions: dict, settings: dict):
        """
        初始化控制器。

        Args:
            positions: 校准的按钮/区域位置字典。
            settings: 测试参数配置字典。

        Raises:
            ValueError: 如果 base_path 未在配置中设置。
        """
        self.positions = positions
        self.settings = settings

        if "base_path" not in settings or not settings["base_path"]:
            raise ValueError(
                "base_path 未设置，请在 config/settings.json 中配置基础储存路径"
            )
        self.base_path: str = settings["base_path"]
        self.total_groups: int = settings.get("total_groups", 30)
        self.expected_frames: int = settings.get("expected_frames", 54)
        self.wait_after_trigger: float = settings.get("wait_after_trigger", 7)
        self.wait_after_click: float = settings.get("wait_after_click", 0.5)
        self.retry_wait: float = settings.get("retry_wait", 1.0)

    def run(self) -> None:
        """执行完整的自动化测试流程。"""
        print()
        print("=" * 60)
        print("  开始自动化重复精度测试")
        print(f"  基础路径: {self.base_path}")
        print(f"  总组数: {self.total_groups}")
        print(f"  期望帧数: {self.expected_frames}")
        print("=" * 60)
        print()
        print("⚠ 提示: 将鼠标移到屏幕左上角可紧急停止程序（PyAutoGUI FailSafe）")
        print("⚠ 提示: 运行过程中按 Esc 可中断并退出程序")
        print()

        group = 1
        while group <= self.total_groups:
            self._check_for_interrupt()
            success = self._run_single_group(group)
            if success:
                print(f"\n{'─' * 40}")
                group += 1
            else:
                print(f"  ⟳ 第 {group} 组将重试...\n")
                self._sleep_with_interrupt(self.retry_wait)

        print()
        print("=" * 60)
        print(f"  ✅ 全部 {self.total_groups} 组合格数据采集完成！")
        print("=" * 60)

    def _run_single_group(self, group_number: int) -> bool:
        """
        执行单组数据采集流程。

        Args:
            group_number: 当前组号（1-based）。

        Returns:
            True 表示本组合格，False 表示需要重试。
        """
        group_path = os.path.join(self.base_path, str(group_number))
        print(f"📋 第 {group_number}/{self.total_groups} 组")
        print(f"   储存路径: {group_path}")

        # 步骤1: 设置储存路径
        print("   [1/4] 设置储存路径...")
        self._check_for_interrupt()
        self._set_storage_path(group_path)
        self._sleep_with_interrupt(self.wait_after_click)

        # 步骤2: 点击开始录制
        print("   [2/4] 点击开始录制...")
        self._check_for_interrupt()
        self._click_position("start_record")
        self._sleep_with_interrupt(self.wait_after_click)

        # 步骤3: 点击触发采集
        print("   [3/4] 点击触发采集...")
        self._check_for_interrupt()
        self._click_position("trigger_capture")

        # 步骤4: 等待录制完成
        print(
            f"   [4/4] 等待录制完成（{self.wait_after_trigger}秒）...",
            end="",
            flush=True,
        )
        self._sleep_with_interrupt(self.wait_after_trigger)
        print(" 完成")

        # 步骤5: 识别帧数（需在停止录制前读取，避免界面刷新导致识别不到）
        print("   识别录制帧数...", end=" ", flush=True)
        frame_count = self._read_frame_count()
        print(f"识别结果: {frame_count}")

        try:
            # 步骤6: 验证帧数
            if frame_count == self.expected_frames:
                print(f"   ✅ 第 {group_number} 组合格！帧数 = {frame_count}")
                return True
            else:
                print(
                    f"   ❌ 第 {group_number} 组不合格！"
                    f"帧数 = {frame_count}，期望 = {self.expected_frames}"
                )
                self._dismiss_popup()
                self._cleanup_group_data(group_path)
                return False
        finally:
            # 无论本轮结果如何，都点击结束录制，确保每轮录制被正确关闭
            print("   点击结束录制...")
            self._check_for_interrupt()
            self._click_position("stop_record")
            self._sleep_with_interrupt(self.wait_after_click)

    def _click_position(self, key: str) -> None:
        """
        点击指定的标定位置。

        Args:
            key: 位置标识键名（如 'start_record'）。
        """
        pos = self.positions[key]
        pyautogui.click(pos["x"], pos["y"])

    def _set_storage_path(self, path: str) -> None:
        """
        设置储存路径：点击路径输入框，全选内容，删除，输入新路径。

        Args:
            path: 新的储存路径字符串。
        """
        # 点击储存路径输入框
        self._click_position("storage_path")
        time.sleep(0.3)

        # Ctrl+A 全选
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.1)

        # Delete 删除
        pyautogui.press("delete")
        time.sleep(0.1)

        # 输入新路径（使用 pyperclip 和粘贴方式避免中文输入法问题）
        self._type_path(path)
        time.sleep(0.2)

    def _type_path(self, path: str) -> None:
        """
        通过剪贴板粘贴方式输入路径。

        直接使用 pyautogui.typewrite 无法输入中文路径，
        因此使用剪贴板复制粘贴方式。

        Args:
            path: 要输入的路径字符串。
        """
        import subprocess

        # 使用 PowerShell 将文本写入剪贴板（Windows 环境）
        try:
            process = subprocess.Popen(
                ["powershell", "-command", f'Set-Clipboard -Value "{path}"'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            process.wait(timeout=self.CLIPBOARD_TIMEOUT)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # 回退：尝试使用 pyperclip
            try:
                import pyperclip

                pyperclip.copy(path)
            except ImportError:
                # 最后回退：直接用 typewrite（不支持中文）
                pyautogui.typewrite(path, interval=0.02)
                return

        # Ctrl+V 粘贴
        pyautogui.hotkey("ctrl", "v")

    def _read_frame_count(self) -> int | None:
        """
        读取帧数显示区域的帧数值。

        Returns:
            识别出的帧数整数，无法识别返回 None。
        """
        region = self.positions.get("frame_count_region")
        if region is None:
            print("   ⚠ 未找到帧数显示区域的标定信息！")
            return None

        image = capture_region(region)
        frame_count = recognize_number(image)
        return frame_count

    def _dismiss_popup(self) -> None:
        """点击报错弹窗的 Close 按钮。"""
        if "error_close" not in self.positions:
            print("   ⚠ 未标定报错 Close 按钮，跳过点击。")
            return
        self._check_for_interrupt()
        self._click_position("error_close")
        self._sleep_with_interrupt(self.wait_after_click)

    def _check_for_interrupt(self) -> None:
        """检测 Esc 按键中断请求。"""
        if keyboard.is_pressed("esc"):
            print("\n🛑 检测到 Esc 中断，程序即将退出。")
            raise KeyboardInterrupt

    def _sleep_with_interrupt(self, duration: float, step: float = 0.1) -> None:
        """
        可响应 Esc 中断的 sleep。

        Args:
            duration: 总等待时长（秒）。
            step: 每次检查中断的步长（秒）。
        """
        end_time = time.time() + max(0.0, duration)
        while time.time() < end_time:
            self._check_for_interrupt()
            time.sleep(min(step, end_time - time.time()))

    def _cleanup_group_data(self, group_path: str) -> None:
        """
        清理不合格组的已采集数据。

        Args:
            group_path: 要清理的组数据文件夹路径。
        """
        if os.path.exists(group_path):
            try:
                shutil.rmtree(group_path)
                print(f"   🗑 已删除不合格数据: {group_path}")
            except OSError as e:
                print(f"   ⚠ 删除失败: {e}")
        else:
            print(f"   ℹ 路径不存在，无需清理: {group_path}")

