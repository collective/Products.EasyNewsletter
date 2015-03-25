# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.EasyNewsletter import EasyNewsletterMessageFactory as _
from Products.EasyNewsletter import config
from Products.EasyNewsletter.interfaces import IENLSubscriber
from zope.interface import implements


schema = atapi.BaseSchema + atapi.Schema((

    atapi.StringField(
        'title',
        required=False,
        widget=atapi.StringWidget(
            visible={'edit': 'invisible', 'view': 'invisible'},
            label=_(u'EasyNewsletter_label_title', default=u'Title'),
            description=_(u'EasyNewsletter_help_title', default=u''),
            i18n_domain='EasyNewsletter',
        ),
    ),

    atapi.StringField(
        'salutation',
        required=False,
        vocabulary=config.SALUTATION,
        widget=atapi.SelectionWidget(
            label=_(
                u'EasyNewsletter_label_salutation',
                default='Salutation'),
            description=_('EasyNewsletter_help_salutation', default=u''),
            i18n_domain='EasyNewsletter',
            format='select',
        ),
    ),

    atapi.StringField(
        'nl_language',
        required=False,
        vocabulary=config.NL_LANGUAGE,
        widget=atapi.SelectionWidget(
            label=_(
                u'EasyNewsletter_label_help_nl_language',
                default='Newsletter language'),
            description=_('EasyNewsletter_help_nl_language', default=u''),
            i18n_domain='EasyNewsletter',
            format='select',
        ),
    ),

#    atapi.StringField(
#        'fullname',
#        required=False,
#        widget=atapi.StringWidget(
#            label=_(u'EasyNewsletter_label_fullname', default=u'Full Name'),
#            description=_('EasyNewsletter_help_fullname', default=u''),
#            i18n_domain='EasyNewsletter',
#        ),
#    ),

    atapi.StringField(
        'firstname',
        required=False,
        widget=atapi.StringWidget(
            label=_(u'EasyNewsletter_label_firstname', default=u'First Name'),
            description=_('EasyNewsletter_help_firstname', default=u''),
            i18n_domain='EasyNewsletter',
        ),
    ),

    atapi.StringField(
        'lastname',
        required=False,
        widget=atapi.StringWidget(
            label=_(u'EasyNewsletter_label_lastname', default=u'Last Name'),
            description=_('EasyNewsletter_help_lastname', default=u''),
            i18n_domain='EasyNewsletter',
        ),
    ),

    atapi.StringField(
        'organization',
        required=False,
        widget=atapi.StringWidget(
            label=_(
                u'EasyNewsletter_label_organization',
                default=u'Organization'),
            description=_(
                'EasyNewsletter_help_organization',
                default=u''),
            i18n_domain='EasyNewsletter',
        ),
    ),

    atapi.StringField(
        'email',
        required=True,
        validators=('isEmail', ),
        widget=atapi.StringWidget(
            label=_(
                u'EasyNewsletter_label_email',
                default=u'Email'),
            description=_(
                u'EasyNewsletter_help_email',
                default=u''),
            i18n_domain='EasyNewsletter',
        ),
    ),

), )


class ENLSubscriber(atapi.BaseContent):
    """An newsletter subscriber.
    """
    implements(IENLSubscriber)
    security = ClassSecurityInfo()
    schema = schema
    _at_rename_after_creation = True

    def initializeArchetype(self, **kwargs):
        """Overwritten hook
        """
        atapi.BaseContent.initializeArchetype(self, **kwargs)

    def setEmail(self, value):
        """
        """
        self.email = value
        self.title = value

        # reindex to set title for catalog
        self.reindexObject()

    def Title(self):
        """Overwritten accessor for Title
        """
        title_str = self.getEmail()
        if self['firstname'] or self['lastname']:
            title_str += ' - ' + ' '.join([self.getLastname(),
                                           self.getFirstname()])
        return title_str


atapi.registerType(ENLSubscriber, config.PROJECTNAME)
