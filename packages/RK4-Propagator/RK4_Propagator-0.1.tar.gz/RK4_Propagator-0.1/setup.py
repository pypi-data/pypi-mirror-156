import setuptools
setuptools.setup(
    name='RK4_Propagator',
    version='0.1',
    description='A package that can approximate orbital motion around the Earth with 4th order accuracy.',
    url='https://github.com/zackgwillson/RK4_Propagator',
    author='Zack Willson',
    install_requires=['numpy'],
    author_email='',
    packages=setuptools.find_packages(),
    zip_safe=False
)