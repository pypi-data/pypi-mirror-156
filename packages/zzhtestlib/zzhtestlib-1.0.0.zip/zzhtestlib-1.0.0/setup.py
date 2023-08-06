
from setuptools import setup

def readme_file():
      with open("README.rst",encoding="utf-8") as rf:
            return rf.read()

setup(name="zzhtestlib",version="1.0.0",description="this is a niu lib",
      packages=["zzhtestlib"],py_modules=["Tool"],author="zzh",author_email="1004923690@qq.com",
      long_description=readme_file(),url="https://github/wangshi",license="MIT")

