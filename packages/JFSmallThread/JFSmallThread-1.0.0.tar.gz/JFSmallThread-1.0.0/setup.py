from setuptools import setup, find_packages
from os import path

# 读取readme文件 这样可以直接显示在主页上

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='JFSmallThread',
    version='1.0.0',
    packages=find_packages(),
    url='',
    license='MIT',
    author='LiuJunFeng',
    author_email='',
    description='飞快的请求库',
    keywords='',
    python_requires='>=3.7,<4',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=['loguru']

)
