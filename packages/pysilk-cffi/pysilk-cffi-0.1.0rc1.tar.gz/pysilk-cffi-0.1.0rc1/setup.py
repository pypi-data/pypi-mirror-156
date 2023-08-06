import os
import re

from setuptools import find_packages, setup


def get_dis():
    with open("README.markdown", "r", encoding="utf-8") as f:
        return f.read()


def get_version() -> str:
    path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "pysilk", "__init__.py"
    )
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
    result = re.findall(r"(?<=__version__ = \")\S+(?=\")", data)
    return result[0]


packages = find_packages(exclude=("test", "tests.*", "test*"))


def main():
    version: str = get_version()
    dis = get_dis()
    setup(
        name="pysilk-cffi",
        version=version,
        url="https://github.com/synodriver/pysilk-cffi",
        packages=packages,
        keywords=["silk", "encode", "decode", "pcm", "audio"],
        description="silk encode and decode",
        long_description_content_type="text/markdown",
        long_description=dis,
        author="synodriver",
        author_email="diguohuangjiajinweijun@gmail.com",
        python_requires=">=3.6",
        setup_requires=["cffi>=1.0.0"],
        cffi_modules=["pysilk/build.py:ffibuilder"],
        install_requires=["cffi>=1.0.0"],
        license="GPLv3",
        classifiers=[
            "Development Status :: 4 - Beta",
            "Operating System :: OS Independent",
            "License :: OSI Approved :: BSD License",
            "Topic :: Multimedia :: Sound/Audio",
            "Programming Language :: C",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: Implementation :: CPython",
            "Programming Language :: Python :: Implementation :: PyPy",
        ],
        include_package_data=True,
        zip_safe=False,
    )


if __name__ == "__main__":
    main()
