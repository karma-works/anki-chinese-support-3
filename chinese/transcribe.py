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

from re import findall, IGNORECASE, search, split, sub
from unicodedata import lookup, name, normalize

from .bopomofo import bopomofo
from .consts import (
    BOPOMOFO_REGEX,
    CHINESE_PUNC_TO_LATIN,
    DIACRITIC_NAME_TO_NUM,
    HANZI_REGEX,
    JYUTPING_REGEX,
    NOT_PINYIN_REGEX,
    PINYIN_REGEX,
    PINYIN_VOWELS,
    TONE_NUMBERS,
    TONE_NUM_REGEX,
)
from .hanzi import has_hanzi
from .log import log
from .main import dictionary
from .ruby import has_ruby, ruby_bottom, ruby_top, separate_ruby
from .util import cleanup, is_punc, no_color


def convert_punc(a):
    converted = []
    for s in a:
        if s in CHINESE_PUNC_TO_LATIN:
            converted.append(CHINESE_PUNC_TO_LATIN[s])
        else:
            converted.append(s)
    return converted


def is_sentence(s):
    if len(s) > 6:
        return True
    for c in s:
        if is_punc(c):
            return True
    return False


def transcribe(words, target, type_):
    try:
        assert isinstance(words, list)

        if target == 'pinyin':
            prefer_tw = False
        elif target in ['pinyin_tw', 'bopomofo']:
            prefer_tw = True
        elif target != 'jyutping':
            error_msg = f"Unsupported target for transcribe: {target}"
            log.error(error_msg)
            # Return empty list instead of raising
            return []

        transcribed = []

        if not list(filter(has_hanzi, words)):
            return transcribed

        for text in words:
            try:
                text = cleanup(text)

                if not has_hanzi(text):
                    transcribed.append(text)
                    continue

                try:
                    if target in ['pinyin', 'pinyin_tw', 'bopomofo']:
                        s = dictionary.get_pinyin(text, type_, prefer_tw)
                    elif target == 'jyutping':
                        s = dictionary.get_cantonese(text, type_)
                    else:
                        log.warning("Unknown target %r in transcribe, skipping %r", target, text)
                        transcribed.append(text)
                        continue
                except Exception as e:
                    log.exception("Error getting transcription for %r (target: %r, type: %r)", text, target, type_)
                    # Skip this word on error
                    transcribed.append(text)
                    continue

                try:
                    if target == 'bopomofo':
                        transcribed.extend(bopomofo([s]))
                    else:
                        transcribed.append(s)
                except Exception as e:
                    log.exception("Error processing bopomofo for %r", s)
                    # Fallback to original transcription
                    transcribed.append(s)
            except Exception as e:
                log.exception("Error processing word %r in transcribe", text)
                # Add original text on error
                transcribed.append(text if isinstance(text, str) else '')

        return convert_punc(transcribed)
    except Exception as e:
        log.exception("Error in transcribe for words %r, target %r, type %r", words, target, type_)
        # Return empty list or original words as fallback
        if isinstance(words, list):
            return words
        return []


def transcribe_char(hanzi, target, type_):
    if target == 'pinyin':
        return dictionary.get_pinyin(hanzi, type_)
    if target == 'pinyin_tw':
        return dictionary.get_pinyin(hanzi, type_, prefer_tw=True)
    if target == 'jyutping':
        return dictionary.get_cantonese(hanzi, type_)
    if target == 'bopomofo':
        return bopomofo(dictionary.get_pinyin(hanzi, type_, prefer_tw=True))

    raise NotImplementedError(target)


def accentuate(text, target):
    assert isinstance(text, list)

    if target not in ['pinyin', 'pinyin_tw']:
        return text

    accentuated = []

    def _accentuate(word):
        if not search('[12345]', word):
            return word

        word = no_color(word)
        tone = tone_number(word)
        word = word[:-1]

        if tone == '5':
            return word

        for k, v in DIACRITIC_NAME_TO_NUM.items():
            if v == tone:
                diacritic = lookup(k)
                break

        vowel = '([aeiouüv])'
        n_vowels = len(findall(vowel, word, IGNORECASE))
        if n_vowels == 1:
            s = sub(vowel, f'\\1{diacritic}', word)
        elif search('ao', word):
            s = sub('ao', f'a{diacritic}o', word)
        elif search('(iu|ui)', word):
            s = sub('(iu|ui)', f'\\1{diacritic}', word)
        elif search('[aeo]', word):
            s = sub('([aeo])', f'\\1{diacritic}', word)
        else:
            s = word
        return s

    for word in text:
        s = ' '.join(_accentuate(w) for w in word.split())
        accentuated.append(normalize('NFC', s))

    return accentuated


def replace_tone_marks(pinyin: list) -> list:
    # FIXME
    # test_tone_styling_unspaced assumes that this should preserve space / no space,
    # while all other tests assume that it will insert spaces between syllables.
    assert isinstance(pinyin, list)
    result = []
    for bottom, top in separate_ruby(pinyin):
        a = []
        top = normalize('NFC', top)
        for syllable in split_transcript(top, target='pinyin', grouped=False):
            s = get_tone_number_pinyin(syllable)
            if bottom:
                s = f'{bottom}[{s}]'
            a.append(s)
        result.append(' '.join(a))
    return result


