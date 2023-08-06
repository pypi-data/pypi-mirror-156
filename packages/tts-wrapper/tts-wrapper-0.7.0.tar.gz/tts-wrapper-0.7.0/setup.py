# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tts_wrapper',
 'tts_wrapper.engines',
 'tts_wrapper.engines.google',
 'tts_wrapper.engines.microsoft',
 'tts_wrapper.engines.polly',
 'tts_wrapper.engines.watson']

package_data = \
{'': ['*']}

extras_require = \
{':extra == "watson"': ['PyJWT==1.7.1'],
 'google': ['google-cloud-texttospeech>=2.11.1,<3.0.0'],
 'microsoft': ['requests>=2.28.0,<3.0.0'],
 'polly': ['boto3>=1.24.15,<2.0.0'],
 'watson': ['ibm-watson>=5.0.0,<6.0.0']}

setup_kwargs = {
    'name': 'tts-wrapper',
    'version': '0.7.0',
    'description': 'A hassle-free Python library that allows one to use text-to-speech APIs with the same interface',
    'long_description': '# TTS-Wrapper\n\n![](https://github.com/mediatechlab/tts-wrapper/workflows/Python%20package/badge.svg)\n\n_TTS-Wrapper_ is a hassle-free Python library that allows one to use text-to-speech APIs with the same interface.\n\nCurrently the following services are supported:\n\n- AWS Polly\n- Google TTS\n- Microsoft TTS\n- IBM Watson\n\n## Installation\n\nInstall using pip.\n\n```sh\npip install TTS-Wrapper\n```\n\n**Note: for each service you want to use, you have to install the required packages.**\n\nExample: to use `google` and `watson`:\n\n```sh\npip install TTS-Wrapper[google, watson]\n```\n\n## Usage\n\nSimply instantiate an object from the desired service and call `synth()`.\n\n```Python\nfrom tts_wrapper import PollyTTS\n\ntts = PollyTTS()\ntts.synth(\'<speak>Hello, world!</speak>\', \'hello.wav\')\n```\n\n### Selecting a Voice\n\nYou can change the default voice and lang like this:\n\n```Python\nPollyTTS(voice=\'Camila\', lang=\'pt-BR\')\n```\n\nCheck out the list of available voices for [Polly](https://docs.aws.amazon.com/polly/latest/dg/voicelist.html), [Google](https://cloud.google.com/text-to-speech/docs/voices), [Microsoft](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/rest-text-to-speech#get-a-list-of-voices), and [Watson](https://cloud.ibm.com/docs/text-to-speech?topic=text-to-speech-voices).\n\n### SSML\n\nYou can also use [SSML](https://en.wikipedia.org/wiki/Speech_Synthesis_Markup_Language) markup to control the output.\n\n```Python\ntts.synth(\'<speak>Hello, <break time="3s"/> world!</speak>\', \'hello.wav\')\n```\n\nAs a convenience you can use the `wrap_ssml` function that will create the correct boilerplate tags for each engine:\n\n```Python\ntts.synth(tts.wrap_ssml(\'Hello, <break time="3s"/> world!\'), \'hello.wav\')\n```\n\nLearn which tags are available for each service: [Polly](https://docs.aws.amazon.com/polly/latest/dg/supportedtags.html), [Google](https://cloud.google.com/text-to-speech/docs/ssml), [Microsoft](https://docs.microsoft.com/en-us/cortana/skills/speech-synthesis-markup-language), and [Watson](https://cloud.ibm.com/docs/text-to-speech?topic=text-to-speech-ssml).\n\n### Credentials\n\nTo setup credentials to access each engine, use the `credentials` argument.\n\n#### Polly\n\nIf you don\'t explicitly define credentials, `boto3` will try to find them in your system\'s credentials file or your environment variables. However, you can specify them with a tuple:\n\n```Python\nfrom tts_wrapper import PollyTTS\ntts = PollyTTS(credentials=(region, aws_key_id, aws_access_key))\n```\n\n#### Google\n\nPoint to your [Oauth 2.0 credentials file](https://developers.google.com/identity/protocols/OAuth2) path:\n\n```Python\nfrom tts_wrapper import GoogleTTS\ntts = GoogleTTS(credentials=\'path/to/creds.json\')\n```\n\n#### Microsoft\n\nJust provide your [subscription key](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/rest-text-to-speech#authentication), like so:\n\n```Python\nfrom tts_wrapper import MicrosoftTTS\ntts = MicrosoftTTS(credentials=\'TOKEN\')\n```\n\nIf your region is not the default "useast", you can change it like so:\n\n```Python\ntts = MicrosoftTTS(credentials=\'TOKEN\', region=\'brazilsouth\')\n```\n\n#### Watson\n\nPass your [API key and URL](https://cloud.ibm.com/apidocs/text-to-speech/text-to-speech#authentication) to the initializer:\n\n```Python\nfrom tts_wrapper import WatsonTTS\ntts = WatsonTTS(credentials=(\'API_KEY\', \'API_URL\'))\n```\n\n## License\n\nLicensed under the [MIT License](./LICENSE).\n',
    'author': 'Giulio Bottari',
    'author_email': 'giuliobottari@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mediatechlab/tts-wrapper',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
