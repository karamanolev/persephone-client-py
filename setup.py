import os

from setuptools import setup

BASE_DIR = os.path.dirname(__file__)

# Get the long description from the README file
with open(os.path.join(BASE_DIR, 'README.rst')) as f:
    long_description = f.read()

setup(
    name='persephone-client-py',
    version='0.0.1',
    description='A Python client for the Persephone REST API',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Testing',
    ],
    keywords='python visual-regression-testing',
    url='http://github.com/karamanolev/persephone-client-py',
    author='Ivailo Karamanolev',
    author_email='ivailo@karamanolev.com',
    license='MIT',
    packages=['persephone_client'],
    install_requires=[
        'requests',
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'persephone-cli=persephone_client.persephone_cli:main',
        ],
    },
)
