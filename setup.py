from pathlib import Path

from setuptools import find_packages, setup

with open(Path(__file__).resolve().parent / "README.md") as f:
    readme = f.read()

setup(
    name="clip_for_me",
    url="https://github.com/plt3/clip_for_me",
    author="Paul Taylor",
    description="Download YouTube videos and clip timestamps from them just by writing Markdown",
    long_description=readme,
    long_description_content_type="text/markdown",
    package_dir={"": "src"},
    packages=find_packages(
        where="src",
        include=["clip_for_me*"]
    ),
    install_requires=[
        "jsonschema>=4.17",
        "moviepy>=1",
        "markdown-to-json>=1.1",
        "yt-dlp>=2023.3",
    ],
    python_requires=">=3.8, <4.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    entry_points = {
        "console_scripts": ["clip-for-me=clip_for_me.cli:main"],
    },
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
)
