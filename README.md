# Products.EasyNewsletter

[![CI](https://github.com/collective/Products.EasyNewsletter/workflows/Plone%20package/badge.svg)](https://github.com/collective/Products.EasyNewsletter/actions)
[![codecov](https://codecov.io/gh/collective/Products.EasyNewsletter/branch/master/graph/badge.svg?token=xEu330kMw5)](https://codecov.io/gh/collective/Products.EasyNewsletter)
[![PyPI](https://img.shields.io/pypi/v/Products.EasyNewsletter.svg)](https://pypi.python.org/pypi/Products.EasyNewsletter/)
[![PyPI Status](https://img.shields.io/pypi/status/Products.EasyNewsletter.svg)](https://pypi.python.org/pypi/Products.EasyNewsletter/)
[![Python Versions](https://img.shields.io/pypi/pyversions/Products.EasyNewsletter.svg)](https://pypi.python.org/pypi/Products.EasyNewsletter/)
[![License](https://img.shields.io/pypi/l/Products.EasyNewsletter.svg)](https://pypi.python.org/pypi/Products.EasyNewsletter/)

EasyNewsletter is a simple but powerful newsletter/mailing add-on for Plone.

## Features

- Plain text and HTML newsletters (including images)
- Manual written newsletters/mailings
- Automatic Plonish newsletters/mailings: Utilize Plone's Collections to collect content
- Send out daily/weekly/monthly issues automatically, based on collections (by cron or clock-server)
- Flexible templates for Collections, to generate newsletter content
- TTW customizable output template to generate HTML newsletters
- Personalized emails
- Subscribing/unsubscribing
- Import/export subscribers via CSV
- Use Plone Members/Groups as receivers (works also with Membrane)
- External subscriber filtering/manipulation with plugins (filter out or add more subscribers)

## Requirements

- Python 3.10+
- Plone 6.1.1

## Installation

Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

## Running

Start the Plone instance:

```bash
invoke start
```

Or run directly:

```bash
runwsgi instance/etc/zope.ini
```

The initial admin user is configured in `instance/inituser` (default: admin/admin).

## Development

### Running Tests

```bash
pytest
```

### Tasks

Use invoke for common tasks:

```bash
invoke --list
```

## Documentation

For more documentation please visit: http://productseasynewsletter.readthedocs.io

## Known Issues

- If parts of the ENLIssue footer show up in the Plone footer, change the footer portlet view name from `footer` to `@@footer`. This issue was fixed in Plone already, but you have to manually update this in an existing site.

## Translations

[![translation status](https://hosted.weblate.org/widgets/products-easynewsletter/-/products-easynewsletter/multi-auto.svg)](https://hosted.weblate.org/engage/products-easynewsletter/)

Please help us to improve translations with Weblate:
https://hosted.weblate.org/engage/products-easynewsletter/

## Source Code

https://github.com/collective/Products.EasyNewsletter

## Bug Tracker

https://github.com/collective/Products.EasyNewsletter/issues

## ToDo

Funding welcome ;)

- Async task queue for WSGI as an alternative to collective.taskqueue which will not support WSGI
- Integration of Mosaico newsletter editor
- External subscriber sources / delivery services
- Content migration AT >> DX

## Maintainer

- Maik Derstappen [MrTango] md@derico.de

## Contributors

- Kai Dieffenbach: initial release
- Andreas Jung
- Dinu Gherman
- Jens W. Klein
- Peter Holzer
- Philip Bauer
- Thomas Massman [tmassmann]
- Timo Stollenwerk

## License

GPL-2.0-or-later
