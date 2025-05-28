from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="stripesnoop",
    version="2.0.0",
    author="Acidus",
    author_email="acidus@msblabs.net",
    description="Stripe Snoop - Magstripe Card Reader and Analyzer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/msblabs/stripesnoop",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        # Core dependencies
        'pyserial>=3.5',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
            'mypy>=0.900',
            'sphinx>=4.0.0',
            'sphinx-rtd-theme>=1.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'stripesnoop=stripesnoop.main:main',
        ],
    },
)
