from setuptools import setup, find_packages

setup(
    name='checkmarkandcross',
    version='0.1.0',
    author='Eric Tröbs',
    author_email='eric.troebs@tu-ilmenau.de',
    description='checkmarks and crosses',
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.6',
    install_requires=['IPython'],
    include_package_data=True,
    package_data={
        'checkmarkandcross': ['*.png']
    }
)
