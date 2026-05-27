import ctypes
import time

user32 = ctypes.windll.user32
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

def move_mouse(dx, dy):
    """硬件级相对移动"""
    user32.mouse_event(MOUSEEVENTF_MOVE, int(dx), int(dy), 0, 0)

def click_mouse():
    """硬件级模拟人类点击"""
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.01)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)