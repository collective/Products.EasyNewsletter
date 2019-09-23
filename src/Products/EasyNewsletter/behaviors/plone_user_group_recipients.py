# -*- coding: utf-8 -*-
from ..content.newsletter import INewsletter
from plone import api
from plone import schema
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from Products.EasyNewsletter import _
from Products.EasyNewsletter.config import EMAIL_RE
from Products.EasyNewsletter.interfaces import IReceiversPostSendingFilter
from zope.component import adapter
from zope.component import subscribers
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import provider
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
        if hasattr(self.context, 'plone_receiver_members'):
            return self.context.plone_receiver_members
        return set()

    @plone_receiver_members.setter
    def plone_receiver_members(self, value):
        self.context.plone_receiver_members = value

    @property
    def plone_receiver_groups(self):
        if hasattr(self.context, 'plone_receiver_groups'):
            return self.context.plone_receiver_groups
        return set()

    @plone_receiver_groups.setter
    def plone_receiver_groups(self, value):
        self.context.plone_receiver_groups = value

    def get_plone_subscribers(self):
        """ Search for all selected Members and Groups
            and return a filtered list of subscribers as dicts.
        """
        enl = self.get_newsletter()
        plone_subscribers = []
        if self.send_to_all_plone_members:
            log.info(
                "send_to_all_plone_members is true, so we add all existing"
                " members to receiver_member_list!"
            )
            receiver_member_list = enl.plone_receiver_members
            # if all members are receivers we don't need group relations:
            receiver_group_list = []
        else:
            receiver_member_list = self.plone_receiver_members
            receiver_group_list = self.plone_receiver_groups
        gtool = api.portal.get_tool(name="portal_groups")
        acl_userfolder = api.portal.get_tool(self, "acl_users")
        member_objs = acl_userfolder.getUsers()
        member_properties = {}
        for member in member_objs:
            probdict = {}
            probdict["id"] = member.getUserId()
            probdict["email"] = member.getProperty("email")
            # probdict["gender"] = member.getProperty("nl_gender", "default")
            # try last name first
            probdict["fullname"] = member.getProperty(
                "last_name", member.getProperty("fullname")
            )
            probdict["language"] = member.getProperty("language")
            # fallback for default plone users without a enl language
            if not probdict["language"]:
                probdict["language"] = self.language
            member_properties[probdict["id"]] = probdict
        if not member_properties:
            return []
        selected_group_members = []
        for group in receiver_group_list:
            selected_group_members.extend(gtool.getGroupMembers(group))
        receiver_member_list = receiver_member_list + tuple(selected_group_members)

        # get salutation mappings
        salutation_mappings = self._get_salutation_mappings()
        # get all selected member properties
        for receiver_id in set(receiver_member_list):
            if receiver_id not in member_properties:
                log.debug(
                    'Ignore reveiver "%s", because we have '
                    "no properties for this member!" % receiver_id
                )
                continue
            member_property = member_properties[receiver_id]
            if EMAIL_RE.findall(member_property["email"]):
                salutation = salutation_mappings[
                    member_property.get("gender", "default")
                ]
                plone_subscribers.append(
                    {
                        "fullname": member_property["fullname"],
                        "email": member_property["email"],
                        "salutation": salutation.get(
                            member_property.get("language", ""),
                            salutation.get(self.language or "en", "unset"),
                        ),
                        "nl_language": member_property.get("language", ""),
                    }
                )
            else:
                log.debug(
                    "Skip '%s' because \"%s\" is not a real email!"
                    % (receiver_id, member_property["email"])
                )
        # run registered receivers post sending filters:
        for subscriber in subscribers([enl], IReceiversPostSendingFilter):
            plone_subscribers = subscriber.filter(plone_subscribers)
        return plone_subscribers
