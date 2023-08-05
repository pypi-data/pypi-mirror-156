import setuptools


with open('README.md', 'r') as fh:
    long_description = fh.read()
with open('requirements.txt') as f:
    required = f.read().splitlines()
classifiers = [
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
]
setuptools.setup(name='cambriantools',
                 version='0.0.1',
                 description='Library with basic and general python methods',
                 python_requires='>=3.10',
                 install_requires=required,
                 keywords='experimental',
                 author='Oscar Pimentel Fuentes',
                 author_email='oscarlo.pimentel@gmail.com',
                 #  include_package_data=True,
                 packages=setuptools.find_packages(),
                 long_description=long_description,
                 long_description_content_type='text/markdown',
                 license='MIT licence',
                 classifiers=classifiers,
                 )
