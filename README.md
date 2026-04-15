# 相机重复精度自动化测试工具

Camera Precision Auto-Test —— 基于模拟点击与 OCR 识别的单目相机重复精度自动化采集系统。

## 项目简介

本工具用于自动化完成相机重复精度测试中的数据采集流程。在不同曝光时间下，以相同帧率采集录制多组投影照片（单目相机），通过模拟鼠标点击和键盘输入来控制相机软件和采集触发软件的界面，实现全自动采集 30 组合格数据集的目标。

**核心功能：**
- 交互式校准：引导用户标定软件界面中各按钮和区域的位置
- 自动路径管理：自动设置每组数据的储存路径
- 自动采集控制：模拟点击完成录制启动和触发采集
- OCR 帧数识别：自动截取屏幕区域并识别录制帧数
- 质量验证与重试：帧数不符时点击弹窗 `Close` 并清除数据重试
- 每轮强制收尾：每一组无论成功与否都会点击一次“结束录制”
- Esc 中断：运行中按 `Esc` 可立即中断程序
- 30 组数据自动循环：直到采集完 30 组合格数据

## 项目结构

```
camera-precision-auto-test/
├── main.py                         # 主程序入口
├── 改名.py                          # TIFF 文件批量重命名工具
├── rotate.py                       # 图片批量左右镜像翻转工具
├── requirements.txt                # Python 依赖
├── README.md                       # 项目说明文档
├── config/
│   ├── __init__.py
│   ├── settings.json               # 测试参数配置
│   └── positions.json              # 校准位置数据（运行后自动生成）
├── calibration/
│   ├── __init__.py
│   └── calibration_ui.py           # 交互式校准界面模块
├── automation/
│   ├── __init__.py
│   └── controller.py               # 自动化测试控制器
├── utils/
│   ├── __init__.py
│   └── screen_utils.py             # 屏幕截取与 OCR 识别工具
└── resources/                      # 资源目录（当前流程未强依赖）
```

## 环境要求

