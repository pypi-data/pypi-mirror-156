from setuptools import setup, find_packages

setup(name="network_chat_server_2021",
      version="0.0.1",
      description="Network Chat Server",
      author="Omega Omega",
      author_email="om.om@yandex.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
