# Copyright © 2017-2018 Joseph Lorimer <joseph@lorimer.me>
#
# This file is part of Chinese Support 3.
#
# Chinese Support 3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Chinese Support 3 is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Chinese Support 3.  If not, see <https://www.gnu.org/licenses/>.

# Import log first to ensure exception handlers are installed
# This must happen before any other imports that might fail
from .log import log, wrap_hook

# Import Anki modules and plugin dependencies with error handling
try:
    # Note: wrap is deprecated but no direct replacement hook exists yet for CollectionStats.todayStats
    # TODO: Replace with gui_hooks when a stats hook becomes available
    from anki.hooks import wrap
    from anki.stats import CollectionStats
    from anki.stdmodels import models
    from aqt import gui_hooks

    from .config import ConfigManager
    from .database import Dictionary

    config = ConfigManager()
    dictionary = Dictionary()

    from .edit import EditManager
    from .graph import todayStats
    from .gui import load_menu, unload_menu
    from .models import advanced, basic
    from .templates import chinese, ruby

    if config['firstRun']:
        dictionary.create_indices()
        config['firstRun'] = False
except ImportError as e:
    log.exception("Failed to import required dependencies (missing module: %s)", e.name if hasattr(e, 'name') else 'unknown')
    raise
except Exception:
    log.exception("Failed to import plugin dependencies")
    raise


def load():
    ruby.install()
    chinese.install()
    # Wrap all hooks with exception logging
    gui_hooks.profile_did_open.append(wrap_hook(load_menu))
    gui_hooks.profile_did_open.append(wrap_hook(add_models))
    gui_hooks.profile_did_open.append(wrap_hook(dictionary.connect))
    gui_hooks.profile_will_close.append(wrap_hook(config.save))
    gui_hooks.profile_will_close.append(wrap_hook(dictionary.close))
    gui_hooks.profile_will_close.append(wrap_hook(unload_menu))
    CollectionStats.todayStats = wrap(
        CollectionStats.todayStats, wrap_hook(todayStats), 'around'
    )
    EditManager()
    log.info("Plugin was started successfully")


def add_models():
    models.append(('Chinese (Advanced)', advanced.add_model))
    models.append(('Chinese (Basic)', basic.add_model))
