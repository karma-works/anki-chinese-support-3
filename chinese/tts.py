# Copyright © 2012 Roland Sieker <ospalh@gmail.com>
# Copyright © 2012 Thomas TEMPÉ <thomas.tempe@alysse.org>
# Copyright © 2017 Pu Anlai <https://github.com/InspectorMustache>
# Copyright © 2019 Oliver Rice <orice@apple.com>
# Copyright © 2017-2021 Joseph Lorimer <joseph@lorimer.me>
# Inspiration: Tymon Warecki
# License: GNU AGPL, version 3 or later; http://www.gnu.org/copyleft/agpl.html

import ssl
from os.path import basename, exists, join
from re import sub
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import requests
from aqt import mw
from gtts import gTTS
from gtts.tts import gTTSError

from .aws import AWS4Signer
from .log import log

requests.packages.urllib3.disable_warnings()


class AudioDownloader:
    def __init__(self, text, source='google|zh-CN'):
        try:
            self.text = text
            if source.count('|') != 1:
                raise ValueError("Invalid source format (expected 'service|lang'): {}".format(source))
            self.service, self.lang = source.split('|')
            self.path = self.get_path()
            self.func = {
                'google': self.get_google,
                'baidu': self.get_baidu,
                'aws': self.get_aws,
            }.get(self.service)
        except Exception as e:
            log.info("Error initializing AudioDownloader for %r with source %r: %s", text, source, e)
            raise

    def get_path(self):
        try:
            filename = '{}_{}_{}.mp3'.format(
                self.sanitize(self.text), self.service, self.lang
            )
            return join(mw.col.media.dir(), filename)
        except Exception as e:
            log.info("Error getting media path for %r: %s", self.text, e)
            raise

    def sanitize(self, s):
        return sub(r'[/:*?"<>|]', '', s)

    def download(self):
        if exists(self.path):
            return basename(self.path)

        if not self.func:
            error_msg = "Service not implemented: {}".format(self.service)
            log.error(error_msg)
            raise NotImplementedError(self.service)

        try:
            self.func()
            return basename(self.path)
        except Exception as e:
            # Log any download failures as info (not errors, since TTS can be unreliable)
            log.info("Could not download audio for %r using %s: %s", self.text, self.service, e)
            # Re-raise so sound() can handle it appropriately
            raise

    def get_google(self):
        tts = gTTS(self.text, lang=self.lang, tld='com')
        try:
            tts.save(self.path)
        except gTTSError as e:
            log.info("Could not download audio for %r using gTTS: %s", self.text, e)
            # Re-raise so download() knows it failed
            raise

    def get_baidu(self):
        query = {
            'lan': self.lang,
            'ie': 'UTF-8',
            'text': self.text.encode('utf-8'),
            'spd': 2,
            'source': 'web',
        }

        url = 'https://fanyi.baidu.com/gettts?' + urlencode(query)
        request = Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')

        # baidu web server seems to behave nondeterministically when the alpn extension is not supplied where it
        # sometimes returns 200 OK but with Content-Length 0
        # when the extension is sent, the audio/mpeg content is returned as expected
        # automatically sending the alpn extension was added in python 3.10, but Anki is currently using 3.9
        context = ssl.create_default_context()
        context.set_alpn_protocols(['http/1.1'])

        try:
            with urlopen(request, context=context, timeout=5) as response, open(self.path, 'wb') as audio:
                if response.code != 200:
                    error_msg = 'Baidu TTS request failed: {}: {}'.format(response.code, response.msg)
                    log.info("Could not download audio for %r using Baidu: %s", self.text, error_msg)
                    raise ValueError(error_msg)

                bytes_response = response.read()
                audio.write(bytes_response)
        except Exception as e:
            log.info("Could not download audio for %r using Baidu: %s", self.text, e)
            raise

    def get_aws(self):
        try:
            signer = AWS4Signer(service='polly')
            signer.use_aws_profile('chinese_support_redux')

            url = 'https://polly.%s.amazonaws.com/v1/speech' % (signer.region_name)
            query = {
                'OutputFormat': 'mp3',
                'Text': self.text,
                'VoiceId': self.lang,
            }

            response = requests.post(url, json=query, auth=signer)

            if response.status_code != 200:
                error_msg = 'Polly Request Failed: Error Code {}'.format(
                    response.status_code
                )
                log.info("Could not download audio for %r using AWS Polly: %s", self.text, error_msg)
                raise ValueError(error_msg)

            with open(self.path, 'wb') as audio:
                audio.write(response.content)
        except Exception as e:
            log.info("Could not download audio for %r using AWS Polly: %s", self.text, e)
            raise
