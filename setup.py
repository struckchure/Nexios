from setuptools import setup, find_packages

setup(
    name="nexio", 
    version="0.1.0",
    author="Chidebele Dunamis",
    author_email="techwithdunamix@example.com",
    description="A brief description of your package",
    long_description_content_type="text/markdown",
    url="https://github.com/techwithdunamix/nexio",
    packages=find_packages(),
    install_requires=[
        "tortoise-orm", 
        "uvicorn",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'nexio=nexio.cli.main:main',
        ],
    },
)
