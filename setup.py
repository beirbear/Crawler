from setuptools import setup

setup(name='crawler',
      version='0.1.0',
      packages=['crawler'],
      install_requires=['BeautifulSoup'],
      entry_points={
          'console_scripts': [
              'crawler = crawler.__main__:main'
          ]
      }
      )
