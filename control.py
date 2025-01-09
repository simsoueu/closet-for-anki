# controller.py
from aqt import mw
from aqt.utils import showInfo
from aqt import gui_hooks
import json
import os
import re
import logging
from .view import ClosetConfigDialog, ClosetMenu

class ClosetController:
    COLOR_MAP = {
        "Blue": "#3f8cf1",
        "Red": "#8f0710",
        "Yellow": "#f1c40f",
        "Green": "#177d05",
        "Purple": "#6f0d6f",
        "Orange": "#d36f03",
    }

    def __init__(self, note_type_name='Closet-r'):
        self.note_type_name = note_type_name
        self.logger = logging.getLogger(__name__)
        self.config_path = os.path.join(mw.pm.addonFolder(), "closet_note_type_reloaded", "config.json")
        self.setup()

    def setup(self):
        self.menu = ClosetMenu(
            on_update_cards=lambda: self.update_all_notes(silent=False),
            on_open_settings=self.open_config_dialog
        )
        self.menu.setup_menu()

    def load_config(self):
        """Loads the configuration from the file"""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                return json.load(f)
        return {
            "closet_color": "Blue",
            "highlight_all_cloze": False,
            "show_deck_name": True
        }

    def save_config(self, config):
        """Saves the configuration to the file"""
        with open(self.config_path, "w") as f:
            json.dump(config, f)

    def apply_css(self, color_name, highlight_all_cloze, show_deck_name):
        """Applies the selected color to the CSS and configures the visibility of the deck name"""
        color = self.COLOR_MAP.get(color_name, "#3f8cf1")
        model = mw.col.models.by_name(self.note_type_name)

        # Remove existing closet-tag-color style
        for template in model['tmpls']:
            for field in ['qfmt', 'afmt']:
                if field in template:
                    template[field] = re.sub(
                        r'<style id="closet-tag-color">.*?</style>',
                        '',
                        template[field],
                        flags=re.DOTALL
                    )

        # Create new style based on settings
        new_style = self._generate_style(color, highlight_all_cloze)

        # Apply new style
        for template in model['tmpls']:
            for field in ['qfmt', 'afmt']:
                if field in template:
                    template[field] = template[field] + "\n" + new_style

        # Update deck name visibility
        self._update_deck_name_visibility(model, show_deck_name)

        # Save changes and update hooks
        mw.col.models.save(model)
        self._update_hooks()

    def _generate_style(self, color, highlight_all_cloze):
        if highlight_all_cloze:
            return f"""<style id="closet-tag-color">
    .closet-cloze.is-active.is-front,
    .cl--obscure,
    .closet-cloze.is-inactive .closet-cloze__answer,
    .closet-cloze__answer {{
        color: {color} !important;
    }}</style>"""
        else:
            return f"""<style id="closet-tag-color">
    .closet-cloze.is-active,
    .cl--obscure {{
        color: {color} !important;
    }}
    .closet-cloze.is-inactive .closet-cloze__answer,
    .closet-cloze__answer {{
        color: var(--text-color);
    }}</style>"""

    def _update_deck_name_visibility(self, model, show_deck_name):
        deck_name_css = f"""
        .deck-name {{
            opacity: {"1" if show_deck_name else "0"};
            transition: opacity 0.3s ease;
        }}
        """
        model['css'] = re.sub(r'\.deck-name\s*\{[^}]*\}', '', model['css'])
        if "<style>" in model['css']:
            model['css'] = re.sub(r'<style>.*?</style>', deck_name_css, model['css'],
                                flags=re.DOTALL)
        else:
            model['css'] += f"\n{deck_name_css}"

    def _update_hooks(self):
        from .closet_note_updater import closet_note_updater
        gui_hooks.reviewer_did_show_question.append(closet_note_updater.on_review_card)

    def open_config_dialog(self):
        """Opens the configuration dialog"""
        try:
            config = self.load_config()
            config["COLOR_MAP"] = self.COLOR_MAP

            dialog = ClosetConfigDialog(
                parent=mw,
                current_config=config,
                on_save=self._handle_config_save
            )
            dialog.exec()
        except Exception as e:
            showInfo(f"Error opening config dialog: {str(e)}")

    def _handle_config_save(self, new_config):
        self.save_config(new_config)
        self.apply_css(
            new_config["closet_color"],
            new_config["highlight_all_cloze"],
            new_config["show_deck_name"]
        )

        # Refresh current card if in review
        if mw.reviewer and mw.reviewer.card:
            mw.reviewer.show()

    def update_all_notes(self, silent=False):
        """Updates all notes (implementation needed)"""
        pass  # Implement the update_all_notes functionality here

# Initialize the controller
closet_controller = ClosetController()