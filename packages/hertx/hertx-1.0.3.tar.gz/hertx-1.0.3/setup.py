from setuptools import find_packages, setup

setup(name='hertx',
      author='hxq',
      version='1.0.3',
      packages=find_packages(),
      author_email='337168530@qq.com',
      description="这是一个工具包",
      license="GPL",
      # requires=['xmltodict==0.12.0',
      #           'bs4==0.0.1'
      #           ],
      install_requires=[
          'requests>=2.24.0',
          'lxml>=4.3.0',
      ]
      )
