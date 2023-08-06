import setuptools

with open('README.md', 'rt') as readme:
    long_description = readme.read()

setuptools.setup(
    name='randomus',
    version='1.0.0',
    author='Chechkenev Andrey (@DarkCat09)',
    author_email='aacd0709@mail.ru',
    description='Парсер русского сервиса генерации имён',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/DarkCat09/randomus',
    project_urls={
        'Bug Tracker': 'https://github.com/DarkCat09/randomus/issues',
        'Bug Tracker 2': 'https://codeberg.org/DarkCat09/randomus/issues'
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent'
    ],
    install_requires=[
        'requests'
    ],
    packages=['randomus'],
    python_requires=">=3.6",
)
