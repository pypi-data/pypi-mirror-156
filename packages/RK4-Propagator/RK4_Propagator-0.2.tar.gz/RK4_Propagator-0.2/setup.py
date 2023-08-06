import setuptools
setuptools.setup(
    name='RK4_Propagator',
    version='0.2',
    description='A package that can approximate orbital motion around the Earth with 4th order accuracy. To import, use the command "from RK4_Propagator import RK4_Propagator"',
    url='https://github.com/zackgwillson/RK4_Propagator',
    author='Zack Willson',
    install_requires=['numpy'],
    author_email='',
    packages=setuptools.find_packages(),
    zip_safe=False
)