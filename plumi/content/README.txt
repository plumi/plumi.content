Introduction
============

This is a full-blown functional test. The emphasis here is on testing what
the user may input and see, and the system is largely tested as a black box.
We use PloneTestCase to set up this test as well, so we have a full Plone site
to play with. We *can* inspect the state of the portal, e.g. using 
self.portal and self.folder, but it is often frowned upon since you are not
treating the system as a black box. Also, if you, for example, log in or set
roles using calls like self.setRoles(), these are not reflected in the test
browser, which runs as a separate session.

Being a doctest, we can tell a story here.

First, we must perform some setup. We use the testbrowser that is shipped
with Five, as this provides proper Zope 2 integration. Most of the 
documentation, though, is in the underlying zope.testbrower package.

    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()
    >>> browser.handleErrors = False
    >>> portal_url = self.portal.absolute_url()

The following is useful when writing and debugging testbrowser tests. It lets
us see all error messages in the error_log.

    >>> self.portal.error_log._ignored_exceptions = ()

With that in place, we can go to the portal front page and log in. We will
do this using the default user from PloneTestCase:

    >>> from Products.PloneTestCase.setup import portal_owner, default_password

    >>> browser.open(portal_url)

We have the login portlet, so let's use that.

    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()

Here, we set the value of the fields on the login form and then simulate a
submit click.

We then test that we are still on the portal front page:

    >>> browser.url == portal_url
    True

And we ensure that we get the friendly logged-in message:

    >>> "You are now logged in" in browser.contents
    True


-*- extra stuff goes here -*-

Specific PLUMI test setup
=========================

We are going to make PlumiVideo/PlumiCallOut types for the purposes of this test have global allow True

    >>> from Products.CMFCore.utils import getToolByName
    >>> types=getToolByName(self.portal,'portal_types')
    >>> fti_pv = getattr(types,'PlumiVideo')
    >>> fti_pv.manage_changeProperties(global_allow=True)
    >>> fti_pv.globalAllow()
    True
    >>> fti_pco = getattr(types,'PlumiCallOut')
    >>> fti_pco.manage_changeProperties(global_allow=True)
    >>> fti_pco.globalAllow()
    True


The Plumi Callout Folder content type
===============================

In this section we are tesing the Plumi Callout Folder content type by performing
basic operations like adding, updadating and deleting Plumi Callout Folder content
items.

Adding a new Plumi Callout Folder content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Plumi Callout Folder' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Plumi Callout Folder').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Plumi Callout Folder' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Plumi Callout Folder Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Plumi Callout Folder' content item to the portal.

Updating an existing Plumi Callout Folder content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Plumi Callout Folder Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Plumi Callout Folder Sample' in browser.contents
    True

Removing a/an Plumi Callout Folder content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Plumi Callout Folder
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Plumi Callout Folder Sample' in browser.contents
    True

Now we are going to delete the 'New Plumi Callout Folder Sample' object. First we
go to the contents tab and select the 'New Plumi Callout Folder Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Plumi Callout Folder Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Plumi Callout Folder
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Plumi Callout Folder Sample' in browser.contents
    False

Adding a new Plumi Callout Folder content item as contributor
------------------------------------------------

Not only site managers are allowed to add Plumi Callout Folder content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Plumi Callout Folder' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Plumi Callout Folder').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Plumi Callout Folder' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Plumi Callout Folder Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Plumi Callout Folder content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()

    Go into the just made plumi callout folder , so we can make the PlumiCallouts below

    >>> browser.open(portal_url+'/plumi-callout-folder-sample')

The PlumiCallOut content type
===============================

In this section we are tesing the PlumiCallOut content type by performing
basic operations like adding, updadating and deleting PlumiCallOut content
items.

Adding a new PlumiCallOut content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'PlumiCallOut' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Plumi Call Out').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'PlumiCallOut' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'PlumiCallOut Sample'
    >>> import cStringIO
    >>> browser.getControl(name='calloutImage_file').add_file(cStringIO.StringIO('\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x02\x00\x02\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xf9\xfe\xbf\xff\xd9'), 'image/jpeg', 'test.jpg')
    >>> browser.getControl(name='calloutImageCaption').value = 'PlumiCallOut Sample'
    >>> browser.getControl(name='bodyText').value = 'PlumiCallOut Sample' 
    >>> browser.getControl(name='submissionCategories:list').value=('test',)
    >>> browser.getControl(name='closingDate_year').value=('2010',)
    >>> browser.getControl(name='closingDate_month').value=('01',)
    >>> browser.getControl(name='closingDate_day').value=('01',)
    >>> browser.getControl(name='closingDate_hour').value=('01',)    
    >>> browser.getControl(name='closingDate_minute').value=('00',)    
    >>> browser.getControl(name='closingDate_ampm').value=('AM',)      
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'PlumiCallOut' content item to the portal.

