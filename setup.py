from setuptools import setup

setup(
    name='arqanmode',
    version='0.0.2',
    platforms='all',
    python_requires='>=3.12',
    packages=[
        "arqanmode",
        "arqanmode.storage",
        "arqanmode.domain",
        "arqanmode.kafka",
    ]
)
