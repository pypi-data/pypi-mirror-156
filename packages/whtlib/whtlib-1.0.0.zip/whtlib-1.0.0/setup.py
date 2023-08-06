from setuptools import setup


def readme_file():
    with open("README.rst", encoding="utf-8") as rf:
        return rf.read()


setup(name="whtlib", version="1.0.0", description="this is a outstanding lib", packages=["whtlib"]
      , py_modules=["tool"], author="wht", author_email="1781329447@qq.com",
      long_description=readme_file(), url="https://github.com/wangshunzi/Python_code", license="MIT")
