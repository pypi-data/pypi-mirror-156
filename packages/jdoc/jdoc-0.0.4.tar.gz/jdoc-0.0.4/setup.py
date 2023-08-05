import setuptools
from app.resource.config import __version__
# readme.md = github readme.md, 這裡可接受markdown寫法
# 如果沒有的話，需要自己打出介紹此專案的檔案，再讓程式知道
with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="jdoc",
    version=__version__,
    author=[
        'sheng-kai-wang',
        'Chung-Chieh-Li',
        'hsih-min-tang',
        'chun-kai-yang',
    ],
    author_email="nssh94879487@gmail.com",
    description="java document search engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sheng-kai-wang/java-doc-search-engine",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True,
    py_modules=['jdoc'],
    install_requires=[
        'pyfiglet==0.8.post1',
        'click==8.1.3',
        'jsonpath==0.82',
        'nltk==3.7',
        'numpy==1.22.4',
        'pandas==1.4.2',
        'regex==2022.6.2',
    ],
    entry_points={
        'console_scripts': [
            'jdoc = app.app:cli',
        ]
    }
)
