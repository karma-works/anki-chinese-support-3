# Copyright © 2012 Thomas TEMPÉ <thomas.tempe@alysse.org>
# Copyright © 2017-2019 Joseph Lorimer <joseph@lorimer.me>
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

from re import findall, sub

from .consts import SOUND_TAG_REGEX
from .hanzi import has_hanzi
from .log import log
from .main import config
from .tts import AudioDownloader


def sound(hanzi, source=None):
    """Returns sound tag for a given Hanzi string."""

    from .ruby import ruby_bottom, has_ruby

    if not has_hanzi(hanzi):
        return ''

    if not source:
        source = config['speech']

    if not source:
        return ''

    if source.count('|') != 1:
        error_msg = "Invalid source format (expected 'service|lang'): {}".format(source)
        log.error(error_msg)
        raise ValueError(error_msg)

    if has_ruby(hanzi):
        hanzi = ruby_bottom(hanzi)

    if not hanzi:
        return ''

    if source:
        try:
            return '[sound:%s]' % AudioDownloader(hanzi, source).download()
        except Exception as e:
            # Audio download failed - log as info and return empty string
            # This is expected behavior when TTS services are unavailable
            log.info("Audio download failed for %r: %s", hanzi, e)
            return ''

    return ''


def extract_tags(text):
    tags = findall(SOUND_TAG_REGEX, text)
    if not tags:
        return text, ''
    return no_sound(text), ''.join(tags)


def no_sound(text):
    return sub(SOUND_TAG_REGEX, '', text)
