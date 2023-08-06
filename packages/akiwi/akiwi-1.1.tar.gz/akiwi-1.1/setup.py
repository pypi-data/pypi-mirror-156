
from setuptools import find_packages
from setuptools import setup
import platform
import os

package_data = []

setup(
    name="akiwi",
    version="1.1",
    author="djw.hope",
    author_email="512690069@qq.com",
    url="https://github.com/shouxieai/tensorRT_Pro",
    description="TensorRTPro python interface",
    python_requires=">=3.6",
    install_requires=["requests", "tqdm"],
    packages=find_packages(),
    package_data={
        "": package_data
    },
    zip_safe=False,
    platforms="linux"
)
