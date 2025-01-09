from aqt import mw
from aqt.utils import showInfo
from aqt.qt import QAction
from aqt import gui_hooks
import re
import logging

class ClosetNoteUpdater:
    def __init__(self, note_type_name='Closet-r'):
        self.note_type_name = note_type_name
        self.logger = logging.getLogger(__name__)

    def count_tags(self, text):
        """Conta o número de tags [[c]], [[cl]], [[cx]], [[mix]] e [[mc]] no texto e retorna o maior número encontrado"""
        if not text:
            return 0
        matches = re.findall(r'\[\[(?:c|cl|cx|mix|mc)(\d+)::', text)
        return max(map(int, matches)) if matches else 0

    def reorganize_tags(self, text):
        """Reorganiza as tags c para que c6, c4 e c9 sejam tratados como c1, c2 e c3"""
        tags = re.findall(r'\[\[c(\d+)::', text)
        tags = sorted(set(map(int, tags)))
        tag_map = {old: new for new, old in enumerate(tags, start=1)}
        for old, new in tag_map.items():
            text = re.sub(rf'\[\[c{old}::', rf'[[c{new}::', text)
        return text

    def ensure_fields_exist(self, note, max_tag_num):
        """Garante que os campos cmds existam no modelo de nota"""
        model = mw.col.models.get(note.mid)
        field_names = [field['name'] for field in model['flds']]
        for i in range(1, max_tag_num + 1):
            field_name = f'cmds{i}'
            if field_name not in field_names:
                mw.col.models.addField(model, mw.col.models.newField(field_name))
        mw.col.models.save(model)

    def update_cmds_fields(self, note, silent=False):
        """Atualiza os campos cmds baseado no número de tags encontradas"""
        if not note or note.note_type()['name'] != self.note_type_name:
            return False

        try:
            block_content = note['block']
            if not isinstance(block_content, str):
                return False

            # Reorganiza as tags c
            block_content = self.reorganize_tags(block_content)

            # Renomeia a tag mix para mix sem numeração se houver apenas uma
            mix_tags = re.findall(r'\[\[mix(\d*)::', block_content)
            if len(mix_tags) == 1:
                block_content = re.sub(r'\[\[mix\d*::', r'[[mix::', block_content)

            note['block'] = block_content

            max_tag_num = self.count_tags(block_content)
            self.ensure_fields_exist(note, max_tag_num)
            changed = False

            # Atualiza todos os campos cmds existentes até o maior número de tag encontrado
            for i in range(1, max_tag_num + 1):
                field_name = f'cmds{i}'
                # Define como 'active'
                if note[field_name] != 'active':
                    note[field_name] = 'active'
                    changed = True

            # Desativa campos cmds que não devem estar ativos
            for i in range(max_tag_num + 1, 100):  # Assume um limite de 100 campos cmds
                field_name = f'cmds{i}'
                if field_name in note and note[field_name] == 'active':
                    note[field_name] = ''
                    changed = True

            if changed:
                mw.col.update_note(note)
                return True
            return False
        except Exception as e:
            if silent:
                self.logger.error(f"Error updating fields: {str(e)}")
            else:
                showInfo(f"Error updating fields: {str(e)}")
            return False

    def update_all_notes(self, silent=False):
        """Atualiza todas as notas do tipo especificado"""
        try:
            note_ids = mw.col.find_notes(f"note:{self.note_type_name}")
            for note_id in note_ids:
                note = mw.col.get_note(note_id)
                self.update_cmds_fields(note, silent=silent)
            if not silent:
                showInfo(f"All {self.note_type_name} notes have been updated.")
        except Exception as e:
            if silent:
                self.logger.error(f"Error updating {self.note_type_name} notes: {str(e)}")
            else:
                showInfo(f"Error updating {self.note_type_name} notes: {str(e)}")

    def on_deck_browser(self, deck_browser, content):
        """Busca por cartões do tipo especificado e aplica a função update_cmds_fields"""
        self.update_all_notes(silent=True)

    def on_review_card(self, reviewer_or_card):
        """Chamado durante a revisão do cartão"""
        try:
            # Verifica se é um objeto reviewer ou card
            card = reviewer_or_card.card if hasattr(reviewer_or_card, 'card') else reviewer_or_card

            # Verifica se temos um card válido
            if not card:
                return

            # Obtém a nota do cartão
            note = card.note()
            if note and note.note_type()['name'] == self.note_type_name:
                self.update_cmds_fields(note, silent=True)
        except Exception as e:
            pass  # Silenciosamente ignora erros não críticos

    def test_update_cmds_fields(self):
        """Função de teste para verificar se cmds1 está sendo ativado"""
        note = mw.col.newNote()
        note.note_type()['name'] = self.note_type_name
        note['block'] = "To mix (shuffle) cards, there's a few ways to do it.\nMethod #1. To reorganize sentences:\n[[mix1::This is my first sentence]], and here is the rest of the first phrase.\n[[mix1::This is the second sentence]], and here is the last of this second phrase."
        deck_id = mw.col.decks.id("Default")
        mw.col.add_note(note, deck_id)
        self.update_cmds_fields(note)
        assert note['cmds1'] == 'active', "cmds1 should be active"

    def init(self):
        """Inicializa os hooks"""
        try:
            # Adiciona os hooks necessários
            gui_hooks.reviewer_did_show_question.append(self.on_review_card)
            gui_hooks.deck_browser_will_render_content.append(self.on_deck_browser)
            # Adiciona o teste após a coleção estar carregada
            gui_hooks.profile_did_open.append(lambda: mw.progress.single_shot(1000, self.test_update_cmds_fields))
        except Exception as e:
            showInfo(f"Error in init: {str(e)}")

    def on_overview_will_render_content(self, overview, content):
        """Busca por cartões do tipo especificado e aplica a função update_cmds_fields"""
        self.update_all_notes(silent=True)

    def on_addcards_did_change_note_type(self, addcards, old, new):
        """Atualiza os campos cmds baseado no número de tags encontradas"""
        if not new or new.note_type()['name'] != self.note_type_name:
            return False
        self.update_cmds_fields(new, silent=True)

    def on_editor_will_munge_html(self, txt, editor):
        """
        Hook chamado antes do Anki processar o HTML no editor.
        Deve retornar o texto processado ou None para manter o texto original.
        """
        try:
            note = editor.note
            if note and note.note_type()['name'] == self.note_type_name:
                self.update_cmds_fields(note, silent=True)
            return txt  # Retorna o texto original
        except Exception as e:
            self.logger.error(f"Error in on_editor_will_munge_html: {str(e)}")
            return txt

# Instancia o atualizador de notas Closet
closet_note_updater = ClosetNoteUpdater()
