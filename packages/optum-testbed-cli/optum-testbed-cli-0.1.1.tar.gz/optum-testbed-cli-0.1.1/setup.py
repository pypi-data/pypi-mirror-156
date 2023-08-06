from setuptools import setup
setup(
    name = 'optum-testbed-cli',
    version = '0.1.1',
    packages = ['otbctl'],
    author = 'Venkata Krishna Lolla',
    author_email = 'venkata.lolla@optum.com',
    maintainer = 'Venkata Krishna Lolla',
    url = 'https://github.optum.com/OCS-Transformation-Optimization/optum-testbed-cli',
    install_requires=[
        'python-dotenv', 'requests', 'pyyaml', 'tabulate', 'numpy', 'munch'
    ],
    entry_points = {
        'console_scripts': [
            'otbctl = otbctl.__main__:main'
        ]
    })
