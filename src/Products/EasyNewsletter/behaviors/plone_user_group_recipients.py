# -*- coding: utf-8 -*-
from ..content.newsletter import INewsletter
from plone import api, schema
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from Products.EasyNewsletter import _
from zope.component import adapter
from zope.interface import implementer, Interface, provider
from zope.schema.interfaces import IContextAwareDefaultFactory

import logging


log = logging.getLogger("Products.EasyNewsletter")


@provider(IContextAwareDefaultFactory)
def get_default_plone_receiver_members(parent):
    if not INewsletter.providedBy(parent) or not parent.__parent__:
        return set()
    return parent.plone_receiver_members


@provider(IContextAwareDefaultFactory)
def get_default_plone_receiver_groups(parent):
    if not INewsletter.providedBy(parent) or not parent.__parent__:
        return set()
    return parent.plone_receiver_groups


class IPloneUserGroupRecipientsMarker(Interface):
    pass


@provider(IFormFieldProvider)
class IPloneUserGroupRecipients(model.Schema):
    """
    """

    model.fieldset(
        "recipients",
        label=_(u"Recipients"),
        fields=["plone_receiver_members", "plone_receiver_groups"],
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
        return getattr(self.context, 'plone_receiver_members', set())

    @plone_receiver_members.setter
    def plone_receiver_members(self, value):
        self.context.plone_receiver_members = value

    @property
    def plone_receiver_groups(self):
        return getattr(self.context, 'plone_receiver_groups', set())

    @plone_receiver_groups.setter
    def plone_receiver_groups(self, value):
        self.context.plone_receiver_groups = value

    def _get_salutation_mappings(self):
        """
        returns mapping of salutations. Each salutation itself is a dict
        with key as language. (prepared for multilingual newsletter)
        """
        enl = self.context.get_newsletter()
        result = {}
        lang = self.context.language or 'en'

        for line in enl.salutations:
            if "|" not in line:
                continue
            key, value = line.split('|')
            result[key.strip()] = {lang: value.strip()}
        return result

    def get_plone_subscribers(self):
        """ Search for all selected Members and Groups
            and return a filtered list of subscribers as dicts.
        """
        plone_subscribers = []
        receiver_list = set()
        receiver_member_list = self.plone_receiver_members
        receiver_group_list = self.plone_receiver_groups

        for member_id in receiver_member_list:
            try:
                member = api.user.get(userid=member_id)
            except (AttributeError, api.exc.PloneApiError):
                continue
            else:
                receiver_list.add(member)

        for group in receiver_group_list:
            try:
                members = api.user.get_users(groupname=group)
            except (AttributeError, api.exc.PloneApiError):
                continue
            else:
                receiver_list.update(members)

        # get salutation mappings
        salutation_mappings = self._get_salutation_mappings()

        # get all selected member properties
        for member in receiver_list:
            email = member.getProperty("email")
            if not email:
                continue
            salutation = salutation_mappings[
                member.getProperty("nl_gender", "default")
            ]
            language = member.getProperty("language") or self.context.language
            plone_subscribers.append(
                {
                    "userid": member.getUserId(),
                    "fullname": member.getProperty("fullname"),
                    "email": email,
                    "salutation": salutation.get(
                        language,
                        salutation.get(self.context.language or "en", "unset"),
                    ),
                    "nl_language": language,
                }
            )
        return plone_subscribers
