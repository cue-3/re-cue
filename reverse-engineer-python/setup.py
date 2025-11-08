"""Setup configuration for reverse-engineer package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="reverse-engineer",
    version="1.0.0",
    description="Reverse-engineer specifications from existing codebases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Specify Reverse Engineering",
    author_email="",
    url="https://github.com/quickcue3/specify-reverse",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies required!
    ],
    entry_points={
        "console_scripts": [
            "reverse-engineer=reverse_engineer.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Code Generators",
    ],
    keywords="reverse-engineering specification documentation api openapi",
)
