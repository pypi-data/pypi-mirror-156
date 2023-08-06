from setuptools import setup, find_packages

with open("README.rst",'r',encoding="utf8") as f:
    long_description=f.read()

setup(
    name="robottest",
    version="0.0.1",
    description=("robottest 测试框架"),
    long_description= long_description,
    packages=find_packages(),
    author="redrose2100",
    author_email="hitredrose@163.com",
    maintainer="hitredrose@163.com",
    license="MIT",
    url="https://github.com/redrose2100/RobotTest",
    entry_points={
        'console_scripts': [
            'robot = robottest.cli:main'
        ],
        "pytest11": [
            "robot = robottest.pytest11"
        ]
    },
    install_requires=[
        "fire==0.4.0",
        "six==1.16.0",
        "termcolor==1.1.0",
        "pytest==7.1.2",
        "allure-pytest==2.9.45"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)