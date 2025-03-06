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