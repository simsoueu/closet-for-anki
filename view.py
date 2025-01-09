# view.py
from aqt.qt import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QCheckBox, QMenu, QAction
from aqt import mw

class ClosetConfigDialog(QDialog):
    def __init__(self, parent=None, current_config=None, on_save=None):
        super().__init__(parent)
        self.current_config = current_config or {}
        self.on_save = on_save
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Closet Settings")
        layout = QVBoxLayout()

        # Color selection
        label = QLabel("Closet Color")
        layout.addWidget(label)

        self.combo_box = QComboBox()
        self.combo_box.addItems(self.current_config.get("COLOR_MAP", {}).keys())
        self.combo_box.setCurrentText(self.current_config.get("closet_color", "Blue"))
        layout.addWidget(self.combo_box)

        # Checkboxes
        self.highlight_checkbox = QCheckBox("Highlight all cloze")
        self.highlight_checkbox.setChecked(self.current_config.get("highlight_all_cloze", False))
        layout.addWidget(self.highlight_checkbox)

        self.deck_name_checkbox = QCheckBox("Show deck name as header")
        self.deck_name_checkbox.setChecked(self.current_config.get("show_deck_name", True))
        layout.addWidget(self.deck_name_checkbox)

        # Save button
        button_box = QPushButton("Save")
        button_box.clicked.connect(self.save_settings)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def save_settings(self):
        if self.on_save:
            config = {
                "closet_color": self.combo_box.currentText(),
                "highlight_all_cloze": self.highlight_checkbox.isChecked(),
                "show_deck_name": self.deck_name_checkbox.isChecked()
            }
            self.on_save(config)
        self.accept()

class ClosetMenu:
    def __init__(self, on_update_cards=None, on_open_settings=None):
        self.on_update_cards = on_update_cards
        self.on_open_settings = on_open_settings

    def setup_menu(self):
        closet_menu = QMenu("Closet", mw)

        update_action = QAction("Update Closet Cards", mw)
        update_action.triggered.connect(lambda: self.on_update_cards() if self.on_update_cards else None)
        closet_menu.addAction(update_action)

        config_action = QAction("Settings", mw)
        config_action.triggered.connect(lambda: self.on_open_settings() if self.on_open_settings else None)
        closet_menu.addAction(config_action)

        mw.form.menuTools.addMenu(closet_menu)
        return closet_menu