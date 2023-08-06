from distutils.core import setup
setup(
  name = 'reading_poetry',
  packages = ['reading_poetry'],
  version = '0.1.9',
  license='MIT',
  description = 'Tool for the computational analysis of poetry',
  package_data={'reading_poetry': ['pronunciationDictionary.json']},
  include_package_data=True ,
  author = 'Peter Verhaar',
  author_email = 'peter.verhaar@gmail.com',
  url = 'https://github.com/peterverhaar/reading_poetry',
  download_url = 'https://github.com/peterverhaar/reading_poetry/archive/refs/tags/0.1.9.tar.gz',
  keywords = ['NLP', 'Digital Humanities', 'Text Mining','Computational literary studies'],
  install_requires=[],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7'
  ],
)
