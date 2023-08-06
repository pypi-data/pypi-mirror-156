# -*- coding: utf-8 -*-

from plone.memoize import forever
from Products.MeetingBEP.config import HR_CONFIDENTIAL_GROUP_ID
from Products.PloneMeeting.utils import org_id_to_uid


@forever.memoize
def hr_group_uid(raise_on_error=False):
    """ """
    return org_id_to_uid(HR_CONFIDENTIAL_GROUP_ID, raise_on_error=raise_on_error)