- **操作系统：** Windows 10/11
- **Python：** >= 3.10
- **Tesseract OCR：** 需要安装 [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- **屏幕分辨率：** 校准后请勿更改分辨率或缩放比例

## 安装

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 安装 Tesseract OCR

1. 从 [Tesseract 官方仓库](https://github.com/UB-Mannheim/tesseract/wiki) 下载安装程序
2. 安装到默认路径（`C:\Program Files\Tesseract-OCR\`）
3. 如果安装到其他路径，请修改 `config/settings.json` 中的 `tesseract_cmd` 字段

## 配置

编辑 `config/settings.json` 设置测试参数：

```json
{
    "base_path": "C:\\Users\\mech-mind\\Desktop\\振镜\\8ms",
    "total_groups": 30,
    "expected_frames": 54,
    "wait_after_trigger": 7,
    "wait_after_click": 0.5,
    "retry_wait": 1.0,
    "ocr_language": "eng",
    "tesseract_cmd": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
}
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `base_path` | 基础储存路径，每组数据存入以数字命名的子文件夹 | `C:\Users\mech-mind\Desktop\振镜\8ms` |
| `total_groups` | 总共需要采集的合格数据组数 | `30` |
| `expected_frames` | 每组录制的期望帧数 | `54` |
| `wait_after_trigger` | 触发采集后的等待时间（秒） | `7` |
| `wait_after_click` | 每次点击操作后的等待时间（秒） | `0.5` |
| `retry_wait` | 重试前的等待时间（秒） | `1.0` |
| `tesseract_cmd` | Tesseract 可执行文件路径 | `C:\Program Files\Tesseract-OCR\tesseract.exe` |

## 使用方法

### 准备工作

1. 打开相机软件和采集触发软件
2. 手工设置好各项参数（曝光时间、帧率等）
3. 调整好各窗口位置，确保按钮和帧数显示区域可见
4. **保持窗口位置不动**

### 运行程序

```bash
# 正常运行（首次运行会自动进入校准流程）
python main.py

# 强制重新校准
python main.py --calibrate

# 指定配置文件
python main.py --config path/to/settings.json

# 覆盖基础路径和组数
python main.py --base-path "C:\Users\mech-mind\Desktop\振镜\12ms" --groups 20
```

### 校准流程

首次运行时，程序会引导您完成以下校准步骤：

1. **标定"开始录制"按钮：** 将鼠标移到软件中"开始录制"按钮上，按 Enter 确认
2. **标定"结束录制"按钮：** 将鼠标移到软件中"结束录制"按钮上，按 Enter 确认
3. **标定"报错弹窗 Close 按钮"：** 将鼠标移到报错弹窗中的 `Close` 按钮上，按 Enter 确认
4. **标定"储存路径"输入框：** 将鼠标移到储存路径输入框上，按 Enter 确认
5. **标定"触发采集"按钮：** 将鼠标移到触发采集按钮上，按 Enter 确认
6. **框选"帧数显示区域"：** 在弹出的半透明覆盖层上，用鼠标拖拽框选帧数数字显示区域

校准完成后位置信息会自动保存到 `config/positions.json`，下次运行无需重复校准。

### 自动测试流程

校准完成后，程序会自动执行以下循环（共 30 组）：

```
对于每组数据（第 n 组）：
  1. 点击储存路径输入框 → Ctrl+A 全选 → Delete 删除 → 粘贴新路径
     路径格式: {base_path}\{n}\
  2. 点击"开始录制"按钮
  3. 点击"触发采集"按钮
  4. 等待约 7 秒录制完成
  5. OCR 识别帧数显示区域的数字
  6. 如果帧数 == 54 → 合格
     如果帧数 ≠ 54 → 点击已标定的弹窗 `Close` 按钮，删除已采集数据，重试本组
  7. 无论本轮是否合格，都会点击一次"结束录制"按钮后再进入下一轮
```

### 紧急停止

在自动测试过程中，支持两种中断方式：

1. **将鼠标快速移到屏幕左上角**，触发 PyAutoGUI FailSafe 立即停止  
2. **按 `Esc` 键**，程序会捕获中断并安全退出

## 图片后处理工具

除自动化采集主流程外，项目内还提供 2 个离线图片处理脚本，用于整理采集后的数据。

### 1) `改名.py`（TIFF 批量重命名）

**功能：**
- 从脚本运行目录开始递归处理曝光时间文件夹（如 `8ms/`、`12ms/`）
- 在每个数字子目录（`1` 到 `30`）内查找 `*.tiff`
- 仅处理文件名末尾符合 `_(\d{4})` 的文件（例如 `xxx_0123.tiff`）
- 按末尾 4 位数字排序后，重命名为 `cam1_proj0_exp0_{idx}.tiff`（`idx` 从 `0` 开始）

**运行方式：**

```bash
python 改名.py
```

脚本会先进行确认提示（`yes/no`），确认后才执行重命名。

### 2) `rotate.py`（图片批量左右镜像）

**功能：**
- 以当前目录为源目录递归扫描图片
- 支持格式：`.tif`、`.tiff`、`.png`、`.jpg`、`.jpeg`、`.bmp`、`.webp`
- 对每张图片执行左右镜像翻转（`ImageOps.mirror`）
- 保持原有目录结构，将结果输出到同级新目录：`当前目录名_flipped`
- 不覆盖原图

**运行方式：**

```bash
python rotate.py
```

脚本会提示源目录、目标目录并要求 `yes/no` 确认后开始处理。

## 注意事项

1. **请勿在测试过程中移动鼠标或操作键盘**，否则会干扰自动化操作
2. **请勿改变窗口位置或大小**，否则校准位置会失效
3. 如果更换了曝光时间或调整了窗口布局，请使用 `--calibrate` 参数重新校准
4. 中文路径通过剪贴板粘贴方式输入，避免输入法兼容问题
5. 程序依赖 Windows 系统的 PowerShell 来操作剪贴板
6. `改名.py` 会直接修改原 TIFF 文件名，建议先备份后再执行
7. `rotate.py` 默认输出到新目录 `*_flipped`，不会改动原图

## 依赖说明

| 包名 | 用途 |
|------|------|
| `pyautogui` | 模拟鼠标点击和键盘输入 |
| `Pillow` | 图像处理 |
| `pytesseract` | OCR 文字识别 |
| `keyboard` | 监听 `Esc` 中断 |

## 常见问题

**Q: OCR 识别不准确怎么办？**
A: 确保帧数显示区域框选准确，只包含数字部分。可以尝试调整屏幕分辨率或字体大小使数字更清晰。

**Q: 中文路径输入失败？**
A: 本工具通过剪贴板粘贴方式输入路径。请确保 Windows PowerShell 可用，或安装 `pyperclip` 包作为备选方案。

**Q: 报错弹窗没被关闭？**
A: 当前流程使用校准得到的 `error_close` 坐标点击弹窗 `Close`。如果软件窗口位置变化或分辨率变化，请重新执行 `python main.py --calibrate`。

## License

MIT