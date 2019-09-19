# -*- coding: utf-8 -*-
from plone import schema
from plone.dexterity.content import Item
from plone.supermodel import model
from Products.EasyNewsletter import _
from zope.interface import implementer


class INewsletterSubscriber(model.Schema):
    """ Marker interface and Dexterity Python Schema for NewsletterSubscriber
    """

    salutation = schema.Choice(
        title=_(u"EasyNewsletter_label_salutation", default="Salutation"),
        description=_(u"EasyNewsletter_help_salutation", default=u""),
        vocabulary=u"Products.EasyNewsletter.Salutations",
        required=False,
    )

    name_prefix = schema.TextLine(
        title=_(u"EasyNewsletter_label_name_prefix", default=u"Name Prefix"),
        description=_(u"EasyNewsletter_help_name_prefix", default=u""),
        default=u"",
        required=False,
    )

    firstname = schema.TextLine(
        title=_(u"EasyNewsletter_label_firstname", default=u"First Name"),
        required=False,
    )

    lastname = schema.TextLine(
        title=_(u"EasyNewsletter_label_lastname", default=u"Last Name"), required=False
    )

    organization = schema.TextLine(
        title=_(u"EasyNewsletter_label_organization", default=u"Organization"),
        required=False,
    )

    email = schema.TextLine(
        title=_(u"EasyNewsletter_label_email", default=u"Email"), required=True
    )


@implementer(INewsletterSubscriber)
class NewsletterSubscriber(Item):
    """
    """

    @property
    def title(self):
        title = self.email
        prefix = self.name_prefix or u''
        firstname = self.firstname or u''
        lastname = self.lastname or u''
        if self.firstname or self.lastname:
            title += " - " + " ".join([prefix, firstname, lastname])
        return title

    @title.setter
    def title(self, value):
        return
