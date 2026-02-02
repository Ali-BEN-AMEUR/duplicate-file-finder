from setuptools import setup, find_packages

setup(
    name='duplicate-file-finder',
    version='0.1.0',
    author='Ali BEN AMEUR',
    author_email='ali.ben-ameur@wanadoo.fr',
    description='A Python application to locate duplicate files across storage systems.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Ali-BEN-AMEUR/duplicate-file-finder',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        # Add any dependencies required for your project here
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache License 2.0',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)