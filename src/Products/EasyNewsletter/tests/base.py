# -*- coding: utf-8 -*-
from Products.Five import fiveconfigure
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Testing import ZopeTestCase as ztc


@onsetup
def setup_registration():
    fiveconfigure.debug_mode = True
    import Products.EasyNewsletter
    zcml.load_config('configure.zcml', Products.EasyNewsletter)
    fiveconfigure.debug_mode = False


ztc.installProduct('EasyNewsletter')
setup_registration()
ptc.setupPloneSite(products=['EasyNewsletter'])
