"""Setup configuration for reverse-engineer package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="re-cue",
    version="0.3.4",
    description="RE-cue: Universal reverse engineering toolkit for multi-framework codebases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="RE-cue Project",
    author_email="",
    url="https://github.com/cue-3/re-cue",
    packages=find_packages(),
    package_data={
        'reverse_engineer': [
            'templates/**/*.md',
            'templates/**/*.json',
            'templates/**/*.yaml',
        ],
    },
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "pyyaml>=6.0",
        "jinja2>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "recue=reverse_engineer.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Quality Assurance",
    ],
    keywords="reverse-engineering specification documentation api openapi",
)
