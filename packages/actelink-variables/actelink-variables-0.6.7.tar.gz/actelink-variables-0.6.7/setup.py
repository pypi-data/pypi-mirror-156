from setuptools import find_namespace_packages, setup
setup(
    name = 'actelink-variables',
    packages=find_namespace_packages(include=['actelink*']),
    license='LICENSE.txt',
    install_requires=['requests', 'actelink.computation']
)