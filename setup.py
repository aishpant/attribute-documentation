from setuptools import setup
def readme():
    with open('README.rst') as f:
        return f.read()
setup(
    name = 'abi2doc',
    description = 'Linux Kernel sysfs attribute documentation generator',
    long_description = readme(),
    packages = ['abi2doc'],
    include_package_data=True,
    version = '1.5',
    author = 'Aishwarya Pant',
    author_email = 'aishpant@gmail.com',
    license = 'GPLv2',
    python_requires = '>=3',
    url = 'https://github.com/aishpant/attribute-documentation',
    download_url = 'https://github.com/aishpant/attribute-documentation/archive/1.5.tar.gz',
    keywords = 'documentation sysfs linux',
    entry_points={
        'console_scripts': [
            'abi2doc=abi2doc.doc:document',
        ],
},
)
