with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

from distutils.core import setup

setup(
  name = 'Fliicoin',
  packages = ['Fliicoin'],
  version = '0.1.13',
  license='MIT',
  description = 'Useful API commands to interact with the fliicoin network.',
  long_description_content_type="text/markdown",
long_description=README + '\n\n' + HISTORY,
  author = 'Fliicoin',
  author_email = 'admin@fliicoin.com',
  url = 'https://github.com/Fliicoin/Fliicoin-API',
  download_url = 'https://pypi.org/project/Fliicoin/',
  keywords = ['Fliicoin', 'Flii', 'Fliic', 'Fliicoin.com', 'Fliicoin api', 'Flii api'],
  install_requires=[
          'urllib',
          'urllib.request',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
  ],
)