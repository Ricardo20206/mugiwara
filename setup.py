"""Configuration pour l'installation du package."""

from setuptools import find_packages, setup

setup(
    name="chronobio-client",
    version="0.1.0",
    description="Client pour le jeu Chronobio",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="",
    author_email="",
    url="",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "chronobio-client=chronobio_client.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
)












