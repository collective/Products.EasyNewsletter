from Products.CMFCore.utils import getToolByName

def sendENLIssue(obj, event):
    """ workflow subscriber."""
    # do only change the code section inside this function.
    if not event.transition \
       or event.transition.id not in ['send'] \
       or obj != event.object:
        return

    obj.send()