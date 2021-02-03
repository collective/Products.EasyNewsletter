# -*- coding:utf-8 -*-

from setuptools import find_packages
from setuptools import setup


version = '5.0.0b3'
long_description = (
    open('README.rst').read() + '\n'
    + open('CHANGES.rst').read()
)

setup(
    name='Products.EasyNewsletter',
    version=version,
    description="Powerful newsletter/mailing addon for Plone",
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Plone',
        'Framework :: Plone :: 5.2',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.7',
        "Framework :: Plone :: Addon",
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='Plone Newsletter Mailing Email Mailinglist',
    maintainer='MrTango',
    author='Maik Derstappen (MrTango)',
    author_email='md@derico.de',
    url='https://github.com/collective/Products.EasyNewsletter',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['Products'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Plone',
        'zope.formlib',
        'jinja2',
        'nameparser',
        'plone.api',
        'plone.app.upgrade',
        'Products.CMFPlone',
        'plone.app.registry',
        'plone.resource',
        'beautifulsoup4',
        'setuptools',
        'plone.protect>=3.1.1',
        'emails',
        'premailer',
        'html2text',
        'email_validator',
        'six',
    ],
    extras_require=dict(
        test=[
            'Pillow',
            'plone.app.testing',
            'plone.testing',
            'plone.app.contenttypes',
            'plone.app.robotframework[debug]',
            'pdbpp',
            'isort<5'
        ],
    ),
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = Products.EasyNewsletter.locales.update:update_locale
    """,
)
