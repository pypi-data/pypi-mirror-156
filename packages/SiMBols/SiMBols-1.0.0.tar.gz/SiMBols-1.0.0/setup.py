import setuptools

setuptools.setup(
    name="SiMBols",
    version="1.0.0",
    author="Fabian Schuhmann",
    author_email="fabian.schuhmann@uol.de",
    description="A package containing similarity measures for life science purposes.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)