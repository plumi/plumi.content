# -*- coding: utf-8 -*-
"""
This module contains the tool of plumi.content
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '4.3.1'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Contributors\n'
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    )

setup(name='plumi.content',
      version=version,
      description="Plumi Content Types Product",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        ],
      keywords='plone plumi content',
      author='Andy Nicholson',
      author_email='andy@infiniterecursion.com.au',
      url='https://github.com/plumi/plumi.content',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plumi', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'plone.app.discussion',
                        'Products.ATVocabularyManager',
                        'Products.LinguaPlone',
                        'collective.contentlicensing',
                        'collective.transcode.star',
                        'hachoir_metadata',
                        'hachoir_parser',
                        'simplejson'
                        # -*- Extra requirements: -*-
                        ],
      extras_require = {
          'test': ['plone.app.testing',]
      },
      test_suite = 'plumi.content.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
