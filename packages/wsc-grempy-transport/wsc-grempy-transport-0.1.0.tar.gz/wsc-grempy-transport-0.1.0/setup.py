import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wsc-grempy-transport",
    version="0.1.0",
    license="Apache 2.0",
    description="Supports gremlinpython without asyncio",
    url="https://github.com/skieffer/wsc-grempy-transport",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        'gremlinpython>=3.5.0',
        'websocket-client>=1.3.0'
    ],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
)

