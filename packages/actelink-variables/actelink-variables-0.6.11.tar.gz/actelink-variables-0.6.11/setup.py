from setuptools import find_namespace_packages, setup
setup(
    name = 'actelink-variables',
    long_description="Actelink helpers library for variables management",
    packages=find_namespace_packages(include=['actelink*']),
    license='LICENSE.txt',
    install_requires=['requests', 'actelink.computation'],
)