from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    print("未检测到 Pillow 库，请先安装：pip install pillow")
    raise SystemExit(1)


SUPPORTED_EXTENSIONS = {
    ".tif",
    ".tiff",
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".webp",
}


def mirror_images_recursive(source_dir: Path, target_dir: Path):
    """递归遍历源目录，左右镜像翻转所有图片并保存到目标目录（不覆盖原图）"""
    processed_count = 0
    failed_count = 0

    for file_path in source_dir.rglob("*"):
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        # 跳过隐藏目录中的文件
        if any(part.startswith(".") for part in file_path.parts):
            continue

        try:
            relative_path = file_path.relative_to(source_dir)
            output_path = target_dir / relative_path
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with Image.open(file_path) as img:
                mirrored = ImageOps.mirror(img)
                mirrored.save(output_path)
            processed_count += 1
            print(f"✓ 已翻转: {relative_path}")
        except Exception as e:
            failed_count += 1
            print(f"✗ 处理失败: {file_path.relative_to(source_dir)} | 错误: {e}")

    return processed_count, failed_count


def main():
    """主函数"""
    source_dir = Path.cwd()
    target_dir = source_dir.parent / f"{source_dir.name}_flipped"

    print("=" * 60)
    print("图片批量左右镜像翻转工具 (递归版本)")
    print("=" * 60)
    print("目录结构要求:")
    print("当前目录/")
    print("├── 曝光时间文件夹1/ (如: 8ms/)")
    print("│   ├── 1/ (包含图片文件)")
    print("│   ├── 2/")
    print("│   └── ... 30/")
    print("├── 曝光时间文件夹2/ (如: 12ms/)")
    print("└── ...")
    print("=" * 60)
    print(f"源目录: {source_dir}")
    print(f"目标目录: {target_dir}")
    print(f"支持格式: {', '.join(sorted(SUPPORTED_EXTENSIONS))}")
    print("说明: 原图不变，翻转结果会按原目录结构另存到目标目录")

    # 确认操作
    response = input("\n确认开始处理？(yes/no): ").strip().lower()
    if response not in ["yes", "y", "是", "确认"]:
        print("操作已取消")
        return

    try:
        processed_count, failed_count = mirror_images_recursive(source_dir, target_dir)
        print("\n" + "=" * 60)
        print(f"处理完成！成功: {processed_count}，失败: {failed_count}")
        print(f"输出目录: {target_dir}")
        print("=" * 60)
    except Exception as e:
        print(f"\n发生错误: {e}")


if __name__ == "__main__":
    main()
