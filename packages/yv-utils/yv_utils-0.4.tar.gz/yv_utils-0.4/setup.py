from setuptools import setup, find_packages


setup(
    name='yv_utils',
    version='0.4',
    license='MIT',
    author="Yerram Varun",
    author_email='yerram.varun@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    # url='https://github.com/gmyrianthous/example-publish-pypi',
    keywords='utils package',
    install_requires=[
          'tqdm',
          'pandas'
      ],

)