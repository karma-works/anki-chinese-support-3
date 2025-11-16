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

from re import IGNORECASE, search, sub

from .consts import (
    BOPOMOFO_REGEX,
    COLOR_RUBY_TEMPLATE,
    COLOR_TEMPLATE,
    HALF_RUBY_REGEX,
    HANZI_RANGE,
    JYUTPING_REGEX,
    PINYIN_REGEX,
    RUBY_REGEX,
)
from .hanzi import split_hanzi
from .log import log
from .sound import extract_tags
from .transcribe import tone_number, sanitize_transcript
from .util import align, is_punc, no_color


def colorize(words, target='pinyin', ruby_whole=False):
    from .ruby import has_ruby

    try:
        assert isinstance(words, list)

        def _repl(p):
            try:
                return COLOR_TEMPLATE.format(
                    tone=tone_number(p.group(1)), chars=p.group()
                )
            except Exception as e:
                log.exception("Error calculating tone in colorize._repl for %r", p.group(1))
                # Return default tone5 on error
                return COLOR_TEMPLATE.format(tone='5', chars=p.group())

        done = []

        d = {
            'pinyin': PINYIN_REGEX,
            'pinyin_tw': PINYIN_REGEX,
            'jyutping': JYUTPING_REGEX,
            'bopomofo': BOPOMOFO_REGEX,
        }

        for word in words:
            try:
                (word, sound_tags) = extract_tags(no_color(word))

                if target in d:
                    pattern = d[target]
                    text = ''
                    for syllable in word.split():
                        try:
                            if search(f'^{pattern}$', syllable):
                                text += sub(f'^{pattern}$', _repl, syllable, IGNORECASE)
                            elif has_ruby(syllable):
                                if ruby_whole:
                                    pattern = RUBY_REGEX
                                else:
                                    pattern = HALF_RUBY_REGEX
                                text += sub(pattern, _repl, syllable, IGNORECASE)
                            else:
                                text += f'<span class="tone5">{syllable}</span>'
                        except Exception as e:
                            log.exception("Error processing syllable %r in colorize", syllable)
                            # Fallback to tone5 for this syllable
                            text += f'<span class="tone5">{syllable}</span>'
                else:
                    error_msg = f"Unsupported target for colorize: {target}"
                    log.error(error_msg)
                    # Return words with default tone5 instead of raising
                    return ' '.join(f'<span class="tone5">{w}</span>' for w in words)

                done.append(text + sound_tags)
            except Exception as e:
                log.exception("Error processing word %r in colorize", word)
                # Fallback: return word with default tone5
                done.append(f'<span class="tone5">{word}</span>')

        return ' '.join(done)
    except Exception as e:
        log.exception("Error in colorize for words %r, target %r", words, target)
        # Return safe fallback
        if isinstance(words, list):
            return ' '.join(f'<span class="tone5">{w}</span>' for w in words)
        return ''


def colorize_dict(text):
    try:
        assert isinstance(text, str)

        def _sub(p):
            try:
                s = ''
                hanzi = p.group(1)
                pinyin = sanitize_transcript(p.group(2), 'pinyin', grouped=False)
                delim = '|'

                if hanzi.count(delim) == 1:
                    hanzi = hanzi.split(delim)
                    s += colorize_fuse(
                        split_hanzi(hanzi[0], grouped=False), pinyin, True
                    )
                    s += delim
                    s += colorize_fuse(
                        split_hanzi(hanzi[1], grouped=False), pinyin, False
                    )
                else:
                    s += colorize_fuse(split_hanzi(hanzi, grouped=False), pinyin, True)

                return s
            except Exception as e:
                log.exception("Error in colorize_dict._sub for %r", p.group(0))
                # Return uncolored text on error
                return p.group(0)

        return sub(r'([\%s|]+)\[(.*?)\]' % HANZI_RANGE, _sub, text)
    except Exception as e:
        log.exception("Error in colorize_dict for text %r", text)
        # Return original text on error
        return text if isinstance(text, str) else ''


def colorize_fuse(chars: list, trans: list, ruby=False):
    try:
        assert isinstance(chars, list)
        assert isinstance(trans, list)

        colorized = ''

        for c, t in align(chars, trans):
            try:
                if c is None or t is None:
                    continue
                if is_punc(c) and is_punc(t):
                    colorized += c
                    continue
                try:
                    tone = tone_number(t)
                except Exception as e:
                    log.exception("Error calculating tone_number for %r in colorize_fuse", t)
                    tone = '5'  # Default to neutral tone
                
                if ruby:
                    colorized += COLOR_RUBY_TEMPLATE.format(
                        tone=tone, chars=c, trans=t
                    )
                else:
                    colorized += COLOR_TEMPLATE.format(tone=tone, chars=c)
            except Exception as e:
                log.exception("Error processing char %r, trans %r in colorize_fuse", c, t)
                # Fallback: add char with default tone5
                if c:
                    colorized += COLOR_TEMPLATE.format(tone='5', chars=c)

        return colorized
    except Exception as e:
        log.exception("Error in colorize_fuse for chars %r, trans %r, ruby %r", chars, trans, ruby)
        # Return uncolored chars as fallback
        if isinstance(chars, list):
            return ''.join(c if c else '' for c in chars)
        return ''
