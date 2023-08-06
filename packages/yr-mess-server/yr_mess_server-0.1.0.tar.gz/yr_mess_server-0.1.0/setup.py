from setuptools import setup, find_packages

setup_requires = ['wheel']
setup(setup_requires=['wheel'],
      name="yr_mess_server",
      version="0.1.0",
      description="Mess Server",
      author="Yury Rozhkov",
      author_email="yrozhkov1983@gmail.com",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
      )
