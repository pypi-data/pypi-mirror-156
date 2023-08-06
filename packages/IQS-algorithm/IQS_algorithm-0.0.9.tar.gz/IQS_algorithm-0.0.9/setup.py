import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="IQS_algorithm",
    version="0.0.9",
    author="Ori Ben-Artzy, Ophir Porat, Mor Zweig",
    author_email="iqs.bgu@gmail.com",
    description="The IQS is an iterative approach for optimizing short keyword queries given a prototype document through interaction with an opaque search engine such as Twitter.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://iqs.cs.bgu.ac.il/",
    project_urls={
        "Frontend repository": "https://github.com/ophirporat/ProjectIQS-Front",
        "Backend repository": "https://github.com/oribena/projectIQS",
        "Academic Article": "https://www.sciencedirect.com/science/article/pii/S0957417422004432",
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