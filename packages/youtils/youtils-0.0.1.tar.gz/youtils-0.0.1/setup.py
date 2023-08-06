from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='youtils',
      version='0.0.1',
      description='Utils for You',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='funniest joke comedy flying circus',
      url='http://github.com/antonitto/youtils',
      author='amarkov',
      author_email='markov.anton.a@gmail.com',
      license='MIT',
      packages=['youtils'],
      install_requires=[
          'markdown',
      ],
      test_suite='nose.collector',
      tests_require=['nose', 'nose-cover3'],
      entry_points={
          'console_scripts': ['funniest-joke=youtils.command_line:main'],
      },
      include_package_data=True,
      zip_safe=False)