def get_tone_number_pinyin(syllable):
    assert isinstance(syllable, str)

    if (
        search(TONE_NUM_REGEX, syllable)
        or search(BOPOMOFO_REGEX, syllable)
        or is_punc(syllable)
    ):
        return syllable

    if has_ruby(syllable):
        s = ruby_bottom(syllable) + '['
        syllable = ruby_top(syllable)
    else:
        s = ''

    tone = '5'
    for c in normalize('NFD', syllable):
        if name(c) in DIACRITIC_NAME_TO_NUM:
            tone = DIACRITIC_NAME_TO_NUM[name(c)]
        else:
            s += c

    if '[' in s:
        s += ']'

    return normalize('NFC', s + tone)


def split_transcript(transcript, target, grouped=True):
    try:
        assert isinstance(transcript, str)

        if target not in ['pinyin', 'pinyin_tw', 'jyutping']:
            error_msg = f"Unsupported target for split_transcript: {target}"
            log.error(error_msg)
            # Return transcript as single item instead of raising
            return [transcript] if grouped else transcript.split()

        def _split(pattern, s):
            try:
                if search(f'^{pattern}$', s, IGNORECASE):
                    return s

                remainder = s.replace("'", '')
                done = []
                while True:
                    found = False
                    for i in range(len(remainder), 0, -1):
                        if search(f'^{pattern}$', remainder[:i], IGNORECASE):
                            done.append(remainder[:i])
                            remainder = remainder[i:]
                            found = True
                            break
                    if found and remainder:
                        continue
                    elif remainder:
                        done.append(remainder)
                        break
                    else:
                        break
                return ' '.join(done)
            except Exception as e:
                log.exception("Error in split_transcript._split for pattern %r, text %r", pattern, s)
                # Return original text on error
                return s

        separated = []

        for text in split(NOT_PINYIN_REGEX, transcript):
            try:
                if target in ['pinyin', 'pinyin_tw']:
                    text = _split(PINYIN_REGEX, text)
                elif target == 'jyutping':
                    text = _split(JYUTPING_REGEX, text)

                if grouped:
                    separated.append(text)
                else:
                    separated.extend(text.split())
            except Exception as e:
                log.exception("Error processing text %r in split_transcript", text)
                # Add original text on error
                separated.append(text)

        return list(filter(lambda s: s.strip(), separated))
    except Exception as e:
        log.exception("Error in split_transcript for transcript %r, target %r", transcript, target)
        # Return safe fallback
        if isinstance(transcript, str):
            return [transcript] if grouped else transcript.split()
        return []


def tone_number(s):
    try:
        assert isinstance(s, str)

        try:
            s, *_ = replace_tone_marks([cleanup(s)])
        except Exception as e:
            log.exception("Error in replace_tone_marks for %r in tone_number", s)
            # Continue with original s

        try:
            if search(f'[¹²³⁴]$', s):
                return str(' ¹²³⁴'.index(s[-1:]))
        except (ValueError, IndexError) as e:
            log.debug("Could not find tone superscript in %r", s)

        try:
            if search(f'[{TONE_NUMBERS}]$', s):
                return s[-1]
        except (IndexError, AttributeError) as e:
            log.debug("Could not extract tone number from %r", s)

        try:
            if search(BOPOMOFO_REGEX, s):
                if search(r'[ˊˇˋ˙]$', s):
                    return str('  ˊˇˋ˙'.index(s[-1]))
                return '1'
        except (ValueError, IndexError) as e:
            log.debug("Could not extract bopomofo tone from %r", s)

        # Default to neutral tone
        return '5'
    except Exception as e:
        log.exception("Error in tone_number for %r", s)
        # Return neutral tone as safe default
        return '5'


def no_tone(text: str):
    assert isinstance(text, str)

    text = no_color(text)
    text, *_ = replace_tone_marks([text])

    def _remove_tone(p):
        return p.group(1) + sub(TONE_NUM_REGEX, '', p.group(2)) + ']'

    if has_ruby(text):
        return sub(r'(%s\[)([^[]+?)\]' % HANZI_REGEX, _remove_tone, text)

    return sub(r'([a-zü]+)%s' % TONE_NUM_REGEX, r'\1', text)


def sanitize_transcript(transcript, target, grouped=False):
    try:
        return ' '.join(
            accentuate(
                split_transcript(cleanup(no_color(transcript)), target, grouped),
                target,
            )
        ).split()
    except Exception as e:
        log.exception("Error in sanitize_transcript for transcript %r, target %r", transcript, target)
        # Return empty list or try to return cleaned transcript
        try:
            cleaned = cleanup(no_color(transcript))
            return [cleaned] if cleaned else []
        except Exception:
            return []
