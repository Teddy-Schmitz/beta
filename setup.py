try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='beta',
    version='0.1',
    url='https://github.com/jdioutkast/beta',
    author='Teddy Schmitz',
    description='Continuous delivery for AWS API Gateway',
    py_modules=['beta', 'betacli'],
    include_package_data=True,
    install_requires=required,
    entry_points='''
        [console_scripts]
        beta=betacli:cli
    ''',
)