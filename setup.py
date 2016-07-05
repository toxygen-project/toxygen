from setuptools import setup
from setuptools.command.install import install
from platform import system
from ctypes import CDLL


class DownloadScript(install):
    """Install all required libs"""
    def run(self):
        OS = system()
        if OS == 'Linux':  # install libtoxcore
            try:
                libtoxcore = CDLL('libtoxcore.so')
                libtoxencryptsave = CDLL('libtoxencryptsave.so')
                libtoxav = CDLL('libtoxav.so')
            except:  # toxcore is not installed
                pass
        install.run(self)

setup(name='Toxygen',
      version='0.2.1.50',
      description='Toxygen - Tox client',
      long_description='Toxygen is powerful Tox client written in Python3',
      url='https://github.com/xveduk/toxygen/',
      keywords='toxygen tox',
      author='Ingvar',
      license='GPL3',
      package_dir={'': 'src'},
      packages=['', 'plugins', 'styles'],
      install_requires=['PyAudio', 'PySide', 'PySocks'],
      include_package_data=True,
      classifiers=[
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
      ],
      entry_points={
          'console_scripts': ['toxygen=main:main'],
      },
      cmdclass={
          'install': DownloadScript,
      },
      )
