#!/usr/bin/env python
# coding: utf-8
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fd:
    long_description = fd.read()

setup(
    name = 'ProcessLock',
    version = '1.0.0',
    author = 'jianjun',
    author_email = '910667956@qq.com',
    url = 'https://github.com/EVA-JianJun/ProcessLock',
    description = u'Python全局进程锁,文件锁!',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    packages = ["ProcessLock"],
    install_requires = [
        "portalocker>=1.6.0",
    ],
    entry_points={
    },
)