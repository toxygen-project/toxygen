from setuptools import setup
from setuptools.command.install import install
from platform import system
from subprocess import call
from toxygen.util import program_version
import sys


version = program_version + '.0'

MODULES = ['PyQt5', 'PyAudio', 'numpy']

if system() == 'Windows':
    MODULES.append('opencv-python')


class InstallScript(install):
    """This class configures Toxygen after installation"""

    def run(self):
        install.run(self)
        try:
            if system() != 'Windows':
                call(["toxygen", "--clean"])
        except:
            try:
                params = list(filter(lambda x: x.startswith('--prefix='), sys.argv))
                if params:
                    path = params[0][len('--prefix='):]
                    if path[-1] not in ('/', '\\'):
                        path += '/'
                    path += 'bin/toxygen'
                    if system() != 'Windows':
                        call([path, "--clean"])
            except:
                pass

setup(name='Toxygen',
      version=version,
      description='Toxygen - Tox client',
      long_description='Toxygen is powerful Tox client written in Python3',
      url='https://github.com/toxygen-project/toxygen/',
      keywords='toxygen tox messenger',
      author='Ingvar',
      maintainer='Ingvar',
      license='GPL3',
      packages=['toxygen', 'toxygen.plugins', 'toxygen.styles'],
      install_requires=MODULES,
      include_package_data=True,
      classifiers=[
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
      entry_points={
          'console_scripts': ['toxygen=toxygen.main:main'],
      },
      cmdclass={
          'install': InstallScript,
      })
