import os
import sys
import json
import shutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QFileDialog, QHeaderView

class GameSaveManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Save Manager")

        self.save_paths = []

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # Save paths section
        self.save_path_label = QLabel("Saved Paths:")
        main_layout.addWidget(self.save_path_label)

        self.save_path_table = QTableWidget()
        self.save_path_table.setColumnCount(2)
        self.save_path_table.setHorizontalHeaderLabels(["Game Name", "Path"])
        self.save_path_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.save_path_table)

        # Game name entry section
        self.game_name_label = QLabel("Game Name:")
        main_layout.addWidget(self.game_name_label)

        self.game_name_entry = QLineEdit()
        main_layout.addWidget(self.game_name_entry)

        # Manual path entry section
        self.manual_path_label = QLabel("Manual Path Entry:")
        main_layout.addWidget(self.manual_path_label)

        path_entry_layout = QHBoxLayout()
        main_layout.addLayout(path_entry_layout)

        self.manual_path_entry = QLineEdit()
        path_entry_layout.addWidget(self.manual_path_entry)

        self.add_button = QPushButton("Add Path")
        self.add_button.clicked.connect(self.add_save_path)
        path_entry_layout.addWidget(self.add_button)

        

        # Button section
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_path_manually)
        button_layout.addWidget(self.save_button)

        self.open_button = QPushButton("Open Selected Path")
        self.open_button.clicked.connect(self.open_selected_path)
        button_layout.addWidget(self.open_button)

        self.delete_button = QPushButton("Delete Path")
        self.delete_button.clicked.connect(self.delete_selected_path)
        button_layout.addWidget(self.delete_button)

        # Copy folders button
        self.copy_button = QPushButton("Backup")
        self.copy_button.clicked.connect(self.copy_folders)
        button_layout.addWidget(self.copy_button)

        # Load paths from JSON file
        self.load_paths_from_json()

    def load_paths_from_json(self):
        file_path = "save_paths.json"
        if not os.path.exists(file_path):
            with open(file_path, "w") as file:
                json.dump([], file)

        try:
            with open(file_path, "r") as file:
                self.save_paths = json.load(file)
        except FileNotFoundError:
            self.save_paths = []

        self.update_table()

    def update_table(self):
        self.save_path_table.setRowCount(len(self.save_paths))
        for i, path_info in enumerate(self.save_paths):
            game_name = path_info.get("game_name", "")
            path = path_info["path"]
            game_name_item = QTableWidgetItem(game_name)
            path_item = QTableWidgetItem(path)
            self.save_path_table.setItem(i, 0, game_name_item)
            self.save_path_table.setItem(i, 1, path_item)
        self.save_path_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def add_save_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory", directory=os.getenv('APPDATA'))
        if path and path not in [item["path"] for item in self.save_paths]:
            game_name = ""
            if self.game_name_entry.text():
                game_name = self.game_name_entry.text()
            self.save_paths.append({"path": path, "game_name": game_name})
            self.save_to_json()
            self.update_table()

    def save_path_manually(self):
        path = self.manual_path_entry.text()
        game_name = self.game_name_entry.text()
        if path and path not in [item["path"] for item in self.save_paths]:
            self.save_paths.append({"path": path, "game_name": game_name})
            self.save_to_json()
            self.update_table()

    def save_to_json(self):
        with open("save_paths.json", "w") as file:
            json.dump(self.save_paths, file)

    def open_selected_path(self):
        selected_item = self.save_path_table.currentItem()
        if selected_item:
            row = selected_item.row()
            path = self.save_paths[row]["path"]
            os.startfile(path)

    def delete_selected_path(self):
        selected_item = self.save_path_table.currentItem()
        if selected_item:
            row = selected_item.row()
            del self.save_paths[row]
            self.save_to_json()
            self.update_table()

    def copy_folders(self):
        if not self.save_paths:
            return

        destination_folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if destination_folder:
            for path_info in self.save_paths:
                source_path = path_info["path"]
                destination_path = os.path.join(destination_folder, os.path.basename(source_path))  
                try:
                    if os.path.exists(destination_path):
                        shutil.rmtree(destination_path)  
                    shutil.copytree(source_path, destination_path)
                except Exception as e:
                    print(f"Failed to copy '{source_path}' to '{destination_path}': {e}")

def main():
    app = QApplication(sys.argv)
    window = GameSaveManager()
    window.resize(1600, 900)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
