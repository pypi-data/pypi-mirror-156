from distutils.core import  setup
import setuptools
from setuptools import find_packages, setup
# import py_ToTToT
# packages = [' ']# 唯一的包名，自己取名
# setup(
#         # name='py_yyds',
#         # version ='1.0',
#         # author ='派森',
#         name='py_kobeyyds',# 需要打包的名字,即本模块要发布的名字
#         version='v1.0',#版本
#         description='A  module for test', # 简要描述
#         py_modules=['pandas'],   #  需要打包的模块
#         author='派森', # 作者名
#         # author_email='809518335@qq.com',   # 作者邮件
#         # url='https://github.com/vfrtgb158/email', # 项目地址,一般是代码托管的网站
#         # requires=['requests','urllib3'], # 依赖包,如果没有,可以不要
#         # license='MIT'
#       )
setup(
    name='py_ToT',
    version='2.0',
    # description='sdk for di input , output and param',
    author='派森',
    # author_email='sam@qq.com',
    # url='',
    # license='No License',
    # platforms='python 2.7',
    # py_modules=['factory'],
    # package_dir={'': '星球'},
    packages=['py_yyds']
)
