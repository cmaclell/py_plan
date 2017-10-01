import setuptools

setuptools.setup(
    name='py_plan',
    version='0.1.0',
    author='Christopher J. MacLellan',
    author_email='maclellan.christopher@gmail.com',
    packages=setuptools.find_packages(),
    include_package_data=True,
    url='http://pypi.python.org/pypi/py_plan/',
    license='LICENSE.txt',
    description=('A library of propositional and relational '
                 'planning algorithms'),
    long_description=open('README.rst').read(),
    install_requires=['py_search', 'concept_formation'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Intended Audience :: Science/Research',
                 'Topic :: Scientific/Engineering :: Artificial Intelligence',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.3',
                 'Programming Language :: Python :: 2.4',
                 'Programming Language :: Python :: 2.5',
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.0',
                 'Programming Language :: Python :: 3.1',
                 'Programming Language :: Python :: 3.2',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6'],
)
