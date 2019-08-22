# -*- coding: utf-8 -*-

from ..content.newsletter import INewsletter
from plone import schema
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from Products.EasyNewsletter import _
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory


@provider(IContextAwareDefaultFactory)
def get_default_plone_receiver_members(context):
    if not INewsletter.providedBy(context):
        return []
    return context.plone_receiver_members


@provider(IContextAwareDefaultFactory)
def get_default_plone_receiver_groups(context):
    if not INewsletter.providedBy(context):
        return []
    return context.plone_receiver_groups


class IPloneUserGroupRecipientsMarker(Interface):
    pass


@provider(IFormFieldProvider)
class IPloneUserGroupRecipients(model.Schema):
    """
    """
    model.fieldset(
        "recipients",
        label=_(u"Recipients"),
        fields=[
            "plone_receiver_members",
            "plone_receiver_groups",
        ],
    )

    plone_receiver_members = schema.Set(
        title=_(
            u"EasyNewsletter_label_ploneReceiverMembers",
            default=u"Plone Members to receive the newsletter",
        ),
        description=_(
            u"EasyNewsletter_help_ploneReceiverMembers",
            default=u"Choose Plone Members which should receive \
                    the newsletter. Changing this setting does not affect \
                    already existing issues.",
        ),
        value_type=schema.Choice(vocabulary=u"Products.EasyNewsletter.PloneUsers"),
        required=False,
        defaultFactory=get_default_plone_receiver_members,
    )

    plone_receiver_groups = schema.Set(
        title=_(
            u"EasyNewsletter_label_ploneReceiverGroups",
            default=u"Plone Groups to receive the newsletter",
        ),
        description=_(
            u"EasyNewsletter_help_ploneReceiverGroups",
            default=u"Choose Plone Groups which should receive \
                    the newsletter. Changing this setting does not affect \
                    already existing issues.",
        ),
        value_type=schema.Choice(vocabulary=u"Products.EasyNewsletter.PloneGroups"),
        required=False,
        defaultFactory=get_default_plone_receiver_groups,
    )


@implementer(IPloneUserGroupRecipients)
@adapter(IPloneUserGroupRecipientsMarker)
class PloneUserGroupRecipients(object):
    def __init__(self, context):
        self.context = context

    @property
    def plone_receiver_members(self):
        return self.context.plone_receiver_members

    @plone_receiver_members.setter
    def plone_receiver_members(self, value):
        self.context.plone_receiver_members = value

    @property
    def plone_receiver_groups(self):
        return self.context.plone_receiver_groups

    @plone_receiver_groups.setter
    def plone_receiver_groups(self, value):
        self.context.plone_receiver_groups = value
