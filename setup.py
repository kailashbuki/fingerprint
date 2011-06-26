# set up details
from distutils.core import setup

setup(
    name='fingerprint',
    version='0.1.0',
    url='http://github.com/kailashbuki/fingerprint',
    license='LICENSE.txt',
    author='Kailash Budhathoki',
    author_email='kailash.buki@gmail.com',
    description='Document fingerprint generator',
    long_description=open('README.rst').read(),
    packages=['fingerprint'],
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
