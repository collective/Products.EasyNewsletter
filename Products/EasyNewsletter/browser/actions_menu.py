# -*- coding: utf-8 -*-
from plone.app.contentmenu.interfaces import IActionsMenu
from plone.app.contentmenu.interfaces import IActionsSubMenuItem
from plone.app.contentmenu.menu import BrowserMenu
from plone.app.contentmenu.menu import BrowserSubMenuItem
from plone.protect.utils import addTokenToUrl
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.security import checkPermission
from Products.EasyNewsletter.interfaces import IENLBase


@implementer(IActionsSubMenuItem)
class EasyNewsletterActionsSubMenuItem(BrowserSubMenuItem):

    title = 'Newsletter'
    submenuId = 'easynewsletter-actions'

    extra = {
        'id': 'easynewsletter-actions',
        'li_class': 'plonetoolbar-easynewsletter-action'
    }

    order = 40

    @property
    def action(self):
        return self.context.getNewsletter().absolute_url()

    def available(self):
        if checkPermission('cmf.ModifyPortalContent', self.context) and \
                IENLBase.providedBy(self.context):
            return True
        return False

    def selected(self):
        return False


@implementer(IActionsMenu)
class EasyNewsletterActionsMenu(BrowserMenu):

    def getMenuItems(self, context, request):  # flack8: noqa
        """Return menu item entries in a TAL-friendly form."""
        results = []

        context_state = getMultiAdapter((context, request),
                                        name='plone_context_state')
        edit_actions = context_state.actions('easynewsletter')
        if not edit_actions:
            return results

        for action in edit_actions:
            if action['allowed']:
                aid = action['id']
                css_class = 'actionicon-object_buttons-%s' % aid
                icon = action.get('icon', None)
                modal = action.get('modal', None)
                if modal:
                    css_class += ' pat-plone-modal'

                results.append({
                    'title': action['title'],
                    'description': '',
                    'action': addTokenToUrl(action['url'], request),
                    'selected': False,
                    'icon': icon,
                    'extra': {'id': 'plone-contentmenu-actions-' + aid,
                              'separator': None,
                              'class': css_class,
                              'modal': modal},
                    'submenu': None,
                })
        return results
