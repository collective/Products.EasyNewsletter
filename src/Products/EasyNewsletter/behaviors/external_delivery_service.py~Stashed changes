# -*- coding: utf-8 -*-

# from plone import schema
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
# from Products.EasyNewsletter import _
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import provider


class IExternalDeliveryServiceMarker(Interface):
    pass


# XXX not implemented yet!
@provider(IFormFieldProvider)
class IExternalDeliveryService(model.Schema):
    """
    """

    # project = schema.TextLine(
    #     title=_(u'Project'),
    #     description=_(u'Give in a project name'),
    #     required=False,
    # )


@implementer(IExternalDeliveryService)
@adapter(IExternalDeliveryServiceMarker)
class ExternalDeliveryService(object):
    def __init__(self, context):
        self.context = context

    # @property
    # def project(self):
    #     if hasattr(self.context, 'project'):
    #         return self.context.project
    #     return None

    # @project.setter
    # def project(self, value):
    #     self.context.project = value
