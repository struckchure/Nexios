from setuptools import setup, find_packages
with open("readme.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()
setup(
    name="nexios", 
    version="0.1.3",
    author="Chidebele Dunamis",
    author_email="techwithdunamix@example.com",
    description="Nexios is a modern, high-performance ASGI web framework for Python that emphasizes developer productivity without sacrificing speed. Built on top of industry-standard ASGI specifications, Nexio provides an elegant, batteries-included approach to web development with built-in support for sessions, file storage, and background task processing.",
    long_description_content_type="text/markdown",
    url="https://github.com/techwithdunamix/nexio",
    long_description = long_description,
    packages=find_packages(),
    install_requires=[
        "tortoise-orm", 
        "uvicorn",
        "aerich",
        "asgiref",
        "anyio",
        "aiofiles",
        "itsdangerous",
        

    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        'console_scripts': [
            'nexios=nexios.cli.main:main',
        ],
    },
)
