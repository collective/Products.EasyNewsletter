# Products.easynewsletter

A Newsletter and Mailing addon for Plone

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

## License

GPL-2.0-or-later
