from setuptools import setup, find_packages

setup(name="message_server_unfun",
      version="0.8.7",
      description="message_server_unfun",
      author="Vladimir Gromov",
      author_email="gromovvladimir@myrambler.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
      # scripts=['server_dist/server_run']
      )
