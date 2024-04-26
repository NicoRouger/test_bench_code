from PyQt5.QtWidgets import QApplication, QLabel, QWidget
import sys
from queue import Queue

def gui(shared_data):
    # Create a QApplication instance
    app = QApplication(sys.argv)

    # Create a QWidget instance (the main window)
    window = QWidget()

    # Set window properties
    window.setWindowTitle('Hello, World!')
    window.setGeometry(100, 100, 250, 100)  # x-position, y-position, width, height

    # Create a QLabel instance with "Hello, World!" text
    label = QLabel('Hello, World!', parent=window)
    label.setGeometry(20, 20, 200, 50)  # x-position, y-position, width, height

    # Show the window
    window.show()

    # Execute the application's event loop
    sys.exit(app.exec_())