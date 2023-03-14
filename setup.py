from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

#with open('HISTORY.md') as history_file:
#    HISTORY = history_file.read()

setup_args = dict(
    name='srt_equalizer',
    version='0.0.1',
    description='Adjust line lengths of subtitles in SRT format.',
    long_description_content_type="text/markdown",
    long_description=README,
    license='MIT',
    packages=["srt_equalizer"],
    author='Peter Krantz',
    author_email='peter.krantzn@gmail.com',
    keywords=['SRT', 'Subtitles', 'Closed captions', 'Whisper'],
    url='https://www.peterkrantz.com',
    download_url='https://pypi.org/project/srt_equalizer/'
)

install_requires = [
    "setuptools>=61.0", 
    "srt>=3.5.2"
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)