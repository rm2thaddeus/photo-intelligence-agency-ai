import os
from setuptools import setup, find_packages

setup(
    name="MediaManager",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "torch",
        "transformers",
        "qdrant-client",
        "Pillow",
        "ffmpeg-python",
        "scenedetect",
        "python-dotenv"
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A package for managing and processing media files",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
) 