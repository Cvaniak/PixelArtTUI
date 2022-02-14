from setuptools import setup

setup(name='pixelart-tui',
      version='0.1',
      description = "Terminal based app for Pixel Art",
      url='http://github.com/Cvaniak/PixelArtTUI',
      author='Cvaniak',
      author_email='igna.cwaniak@gmail.com',
      license='MIT',
      packages=['pixelart_tui'],
      entry_points = {
          'console_scripts': ['pixelart-tui=pixelart_tui.command_line:run']
        },
      zip_safe=False)

