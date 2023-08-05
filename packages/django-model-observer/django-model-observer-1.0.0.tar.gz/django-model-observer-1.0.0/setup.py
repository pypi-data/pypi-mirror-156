# coding: utf-8
from pathlib import Path

from setuptools import find_packages
from setuptools import setup


setup(
    name='django-model-observer',
    author="BARS Group",
    author_email='education_dev@bars-open.ru',
    description='Наблюдатель за моделями Django',
    url=(
        'https://stash.bars-open.ru/projects/'
        'EDUBASE/repos/django-model-observer/'
    ),
    classifiers=[
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Natural Language :: Russian',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',
        'Framework :: Django :: 3.1',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
    ],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    dependency_links=(
        'http://pypi.bars-open.ru/simple/m3-builder',
    ),
    setup_requires=(
        'm3-builder>=1.2,<2',
    ),
    install_requires=(
        'six>=1.11,<2',
        'Django>=2.2,<4.1',
    ),
    set_build_info=Path(__file__).parent,
)
