import logging
from zope.component import adapts
from zope.interface import implements
from interfaces.plumivideo import IPlumiVideo
from interfaces.workflow import IPlumiWorkflow

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException

from zope import i18n
_ = i18n.MessageFactory("plumi")
import sys

class PlumiWorkflowAdapter(object):
    implements(IPlumiWorkflow)
    adapts(IPlumiVideo)

    def __init__(self, context):
        self.context = context

    def notifyOwnerVideoSubmitted(self):
        """ Email the owner of the submitted video """
        logger = logging.getLogger('plumi.content.adapters')
        #IPlumiVideo implementing objects only
        if IPlumiVideo.providedBy(self.context):

            obj_title=self.context.Title()
            creator=self.context.Creator()
            obj_url=self.context.absolute_url()
            membr_tool = getToolByName(self.context,'portal_membership')
            member=membr_tool.getMemberById(creator)
            urltool = getToolByName(self.context, 'portal_url')
            portal = urltool.getPortalObject()            
            mTo = member.getProperty('email',None)
            mFrom = portal.getProperty('email_from_address')
            mSubj = 'Your contribution : %s : was submitted for review.' % obj_title            
            if mTo is not None and mTo is not '':
                mMsg = 'To: %s\n' % mTo
                mMsg += 'From: %s\n' % mFrom
                mMsg += 'Content-Type: text/plain; charset=utf-8\n\n'
                mMsg += 'Hi %s \nYour contribution has been submitted for review before publishing on the site\n' % member.getProperty('fullname', creator)
                mMsg += 'Title: %s\n\n' % obj_title
                mMsg += '%s/view \n\n' % obj_url
                logger.info('notifyOwnerVideoSubmitted')
                #send email to object owner
                try:
                    logger.info('notifyOwnerVideoSubmitted , im %s - sending email to %s from %s ' % (self.context, mTo, mFrom) )
                    self.context.MailHost.send(mMsg.encode('utf-8','ignore'), subject=mSubj)
                except:
                    logger.error('Didnt actually send email! Something amiss with SecureMailHost.')
                    pass


    def notifyReviewersVideoSubmitted(self):
        """ Email the reviewers of the submitted video """
        logger = logging.getLogger('plumi.content.adapters')
        #IPlumiVideo implementing objects only
        if IPlumiVideo.providedBy(self.context):
            logger.info('notifyReviewersVideoSubmitted , im %s ' % self.context )
            obj_title=self.context.Title()
            obj_url=self.context.absolute_url()
            creator = self.context.Creator()
            membr_tool = getToolByName(self.context,'portal_membership')
            member=membr_tool.getMemberById(creator)
            creator_info = {'fullname':member.getProperty('fullname', 'Fullname missing'),
                            'email':member.getProperty('email', None)}
            #XXX is there a better way to search for reviewers ??
            for reviewer in self.context.portal_membership.listMembers():
                memberId = reviewer.id
                if 'Reviewer' in membr_tool.getMemberById(memberId).getRoles():
                    mTo = reviewer.getProperty('email',None)
                    urltool = getToolByName(self.context, 'portal_url')
                    portal = urltool.getPortalObject()
                    mFrom = portal.getProperty('email_from_address')
                    mSubj = '%s -- submitted for your review' % obj_title
                    mMsg = 'To: %s\n' % mTo
                    mMsg += 'From: %s\n' % mFrom
                    mMsg += 'Content-Type: text/plain; charset=utf-8\n\n'                    
                    mMsg += _('Item has been submitted for your review\n')
                    mMsg += _('Please review the submitted content. \n\n')
                    mMsg += 'Title: %s\n\n' % obj_title
                    mMsg += '%s/view \n\n' % obj_url
                    mMsg += 'The contributor was %s\n\n' % creator_info['fullname']
                    mMsg += 'Email: %s\n\n' % creator_info['email']                    
                    logger.info('notifyReviewersVideoSubmitted')
                    try:
                        logger.info('notifyReviewersVideoSubmitted , im %s . sending email to %s from %s ' % (self.context, mTo, mFrom) )
                        self.context.MailHost.send(mMsg.encode('utf-8','ignore'), subject=mSubj)
                    except:
                        logger.error('Didnt actually send email to reviewer! Something amiss with SecureMailHost.')
                        pass


    def notifyReviewersVideoRejected(self):
        """ Email the reviewers of the rejected video """
        logger = logging.getLogger('plumi.content.adapters')
        #IPlumiVideo implementing objects only
        if IPlumiVideo.providedBy(self.context):
            logger.info('notifyReviewersVideoRejected , im %s ' % self.context )
            obj_title=self.context.Title()
            obj_url=self.context.absolute_url()
            creator = self.context.Creator()
            membr_tool = getToolByName(self.context,'portal_membership')
            member=membr_tool.getMemberById(creator)
            creator_info = {'fullname':member.getProperty('fullname', 'Fullname missing'),
                            'email':member.getProperty('email', None)}
            #XXX is there a better way to search for reviewers ??
            for reviewer in self.context.portal_membership.listMembers():
                memberId = reviewer.id
                if 'Reviewer' in membr_tool.getMemberById(memberId).getRoles():   
                    mTo = reviewer.getProperty('email',None)
                    urltool = getToolByName(self.context, 'portal_url')
                    portal = urltool.getPortalObject()
                    mFrom = portal.getProperty('email_from_address')
                    mSubj = '%s -- has been rejected' % obj_title                
                    mMsg = 'To: %s\n' % mTo
                    mMsg += 'From: %s\n' % mFrom
                    mMsg += 'Content-Type: text/plain; charset=utf-8\n\n'                                  
                    mMsg += _('Item has been rejected..\n')
                    mMsg += 'Title: %s\n\n' % obj_title
                    mMsg += '%s/view \n\n' % obj_url
                    mMsg += 'The contributor was %s\n\n' % creator_info['fullname']
                    mMsg += 'Email: %s\n\n' % creator_info['email']
                    logger.info('notifyReviewersVideoRejected')
                    try:
                        logger.info('notifyReviewersVideoRejected , im %s . sending email to %s from %s ' % (self.context, mTo, mFrom) )
                        self.context.MailHost.send(mMsg.encode('utf-8','ignore'),subject=mSubj)
                    except:
                        logger.error('Didnt actually send email to reviewer! Something amiss with SecureMailHost.')
                        pass

    def notifyReviewersVideoRetracted(self):
        """ Email the reviewers of the retracted video """
        logger = logging.getLogger('plumi.content.adapters')
        #IPlumiVideo implementing objects only
        if IPlumiVideo.providedBy(self.context):
            logger.info('notifyReviewersVideoRetracted , im %s ' % self.context )
            obj_title=self.context.Title()
            obj_url=self.context.absolute_url()
            creator = self.context.Creator()
            membr_tool = getToolByName(self.context,'portal_membership')
            member=membr_tool.getMemberById(creator)
            creator_info = {'fullname':member.getProperty('fullname', 'Fullname missing'),
                            'email':member.getProperty('email', None)}
            #XXX is there a better way to search for reviewers ??
            for reviewer in self.context.portal_membership.listMembers():
                memberId = reviewer.id
                if 'Reviewer' in membr_tool.getMemberById(memberId).getRoles():
                    mTo = reviewer.getProperty('email',None)
                    urltool = getToolByName(self.context, 'portal_url')
                    portal = urltool.getPortalObject()
                    mFrom = portal.getProperty('email_from_address')
                    mSubj = '%s -- has been retracted' % obj_title                
                    mMsg = 'To: %s\n' % mTo
                    mMsg += 'From: %s\n' % mFrom
                    mMsg += 'Content-Type: text/plain; charset=utf-8\n\n'
                    mMsg += _('Item has been retracted..\n')
                    mMsg += 'Title: %s\n\n' % obj_title
                    mMsg += '%s/view \n\n' % obj_url
                    mMsg += 'The contributor was %s\n\n' % creator_info['fullname']
                    mMsg += 'Email: %s\n\n' % creator_info['email']
                    logger.info('notifyReviewersVideoRetracted')
                    try:
                        logger.info('notifyReviewersVideoRetracted , im %s . sending email to %s from %s ' % (self.context, mTo, mFrom) )
                        self.context.MailHost.send(mMsg.encode('utf-8','ignore'), subject=mSubj)
                    except:
                        logger.error('Didnt actually send email to reviewer! Something amiss with SecureMailHost.')
                        pass

    def notifyOwnerVideoPublished(self):
        """ Email the owner of the published video """
        logger = logging.getLogger('plumi.content.adapters')
        #IPlumiVideo implementing objects only
        if IPlumiVideo.providedBy(self.context):
            logger.info('notifyOwnerVideoPublished, im %s ' % self.context )
            obj_title=self.context.Title()
            creator=self.context.Creator()
            obj_url=self.context.absolute_url()
            membr_tool = getToolByName(self.context,'portal_membership')
            member=membr_tool.getMemberById(creator)
            mTo = member.getProperty('email',None)
            if mTo is not None and mTo is not '':
                mMsg = 'Hi %s \n' % member.getProperty('fullname', 'you')
                mMsg += _('Your contribution has been accepted for publishing on the site\n')
                mMsg += 'Title: %s\n\n' % obj_title
                mMsg += '%s/view \n\n' % obj_url
                urltool = getToolByName(self.context, 'portal_url')
                portal = urltool.getPortalObject()
                mFrom = portal.getProperty('email_from_address')
                mSubj = 'Your contribution : %s : was published.' % obj_title
                #send email to object owner
                try:
                    logger.info('notifyOwnerVideoPublished , im %s - sending email to %s from %s ' % (self.context, mTo, mFrom) )
                    self.context.MailHost.send(mMsg.encode('utf-8','ignore'), mTo, mFrom, mSubj)
                except:
                    logger.error('Didnt actually send email! Something amiss with SecureMailHost.')
                    pass

    def notifyOwnerVideoRejected(self):
        """ Notify owner that the video is rejected """
        logger = logging.getLogger('plumi.content.adapters')
        #IPlumiVideo implementing objects only
        if IPlumiVideo.providedBy(self.context):
            logger.info('notifyOwnerVideoRejected, im %s ' % self.context )
            obj_title=self.context.Title()
            creator=self.context.Creator()
            obj_url=self.context.absolute_url()
            membr_tool = getToolByName(self.context,'portal_membership')
            member=membr_tool.getMemberById(creator)
            mTo = member.getProperty('email',None)
            if mTo is not None and mTo is not '':
                urltool = getToolByName(self.context, 'portal_url')
                portal = urltool.getPortalObject()
                mFrom = portal.getProperty('email_from_address')
                mRej = portal.getProperty('rejected_text',None)            
                mMsg = 'Hi %s \n' % member.getProperty('fullname', 'you')
                if mRej:
                    mMsg += mRej
                else:
                    mMsg += _('Your contribution has been rejected ..\n')
                
                mMsg += 'Title: %s\n\n' % obj_title
                mMsg += '%s/view \n\n' % obj_url
                mSubj = 'Your contribution : %s : was rejected.' % obj_title
                #send email to object owner
                try:
                    logger.info('notifyOwnerVideoRejected , im %s - sending email to %s from %s ' % (self.context, mTo, mFrom) )
                    self.context.MailHost.send(mMsg.encode('utf-8','ignore'), mTo, mFrom, mSubj)
                except:
                    logger.error('Didnt actually send email! Something amiss with SecureMailHost.')
                    pass

    def notifyOwnerVideoRetracted(self):
        """ Notify owner that the video is retracted """
        logger = logging.getLogger('plumi.content.adapters')
        #IPlumiVideo implementing objects only
        if IPlumiVideo.providedBy(self.context):
            logger.info('notifyOwnerVideoRetracted, im %s ' % self.context )
            obj_title=self.context.Title()
            creator=self.context.Creator()
            obj_url=self.context.absolute_url()
            membr_tool = getToolByName(self.context,'portal_membership')
            member=membr_tool.getMemberById(creator)
            mTo = member.getProperty('email',None)
            if mTo is not None and mTo is not '':
                mMsg = 'Hi %s \n' % member.getProperty('fullname', 'you')
                mMsg += _('Your contribution has been retracted ..\n')
                mMsg += 'Title: %s\n\n' % obj_title
                mMsg += '%s/view \n\n' % obj_url
                urltool = getToolByName(self.context, 'portal_url')
                portal = urltool.getPortalObject()
                mFrom = portal.getProperty('email_from_address')
                mSubj = 'Your contribution : %s : was retracted.' % obj_title
                #send email to object owner
                try:
                    logger.info('notifyOwnerVideoRetracted , im %s - sending email to %s from %s ' % (self.context, mTo, mFrom) )
                    self.context.MailHost.send(mMsg.encode('utf-8','ignore'), mTo, mFrom, mSubj)
                except:
                    logger.error('Didnt actually send email! Something amiss with SecureMailHost.')
                    pass

    def autoPublishOrHide(self):
        """ Implement auto publish or hide functionality. Returns TRUE if we submitted for review via workflow tool properly, or FALSE otherwise. """
        logger = logging.getLogger('plumi.content.adapters')
        worked = False
        #IPlumiVideo implementing objects only
        if IPlumiVideo.providedBy(self.context):
            logger.info('autoPublishOrHide , im %s ' % self.context )

            #Conditions XXX
            #check if our requirements are met then auto-submit this video.
            #basically, an attached video

            try:
                workflow = getToolByName(self.context, 'portal_workflow')
                state = workflow.getInfoFor(self.context,'review_state')
                #dont try to resubmit if already published.
                if not state == 'published':
                    workflow.doActionFor(self.context, 'submit')
                worked = True
            except WorkflowException:
                worked = False
                pass
            #XXX if conditions arent met, hide the video
            # We arent implementing this by default in IPlumiVideo atm

        #return value
        return worked
