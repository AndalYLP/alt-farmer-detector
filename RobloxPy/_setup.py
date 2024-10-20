from setuptools import setup, find_packages

setup(
    name="RobloxPy",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "aiohttp",
    ],
    python_requires='>=3.8',
)
