from setuptools import setup, find_packages


setup(
    name='eucalyptus',
    version='0.0.1',
    license='MIT',
    author="Het Trivedi",
    author_email='het.trivedi05@gmail.com',
    packages=find_packages(include=['eucalyptus', 'utils']),
    url='https://github.com/htrivedi99/eucalyptus-sdk',
    install_requires=[
          'requests', 'pandas', 'numpy', 'pandera'
      ],

)