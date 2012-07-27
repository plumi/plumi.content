import logging
#import transaction

from Products.CMFCore.utils import getToolByName
from plumi.content.vocabs  import vocab_set as vocabs
from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
from Products.CMFPlone.utils import _createObjectByType

def setupVocabs(portal, logger):
    #
    #ATVocabManager setup
    #
    logger.info('Starting ATVocabManager configuration ')
    atvm = getToolByName(portal, ATVOCABULARYTOOL)
    wftool = getToolByName(portal,'portal_workflow')

    for vkey in vocabs.keys():
        # create vocabulary if it doesnt exist:
        vocabname = vkey
        if not atvm.getVocabularyByName(vocabname):
            _createObjectByType('SimpleVocabulary', atvm, vocabname)
            logger.debug("adding vocabulary %s" % vocabname)

        vocab = atvm[vocabname]

        #delete the 'default' item
        if hasattr(vocab, 'default'):
            vocab.manage_delObjects(['default'])

        for (ikey, value) in vocabs [vkey]:
            if not hasattr(vocab, ikey):
                _createObjectByType('SimpleVocabularyTerm', vocab, ikey)
                logger.debug("adding vocabulary item %s %s" % (ikey,value))
                vocab[ikey].setTitle(value)

        #reindex
        vocab.reindexObject()

def setupVarious(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('plumi.content_various.txt') is None:
        return

    portal = context.getSite()
    logger = logging.getLogger('plumi.content')
    setupVocabs(portal, logger)

def setupScales(context, logger=None):
    all_videos = context.portal_catalog(show_inactive=True, language="ALL", portal_type="PlumiVideo")

    done = 0

    for brain in all_videos:
        content = brain.getObject()

        # Access schema in Plone 4 / archetypes.schemaextender compatible way
        schema = content.Schema()

        if "thumbnailImage" in schema:
            try:
                schema["thumbnailImage"].createScales(content)
            except:
                print "Failed to recreate scales for " + content.absolute_url()
        else:
            print "Has bad PlumiVideo schema:" + content.absolute_url()

        # Since this is a HUGE operation (think of resizing 2 GB images)
        # it is not a good idea to buffer the transaction in memory
        # (Zope default behavior).
        # Using subtransactions we hint Zope when it would be a good
        # time to buffer the changes on disk.
        # http://www.zodb.org/documentation/guide/transactions.html
        #if done % 10 == 0:
            # Commit subtransaction for every 10th processed item
        #    transaction.commit(True)

        done += 1
        print "(%d / %d) created scales for: %s" % (done, len(all_videos), "/".join(content.getPhysicalPath()))

    # Final commit
    #transaction.commit()
    print "Recreated image scales for %d videos" % len(all_videos)

        
def uninstallVocabs(portal, logger):
    #
    #ATVocabManager setup
    #
    logger.info('Reverting ATVocabManager configuration ')
    atvm = getToolByName(portal, ATVOCABULARYTOOL)

    for vkey in vocabs.keys():
        vocabname = vkey
        if atvm.getVocabularyByName(vocabname):
            atvm._delObject(vocabname)
            logger.debug("removing vocabulary %s" % vocabname)
            
def uninstall(context):
    if context.readDataFile('plumi.content_uninstall.txt') is None:
        return
    print "uninstalling plumi.content"
    portal = context.getSite()    
    logger = logging.getLogger('plumi.content')    
    uninstallVocabs(portal, logger)    
