from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper

from plumi.content.browser.interfaces import IPlumiSettings
from plone.z3cform import layout

class PlumiControlPanelForm(RegistryEditForm):
    schema = IPlumiSettings

PlumiControlPanelView = layout.wrap_form(PlumiControlPanelForm, ControlPanelFormWrapper)

