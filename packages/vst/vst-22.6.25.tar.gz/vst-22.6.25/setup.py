# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['vst', 'vst.classes', 'vst.translation']

package_data = \
{'': ['*']}

install_requires = \
['SpeechRecognition>=3.8.1,<4.0.0',
 'ffmpeg-python>=0.2.0,<0.3.0',
 'phonemizer>=3.2.1,<4.0.0',
 'pydub>=0.25.1,<0.26.0',
 'requests>=2.28.0,<3.0.0']

entry_points = \
{'console_scripts': ['vst_audio_to_wav = vst.audio_to_wav:main',
                     'vst_en_to_pl = vst.en_to_pl:main',
                     'vst_wav_to_text = vst.wav_to_text:main']}

setup_kwargs = {
    'name': 'vst',
    'version': '22.6.25',
    'description': 'VST - Voice Simple Tools',
    'long_description': '# VST (Voice Simple Tools)\n\nPlease check [WIKI](https://github.com/8tm/vst/wiki) pages for project description.\n',
    'author': 'Tadeusz Miszczyk',
    'author_email': '42252259+8tm@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://github.com/8tm/vst',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.13,<4.0.0',
}


setup(**setup_kwargs)
