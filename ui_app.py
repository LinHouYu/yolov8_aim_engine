import tkinter as tk
import ctypes
import queue
import colorsys
import settings

def main_app():
    root = tk.Tk()
    root.title("目标检测 By LinHouYu")
    
    UI_W, UI_H = 420, 680
    root.geometry(f"{UI_W}x{UI_H}")
    root.attributes('-topmost', True)
    
    DARK_BG = "#121212"
    TEXT_FG = "#FFFFFF"
    TROUGH_BG = "#2A2A2A"

    ui_bg_canvas = tk.Canvas(root, width=UI_W, height=UI_H, bg="#000000", highlightthickness=0)
    ui_bg_canvas.pack(fill=tk.BOTH, expand=True)

    ui_border_lines = []
    w_step = UI_W / 15
    h_step = UI_H / 15
    ui_pts = []
    for i in range(15): ui_pts.append((i*w_step, 2, (i+1)*w_step, 2))
    for i in range(15): ui_pts.append((UI_W-2, i*h_step, UI_W-2, (i+1)*h_step))
    for i in range(15): ui_pts.append((UI_W - i*w_step, UI_H-2, UI_W - (i+1)*w_step, UI_H-2))
    for i in range(15): ui_pts.append((2, UI_H - i*h_step, 2, UI_H - (i+1)*h_step))

    for px1, py1, px2, py2 in ui_pts:

        l = ui_bg_canvas.create_line(px1, py1, px2, py2, width=4, fill="black")
        ui_border_lines.append(l)


    content_frame = tk.Frame(ui_bg_canvas, bg=DARK_BG, bd=0)
    ui_bg_canvas.create_window(4, 4, width=UI_W-8, height=UI_H-8, window=content_frame, anchor="nw")

    over = tk.Toplevel(root)
    over.title("Cyber-ESP")
    over.overrideredirect(True) 
    over.geometry(f"{settings.SCREEN_W}x{settings.SCREEN_H}+0+0") 
    over.attributes('-topmost', True)
    
    bg_color = "#FF00FF" 
    over.configure(bg=bg_color)
    over.attributes("-transparentcolor", bg_color)
    
    over.update()
    hwnd = ctypes.windll.user32.GetParent(over.winfo_id())
    ctypes.windll.user32.SetWindowLongW(hwnd, -20, ctypes.windll.user32.GetWindowLongW(hwnd, -20) | 0x80000 | 0x00000020)

    canvas = tk.Canvas(over, width=settings.SCREEN_W, height=settings.SCREEN_H, bg=bg_color, highlightthickness=0)
    canvas.pack()

    MAX_BOXES = 100
    pool_boxes = [canvas.create_rectangle(-100,-100,-50,-50, outline="white", width=3, state="hidden") for _ in range(MAX_BOXES)]
    pool_texts = [canvas.create_text(-100,-100, text="", fill="white", font=("Arial", 12, "bold"), anchor="nw", state="hidden") for _ in range(MAX_BOXES)]
    
    fov_lines = [canvas.create_line(-100,-100,-50,-50, fill="cyan", width=3, state="hidden") for _ in range(40)]
    aim_line = canvas.create_line(-100,-100,-50,-50, fill="lime", width=2, state="hidden")
    

    hud_outlines = []
    offsets = [(-1,-1), (1,-1), (-1,1), (1,1), (0,2), (0,-2), (2,0), (-2,0)]
    for dx, dy in offsets:
        t = canvas.create_text(20+dx, 20+dy, text="", fill="black", font=("Consolas", 14, "bold"), anchor="nw", state="hidden")
        hud_outlines.append(t)
        
    hud_text_main = canvas.create_text(20, 20, text="", fill="white", font=("Consolas", 14, "bold"), anchor="nw", state="hidden")

    def update_overlay():
        if settings.is_running:
            try:
                data = settings.draw_queue.get_nowait()
                current_obj_idx = 0
                line_drawn = False
                
                for item in data:
                    if item["type"] == "hud":
                        s_aim = "ON" if settings.aim_enabled else "OFF"
                        s_trig = "ON" if settings.trigger_enabled else "OFF"
                        hud_info = (
                            f"YoloV8 目标检测\n"
                            f"AI  FPS : {item['fps']} FPS\n"
                            f"Targets : {item['count']} in FOV\n"
                            f"Status  : {item['status']}\n"
                            f"Aimbot  : [{s_aim}] Trig: [{s_trig}]"
                        )
                        for t in hud_outlines: canvas.itemconfig(t, text=hud_info, state="normal")
                        canvas.itemconfig(hud_text_main, text=hud_info, state="normal")
                        size, xo, yo = item["fov"], item["xo"], item["yo"]
                        x1 = settings.SCREEN_CX - (size // 2) + xo
                        y1 = settings.SCREEN_CY - (size // 2) + yo
                        x2 = settings.SCREEN_CX + (size // 2) + xo
                        y2 = settings.SCREEN_CY + (size // 2) + yo
                        
                        step = size / 10.0
                        pts = []
                        for i in range(10): pts.append((x1 + i*step, y1, x1 + (i+1)*step, y1))      # 上
                        for i in range(10): pts.append((x2, y1 + i*step, x2, y1 + (i+1)*step))      # 右
                        for i in range(10): pts.append((x2 - i*step, y2, x2 - (i+1)*step, y2))      # 下
                        for i in range(10): pts.append((x1, y2 - i*step, x1, y2 - (i+1)*step))      # 左
                        
                        for i, (px1, py1, px2, py2) in enumerate(pts):
                            canvas.coords(fov_lines[i], px1, py1, px2, py2)
                            canvas.itemconfig(fov_lines[i], state="normal")
                        
                    elif item["type"] == "box" and current_obj_idx < MAX_BOXES:
                        x1, y1, x2, y2 = item["x1"], item["y1"], item["x2"], item["y2"]
                        canvas.coords(pool_boxes[current_obj_idx], x1, y1, x2, y2)
                        canvas.itemconfig(pool_boxes[current_obj_idx], outline=item["color"], state="normal")
                        canvas.coords(pool_texts[current_obj_idx], x1, y1 - 12)
                        canvas.itemconfig(pool_texts[current_obj_idx], text=item["label"], fill=item["color"], state="normal")
                        current_obj_idx += 1
                        
                    elif item["type"] == "line":
                        canvas.coords(aim_line, item["x1"], item["y1"], item["x2"], item["y2"])
                        canvas.itemconfig(aim_line, fill=item["color"], state="normal")
                        line_drawn = True
                
                if not line_drawn:
                    canvas.itemconfig(aim_line, state="hidden")
                
                for j in range(current_obj_idx, MAX_BOXES):
                    canvas.itemconfig(pool_boxes[j], state="hidden")
                    canvas.itemconfig(pool_texts[j], state="hidden")
                    
            except queue.Empty: pass
        
        root.after(25, update_overlay) 

    update_overlay()

    hue_offset = 0.0
    def update_rgb_effects():
        nonlocal hue_offset
        hue_offset -= 0.02 
        if hue_offset < 0.0: hue_offset += 1.0
        
        num_ui = len(ui_border_lines)
        for i, line in enumerate(ui_border_lines):
            seg_hue = (hue_offset + i / num_ui) % 1.0
            r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(seg_hue, 1.0, 1.0)]
            ui_bg_canvas.itemconfig(line, fill=f"#{r:02x}{g:02x}{b:02x}")
            
     
        if settings.is_running:
            num_fov = len(fov_lines)
            for i, line in enumerate(fov_lines):
                seg_hue = (hue_offset + i / num_fov) % 1.0
                r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(seg_hue, 1.0, 1.0)]
                canvas.itemconfig(line, fill=f"#{r:02x}{g:02x}{b:02x}")
                
        root.after(25, update_rgb_effects) 
        
    update_rgb_effects()

  
    def set_fov(v): settings.fov_size = int(v)
    def set_smooth(v): settings.aim_smooth = float(v)
    def set_deadzone(v): settings.aim_deadzone = int(v)
    def set_offset_x(v): settings.offset_x = int(v)
    def set_offset_y(v): settings.offset_y = int(v)

    tk.Label(content_frame, text="FOV VISUAL RANGE", bg=DARK_BG, fg="cyan", font=("Arial", 10, "bold")).pack(pady=(15,0))
    sl_fov = tk.Scale(content_frame, label="调节检测范围 (FOV)", from_=100, to=1000, orient=tk.HORIZONTAL, 
                           bg=DARK_BG, fg=TEXT_FG, troughcolor=TROUGH_BG, bd=0, highlightthickness=0, command=set_fov)
    sl_fov.set(settings.fov_size); sl_fov.pack(fill=tk.X, padx=20)
    
    tk.Label(content_frame, text="AIMBOT TUNING", bg=DARK_BG, fg="cyan", font=("Arial", 10, "bold")).pack(pady=(15,0))
    sl_smooth = tk.Scale(content_frame, label="平滑度 (Smoothness)", from_=0.01, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, 
                              bg=DARK_BG, fg=TEXT_FG, troughcolor=TROUGH_BG, bd=0, highlightthickness=0, command=set_smooth)
    sl_smooth.set(settings.aim_smooth); sl_smooth.pack(fill=tk.X, padx=20)
    
    sl_dz = tk.Scale(content_frame, label="中心死区 (Deadzone)", from_=1, to=30, orient=tk.HORIZONTAL, 
                          bg=DARK_BG, fg=TEXT_FG, troughcolor=TROUGH_BG, bd=0, highlightthickness=0, command=set_deadzone)
    sl_dz.set(settings.aim_deadzone); sl_dz.pack(fill=tk.X, padx=20)

    tk.Label(content_frame, text="PHYSICAL OFFSET", bg=DARK_BG, fg="cyan", font=("Arial", 10, "bold")).pack(pady=(15,0))
    sl_x = tk.Scale(content_frame, label="X 轴左右偏移", from_=-600, to=600, orient=tk.HORIZONTAL, 
                         bg=DARK_BG, fg=TEXT_FG, troughcolor=TROUGH_BG, bd=0, highlightthickness=0, command=set_offset_x)
    sl_x.set(settings.offset_x); sl_x.pack(fill=tk.X, padx=20)
    
    sl_y = tk.Scale(content_frame, label="Y 轴上下偏移", from_=-600, to=600, orient=tk.HORIZONTAL, 
                         bg=DARK_BG, fg=TEXT_FG, troughcolor=TROUGH_BG, bd=0, highlightthickness=0, command=set_offset_y)
    sl_y.set(settings.offset_y); sl_y.pack(fill=tk.X, padx=20)

    btn_frame = tk.Frame(content_frame, bg=DARK_BG)
    btn_frame.pack(pady=20)
    
    def toggle_aim():
        settings.aim_enabled = not settings.aim_enabled
        btn_aim.config(bg="#00FF00" if settings.aim_enabled else "#333333", fg="black" if settings.aim_enabled else "white")

    def toggle_trig():
        settings.trigger_enabled = not settings.trigger_enabled
        btn_trig.config(bg="#FF0000" if settings.trigger_enabled else "#333333", fg="white")

    btn_aim = tk.Button(btn_frame, text="AIMBOT", bg="#333333", fg="white", font=("Arial", 10, "bold"), width=12, relief="flat", command=toggle_aim)
    btn_aim.pack(side=tk.LEFT, padx=10)
    btn_trig = tk.Button(btn_frame, text="TRIGGER", bg="#333333", fg="white", font=("Arial", 10, "bold"), width=12, relief="flat", command=toggle_trig)
    btn_trig.pack(side=tk.LEFT, padx=10)

    def toggle_sys():
        settings.is_running = not settings.is_running
        btn_sys.config(text="SYSTEM [OFF]" if settings.is_running else "SYSTEM [ON]", bg="#FF0044" if settings.is_running else "#00AAFF")
        if not settings.is_running:
            for line in fov_lines: canvas.itemconfig(line, state="hidden")
            canvas.itemconfig(aim_line, state="hidden")
            for t in hud_outlines: canvas.itemconfig(t, state="hidden")
            canvas.itemconfig(hud_text_main, state="hidden")
            for j in range(MAX_BOXES):
                canvas.itemconfig(pool_boxes[j], state="hidden")
                canvas.itemconfig(pool_texts[j], state="hidden")

    btn_sys = tk.Button(content_frame, text="SYSTEM [ON]", bg="#00AAFF", fg="white", font=("Arial", 14, "bold"), width=20, relief="flat", command=toggle_sys)
    btn_sys.pack(pady=10)

    try: ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception: ctypes.windll.user32.SetProcessDPIAware()

    root.mainloop()