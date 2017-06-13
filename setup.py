# -*- coding:utf-8 -*-

from setuptools import find_packages
from setuptools import setup

version = '3.0b3'
long_description = (
    open('README.rst').read() + '\n' +
    open('CHANGES.rst').read()
)

setup(
    name='Products.EasyNewsletter',
    version=version,
    description="Powerful newsletter/mailing addon for Plone",
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Framework :: Plone :: 5.0',
        'Framework :: Plone :: 5.1',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='Zope Plone Newsletter Mailing',
    maintainer='Maik Derstappen, Timo Stollenwerk, Andreas Jung',
    author='Maik Derstappen',
    author_email='md@derico.de',
    url='https://github.com/collective/Products.EasyNewsletter',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['Products'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'BeautifulSoup',
        'zope.formlib',
        'jinja2',
        'nameparser',
        'plone.api',
        'plone.app.upgrade',
        'Products.Archetypes',
        'Products.ATContentTypes',
        'Products.CMFPlone',
        'Products.TemplateFields',
        'archetypes.referencebrowserwidget',
        'plone.app.referenceablebehavior',
        'plone.app.registry',
        'plone.resource',
        'setuptools',
        'stoneagehtml',
    ],
    extras_require=dict(
        test=[
            'Pillow',
            'plone.app.testing',
            'plone.dexterity',
        ],
        fmp=['inqbus.plone.fastmemberproperties'],
        zamqp=[
            'collective.zamqp',
            'msgpack-python',
        ],
        taskqueue=[
            'collective.taskqueue',
        ],
        taskqueue_redis=[
            'collective.taskqueue[redis]',
        ],
    ),
)
