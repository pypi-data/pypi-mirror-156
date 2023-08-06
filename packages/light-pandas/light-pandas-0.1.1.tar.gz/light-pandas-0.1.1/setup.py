import os
from setuptools import find_packages, setup


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


if __name__ == '__main__':
    setup(
        name='light-pandas',
        packages=find_packages(),
        version='0.1.1',
        description='Light weight Pandas library',
        long_description=long_description,
        author='bomb_hero',
        license='MIT',
        url='https://github.com/bombhero/LightPandas',

    )
