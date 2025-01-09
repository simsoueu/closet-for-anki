from typing import Optional
from aqt.editor import Editor
from aqt.qt import QAction
import re
import logging
import json

class ClosetEditorChanges:
    def __init__(self, note_type_name='Closet-r'):
        self.note_type_name = note_type_name
        self.logger = logging.getLogger(__name__)

    def setup_closet_button(self, buttons, editor: Editor):
        """Setup the closet tag button"""
        if button := self.generate_button(editor):
            buttons.append(button)

    def setup_close_to_closet(self, buttons, editor: Editor):
        """Setup the conversion button"""
        if button := self.generate_button_conversion(editor):
            buttons.append(button)

    def generate_button_conversion(self, editor: Editor) -> Optional[str]:
        """Generate the conversion button"""
        return editor.addButton(
            icon=None,  # No icon for now
            cmd="convert_button",  # Command name
            func=lambda e=editor: self.handle_convert_close_to_closet(e),  # Callback
            tip="Convert {{c#}} tags to [[c#]]",  # Tooltip
            label="[C]",  # Button label
            keys=None,  # No shortcut keys
        )

    def generate_button(self, editor: Editor) -> Optional[str]:
        """Generate the closet button"""
        return editor.addButton(
            icon=None,  # No icon for now
            cmd="closet_button",  # Command name
            func=lambda e=editor: self.handle_closet_shortcut(e),  # Callback
            tip="Insert tag Closet (Ctrl+Shift+C)",  # Tooltip
            label="CL",  # Button label
            keys="Ctrl+Shift+C",  # Shortcut keys
        )

    @staticmethod
    def converter_chaves(texto: str) -> str:
        """Convert cloze tags from {{c#}} to [[c#]]"""
        # Match {{c#::text}} pattern
        padrao = r'\{\{c(\d+)::(.*?)\}\}'
        return re.sub(padrao, r'[[c\1::\2]]', texto)

    def handle_convert_close_to_closet(self, editor: Editor):
        """Handle the conversion from Close to Closet tags"""
        if not editor.note or editor.note.note_type()['name'] != self.note_type_name:
            return

        try:
            # Get the current field content
            field_index = editor.currentField

            # Select all content in the current field
            editor.web.eval("saveSelection();")
            editor.web.eval(f"""
                document.getElementsByClassName('field')[{field_index}].focus();
                document.execCommand('selectAll', false, null);
            """)

            # Get the selected content
            field_content = editor.note.fields[field_index]

            # Convert the content
            converted_content = self.converter_chaves(field_content)

            # Replace the field content
            editor.web.eval(f"document.execCommand('insertText', false, {json.dumps(converted_content)});")

            # Restore the original selection
            editor.web.eval("restoreSelection();")

            # Update the note
            editor.note.fields[field_index] = converted_content
            editor.loadNote()

        except Exception as e:
            self.logger.error(f"Error converting Close to Closet: {str(e)}")

    def handle_closet_shortcut(self, editor: Editor):
        """Handle the closet shortcut"""
        if not editor.note or editor.note.note_type()['name'] != self.note_type_name:
            return

        try:
            selected_text = editor.web.selectedText()
            if not selected_text:
                return

            trimmed_text = selected_text.strip()
            field_content = editor.note.fields[editor.currentField]

            existing_numbers = re.findall(r'\[\[c(\d+)::', field_content)
            next_num = max(map(int, existing_numbers or [0])) + 1

            replacement = f"[[c{next_num}::{trimmed_text}]]"

            editor.web.eval(
                f"document.execCommand('insertText', false, {json.dumps(replacement + ' ')});"
            )
        except Exception as e:
            self.logger.error(f"Error handling closet shortcut: {str(e)}")

def init_editor():
    """Initialize the editor changes"""
    editor_changes = ClosetEditorChanges()

    # Register both buttons with the editor
    from aqt.gui_hooks import editor_did_init_buttons
    editor_did_init_buttons.append(editor_changes.setup_closet_button)
    editor_did_init_buttons.append(editor_changes.setup_close_to_closet)

    return editor_changes

# Create the instance
closet_editor_changes = init_editor()