from setuptools import setup, find_packages


setup(
    name='example_publish_pypi_sorna',
    version='0.6',
    license='MIT',
    author="Sorna JAvadi",
    author_email='sorna.javadi@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='',
    keywords='example project',
    install_requires=[
          'scikit-learn',
      ],

)