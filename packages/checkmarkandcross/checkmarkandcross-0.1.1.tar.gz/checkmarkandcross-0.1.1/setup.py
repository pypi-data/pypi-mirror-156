from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as file:
    long_description = file.read()

setup(
    name='checkmarkandcross',
    version='0.1.1',
    author='Eric Tröbs',
    author_email='eric.troebs@tu-ilmenau.de',
    description='checkmarks and crosses',
    long_description=long_description,
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
