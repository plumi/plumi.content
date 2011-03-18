import logging
from Products.CMFCore.utils import getToolByName
from plumi.content.vocabs  import vocab_set as vocabs
from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL

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
        if atvm.getVocabularyByName(vocabname):
            atvm.manage_delObjects(vocabname)
        logger.debug("adding vocabulary %s" % vocabname)
        atvm.invokeFactory('SimpleVocabulary', vocabname)

        vocab = atvm[vocabname]

        #delete the 'default' item
        if hasattr(vocab, 'default'):
            vocab.manage_delObjects(['default'])

        for (ikey, value) in vocabs [vkey]:
            if not hasattr(vocab, ikey):
                vocab.invokeFactory('SimpleVocabularyTerm', ikey)
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
