from setuptools import setup

version = '0.0.1',

setup(
    name='persephone-client-py',
    version=version,
    description='A Python client for the Persephone REST API',
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
)
