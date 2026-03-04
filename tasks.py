"""Invoke tasks for Products.EasyNewsletter."""

from invoke import task


@task
def start(c):
    """Start the Plone instance."""
    c.run("uv run runwsgi instance/etc/zope.ini", env={"LC_ALL": "C.UTF-8"})


@task
def debug(c):
    """Start the Plone instance in debug mode."""
    c.run("uv run runwsgi -d instance/etc/zope.ini")


@task
def shell(c):
    """Open a Zope debug shell."""
    c.run("uv run zconsole debug instance/etc/zope.conf")


@task
def test(c, verbose=False):
    """Run tests."""
    cmd = "uv run pytest"
    if verbose:
        cmd += " -v"
    c.run(cmd)


@task
def create_site(c, site_id="Plone"):
    """Create a new Plone site."""
    import os
    import tempfile

    script = """
from Testing.makerequest import makerequest
import transaction
app = makerequest(app)
from plone.distribution.api import site as site_api
site_api.create(
    app,
    "classic",
    {
        "site_id": "SITE_ID",
        "title": "Products.easynewsletter",
        "description": "A Newsletter and Mailing addon for Plone",
        "default_language": "en",
        "portal_timezone": "UTC",
        "setup_content": False,
    },
)
transaction.commit()
print("Created site: SITE_ID")
""".replace("SITE_ID", site_id)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(script)
        script_path = f.name
    try:
        c.run(f"uv run zconsole run instance/etc/zope.conf {script_path}")
    finally:
        os.unlink(script_path)


@task
def format(c):
    """Format code with ruff."""
    c.run("uv run ruff format .")
    c.run("uv run ruff check --fix .")


@task
def lint(c):
    """Run linting checks."""
    c.run("uv run ruff check .")
