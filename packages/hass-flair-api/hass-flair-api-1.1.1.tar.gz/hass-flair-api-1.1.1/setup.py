import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hass-flair-api",
    version="1.1.1",
    author="Robert Drinovac",
    author_email="unlisted@gmail.com",
    description="Forked Flair API Client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/RobertD502/flair-api-client-py/tree/hass-flair-api-client',
    keywords='flair, flair vents, flair api, flair home assistant',
    packages=setuptools.find_packages(),
    python_requires= ">=3.6",
    install_requires=[
        "requests>=2.27.1",
        "requests-mock>=1.5.2",
        "pytest>=4.3.1"
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ),
    project_urls={  # Optional
    'Source': 'https://github.com/RobertD502/flair-api-client-py/tree/hass-flair-api-client',
    },
)
