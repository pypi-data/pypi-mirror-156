from setuptools import setup, find_packages

classifiers=[
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 3 - Alpha',

    # Indicate who your project is intended for
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',

    # Pick your license as you wish (should match "license" above)
    'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
]

#from distutils.core import setup

setup(
    name = "ml_tester",
    version = "1.0",
    author = "Dror Lederman",
    author_email = "dror@honeycombinsurance.com",
    description = ("An demonstration of how to create, document, and publish "
                                   "to the cheese shop a5 pypi.org."),
    license = "BSD",
    keywords = "example documentation tutorial",
    url = "http://packages.python.org/an_example_pypi_project",
    #packages=["ml_tester",
    #          "ml_tester.actions",
    #          "ml_tester.dialogs"],
    packages = find_packages(),
        #where = 'ml_tester',
        #include = ['actions','dialogs','pck*'],
        #exclude = ['additional',]
    #),
    package_dir = {"":"ml_tester"},
    install_requires=[
        "matplotlib",
    ],
    entry_points='''
        [console_scripts]
        ml_tester_gui=mltester.ml_tester:main
    ''',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)