from typing import Optional
from aqt.editor import Editor
from aqt.qt import QAction
from aqt import gui_hooks
import logging

class HideCmdFields:
    def __init__(self, note_type_name='Closet-r', num_fields_to_hide=10):
        self.note_type_name = note_type_name
        self.num_fields_to_hide = num_fields_to_hide
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    def setup_editor_fields(self, editor: Editor):
        """Hide the last N fields in the editor"""
        try:
            if not editor.note:
                self.logger.debug("No note loaded in editor")
                return

            note_type = editor.note.note_type()
            if not note_type or note_type['name'] != self.note_type_name:
                self.logger.debug(f"Note type mismatch: expected {self.note_type_name}")
                return

            # Script to hide the last N fields
            script = f"""
            function hideLastFields() {{
                try {{
                    // Get all field containers
                    const fields = document.querySelectorAll('.fields')[0].children;
                    const totalFields = fields.length;

                    // Calculate start index for hiding
                    const startHideIndex = totalFields - {self.num_fields_to_hide};

                    // Hide the last N fields
                    for (let index = 2; index < totalFields - 2; index++) {{
                        fields[index].style.display = 'none';
                    }};

                }} catch (error) {{
                    console.error('Error in hideLastFields:', error);
                }}
            }}

            // Initial execution
            hideLastFields();
            // Set up observer to maintain hiding after dynamic updates
            const observer = new MutationObserver((mutations) => {{
                for (const mutation of mutations) {{
                    if (mutation.type === 'childList') {{
                        hideLastFields();
                    }}
                }}
            }});

            observer.observe(document.body, {{
                childList: true,
                subtree: true
            }});
            """

            editor.web.eval(script)
            self.logger.info(f"Successfully hidden last {self.num_fields_to_hide} fields")

        except Exception as e:
            self.logger.error(f"Error hiding last fields: {str(e)}")

    def init_hide_fields(self):
        """Initialize hooks for field hiding"""
        try:
            # Hook for editor initialization
            gui_hooks.editor_did_init.append(lambda editor: self.setup_editor_fields(editor))

            # Hook for note loading
            gui_hooks.editor_did_load_note.append(self.setup_editor_fields)

            self.logger.info("Successfully initialized field hiding hooks")

        except Exception as e:
            self.logger.error(f"Failed to initialize field hiding: {str(e)}")
            raise

def init_cmd_fields_hiding():
    """Main initialization function"""
    try:
        hide_fields = HideCmdFields(num_fields_to_hide=10)  # Hide last 10 fields
        hide_fields.init_hide_fields()
        return hide_fields
    except Exception as e:
        logging.error(f"Failed to initialize CMD fields hiding: {str(e)}")
        raise

# Create the instance
cmd_fields_handler = init_cmd_fields_hiding()