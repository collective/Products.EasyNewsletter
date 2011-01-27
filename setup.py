from setuptools import setup, find_packages

version = '2.5.6'

setup(name='Products.EasyNewsletter',
    version=version,
    description="An easy to use but powerfull newsletter/mailing product for Plone 3+4",
    long_description=open("README.txt").read() + "\n" +
                     open("CHANGES.txt").read(),    
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 4 - Beta",
    ],
    keywords='Zope Plone Newsletter Mailing',
    maintainer='Andreas Jung, Maik Derstappen',
    author='Kai Diefenbach',
    author_email='kai.diefenbach@iqpp.de',
    url='http://plone.org/products/easynewsletter/',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['Products'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Products.TemplateFields',
    ],
    extras_require = dict(
        tests=[
            'inqbus.plone.fastmemberproperties',
        ],
        fmp=['inqbus.plone.fastmemberproperties'],
        all=['inqbus.plone.fastmemberproperties',]
    ),
)
