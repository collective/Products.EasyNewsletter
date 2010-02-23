## Script (Python) "activate_subscriber"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=brain, email
##title=
##
#

from Products.CMFCore.utils import getToolByName

wf_tool = getToolByName(context, 'portal_workflow')

if brain:
    obj = brain.getObject()
    if obj.getEmail() == email:
        state = wf_tool.getInfoFor(obj,'review_state')
        if state == 'new':
        	wf_tool.doActionFor(obj, 'confirm')
        	return True	
        else:
            return False

raise "E-mail address not found or wrong confirmation code."
