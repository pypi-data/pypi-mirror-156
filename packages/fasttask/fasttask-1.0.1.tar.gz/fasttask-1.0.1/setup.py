import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fasttask",
    version="1.0.1",
    author="Lucas Starling",
    author_email="lucastarling1@gmail.com",
    description="TODO",
    long_description=long_description,
    url="https://github.com/LucasStarlingdePaulaSalles/fasttask",
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'fasttask=fasttask.main:main',
        ],
    },
)