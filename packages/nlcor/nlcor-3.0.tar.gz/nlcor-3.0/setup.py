from setuptools import setup, find_packages

setup(
    name="nlcor",
    packages=find_packages(where='nlcor', exclude=['tests']),
    version="3.0",
    author="Chitta Ranjan, Devleena Banerjee",
    author_email="cranjan@processminer.com, dbanerjee@processminer.com",
    description="Nlcor uses a dynamic partitioning approach with adaptive segmentation for a more precise nonlinear correlation estimation.",
    long_description_content_type="text/markdown",
    url="https://github.com/ProcessMiner/nlcorpython",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite="tests",
    python_requires='>=3.6',
    install_requires=[
        "numpy",
        "pandas",
        "scipy",
    ]
)
