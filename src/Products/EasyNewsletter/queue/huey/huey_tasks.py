import tempfile

from huey import SqliteHuey
from plone import api
from zope.site.hooks import getSite, setSite
from Products.EasyNewsletter import log

QUEUE_NAME = "Products.EasyNewsletter.queue"
# VIEW_NAME = "enl_taskqueue_sendout"

huey_db_name = tempfile.NamedTemporaryFile(suffix=".db", delete=False).name
huey = SqliteHuey(filename=huey_db_name)
log.info(f"Huey SQLite DB: {huey_db_name}")


@huey.task()
def send_newsletters(uid):
    """ resolve the context object by given uid and triggers
        generation and sending of the newsletter issue.
    """
    from zope.component import getGlobalSiteManager
    gsm = getGlobalSiteManager()
    import pdb; pdb.set_trace()  # NOQA: E702
    send_view = api.content.get_view(name="send-issue", context=context)
    send_view.send()
