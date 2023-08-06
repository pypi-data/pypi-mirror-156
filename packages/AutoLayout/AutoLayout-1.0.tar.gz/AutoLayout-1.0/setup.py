from setuptools import setup, find_packages


setup(
    name='AutoLayout',
    version='1.0',
    license='MIT',
    author="Tin Tran",
    author_email='trantin0815@gmail.com',
    packages=["AutoLayout"],
    url='https://github.com/trezitorul/GDSPYUtils/tree/AutoLayout-package/AutoLayout',
    keywords='AutoLayout',
    install_requires=[
          'rectpack', 'gdspy', 'openpyxl'
      ],

)