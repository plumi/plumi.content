from zope.interface import Interface
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from zope import schema
from zope.formlib import form
from plone.scale.scale import scaleImage
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

import datetime

from zope import i18n
_ = i18n.MessageFactory("plumi.content")


class IActiveMembers(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """
    count = schema.Int(title=_(u'Number of items to display'),
                       description=_(u'How many items to list.'),
                       required=True,
                       default=10)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IActiveMembers)

    def __init__(self, count=10):
       self.count = count

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"Active Members")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('activemembers.pt')

    def results(self):
        now = datetime.datetime.now()
        portal_catalog = getToolByName(self, 'portal_catalog')
        mtool = getToolByName(self,'portal_membership')
        members = [member for member in mtool.listMembers() if not member.has_role(['Manager','Reviewer',])]
        results = portal_catalog(created={ 'query' : [pastmonthdate(now), now], 'range':'minmax'}
                                 )
        creators = []
        thelist = []
        for creator in results:
            creators.append(creator.Creator)
        for item in members:
           thelist.append((creators.count(item), item))
        adict = dict(thelist)
        return sortedDictValues(adict)[:self.data.count]


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IActiveMembers)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IActiveMembers)


def sortedDictValues(adict):
    """Helper function for the renderer
    """
    keys = adict.keys()
    keys.sort()
    keys.reverse()
    return map(adict.get, keys)

def pastmonthdate(d):
    year, month= d.year, d.month
    if month == 1:
        year-= 1; month= 12
    else:
        month-= 1
    try:
        return d.replace(year=year, month=month)
    except ValueError:
        return d.replace(day=1) - datetime.timedelta(1)
