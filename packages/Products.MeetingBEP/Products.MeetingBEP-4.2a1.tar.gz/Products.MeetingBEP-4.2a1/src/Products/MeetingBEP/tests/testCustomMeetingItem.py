# -*- coding: utf-8 -*-
#
# File: testCustomMeetingItem.py
#
# GNU General Public License (GPL)
#

from datetime import datetime
from Products.MeetingBEP.config import DU_ORIGINAL_VALUE
from Products.MeetingBEP.config import DU_RATIFICATION_VALUE
from Products.MeetingBEP.utils import hr_group_uid
from Products.MeetingBEP.tests.MeetingBEPTestCase import MeetingBEPTestCase
from Products.MeetingCommunes.tests.testCustomMeetingItem import testCustomMeetingItem as mctcmi


class testCustomMeetingItem(MeetingBEPTestCase, mctcmi):
    """ """

    def test_IsPrivacyViewable(self):
        """Items in state 'returned_to_proposing_group' or using propingGroup HR (Confidential)
           are not viewable by restricted power observers."""
        self.setUpRestrictedPowerObservers()

        self.changeUser('pmManager')
        item = self.create('MeetingItem')
        self.create('Meeting')
        self.presentItem(item)

        # item returned_to_proposing_group is not viewable for restricted power observers
        self.changeUser('pmManager')
        self.do(item, 'return_to_proposing_group')
        self.assertEqual(item.query_state(), 'returned_to_proposing_group')
        self.changeUser('powerobserver1')
        self.assertTrue(item.adapted().isPrivacyViewable())
        self.changeUser('restrictedpowerobserver1')
        self.assertFalse(item.adapted().isPrivacyViewable())
        self.changeUser('pmManager')
        self.do(item, 'backTo_presented_from_returned_to_proposing_group')

        # presented item, isPrivacyViewable
        self.assertEqual(item.query_state(), 'presented')
        self.changeUser('powerobserver1')
        self.assertTrue(item.adapted().isPrivacyViewable())
        self.changeUser('restrictedpowerobserver1')
        self.assertTrue(item.adapted().isPrivacyViewable())

        # item using HR confidential proposingGroup is not viewable by rpo
        item.setProposingGroup(hr_group_uid())
        # proposingGroup was found
        self.assertTrue(item.getProposingGroup(True))
        item._update_after_edit()
        self.changeUser('powerobserver1')
        self.assertTrue(item.adapted().isPrivacyViewable())
        self.changeUser('restrictedpowerobserver1')
        self.assertFalse(item.adapted().isPrivacyViewable())

    def test_AdaptDecisionClonedItem(self):
        """DU for "Décision urgente" is an emergency decision.
           It uses the accepted_out_of_meeting_emergency_and_duplicated WFAdaptation
           but when item duplicated, the content of the duplicated item is adapted
           automatically if some specific sentences are found."""
        cfg = self.meetingConfig
        cfg.setWorkflowAdaptations(('accepted_out_of_meeting_emergency_and_duplicated', ))
        cfg.onTransitionFieldTransforms = (
            {'transition': 'validate',
             'field_name': 'MeetingItem.decision',
             'tal_expression': 'python: here.adapted().adaptDecisionClonedItem()'},)
        # as item is duplicated and advices are kept, check that everything is correct
        # as we have automatically asked advices that are inherited
        cfg.setCustomAdvisers(
            ({'delay_label': '',
              'for_item_created_until': '',
              'org': self.vendors_uid,
              'available_on': '', 'delay': '',
              'gives_auto_advice_on_help_message': '',
              'gives_auto_advice_on': "python: True",
              'delay_left_alert': '',
              'is_linked_to_previous_row': '0',
              'for_item_created_from': '2018/03/14',
              'row_id': '2018-04-05.6949191937'}, ))
        cfg.at_post_edit_script()
        self.changeUser('pmCreator1')
        item = self.create('MeetingItem')
        EXTRA_VALUE = "<p>&nbsp;</p><p>Extra sentence</p>"
        item.setDecision(DU_ORIGINAL_VALUE + EXTRA_VALUE)
        self.validateItem(item)
        # vendors advice is asked
        self.assertTrue(self.vendors_uid in item.adviceIndex)
        self.changeUser('pmManager')
        item.setEmergency('emergency_accepted')
        self.do(item, 'accept_out_of_meeting_emergency')
        # original item not changed
        self.assertEqual(item.getDecision(), DU_ORIGINAL_VALUE + EXTRA_VALUE)
        # cloned item was adapted
        cloned_item = item.get_successors()[0]
        self.assertTrue(cfg.Title() in cloned_item.getDecision())
        data = {'mc_title': cfg.Title(),
                'emergency_decision_date': datetime.now().strftime('%d/%m/%Y')}
        ratification_sentence = DU_RATIFICATION_VALUE.format(**data)
        self.assertEqual(cloned_item.getDecision(), ratification_sentence + EXTRA_VALUE)
        # vendors advice was inherited
        self.assertTrue(cloned_item.adviceIndex[self.vendors_uid]['inherited'])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCustomMeetingItem, prefix='test_'))
    return suite
