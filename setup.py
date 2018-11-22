from setuptools import setup, find_packages

version = '0.1'

setup(name='Products.PerFactErrors',
      version=version,
      description="",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='',
      author_email='',
      url='',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      package_data={
      },
      include_package_data=True,
      zip_safe=False,
      namespace_packages=['Products'],
      install_requires=[
          'zExceptions',
          'zope.cachedescriptors',
          'zope.interface',
          'zope.publisher',
          'zope.security',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
