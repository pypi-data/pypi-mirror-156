import os
import setuptools

metadata = {}
with open('./src/twstocks_crawler/version.py', encoding='utf-8') as f:
    exec(f.read(), metadata)


setuptools.setup(
    name="twstocks-crawler",
    version=metadata['__version__'],
    author="Sunaley",
    author_email="sunaley@gmail.com",
    description="TWStock profiles crawler",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    url="https://github.com/sunaley/stocks",
    install_requires=[
        'requests',
        'lxml',
        'pandas',
        'aiohttp',
        'aiohttp-socks',
        'charset-normalizer==2.0.0'
    ],
    packages=["twstocks_crawler", "twstocks_crawler.repositories"],
    package_dir={"": "src", },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
)