from setuptools import setup

setup(
    name='log_analyzer',
    version="0.2",
    license="MIT License",
    packages=[
        'log_analyzer',
    ],
    include_package_data=True,
    install_requires=[
        "nltk"
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)