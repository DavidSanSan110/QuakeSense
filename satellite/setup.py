import io
from setuptools import setup, find_packages


def readme():
    with io.open('README.md', encoding='utf-8') as f:
        return f.read()


def requirements(filename):
    reqs = list()
    with io.open(filename, encoding='utf-8') as f:
        for line in f.readlines():
            yield line.strip()


setup(
    name='api_satellite',
    version='1.0',
    packages=find_packages(),
    url="https://github.com/DavidSanSan110",
    author='David Sánchez Sánchez',
    author_email='davidsansan@usal',
    description='',
    long_description=readme(),
    long_description_content_type='text/markdown',
    install_requires=requirements(filename='requirements.txt'),
    data_files=[],
    entry_points={
        'console_scripts': [
            'api_satellite=api_satellite.run:main'
        ],
    },
    include_package_data=True,
    python_requires='>=3',
    project_urls={
        'Bug Reports': 'https://github.com/DavidSanSan110',
        'Source': 'https://github.com/DavidSanSan110',
    },
)