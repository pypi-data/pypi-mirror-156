import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="IQS_algorithm",
    version="0.0.7",
    author="Example Author",
    author_email="author@example.com",
    description="Check out the IQS algorithm web platform in the following link: https://iqs.cs.bgu.ac.il/",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    package_data={'IQS_algorithm': ['IQS_utils/RelevantFiles/glove-wiki-gigaword-50.txt'
                            ]},
    include_package_data=True,
    install_requires=['pathlib',
                      'nltk',
                      'tweepy',
                      'numpy',
                      'scipy',
                      'gensim',
                      'uuid',
                      'tqdm',
                      'requests',
                      'importlib_resources'
                      ],
    python_requires=">=3.6",
)