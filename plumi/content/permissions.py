from Products.CMFCore import permissions as CMFCorePermissions
from AccessControl.SecurityInfo import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles

security = ModuleSecurityInfo('plumi.content')
security.declarePublic('plumi.content')
reTranscodePermission = 'Plumi: ReTranscode Video'
setDefaultRoles(reTranscodePermission, ())