Updating an existing PlumiCallOut content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New PlumiCallOut Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New PlumiCallOut Sample' in browser.contents
    True

Removing a/an PlumiCallOut content item
--------------------------------

    >>> browser.open(portal_url+'/plumi-callout-folder-sample')
    >>> browser.getLink('Contents').click()    
    >>> 'New PlumiCallOut Sample' in browser.contents
    True

Now we are going to delete the 'New PlumiCallOut Sample' object. First we
go to the contents tab and select the 'New PlumiCallOut Sample' for
deletion.

    >>> browser.getControl('New PlumiCallOut Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New PlumiCallOut
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New PlumiCallOut Sample' in browser.contents
    False

Adding a new PlumiCallOut content item as contributor
------------------------------------------------

Not only site managers are allowed to add PlumiCallOut content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url+'/plumi-callout-folder-sample')

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'PlumiCallOut' and click the 'Add' button to get to the add form.
We use the 'Add new' menu to add a new content item.

    >>> browser.getControl('Plumi Call Out').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'PlumiCallOut' in browser.contents
    True

Now we fill the form and submit it.
    
    >>> browser.getControl(name='title').value = 'PlumiCallOut'
    >>> import cStringIO
    >>> browser.getControl(name='calloutImage_file').add_file(cStringIO.StringIO('\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x02\x00\x02\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xf9\xfe\xbf\xff\xd9'), 'image/jpeg', 'test.jpg')
    >>> browser.getControl(name='calloutImageCaption').value = 'PlumiCallOut Sample'
    >>> browser.getControl(name='bodyText').value = 'PlumiCallOut Sample' 
    >>> browser.getControl(name='submissionCategories:list').value=('test',)
    >>> browser.getControl(name='closingDate_year').value=('2010',)
    >>> browser.getControl(name='closingDate_month').value=('01',)
    >>> browser.getControl(name='closingDate_day').value=('01',)
    >>> browser.getControl(name='closingDate_hour').value=('01',)    
    >>> browser.getControl(name='closingDate_minute').value=('00',)    
    >>> browser.getControl(name='closingDate_ampm').value=('AM',)      
    >>> browser.getControl('Save').click()    

    >>> 'PlumiCallOut' in browser.contents
    True

Done! We added a new PlumiCallOut content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

The Plumi Video Folder content type
===============================

In this section we are tesing the Plumi Video Folder content type by performing
basic operations like adding, updadating and deleting Plumi Video Folder content
items.

Adding a new Plumi Video Folder content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'Plumi Video Folder' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Plumi Video Folder').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Plumi Video Folder' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Plumi Video Folder Sample'
    >>> browser.getControl(name='form.button.save').click()    
    >>> 'Changes saved' in browser.contents
    True

And we are done! We added a new 'Plumi Video Folder' content item to the portal.

Updating an existing Plumi Video Folder content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New Plumi Video Folder Sample'
    >>> browser.getControl('Save').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> 'New Plumi Video Folder Sample' in browser.contents
    True

Removing a/an Plumi Video Folder content item
--------------------------------

If we go to the home page, we can see a tab with the 'New Plumi Video Folder
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New Plumi Video Folder Sample' in browser.contents
    True

Now we are going to delete the 'New Plumi Video Folder Sample' object. First we
go to the contents tab and select the 'New Plumi Video Folder Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getControl('New Plumi Video Folder Sample').click()

We click on the 'Delete' button.

    >>> browser.getControl('Delete').click()
    >>> 'Item(s) deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New Plumi Video Folder
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New Plumi Video Folder Sample' in browser.contents
    False

Adding a new Plumi Video Folder content item as contributor
------------------------------------------------

Not only site managers are allowed to add Plumi Video Folder content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

We select 'Plumi Video Folder' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Plumi Video Folder').click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'Plumi Video Folder' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'Plumi Video Folder Sample'
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True

Done! We added a new Plumi Video Folder content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)


