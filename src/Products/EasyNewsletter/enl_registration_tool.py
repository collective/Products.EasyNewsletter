# -*- coding: utf-8 -*-
import OFS


class ENLRegistrationTool(OFS.Folder.Folder):
    """
    """

    id = 'enl_registration_tool'
    title = 'ENL registration utility'
    meta_type = 'enl_registration_tool'
    portal_type = meta_type
