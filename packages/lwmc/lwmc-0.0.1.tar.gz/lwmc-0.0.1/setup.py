from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3'
]

setup (
    name='lwmc',
    version='0.0.1',
    description='A lightweight math calculator library',
    long_description=open('README.txt').read(),
    url='',
    author='Pigioty',
    author_email='pigiotyreal@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='',
    packages=find_packages(),
    install_requires=['']
)