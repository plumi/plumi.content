import logging
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
