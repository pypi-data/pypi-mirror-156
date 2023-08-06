from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


version = '4.0.0b1'

long_description = (
    read('README.rst')
    + '\n' +
    read('CHANGES.rst')
    + '\n'
)


setup(
    name='plone.portlet.static',
    version=version,
    description="An editable static HTML portlet for Plone.",
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "Framework :: Zope :: 5",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords='plone portlet static',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://pypi.org/project/plone.portlet.static',
    license='GPL version 2',
    packages=find_packages(),
    namespace_packages=["plone", 'plone.portlet'],
    include_package_data=True,
    zip_safe=False,
    extras_require=dict(
        test=[
            'plone.app.testing',
        ]
    ),
    install_requires=[
        'setuptools',
        "plone.portlets",
        "plone.app.portlets",
        "plone.app.textfield",
        "plone.i18n",
        'six',
        'zope.component',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.schema',
        'Zope2',
    ],
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
