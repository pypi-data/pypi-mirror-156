from setuptools import setup, find_packages

setup(name="message_client_unfun",
      version="0.8.7",
      description="message_client_unfun",
      author="Vladimir Gromov",
      author_email="gromovvladimir@myrambler.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
