# -*- coding: utf-8 -*-
"""Helper functions to work around API inconsistencies among
Archetypes and Dexterity.
"""


def set_image_field(obj, image):
    """Set image field in object on both, Archetypes and Dexterity."""
    from plone.namedfile.file import NamedBlobImage
    try:
        obj.setImage(image)  # Archetypes
    except AttributeError:
        obj.image = NamedBlobImage(data=image)  # Dexterity
    finally:
        obj.reindexObject()
