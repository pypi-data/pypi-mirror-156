import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="krange",
    version=1.0,
    author="Pedro Arturo Mendez Cruz, Jean Michael Cuadrado, Belkis Yazmin Vásquez Peña",
    author_email="1088438@est.intec.edu.do, 1076992@est.intec.edu.do, 1085273@est.intec.edu.do",
    maintainers="Pedro Arturo Mendez Cruz",
    description="A range / interval package.",
    long_description=long_description,
    url="https://github.com/pamendez/Range-Kata",
    packages=setuptools.find_packages(),
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.10.1'
)