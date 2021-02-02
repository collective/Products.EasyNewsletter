# -*- coding: utf-8 -*-

from plone import api
from plone.dexterity.interfaces import IDexterityContent
from Products.CMFPlone.utils import safe_unicode
from Products.EasyNewsletter import _, config
# from Products.EasyNewsletter.interfaces import IReceiversGroupFilter
from Products.EasyNewsletter.interfaces import IReceiversMemberFilter
# from Products.EasyNewsletter.interfaces import ISubscriberSource
from zope.component import subscribers
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

import logging


log = logging.getLogger("Products.EasyNewsletter")


@implementer(IVocabularyFactory)
class PloneUsers(object):
    """
    """

    def __call__(self, context):
        # Just an example list of content for our vocabulary,
        # this can be any static or dynamic data, a catalog result for example.
        results = []
        member_properties = dict()
        users = api.user.get_users()
        for user in users:
            info = dict()
            info["id"] = user.getUserId()
            info["email"] = user.getProperty("email")
            info["fullname"] = safe_unicode(user.getProperty("fullname"))
            member_properties[info["id"]] = info

        try:
            for id, property in member_properties.items():
                if config.EMAIL_RE.findall(property['email']):
                    results.append(
                        (id, property['fullname'] + ' - ' + property['email']))
                else:
                    log.error(
                        _("Property email: \"{0}\" is not an email!").format(property['email'])
                    )
        except TypeError as e:  # noqa
            log.error(
                ":get_plone_members: error in member_properties {0} \
                properties:'{1}'".format(e, member_properties.items())
            )

        # run registered member filter
        for subscriber in subscribers([self], IReceiversMemberFilter):
            results = subscriber.filter(results)

        # Fix context if you are using the vocabulary in DataGridField.
        # See https://github.com/collective/collective.z3cform.datagridfield/issues/31:  # NOQA: 501
        if not IDexterityContent.providedBy(context):
            req = getRequest()
            context = req.PARENTS[0]

        # create a list of SimpleTerm items:
        terms = []
        for item in results:
            terms.append(
                SimpleTerm(value=item[0], token=item[0], title=item[1])
            )
        # Create a SimpleVocabulary from the terms list and return it:
        return SimpleVocabulary(terms)


PloneUsersFactory = PloneUsers()
