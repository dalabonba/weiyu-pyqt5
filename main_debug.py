import debugpy
import threading

def wait_for_debugger():
    print("⏳ 等待 VSCode 連線進來...(按F5連線)")
    debugpy.listen(("localhost", 5678))
    debugpy.wait_for_client()
    print("✅ VSCode 已附加成功，可以除錯！")

# 在背景執行等 VSCode 連線的工作
threading.Thread(target=wait_for_debugger, daemon=True).start()

# 👇 這裡開始執行原本的主程式
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from View.view import View

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("logo.svg"))  
    view = View()
    view.show()
    sys.exit(app.exec_())
