import unittest2 as unittest
import doctest
from plone.testing import layered
from zope.testing import doctestunit
from zope.component import testing, eventtesting
from plumi.content.testing import PLUMI_FIXTURE, PLUMI_FUNCTIONAL_TESTING

def test_suite():
    suite = unittest.TestSuite()
    browser_tests = doctest.DocFileSuite('../README.txt', globs={'layer': PLUMI_FUNCTIONAL_TESTING})
    browser_tests.layer = PLUMI_FUNCTIONAL_TESTING
    suite.addTests([
             browser_tests,
         ])
    return suite	
"""    return unittest.TestSuite([

        # Demonstrate the main content types
        ztc.ZopeDocFileSuite(
            'README.txt', package='plumi.content',
            test_class=base.FunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE |
                doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
				#optionflags= doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        ])
"""
if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
