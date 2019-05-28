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

from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django.utils import timezone
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from taiga.projects.due_dates.models import DueDateMixin
from taiga.projects.occ import OCCModelMixin
from taiga.projects.notifications.mixins import WatchedModelMixin
from taiga.projects.mixins.blocked import BlockedMixin
from taiga.projects.tagging.models import TaggedMixin


class Issue(OCCModelMixin, WatchedModelMixin, BlockedMixin, TaggedMixin, DueDateMixin, models.Model):
    formatted_issue_id = models.CharField(max_length=200, null=True, blank=True, verbose_name=_("Issue Id"))
    issue_id_count = models.IntegerField(null=True, blank=True, verbose_name=_("Issue Id_Count"))
    ref = models.BigIntegerField(db_index=True, null=True, blank=True, default=None,
                                 verbose_name=_("ref"))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, default=None,
                              related_name="owned_issues", verbose_name=_("owner"))
    status = models.ForeignKey("projects.IssueStatus", null=True, blank=True,
                               related_name="issues", verbose_name=_("status"))
    severity = models.ForeignKey("projects.Severity", null=True, blank=True,
                                 related_name="issues", verbose_name=_("severity"))
    priority = models.ForeignKey("projects.Priority", null=True, blank=True,
                                 related_name="issues", verbose_name=_("priority"))
    type = models.ForeignKey("projects.IssueType", null=True, blank=True,
                             related_name="issues", verbose_name=_("type"))
    milestone = models.ForeignKey("milestones.Milestone", null=True, blank=True,
                                  default=None, related_name="issues",
                                  verbose_name=_("milestone"))
    project = models.ForeignKey("projects.Project", null=False, blank=False,
                                related_name="issues", verbose_name=_("project"))
    created_date = models.DateTimeField(null=False, blank=False,
                                        verbose_name=_("created date"),
                                        default=timezone.now)
    modified_date = models.DateTimeField(null=False, blank=False,
                                         verbose_name=_("modified date"))
    finished_date = models.DateTimeField(null=True, blank=True,
                                         verbose_name=_("finished date"))
    subject = models.TextField(null=False, blank=False,
                               verbose_name=_("subject"))
    description = models.TextField(null=False, blank=True, verbose_name=_("description"))
    compliance_description = models.TextField(null=True, blank=True, verbose_name=_("compliance description"))

    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                                    default=None, related_name="issues_assigned_to_me",
                                    verbose_name=_("assigned to"))
    attachments = GenericRelation("attachments.Attachment")
    external_reference = ArrayField(models.TextField(null=False, blank=False),
                                    null=True, blank=True, default=None, verbose_name=_("external reference"))

    chainage_from = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Chainage From"))
    chainage_to = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Chainage To"))
    chainage_side = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Chainage Side"))
    issue_category = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Issue Category"))
    issue_subcategory = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Issue Subcategory"))
    quantity = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Quantity"))
    unit_of_measurement = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Unit Of Measurement"))
    treatment = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Treatment"))
    accident_date = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Accident Date"))
    accident_time = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Accident Time"))
    accident_nature = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Accident Nature"))
    accident_classification = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Accident Classification"))
    accident_causes = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Accident Causes"))
    road_feature = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Road Feature"))
    road_condition = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Road Condition"))
    intersection_type = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Intersection Type"))
    weather_condition = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Weather Condition"))
    vehicle_responsible = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Vehicle Responsible"))
    affected_persons_fatal = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Affected Persons Fatal"))
    affected_persons_grievous = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Affected persons grievous"))
    affected_persons_minor = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Affected persons minor"))
    affected_persons_non_injured = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Affected persons non injured"))
    animals_killed = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Animals killed"))
    help_provided = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Help Provided"))
    target_date = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Target Date"))
    inspection_category = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Inspection Category"))
    compliance_is_update = models.BooleanField(default=False)

    # Investigation
    investigation_description = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Investigation Description"))
    investigation_date = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Investigation Date"))
    asset_name = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Asset Type"))
    test_name = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Test Name"))
    test_specifications = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Test Specification"))
    desirable = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Desirable"))
    acceptable = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Acceptable"))
    frequency = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Frequency"))
    investigation_chainage_from = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Investigation Chainage From"))
    investigation_chainage_to = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Investigation Chainage To"))
    investigation_chainage_side = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Investigation Chainage Side"))
    image_url = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Image Url"))
    testing_method = models.CharField(max_length=500, null=True, blank=True, verbose_name=_("Testng Method"))





    _importing = None

    class Meta:
        verbose_name = "issue"
        verbose_name_plural = "issues"
        ordering = ["project", "-id"]
        permissions = (
            ("view_issue", "Can view issue"),
        )

    def save(self, *args, **kwargs):
        if not self._importing or not self.modified_date:
            self.modified_date = timezone.now()

        if not self.status_id:
            self.status = self.project.default_issue_status

        if not self.type_id:
            self.type = self.project.default_issue_type

        if not self.severity_id:
            self.severity = self.project.default_severity

        if not self.priority_id:
            self.priority = self.project.default_priority

        return super().save(*args, **kwargs)

    def __str__(self):
        return "({1}) {0}".format(self.ref, self.subject)

    @property
    def is_closed(self):
        return self.status is not None and self.status.is_closed
