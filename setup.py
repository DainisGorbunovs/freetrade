import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='freetrade',
    version='0.0.6',
    author='Dainis Gorbunovs',
    author_email='dgdev@protonmail.com',
    description='API for Freetrade app',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/DainisGorbunovs/freetrade',
    packages=setuptools.find_packages(),
    keywords=['Freetrade', 'API', 'stock'],
    install_requires=[
        'requests',
        'pandas',
        'PyJWT',
        'python-dateutil'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Development Status :: 2 - Pre-Alpha',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)