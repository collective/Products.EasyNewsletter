# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager, setSecurityManager
from AccessControl.User import Super as BaseUnrestrictedUser
from contextlib import contextmanager
from Products.CMFPlone.utils import safe_unicode
from Products.EasyNewsletter.utils.mail import get_email_charset
from urllib.parse import urlparse


def safe_portal_encoding(string):
    charset = get_email_charset()
    return safe_unicode(string).encode(charset)


def execute_under_special_role(portal, role, function, *args, **kwargs):
    """ Execute code under special role priviledges.
    Example how to call::
        execute_under_special_role(portal, "Manager",
            doSomeNormallyNotAllowedStuff,
            source_folder, target_folder)

    @param portal: Reference to ISiteRoot obj whose access ctls we are using
    @param function: Method to be called with special priviledges
    @param role: User role we are using for the security context when calling \
                 the priviledged code. For example, use "Manager".
    @param args: Passed to the function
    @param kwargs: Passed to the function
    """

    sm = getSecurityManager()
    try:
        try:
            # Clone the current access control user and assign a new role
            # for him/her. Note that the username (getId()) is left in
            # exception tracebacks in error_log
            # so it is important thing to store
            tmp_user = UnrestrictedUser(
                sm.getUser().getId(), '', [role], '')

            # Act as user of the portal
            tmp_user = tmp_user.__of__(portal.acl_users)
            newSecurityManager(None, tmp_user)

            # Call the function
            return function(*args, **kwargs)

        except Exception:
            # If special exception handlers are needed, run them here
            raise
    finally:
        # Restore the old security manager
        setSecurityManager(sm)


@contextmanager
def use_fixed_newsletter_url(url, request):
    server_url = request.get('SERVER_URL', '')
    old_url = urlparse(server_url)
    # old_virtual_root = request.getVirtualRoot()
    # change url in request
    url_obj = urlparse(url)
    protocol = url_obj.scheme
    hostname = url_obj.hostname
    port = url_obj.port
    if not port:
        if protocol == "https":
            port = 443
        else:
            port = 80
    request.setServerURL(
        protocol=protocol, hostname=hostname, port=port,
    )
    try:
        yield
    finally:
        # reset url in request
        protocol = old_url.scheme
        hostname = old_url.hostname
        port = old_url.port
        request.setServerURL(
            protocol=protocol, hostname=hostname, port=port,
        )


class UnrestrictedUser(BaseUnrestrictedUser):
    """Unrestricted user that still has an id.
    """

    def getId(self):
        """Return the ID of the user.
        """
        return self.getUserName()
