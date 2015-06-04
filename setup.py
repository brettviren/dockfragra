from setuptools import setup, find_packages
setup(name = 'dockfragra',
      version = '0.0.0',
      description = 'Drive Docker through a graph of parameterized Dockerfile fragments',
      author = 'Brett Viren',
      author_email = 'brett.viren@gmail.com',
      license = 'GPLv2',
      url = 'http://github.com/brettviren/dockfragra',
      install_requires=[
          "networkx",
          "click",
          "docker-py",
          "docker-map",
      ],
      entry_points = {
          'console_scripts': [
              'dockfragra = dockfragra.main:main',
          ]
      }
)
