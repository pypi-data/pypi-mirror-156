import setuptools

setuptools.setup(
    name="pytest_aoreporter",
    version="0.1.0",
    author="ancientone",
    author_email="listeningsss@163.com",
    description="pytest report",
    url="https://github.com/ae86sen/pytest-aoreporter",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'pytest',
        'Jinja2',
    ],
    entry_points={"pytest11": ['pytest_aoreporter=pytest_aoreporter.plugin', ], },
    include_package_data=True,
)