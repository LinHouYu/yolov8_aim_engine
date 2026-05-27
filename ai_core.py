import time
import math
import cv2
import numpy as np
import mss
import queue
from ultralytics import YOLO

import settings
import mouse

def ai_detection_logic():
    try:
        print("正在加载 AI 大脑... (纯净环境, 防崩溃)")
        model = YOLO("best.onnx", task="detect") 
        sct = mss.MSS()
        last_time = time.time()
        
        while True:
            if not settings.is_running:
                time.sleep(0.05)
                continue
                
            left = settings.SCREEN_CX - (settings.AI_CAP_REGION // 2) + settings.offset_x
            top = settings.SCREEN_CY - (settings.AI_CAP_REGION // 2) + settings.offset_y
            monitor = {"top": top, "left": left, "width": settings.AI_CAP_REGION, "height": settings.AI_CAP_REGION}
            
            img_raw = np.array(sct.grab(monitor))
            frame = cv2.cvtColor(img_raw, cv2.COLOR_BGRA2BGR)
            
            results = model.predict(frame, conf=0.45, imgsz=settings.AI_CAP_REGION, verbose=False)
            
            now = time.time()
            fps = 1.0 / (now - last_time) if now - last_time > 0 else 0
            last_time = now
            
            draw_data = []
            
            #FOV边界
            fov_min_x = (settings.AI_CAP_REGION // 2) - (settings.fov_size // 2)
            fov_max_x = (settings.AI_CAP_REGION // 2) + (settings.fov_size // 2)
            fov_min_y = (settings.AI_CAP_REGION // 2) - (settings.fov_size // 2)
            fov_max_y = (settings.AI_CAP_REGION // 2) + (settings.fov_size // 2)

            closest_target = None
            min_dist = float('inf')
            target_count = 0

            for box in results[0].boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                label_id = int(box.cls[0].cpu().numpy())
                label_name = model.names[label_id]
                tcx, tcy = (x1 + x2) / 2, (y1 + y2) / 2
                
                if (fov_min_x <= tcx <= fov_max_x) and (fov_min_y <= tcy <= fov_max_y):
                    target_count += 1
                    abs_x1, abs_y1 = int(left + x1), int(top + y1)
                    abs_x2, abs_y2 = int(left + x2), int(top + y2)
                    abs_tcx, abs_tcy = int(left + tcx), int(top + tcy)
                    
                    color = "cyan" if label_name != "circle" else "lime"
                    
                    draw_data.append({
                        "type": "box", "x1": abs_x1, "y1": abs_y1,
                        "x2": abs_x2, "y2": abs_y2, "label": label_name, "color": color
                    })
                    
                    dist = math.hypot(abs_tcx - settings.SCREEN_CX, abs_tcy - settings.SCREEN_CY)
                    if dist < min_dist:
                        min_dist = dist
                        closest_target = (abs_tcx, abs_tcy, abs_x1, abs_y1, abs_x2, abs_y2)

            target_status = "锁定目标" if closest_target else "搜索中..."
            
            draw_data.append({
                "type": "hud", "fps": int(fps), "count": target_count, 
                "status": target_status, "aim": settings.aim_enabled, "trig": settings.trigger_enabled,
                "fov": settings.fov_size, "xo": settings.offset_x, "yo": settings.offset_y
            })

            #自瞄与扳机战术逻辑
            if closest_target:
                abs_tcx, abs_tcy, abs_x1, abs_y1, abs_x2, abs_y2 = closest_target
                
                trigger_margin = 5
                in_crosshair = ((abs_x1 + trigger_margin) <= settings.SCREEN_CX <= (abs_x2 - trigger_margin)) and \
                               ((abs_y1 + trigger_margin) <= settings.SCREEN_CY <= (abs_y2 - trigger_margin))
                
                if settings.trigger_enabled and in_crosshair:
                    mouse.click_mouse()
                    draw_data.append({"type": "line", "x1": settings.SCREEN_CX, "y1": settings.SCREEN_CY, "x2": abs_tcx, "y2": abs_tcy, "color": "red"})
                
                elif settings.aim_enabled:
                    dx = abs_tcx - settings.SCREEN_CX
                    dy = abs_tcy - settings.SCREEN_CY
                    
                    if abs(dx) > settings.aim_deadzone or abs(dy) > settings.aim_deadzone:
                        mouse.move_mouse(dx * settings.aim_smooth, dy * settings.aim_smooth)
                        draw_data.append({"type": "line", "x1": settings.SCREEN_CX, "y1": settings.SCREEN_CY, "x2": abs_tcx, "y2": abs_tcy, "color": "lime"})

            if settings.draw_queue.full():
                try: settings.draw_queue.get_nowait()
                except queue.Empty: pass
            settings.draw_queue.put(draw_data)
            
    except Exception as e:
        print(f"\n后台发生错误: {e}\n")