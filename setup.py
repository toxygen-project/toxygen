from setuptools import setup
from setuptools.command.install import install
from platform import system
from subprocess import call
from toxygen.util import program_version


version = program_version + '.0'

MODULES = []

if system() in ('Windows', 'Darwin'):
    MODULES = ['PyAudio', 'PySide']
else:
    try:
        import pyaudio
    except ImportError:
        MODULES = ['PyAudio']


class InstallScript(install):
    """This class configures Toxygen after installation"""

    def run(self):
        install.run(self)
        try:
            if system() == 'Windows':
                call(["toxygen", "--configure"])
            else:
                call(["toxygen", "--clean"])
        except:
            pass

setup(name='Toxygen',
      version=version,
      description='Toxygen - Tox client',
      long_description='Toxygen is powerful Tox client written in Python3',
      url='https://github.com/xveduk/toxygen/',
      keywords='toxygen tox messenger',
      author='Ingvar',
      maintainer='Ingvar',
      license='GPL3',
      packages=['toxygen', 'toxygen.plugins', 'toxygen.styles'],
      install_requires=MODULES,
      include_package_data=True,
      classifiers=[
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
      ],
      entry_points={
          'console_scripts': ['toxygen=toxygen.main:main'],
      },
      cmdclass={
          'install': InstallScript,
      },
      )
