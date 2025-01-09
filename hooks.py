from aqt import gui_hooks
from aqt.utils import showInfo

from .closet_note_updater import closet_note_updater
from .editor.buttons import closet_editor_changes

def init_hooks():
    """Initializes the hooks"""
    try:
        # Adds the necessary hooks
        gui_hooks.reviewer_did_show_question.append(closet_note_updater.on_review_card)
        gui_hooks.deck_browser_will_render_content.append(closet_note_updater.on_deck_browser)
        gui_hooks.overview_will_render_content.append(closet_note_updater.on_overview_will_render_content)
        gui_hooks.addcards_did_change_note_type.append(closet_note_updater.on_addcards_did_change_note_type)
        gui_hooks.editor_will_munge_html.append(closet_note_updater.on_editor_will_munge_html)

    except Exception as e:
        showInfo(f"Error in init_hooks: {str(e)}")
