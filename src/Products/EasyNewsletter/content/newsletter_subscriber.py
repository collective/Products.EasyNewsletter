# -*- coding: utf-8 -*-
from plone import schema
from plone.dexterity.content import Item
from plone.supermodel import model
from Products.EasyNewsletter import _
from zope.interface import implementer


class INewsletterSubscriber(model.Schema):
    """Marker interface and Dexterity Python Schema for NewsletterSubscriber"""

    salutation = schema.Choice(
        title=_("EasyNewsletter_label_salutation", default="Salutation"),
        description=_("EasyNewsletter_help_salutation", default=""),
        vocabulary="Products.EasyNewsletter.Salutations",
        required=False,
    )

    name_prefix = schema.TextLine(
        title=_("EasyNewsletter_label_name_prefix", default="Name Prefix"),
        description=_("EasyNewsletter_help_name_prefix", default=""),
        default="",
        required=False,
    )

    firstname = schema.TextLine(
        title=_("EasyNewsletter_label_firstname", default="First Name"),
        required=False,
    )

    lastname = schema.TextLine(
        title=_("EasyNewsletter_label_lastname", default="Last Name"), required=False
    )

    organization = schema.TextLine(
        title=_("EasyNewsletter_label_organization", default="Organization"),
        required=False,
    )

    email = schema.TextLine(
        title=_("EasyNewsletter_label_email", default="Email"), required=True
    )


@implementer(INewsletterSubscriber)
class NewsletterSubscriber(Item):
    """ """

    @property
    def title(self):
        title = self.email
        prefix = self.name_prefix or ""
        firstname = self.firstname or ""
        lastname = self.lastname or ""
        if self.firstname or self.lastname:
            title += " - " + " ".join([prefix, firstname, lastname])
        return title

    @title.setter
    def title(self, value):
        return
