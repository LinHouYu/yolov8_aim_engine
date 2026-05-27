# 目标检测视觉辅助系统
**By LinHouYu**

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![YOLOv8](https://img.shields.io/badge/YOLO-v8-yellow.svg)](https://ultralytics.com/)

> ⚠️ **免责声明 (Disclaimer):**
> 本项目及代码仅供 **学术研究、机器视觉学习与 AI 自动化控制交流** 使用。作者不对任何人因使用本软件而导致的任何游戏封号、硬件损坏或法律纠纷承担责任。用户需对自己的行为负全部责任。本项目采用 **CC BY-NC 4.0** 协议，**严禁任何形式的商业用途与盈利行为**。

---

## 演示视频 (Demo)
https://github.com/user-attachments/assets/e16c33dd-ca74-454b-9175-c7a0a559bb85

---

## 核心特性 (Features)

本项目脱胎于传统的 Python 脚本，经过底层架构重构，现已进化为具备现代化工业级 UI 与高频平滑控制的完整视觉引擎：

- **极速视觉引擎**：基于 `YOLOv8` 架构与 `mss` 极速截图，配合缩小推理区域 (AI Cap Region)，大幅提升屏幕抓取与推理帧率。
- **P-Controller 平滑自瞄 (Smooth Aim)**：内置参数化缓动算法。告别僵硬的“瞬移停顿”，准星如吸铁石般平滑拉枪。
- **中心死区防抖 (Deadzone)**：自定义死区像素范围，彻底解决目标锁定后的高频抽搐问题。
- **物理级输入伪装**：采用底层的 `ctypes` 调用 Windows Win32 API (`mouse_event`)，纯物理相对移动，安全可靠。

---

## 硬件兼容性 (Hardware Compatibility)

本项目针对硬件推理环境进行了深度普适性优化，打破了“AI 必须用 N 卡”的刻板印象：

* **纯 CPU 环境**：完美支持。
* **AMD 显卡 (如 RX 6600M)**：**完美原生支持！** 代码已剔除强制绑定 CUDA 的逻辑，通过加载 `.onnx` 模型格式，可自动利用 DirectML 或 CPU 算力进行高效推理。
* **NVIDIA 显卡 (CUDA)**：**理论支持。** 如果你的设备装有 N 卡，并且配置好了完整的 PyTorch CUDA 环境，只需将模型替换回 `.pt` 格式，即可享受巅峰的推理帧率。

---

## 安装与运行 (Installation & Usage)

### 1. 环境依赖
请确保你的电脑已安装 Python 3.8 或以上版本，并在终端运行以下命令安装所需库：

```bash
pip install ultralytics mss opencv-python numpy customtkinter
```
## 交流与反馈 (Community & Support)

如果您在编译、参数调教、模型导出 `.onnx` 的过程中遇到任何技术疑难，或者想要交流更前沿的计算机视觉、ESP 渲染与高频控制自动化闭环技术，欢迎加入官方 Telegram 技术讨论群：
👉 **[点击加入Telegram讨论群 (zhishifenzi8266)](https://t.me/zhishifenzi8266)**
