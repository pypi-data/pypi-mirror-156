from setuptools import setup, find_packages

requirements = [
    "requests",
    "websocket-client==1.3.1", 
    "setuptools", 
    "json_minify", 
    "six",
    "aiohttp",
    "websockets"
]

with open("README.md", "r") as stream:
    long_description = stream.read()

setup(
    name="amino.sf",
    license='MIT',
    author="sfah",
    version="1.0",
    description="Library for Amino. Telegram- https://t.me/spi22der",
    packages=find_packages(),
    long_description=long_description,
    install_requires=requirements,
    keywords=[
        'aminoapps',
        'amino.sf',
        'amino',
        'amino-bot',
        'narvii',
        'api',
        'python',
        'python3',
        'python3.x',
        'sfah'
    ],
    python_requires='>=3.6',
)
