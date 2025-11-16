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

import sys
from os.path import dirname, join

# Set up exception handling as early as possible
# This must be imported before any other plugin code to catch import errors
try:
    from . import log
    # Exception handlers are now installed via log module initialization
except Exception as e:
    # If we can't even import the log module, write to a fallback log file
    try:
        import traceback
        fallback_log_path = join(dirname(__file__), 'anki-chinese-support-import-error.log')
        with open(fallback_log_path, 'a', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("CRITICAL: Failed to import log module\n")
            f.write(f"Error: {e}\n")
            f.write(traceback.format_exc())
            f.write("\n")
    except:
        # If even the fallback fails, there's nothing we can do
        pass
    raise

sys.path.append(join(dirname(__file__), 'lib'))

# Now import and load main module with exception handling
try:
    from . import main
    main.load()
except Exception as e:
    # Log import/load errors
    try:
        log.exception("Failed to load plugin")
    except:
        # If log is not available, try fallback
        try:
            import traceback
            fallback_log_path = join(dirname(__file__), 'anki-chinese-support-import-error.log')
            with open(fallback_log_path, 'a', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("CRITICAL: Failed to load plugin\n")
                f.write(f"Error: {e}\n")
                f.write(traceback.format_exc())
                f.write("\n")
        except:
            pass
    # Re-raise so Anki knows the plugin failed to load
    raise
