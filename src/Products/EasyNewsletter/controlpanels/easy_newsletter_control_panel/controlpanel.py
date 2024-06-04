# -*- coding: utf-8 -*-
from plone.app.registry.browser.controlpanel import (
    ControlPanelFormWrapper,
    RegistryEditForm,
)
from plone.restapi.controlpanels import RegistryConfigletPanel
from plone.z3cform import layout
from Products.EasyNewsletter import _
from Products.EasyNewsletter.interfaces import IProductsEasynewsletterLayer
from zope import schema
from zope.component import adapter
from zope.interface import Interface


class IEasyNewsletterControlPanel(Interface):
    myfield_name = schema.TextLine(
        title=_(
            "This is an example field for this control panel",
        ),
        description=_(
            "",
        ),
        default="",
        required=False,
        readonly=False,
    )


class EasyNewsletterControlPanel(RegistryEditForm):
    schema = IEasyNewsletterControlPanel
    schema_prefix = "Products.EasyNewsletter.easy_newsletter_control_panel"
    label = _("Easy Newsletter Control Panel")


EasyNewsletterControlPanelView = layout.wrap_form(
    EasyNewsletterControlPanel, ControlPanelFormWrapper
)



@adapter(Interface, IProductsEasynewsletterLayer)
class EasyNewsletterControlPanelConfigletPanel(RegistryConfigletPanel):
    """Control Panel endpoint"""

    schema = IEasyNewsletterControlPanel
    configlet_id = "easy_newsletter_control_panel-controlpanel"
    configlet_category_id = "Products"
    title = _("Easy Newsletter Control Panel")
    group = ""
    schema_prefix = "Products.EasyNewsletter.easy_newsletter_control_panel"
