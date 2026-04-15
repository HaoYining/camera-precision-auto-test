"""
main.py - 相机重复精度自动化测试主程序

使用方式:
    python main.py                  # 正常运行（如需要会自动进入校准）
    python main.py --calibrate      # 强制重新校准
    python main.py --config <path>  # 使用指定的配置文件
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

from calibration.calibration_ui import CalibrationUI, load_positions
from automation.controller import AutomationController
from utils.screen_utils import configure_tesseract


def load_settings(config_path: str = None) -> dict:
    """
    加载测试配置。

    Args:
        config_path: 配置文件路径，默认为 config/settings.json。

    Returns:
        配置字典。
    """
    if config_path is None:
        config_path = os.path.join("config", "settings.json")

    if not os.path.exists(config_path):
        print(f"⚠ 配置文件不存在: {config_path}")
        print("  将使用默认配置。")
        return {}

    with open(config_path, "r", encoding="utf-8") as f:
        settings = json.load(f)

    print(f"✓ 已加载配置文件: {config_path}")
    return settings


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="相机重复精度自动化测试工具"
    )
    parser.add_argument(
        "--calibrate",
        action="store_true",
        help="强制重新校准按钮和区域位置",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="指定配置文件路径（默认: config/settings.json）",
    )
    parser.add_argument(
        "--base-path",
        type=str,
        default=None,
        help="覆盖配置中的基础储存路径",
    )
    parser.add_argument(
        "--groups",
        type=int,
        default=None,
        help="覆盖配置中的总组数",
    )
    return parser.parse_args()


def main() -> None:
    """主程序入口。"""
    args = parse_args()

    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║       相机重复精度自动化测试工具 v1.0   create by 郝yining ║")
    print("║       Camera Precision Auto-Test                        ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print(f"  启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 加载配置
    settings = load_settings(args.config)

    # 命令行参数覆盖配置
    if args.base_path:
        settings["base_path"] = args.base_path
    if args.groups:
        settings["total_groups"] = args.groups

    # 配置 Tesseract
    tesseract_cmd = settings.get("tesseract_cmd")
    if tesseract_cmd:
        configure_tesseract(tesseract_cmd)

    # 加载或执行校准
    positions = None
    if not args.calibrate:
        positions = load_positions()
        if positions:
            print("✓ 已加载保存的校准位置。")
            print("  提示: 如需重新校准，请使用 --calibrate 参数。")

    if positions is None or args.calibrate:
        print("\n📌 需要进行校准，请按提示操作：")
        print("   1. 确保相机软件和采集软件窗口已打开并就位")
        print("   2. 各窗口位置保持不动")
        print("   3. 按照提示依次标定各按钮位置和帧数区域\n")
        input("   准备好后按 Enter 开始校准...")

        calibrator = CalibrationUI()
        positions = calibrator.run()

    # 验证校准数据完整性
    required_keys = [
        "start_record",
        "stop_record",
        "error_close",
        "storage_path",
        "trigger_capture",
        "frame_count_region",
    ]
    missing = [k for k in required_keys if k not in positions]
    if missing:
        print(f"\n❌ 校准数据不完整，缺少: {', '.join(missing)}")
        print("   请重新运行程序并使用 --calibrate 参数。")
        sys.exit(1)

    # 确认开始
    print("\n" + "─" * 60)
    print("  所有准备工作完成，即将开始自动化测试。")
    print(f"  基础路径: {settings.get('base_path', '未设置')}")
    print(f"  总组数: {settings.get('total_groups', 30)}")
    print(f"  期望帧数: {settings.get('expected_frames', 54)}")
    print("─" * 60)
    print()
    print("⚠ 注意:")
    print("  - 测试过程中请不要移动鼠标或操作键盘")
    print("  - 如需紧急停止，请将鼠标快速移到屏幕左上角")
    print()
    input("  确认无误后按 Enter 开始测试...")

    # 运行自动化测试
    controller = AutomationController(positions, settings)
    try:
        controller.run()
    except KeyboardInterrupt:
        print("\n🛑 已收到中断请求，测试已停止。")

    print("\n程序结束。")


if __name__ == "__main__":
    main()