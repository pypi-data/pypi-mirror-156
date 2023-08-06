import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="kvv_WordCreator",
    version="0.0.2",
    author="Vladislav Kornilov",
    author_email="v.kornilovv@yandex.ru",
    description="WordCreator is a helper package to create Word spreadsheets out of Publications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VladKornilov/WordCreator",
    project_urls={
        "Bug Tracker": "https://github.com/VladKornilov/WordCreator/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    install_requires=[
        'python-docx',
        'kvv_StoredObjects'
    ],
    python_requires=">=3.6",
)