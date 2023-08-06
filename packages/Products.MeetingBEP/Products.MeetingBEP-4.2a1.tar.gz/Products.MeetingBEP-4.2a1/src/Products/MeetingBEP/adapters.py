# -*- coding: utf-8 -*-
#
# GNU General Public License (GPL)
#

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from imio.history.utils import getLastWFAction
from plone import api
from Products.MeetingBEP.interfaces import IMeetingBEPWorkflowActions
from Products.MeetingBEP.interfaces import IMeetingBEPWorkflowConditions
from Products.MeetingBEP.interfaces import IMeetingItemBEPWorkflowActions
from Products.MeetingBEP.interfaces import IMeetingItemBEPWorkflowConditions
from Products.MeetingBEP.utils import hr_group_uid
from Products.MeetingCommunes.adapters import CustomMeeting
from Products.MeetingCommunes.adapters import CustomMeetingItem
from Products.MeetingCommunes.adapters import MeetingCommunesWorkflowActions
from Products.MeetingCommunes.adapters import MeetingCommunesWorkflowConditions
from Products.MeetingCommunes.adapters import MeetingItemCommunesWorkflowActions
from Products.MeetingCommunes.adapters import MeetingItemCommunesWorkflowConditions
from Products.PloneMeeting.interfaces import IMeetingCustom
from Products.PloneMeeting.interfaces import IMeetingItemCustom
from zope.interface import implements


class CustomBEPMeeting(CustomMeeting):
    '''Adapter that adapts a custom meeting implementing IMeeting to the interface IMeetingCustom.'''

    implements(IMeetingCustom)
    security = ClassSecurityInfo()

    def __init__(self, meeting):
        self.context = meeting


class CustomBEPMeetingItem(CustomMeetingItem):
    '''Adapter that adapts a custom meeting item implementing IMeetingItem to the interface IMeetingItemCustom.'''
    implements(IMeetingItemCustom)
    security = ClassSecurityInfo()

    def __init__(self, item):
        self.context = item

    def showObservations(self):
        """Restricted power observers may not view observations."""
        res = True
        item = self.getSelf()
        tool = api.portal.get_tool('portal_plonemeeting')
        cfg = tool.getMeetingConfig(item)
        # hide observations to restricted power observers
        if tool.isPowerObserverForCfg(
                cfg, power_observer_types=['restrictedpowerobservers']):
            res = False
        return res

    def isPrivacyViewable(self):
        """Not for restricted power observers if :
           - item is returned_to_proposing_group;
           - item.proposingGroup is HR_CONFIDENTIAL_GROUP_ID."""
        item = self.getSelf()
        tool = api.portal.get_tool('portal_plonemeeting')
        cfg = tool.getMeetingConfig(item)
        is_restricted_power_observer = tool.isPowerObserverForCfg(
            cfg, power_observer_types=['restrictedpowerobservers'])
        res = True
        if is_restricted_power_observer and \
           (item.getProposingGroup() == hr_group_uid() or
                item.query_state() == 'returned_to_proposing_group'):
            res = False
        if res:
            res = item.isPrivacyViewable()
        return res

    def adaptDecisionClonedItem(self):
        """If item is cloned from an accepted_out_of_meeting_emergency item,
           we adapt MeetingItem.decision field content."""
        item = self.getSelf()
        raw_value = item.getRawDecision()
        if 'duplicating_and_validating_item' in item.REQUEST:
            tool = api.portal.get_tool('portal_plonemeeting')
            cfg = tool.getMeetingConfig(item)
            # get last time predecessor was 'accepted_out_of_meeting_emergency'
            accept_out_of_meeting_action = getLastWFAction(
                item.get_predecessor(),
                transition='accept_out_of_meeting_emergency')
            data = {'mc_title': cfg.Title(),
                    'emergency_decision_date': accept_out_of_meeting_action['time'].strftime('%d/%m/%Y')}
            raw_value = raw_value.replace(
                "<p><strong><u>Proposition de décision&nbsp;:</u></strong></p>",
                "<p><u><strong>Le {mc_title} décide à l'unanimité de ratifier la décision "
                "prise en urgence en date du {emergency_decision_date}, à savoir de :"
                "</strong></u></p>".format(**data))
        return raw_value


class MeetingBEPWorkflowActions(MeetingCommunesWorkflowActions):
    ''' '''

    implements(IMeetingBEPWorkflowActions)
    security = ClassSecurityInfo()


class MeetingBEPWorkflowConditions(MeetingCommunesWorkflowConditions):
    ''' '''

    implements(IMeetingBEPWorkflowConditions)
    security = ClassSecurityInfo()


class MeetingItemBEPWorkflowActions(MeetingItemCommunesWorkflowActions):
    ''' '''

    implements(IMeetingItemBEPWorkflowActions)
    security = ClassSecurityInfo()


class MeetingItemBEPWorkflowConditions(MeetingItemCommunesWorkflowConditions):
    ''' '''

    implements(IMeetingItemBEPWorkflowConditions)
    security = ClassSecurityInfo()


# ------------------------------------------------------------------------------
InitializeClass(CustomBEPMeeting)
InitializeClass(CustomBEPMeetingItem)
InitializeClass(MeetingBEPWorkflowActions)
InitializeClass(MeetingBEPWorkflowConditions)
InitializeClass(MeetingItemBEPWorkflowActions)
InitializeClass(MeetingItemBEPWorkflowConditions)
# ------------------------------------------------------------------------------
