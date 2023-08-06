from setuptools import find_packages, setup

setup(name='hertx',
      author='hxq',
      version='1.0.2',
      packages=find_packages(),
      author_email='337168530@qq.com',
      description="这是日常使用工具包,希望可以快速帮助解决问题！",
      license="GPL",
      # requires=['xmltodict==0.12.0',
      #           'bs4==0.0.1'
      #           ],
      install_requires=[
          'requests==2.24.0',
          'lxml>=4.3.0',
      ]
      )
