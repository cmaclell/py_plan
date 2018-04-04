import setuptools

setuptools.setup(
    name='py_plan',
    version='0.1.0',
    author='Christopher J. MacLellan',
    author_email='maclellan.christopher@gmail.com',
    packages=setuptools.find_packages(),
    include_package_data=True,
    url='http://pypi.python.org/pypi/py_plan/',
    license='MIT License',
    description=('A library of propositional and relational '
                 'planning algorithms'),
    long_description=open('README.rst').read(),
    install_requires=['py_search', 'concept_formation'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Science/Research',
                 'Topic :: Scientific/Engineering :: Artificial Intelligence',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.6',
                 'Programming Language :: Python :: Implementation :: PyPy'],
)
