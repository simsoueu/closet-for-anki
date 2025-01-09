from aqt import mw
from .closet_note_updater import closet_note_updater
from .hooks import init_hooks

from .control import closet_controller

from aqt import mw

mw.addonManager.setWebExports(__name__, r"web.*")

def init():
    init_hooks()
    closet_controller
    closet_note_updater.init()

init()
