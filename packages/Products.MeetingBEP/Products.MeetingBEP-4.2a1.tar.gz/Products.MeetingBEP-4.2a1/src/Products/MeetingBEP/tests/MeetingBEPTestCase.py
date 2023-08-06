# -*- coding: utf-8 -*-
#
# GNU General Public License (GPL)
#

from Products.MeetingBEP.config import PROJECTNAME
from Products.MeetingBEP.profiles.zbep.import_data import rhc_org
from Products.MeetingBEP.testing import MBEP_TESTING_PROFILE_FUNCTIONAL
from Products.MeetingBEP.tests.helpers import MeetingBEPTestingHelpers
from Products.MeetingCommunes.tests.MeetingCommunesTestCase import MeetingCommunesTestCase
from Products.PloneMeeting.exportimport.content import ToolInitializer


class MeetingBEPTestCase(MeetingCommunesTestCase, MeetingBEPTestingHelpers):
    """Base class for defining MeetingBEP test cases."""

    layer = MBEP_TESTING_PROFILE_FUNCTIONAL
    cfg1_id = 'ca'
    cfg2_id = 'codir'

    subproductIgnoredTestFiles = ['test_robot.py',
                                  'testPerformances.py',
                                  'testContacts.py',
                                  'testVotes.py']

    def setUp(self):
        super(MeetingCommunesTestCase, self).setUp()
        self.meetingConfig = getattr(self.tool, self.cfg1_id)
        self.meetingConfig2 = getattr(self.tool, self.cfg2_id)

    def setUpRestrictedPowerObservers(self):
        """"""
        self.changeUser('siteadmin')
        context = self.portal.portal_setup._getImportContext('Products.MeetingBEP:testing')
        initializer = ToolInitializer(context, PROJECTNAME)
        initializer.addOrgs([rhc_org])
        self._setPowerObserverStates(states=('itemcreated', 'presented', 'returned_to_proposing_group',))
        self._setPowerObserverStates(observer_type='restrictedpowerobservers',
                                     states=('itemcreated', 'presented', 'returned_to_proposing_group',))
        cfg = self.meetingConfig
        cfg.setWorkflowAdaptations(('return_to_proposing_group', ))
        cfg.at_post_edit_script()
