import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QColor, QFont

class StartupMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Application Startup Menu")
        self.setGeometry(100, 100, 300, 200)
        self.setStyleSheet("background-color: black; color: #00FF00;")
        
        layout = QVBoxLayout()
        
        start_button = QPushButton("Start Application")
        start_button.setFont(QFont("Arial", 12, QFont.Bold))
        start_button.clicked.connect(self.start_application)
        layout.addWidget(start_button)
        
        settings_button = QPushButton("Settings")
        settings_button.setFont(QFont("Arial", 12, QFont.Bold))
        settings_button.clicked.connect(self.open_settings)
        layout.addWidget(settings_button)
        
        exit_button = QPushButton("Exit")
        exit_button.setFont(QFont("Arial", 12, QFont.Bold))
        exit_button.clicked.connect(self.close)
        layout.addWidget(exit_button)
        
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
    def start_application(self):
        # Replace this with the actual code to start your application
        print("Starting the application...")
        
    def open_settings(self):
        # Replace this with the actual code to open your settings window
        print("Opening settings...")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Apply the Fusion style
    window = StartupMenu()
    window.show()
    sys.exit(app.exec_())
