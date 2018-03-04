from setuptools import setup
setup(
    name = 'abi2doc',
    description = 'Linux Kernel sysfs attribute documentation generator',
    packages = ['abi2doc'],
    include_package_data=True,
    version = '0.3',
    author = 'Aishwarya Pant',
    author_email = 'aishpant@gmail.com',
    url = 'https://github.com/aishpant/attribute-documentation',
    download_url = 'https://github.com/aishpant/attribute-documentation/archive/0.3.tar.gz',
    keywords = 'documentation sysfs linux',
    entry_points={
        'console_scripts': [
            'abi2doc=abi2doc.doc:document',
        ],
},
)
