# main.py

import sys
from PySide6.QtWidgets import QApplication
from controller import Controller

def main():
    app = QApplication(sys.argv)
    
    controller = Controller()  # 컨트롤러가 UI와 로직을 묶어줌
    controller.show_main_window()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
