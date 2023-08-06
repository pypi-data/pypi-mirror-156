#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="quickpython-mvc",  # 这里是pip项目发布的名称
    version="0.1.1",
    keywords=["quickpython-mvc", "quickpython", "quick", "WEB", "database", "MVC"],  # 关键字
    description="Python rapid development framework .",
    long_description="Python rapid development framework ",
    license="MIT Licence",  # 许可证

    url="https://github.com/quickpython",
    author="lo106258",
    author_email="lo106258@gmail.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=["tornado", "pymysql"]
)
