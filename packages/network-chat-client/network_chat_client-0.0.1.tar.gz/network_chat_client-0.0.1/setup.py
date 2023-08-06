from setuptools import setup, find_packages

setup(name="network_chat_client",
      version="0.0.1",
      description="Network Chat Client",
      author="Omega Omega",
      author_email="om.om@yandex.ru",
      packages=find_packages(),
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
      # scripts=['server/server_run']
      )
