try:
    return context.portal_interface.objectImplements(context, 'OFS.OrderSupport.IOrderedContainer')
except:
    return context.portal_interface.objectImplements(context, 'OFS.OrderSupport.z2IOrderedContainer')

