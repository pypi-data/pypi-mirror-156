from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

with open('requirements/requirements.txt') as f:
    requirements = f.readlines()

setup(
    name='whist-core',
    version='0.2.0',
    author='Whist Team',
    description='Game implementation of Whist.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Whist-Team/Whist-Core',
    project_urls={
        'Bug Tracker': 'https://github.com/Whist-Team/Whist-Core/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    keywords='game whist',
    packages=find_packages(exclude=('tests*',)),
    namespace_package=['whist'],
    python_requires='>=3.9',
    install_requires=requirements,
    extras_require={
        "testing": [
            "pytest==7.1.2",
            "pytest-cov==3.0.0",
            "pytest-asyncio==0.18.3"
        ]
    },
)
