from aqt import gui_hooks
from aqt.editor import Editor
from aqt.qt import QShortcut, QKeySequence

from .buttons import ClosetEditorChanges  # Import the class, not the instance
from .hide_fields import init_cmd_fields_hiding

def setup_editor_shortcuts():
    """Configure custom editor shortcuts"""
    # Create an instance of ClosetEditorChanges
    editor_changes = ClosetEditorChanges()

    def add_closet_shortcut(editor: Editor):
        """Add the Closet shortcut to the editor"""
        shortcut = QShortcut(QKeySequence("Ctrl+Shift+C"), editor.widget)
        shortcut.activated.connect(lambda: editor_changes.handle_closet_shortcut(editor))

    # Add the hook for setting up the shortcut when the editor is created
    gui_hooks.editor_did_init.append(add_closet_shortcut)

    # Register the buttons
    gui_hooks.editor_did_init_buttons.append(editor_changes.setup_closet_button)
    gui_hooks.editor_did_init_buttons.append(editor_changes.setup_close_to_closet)

    cmd_fields_handler = init_cmd_fields_hiding()

    return editor_changes
