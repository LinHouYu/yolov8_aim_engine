import cv2
import numpy as np
import mss
import time
import os

def main():
    save_dir = "dataset_images"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    sct = mss.mss()
    monitor = {"top": 240, "left": 560, "width": 800, "height": 600}
    
    print(f"启动自动采集！图片将保存在项目下的 '{save_dir}' 文件夹中。")
    print("请切回练枪网页开始打靶。每 0.5 秒会自动抓拍一张。")
    print("按下小写 'q' 键停止采集。")

    count = 0
    while True:
        img = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        cv2.imshow("Data Collection Window (Press 'Q' to stop)", frame)
        
        filename = os.path.join(save_dir, f"aim_target_{int(time.time() * 1000)}.jpg")
        cv2.imwrite(filename, frame)
        count += 1
        print(f"📸 咔嚓！已保存第 {count} 张图片")
        
        if cv2.waitKey(500) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    print(f"总共收集了 {count} 张训练素材。")

if __name__ == "__main__":
    main()