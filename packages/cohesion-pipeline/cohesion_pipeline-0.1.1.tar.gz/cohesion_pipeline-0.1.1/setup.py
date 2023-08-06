import setuptools

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "cohesion_pipeline",
    version = "0.1.1",
    author = "Eden Berdugo, Tom Nachman, Asaf Solomon",
    author_email = "berdugogo@gmail.com",
    description = "Cohesion measurement to evaluate topic modeling score. call cohesion_df(df)",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/Berdugo1994/cohesion-pipeline",
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'nltk~=3.7',
        'scikit-learn~=1.1.1',
        'pandas~=1.3.0',
        'transformers~=4.20.1',
        'numpy~=1.21.0',
        'tqdm~=4.64.0',
        'tensorflow~=2.9.1',
        'protobuf~=3.20.1',
        'torch'
    ],
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    python_requires = "~=3.8"
)