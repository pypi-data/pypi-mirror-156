import setuptools

with open("README.md", "r", encoding='utf-8') as fp:
    long_description = fp.read()

version = {}
with open("ta_cn/_version.py", encoding="utf-8") as fp:
    exec(fp.read(), version)

setuptools.setup(
    name="ta_cn",
    version=version['__version__'],
    author="wukan",
    author_email="wu-kan@163.com",
    description="Technical Analysis Indicators",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wukan1986/ta_cn",
    packages=setuptools.find_packages(),
    install_requires=[
        'TA-Lib',
        'numpy',
    ],
    extras_require={
        'all': [
            'numpy>=1.20.0',  # 主要是为了sliding_window_view
            'pandas',
            'bottleneck',
            'TA-Lib>=0.4.19',
            'numba',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
    ],
    python_requires=">=3.7",
)
