# -*- coding: utf-8 -*-
# Copyright (C) 2014-2017 Andrey Antukh <niwi@niwi.nz>
# Copyright (C) 2014-2017 Jesús Espino <jespinog@gmail.com>
# Copyright (C) 2014-2017 David Barragán <bameda@dbarragan.com>
# Copyright (C) 2014-2017 Alejandro Alonso <alejandro.alonso@kaleidos.net>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from taiga.base.api import serializers
from taiga.base.fields import Field, MethodField
from taiga.base.neighbors import NeighborsSerializerMixin

from taiga.mdrender.service import render as mdrender
from taiga.projects.attachments.serializers import BasicAttachmentsInfoSerializerMixin
from taiga.projects.due_dates.serializers import DueDateSerializerMixin
from taiga.projects.mixins.serializers import OwnerExtraInfoSerializerMixin
from taiga.projects.mixins.serializers import ProjectExtraInfoSerializerMixin
from taiga.projects.mixins.serializers import AssignedToExtraInfoSerializerMixin
from taiga.projects.mixins.serializers import StatusExtraInfoSerializerMixin
from taiga.projects.notifications.mixins import WatchedResourceSerializer
from taiga.projects.tagging.serializers import TaggedInProjectResourceSerializer
from taiga.projects.votes.mixins.serializers import VoteResourceSerializerMixin
from taiga.projects.models import IssueStatus, IssueType
from .models import Issue
from ...users.models import User
class IssueListSerializer(VoteResourceSerializerMixin, WatchedResourceSerializer,
                          OwnerExtraInfoSerializerMixin, AssignedToExtraInfoSerializerMixin,
                          StatusExtraInfoSerializerMixin, ProjectExtraInfoSerializerMixin,
                          BasicAttachmentsInfoSerializerMixin, DueDateSerializerMixin,
                          TaggedInProjectResourceSerializer, serializers.LightSerializer):
    id = Field()
    formatted_issue_id = Field()
    ref = Field()
    severity = Field(attr="severity_id")
    priority = Field(attr="priority_id")
    type = Field(attr="type_id")
    milestone = Field(attr="milestone_id")
    project = Field(attr="project_id")
    created_date = Field()
    modified_date = Field()
    finished_date = Field()
    subject = Field()
    external_reference = Field()
    version = Field()
    watchers = Field()
    is_blocked = Field()
    blocked_note = Field()
    is_closed = Field()
    chainage_from = Field()
    chainage_to = Field()
    chainage_side = Field()
    issue_category = Field()
    issue_subcategory = Field()
    quantity = Field()
    unit_of_measurement = Field()
    treatment = Field()
    accident_date = Field()
    accident_time = Field()
    accident_nature = Field()
    accident_classification = Field()
    accident_causes = Field()
    road_feature = Field()
    road_condition = Field()
    intersection_type = Field()
    weather_condition = Field()
    vehicle_responsible = Field()
    affected_persons_fatal = Field()
    affected_persons_grievous = Field()
    affected_persons_minor = Field()
    affected_persons_non_injured = Field()
    animals_killed = Field()
    help_provided = Field()
    status_name = MethodField()
    description = Field()
    compliance_description = Field()
    inspection_category = Field()
    compliance_is_update = Field()
    investigation_description = Field()
    investigation_date = Field()
    asset_name = Field()
    test_name = Field()
    test_specifications = Field()
    desirable = Field()
    acceptable = Field()
    frequency = Field()
    investigation_chainage_from = Field()
    investigation_chainage_to = Field()
    investigation_chainage_side = Field()
    image_url = Field()
    testing_method = Field()

    closed_by_name = MethodField()
    
    def get_closed_by_name(self,obj):
        if obj.closed_by:
            try:
                changed = Issue.objects.get(project=obj.project,closed_by__user__id = obj.closed_by.id).first()
            except:
                changed = None
            if changed:
                return changed
            else:
                return ''
            # if obj.closed_by:
            #     return obj.closed_by
            # else:
            #     return ''

    def get_status_name(self, obj):
        if obj.status_id:
            try:
                status = IssueStatus.objects.get(pk = obj.status_id)
            except Exception as e:
                print(e)
                status = None

            if status:
                return status.name
            else:
                return ''

class IssueSerializer(IssueListSerializer):
    formatted_issue_id = Field()
    comment = MethodField()
    generated_user_stories = MethodField()
    blocked_note_html = MethodField()
    description = Field()
    description_html = MethodField()
    chainage_from = Field()
    chainage_to = Field()
    chainage_side = Field()
    issue_category = Field()
    issue_subcategory = Field()
    quantity = Field()
    unit_of_measurement = Field()
    treatment = Field()
    accident_date = Field()
    accident_time = Field()
    accident_nature = Field()
    accident_classification = Field()
    accident_causes = Field()
    road_feature = Field()
    road_condition = Field()
    intersection_type = Field()
    weather_condition = Field()
    vehicle_responsible = Field()
    affected_persons_fatal = Field()
    affected_persons_grievous = Field()
    affected_persons_minor = Field()
    affected_persons_non_injured = Field()
    animals_killed = Field()
    help_provided = Field()
    status_name = MethodField()
    description = Field()
    compliance_description = Field()
    target_date = Field()
    project_start_end_chainage = MethodField()
    inspection_category = Field()
    compliance_is_update = Field()
    investigation_description = Field()
    investigation_date = Field()
    asset_name = Field()
    test_name = Field()
    test_specifications = Field()
    desirable = Field()
    acceptable = Field()
    frequency = Field()
    investigation_chainage_from = Field()
    investigation_chainage_to = Field()
    investigation_chainage_side = Field()
    image_url = Field()
    testing_method = Field()
    closed_by_name = MethodField()
    
    def get_closed_by_name(self,obj):
        if obj.closed_by:
            try:
                changed = Issue.objects.filter(project=obj.project,closed_by = obj.closed_by.id).first()
            except:
                changed = None
            if changed:
                return changed.closed_by.full_name
            else:
                return ''
        



    def get_project_start_end_chainage(self, obj):
        return obj.project.start_and_end_chainage

    def get_status_name(self, obj):
        if obj.status_id:
            try:
                status = IssueStatus.objects.get(pk = obj.status_id)
            except:
                status = None

            if status:
                return status.name
            else:
                return ''

    def get_comment(self, obj):
        # NOTE: This method and field is necessary to historical comments work
        return ""

    def get_generated_user_stories(self, obj):
        assert hasattr(obj, "generated_user_stories_attr"), "instance must have a generated_user_stories_attr attribute"
        return obj.generated_user_stories_attr

    def get_blocked_note_html(self, obj):
        return mdrender(obj.project, obj.blocked_note)

    def get_description_html(self, obj):
        return mdrender(obj.project, obj.description)


class IssueNeighborsSerializer(NeighborsSerializerMixin, IssueSerializer):
    pass
