import queue
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

user32 = ctypes.windll.user32
SCREEN_W = user32.GetSystemMetrics(0)
SCREEN_H = user32.GetSystemMetrics(1)
SCREEN_CX = SCREEN_W // 2
SCREEN_CY = SCREEN_H // 2

is_running = False
aim_enabled = False
trigger_enabled = False

#默认黄金参数
fov_size = 300
offset_x = 0
offset_y = 0
aim_smooth = 0.15   #平滑度
aim_deadzone = 3    #心死区

#线程通讯与底层配置
draw_queue = queue.Queue(maxsize=1)
AI_CAP_REGION = 320 #CPU优化的截屏大小