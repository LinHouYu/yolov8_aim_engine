from threading import Thread

from ai_core import ai_detection_logic
from ui_app import main_app

if __name__ == "__main__":
    Thread(target=ai_detection_logic, daemon=True).start()
    
    main_app()