The PlumiVideo content type
===============================

In this section we are tesing the PlumiVideo content type by performing
basic operations like adding, updadating and deleting PlumiVideo content
items.

Adding a new PlumiVideo content item
--------------------------------

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'PlumiVideo' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Plumi Video', index=0).click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'PlumiVideo' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'PlumiVideo Sample'
    >>> browser.getControl(name='description').value = 'PlumiVideo Sample Description'    
    >>> browser.getControl(name='DateProduced_year').value=('2010',)
    >>> browser.getControl(name='DateProduced_month').value=('01',)
    >>> browser.getControl(name='DateProduced_day').value=('01',)       
    >>> browser.getControl('Next').click()
    >>> 'Changes saved' in browser.contents
    True
    >>> browser.getControl('Next').click()
    >>> 'Changes saved' in browser.contents
    True
    >>> browser.getControl(name='video_file_file').add_file(cStringIO.StringIO(' '), 'video/flv', 'test.flv')  
    >>> browser.getControl('Save').click()
              
And we are done! We added a new 'PlumiVideo' content item to the portal.

Updating an existing PlumiVideo content item
---------------------------------------

Let's click on the 'edit' tab and update the object attribute values.

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='title').value = 'New PlumiVideo Sample'
    >>> browser.getControl('Next').click()

We check that the changes were applied.

    >>> 'Changes saved' in browser.contents
    True
    >>> browser.getControl('Next').click()
    >>> 'Changes saved' in browser.contents
    True    
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True             
    >>> 'New PlumiVideo Sample' in browser.contents
    True

Removing a/an PlumiVideo content item
--------------------------------

If we go to the home page, we can see a tab with the 'New PlumiVideo
Sample' title in the global navigation tabs.

    >>> browser.open(portal_url)
    >>> 'New PlumiVideo Sample' in browser.contents
    True

Now we are going to delete the 'New PlumiVideo Sample' object. First we
go to the contents tab and select the 'New PlumiVideo Sample' for
deletion.

    >>> browser.getLink('Contents').click()
    >>> browser.getLink('New PlumiVideo Sample').click()

We click on the 'Delete' button.

    >>> browser.getLink('Delete').click()
    >>> browser.getControl('Delete').click()    
    >>> 'New PlumiVideo Sample has been deleted' in browser.contents
    True

So, if we go back to the home page, there is no longer a 'New PlumiVideo
Sample' tab.

    >>> browser.open(portal_url)
    >>> 'New PlumiVideo Sample' in browser.contents
    False

Adding a new PlumiVideo content item as contributor
------------------------------------------------

Not only site managers are allowed to add PlumiVideo content items, but
also site contributors.

Let's logout and then login as 'contributor', a portal member that has the
contributor role assigned.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = 'contributor'
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)

We use the 'Add new' menu to add a new content item.

    >>> browser.getLink('Add new').click()

Then we select the type of item we want to add. In this case we select
'PlumiVideo' and click the 'Add' button to get to the add form.

    >>> browser.getControl('Plumi Video', index=0).click()
    >>> browser.getControl(name='form.button.Add').click()
    >>> 'PlumiVideo' in browser.contents
    True

Now we fill the form and submit it.

    >>> browser.getControl(name='title').value = 'PlumiVideo Sample'
    >>> browser.getControl(name='description').value = 'PlumiVideo Sample Description'    
    >>> browser.getControl(name='DateProduced_year').value=('2010',)
    >>> browser.getControl(name='DateProduced_month').value=('01',)
    >>> browser.getControl(name='DateProduced_day').value=('01',)       
    >>> browser.getControl('Next').click()
    >>> 'Changes saved' in browser.contents
    True
    >>> browser.getControl('Next').click()
    >>> 'Changes saved' in browser.contents
    True
    >>> browser.getControl(name='video_file_file').add_file(cStringIO.StringIO(' '), 'video/flv', 'test.flv')  
    >>> browser.getControl('Save').click()
    >>> 'Changes saved' in browser.contents
    True              

Done! We added a new PlumiVideo content item logged in as contributor.

Finally, let's login back as manager.

    >>> browser.getLink('Log out').click()
    >>> browser.open(portal_url)
    >>> browser.getControl(name='__ac_name').value = portal_owner
    >>> browser.getControl(name='__ac_password').value = default_password
    >>> browser.getControl(name='submit').click()
    >>> browser.open(portal_url)



