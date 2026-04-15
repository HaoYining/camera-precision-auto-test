import os
import re
from pathlib import Path

def rename_tiff_files_recursive():
    """递归遍历目录结构，重命名所有TIFF文件"""
    current_dir = Path.cwd()
    
    # 遍历当前目录下的所有文件夹（曝光时间文件夹）
    for exposure_folder in current_dir.iterdir():
        if not exposure_folder.is_dir():
            continue
            
        # 跳过隐藏文件夹
        if exposure_folder.name.startswith('.'):
            continue
            
        print(f"\n处理曝光时间文件夹: {exposure_folder.name}")
        
        # 遍历曝光时间文件夹下的所有数字文件夹 (1-30)
        for folder_num in range(1, 31):
            folder_path = exposure_folder / str(folder_num)
            
            if not folder_path.exists() or not folder_path.is_dir():
                print(f"  ✓ 文件夹 {exposure_folder.name}/{folder_num} 不存在，跳过")
                continue
                
            print(f"  ✓ 处理文件夹: {exposure_folder.name}/{folder_num}")
            
            # 获取文件夹中的所有tiff文件
            tiff_files = list(folder_path.glob("*.tiff"))
            
            if not tiff_files:
                print(f"    无TIFF文件")
                continue
                
            # 提取最后4位数字并排序
            files_to_rename = []
            for file_path in tiff_files:
                stem = file_path.stem
                match = re.search(r'_(\d{4})$', stem)
                if match:
                    num = int(match.group(1))
                    files_to_rename.append((num, file_path))
            
            if not files_to_rename:
                print(f"    没有符合命名规则的文件")
                continue
            
            # 按数字排序
            files_to_rename.sort(key=lambda x: x[0])
            
            # 重命名
            renamed_count = 0
            for idx, (_, file_path) in enumerate(files_to_rename):
                new_name = f"cam1_proj0_exp0_{idx}.tiff"
                new_path = file_path.parent / new_name
                try:
                    file_path.rename(new_path)
                    renamed_count += 1
                except Exception as e:
                    print(f"    错误: 无法重命名 {file_path.name}: {e}")
            
            print(f"    已重命名 {renamed_count} 个文件")
            
            # 显示前几个文件的重命名示例
            if renamed_count > 0 and folder_num <= 3:  # 只显示前3个文件夹的示例
                sample_files = list(folder_path.glob("cam1_proj0_exp0_*.tiff"))
                sample_files.sort(key=lambda x: int(x.stem.split('_')[-1]))
                if len(sample_files) > 3:
                    print(f"    示例: {sample_files[0].name}, {sample_files[1].name}, {sample_files[2].name}...")

def main():
    """主函数"""
    print("=" * 60)
    print("TIFF文件批量重命名工具 (递归版本)")
    print("=" * 60)
    print("目录结构要求:")
    print("当前目录/")
    print("├── 曝光时间文件夹1/ (如: 8ms/)")
    print("│   ├── 1/ (包含TIFF文件)")
    print("│   ├── 2/")
    print("│   └── ... 30/")
    print("├── 曝光时间文件夹2/ (如: 12ms/)")
    print("└── ...")
    print("=" * 60)
    
    # 确认操作
    response = input("\n请确认已备份重要文件！是否继续？(yes/no): ").strip().lower()
    if response not in ['yes', 'y', '是', '确认']:
        print("操作已取消")
        return
    
    try:
        rename_tiff_files_recursive()
        print("\n" + "=" * 60)
        print("所有文件重命名完成！")
        print("=" * 60)
    except Exception as e:
        print(f"\n发生错误: {e}")

# 直接运行
if __name__ == "__main__":
    main()