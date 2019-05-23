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
import pdfkit
from django.conf import settings

from django.core.files.storage import FileSystemStorage
from django.utils.translation import ugettext as _
from django.http import HttpResponse
from weasyprint import HTML, CSS

from taiga.base import filters
from taiga.base import exceptions as exc
from taiga.base import response
from taiga.base.decorators import list_route
from taiga.base.api import ModelCrudViewSet, ModelListViewSet
from taiga.base.api.mixins import BlockedByProjectMixin
from taiga.base.api.utils import get_object_or_404

from taiga.projects.history.mixins import HistoryResourceMixin
from taiga.projects.mixins.by_ref import ByRefMixin
from taiga.projects.models import Project, IssueStatus, Severity, Priority, IssueType
from taiga.projects.issues.models import Issue
from taiga.users.models import User
from taiga.projects.notifications.mixins import WatchedResourceMixin, WatchersViewSetMixin
from taiga.projects.occ import OCCResourceMixin
from taiga.projects.models import Project
from taiga.projects.tagging.api import TaggedResourceMixin
from taiga.projects.votes.mixins.viewsets import VotedResourceMixin, VotersViewSetMixin

from .utils import attach_extra_info

from . import models
from . import services
from . import write_excel
from . import permissions
from . import serializers
from . import validators
import datetime
from ..custom_attributes.models import IssueCustomAttribute, IssueCustomAttributesValues
from django.http import JsonResponse
from django.db.models import Count
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl import load_workbook
import pandas as pd
# from .export.pdf import html_to_pdf_view
# from .export.excel import WriteToExcel


def dashboard(request, project_id=None):

    result = {}
    project = Project.objects.get(pk = project_id)
    status = ['Closed', 'Maintenance Closed','Maintenance Pending']
    
    result['user_count'] = project.members.count()
    result['issues_identified'] = Issue.objects.filter(project_id = project_id, type__name = 'Issue',status__name__in=status).count()
    result['issue_closed'] = Issue.objects.filter(project_id = project_id, status__name__in = status, type__name = 'Issue').count()
    result['issue_pending'] = Issue.objects.filter(project_id = project_id, status__name = 'Pending', type__name = 'Issue').count()
    result['accidents_report'] = Issue.objects.filter(project_id = project_id, type__name = 'Accident').count()
    result['test_and_investigation'] = Issue.objects.filter(project_id=project_id, type__name='Investigation').count()

    return JsonResponse(result)


def new_registerd_user(request):
    result = {}
    today_date = datetime.datetime.today().strftime('%Y-%m-%d')
    result['new_registered_user'] = User.objects.filter(date_joined__icontains = today_date).count()
    return JsonResponse(result)


def dashboard_graph_data(request, project_id=None):
    issue_identified_months_list = []
    issue_closed_months_list = []
    accident_months_list = []

    time_threshold = datetime.datetime.now() - datetime.timedelta(days=150)

    # queryset = Issue.objects.filter(created_date = time_threshold)

    bymonth_select = {"month": """DATE_TRUNC('month', created_date)"""}

    issue_identified_months = Issue.objects.filter(project_id = int(project_id), created_date__gte = time_threshold).extra(select=bymonth_select).values('month').annotate(num_issues=Count('id')).order_by('-month')

    empty_data = [
        {
            "month": "Sep",
            "count": 0
        }, {
            "month": "Oct",
            "count": 0
        }, {
            "month": "Nov",
            "count": 0
        }, {
            "month": "Dec",
            "count": 0
        }]

    issue_identified_months_list.extend(empty_data)

    if issue_identified_months:
        for month in issue_identified_months:
            issue_identified_months_list.append({
                "month": month['month'].strftime("%b"),
                "count": month['num_issues']
            })
    else:
        issue_identified_months_list.append({
            "month": "Jan",
            "count": 0
        })

    issue_closed_months = Issue.objects.filter(project_id = int(project_id), status__name = 'Closed', created_date__gte = time_threshold).extra(select=bymonth_select).values('month').annotate(num_issues=Count('id')).order_by('-month')
    issue_closed_months_list.extend(empty_data)

    if issue_closed_months:
        for month in issue_closed_months:
            issue_closed_months_list.append({
                "month": month['month'].strftime("%b"),
                "count": month['num_issues']
            })
    else:
        issue_closed_months_list.append({
            "month": "Jan",
            "count": 0
        })


    accident_months = Issue.objects.filter(project_id = int(project_id), type__name = 'Accident', created_date__gte = time_threshold).extra(select=bymonth_select).values('month').annotate(num_issues=Count('id')).order_by('-month')
    accident_months_list.extend(empty_data)
    
    if accident_months:
        for month in accident_months:
            accident_months_list.append({
                "month": month['month'].strftime("%b"),
                "count": month['num_issues']
            })
    else:
        accident_months_list.append({
            "month": "Jan",
            "count": 0
        })

    response_data = {}

    response_data['issue_closed'] = issue_closed_months_list

    response_data['issue_identified'] = issue_identified_months_list 

    response_data['accident'] = accident_months_list

    return JsonResponse(response_data)


def issue_closed_graph_data(request):
    mon_count_list = []

    time_threshold = datetime.datetime.now() - datetime.timedelta(days=180)

    queryset = Issue.objects.filter(created_date = time_threshold)

    bymonth_select = {"month": """DATE_TRUNC('month', created_date)"""}

    months = Issue.objects.filter(status__name = 'open', created_date__gte = time_threshold).extra(select=bymonth_select).values('month').annotate(num_issues=Count('id')).order_by('-month')

    for month in months:
        mon_count_list.append({
            "month": month['month'].strftime("%b"),
            "count": month['num_issues']
        })

    response_data = {}

    return JsonResponse([{ "month": "Jul", "count": 4 }, { "month": "Aug", "count": 7 }, { "month": "Sep", "count": 10 }, { "month": "Oct", "count": 18 }, { "month": "Nov", "count": 22 }], safe = False)

def accident_graph_data(request):
    mon_count_list = []

    time_threshold = datetime.datetime.now() - datetime.timedelta(days=180)

    queryset = Issue.objects.filter(created_date = time_threshold)

    bymonth_select = {"month": """DATE_TRUNC('month', created_date)"""}

    months = Issue.objects.filter(type__name = 'Accident', created_date__gte = time_threshold).extra(select=bymonth_select).values('month').annotate(num_issues=Count('id')).order_by('-month')

    for month in months:
        mon_count_list.append({
            "month": month['month'].strftime("%b"),
            "count": month['num_issues']
        })

    response_data = {}
    response_data['accident_graph_data'] = [{ "month": "Jul", "count": 8 }, { "month": "Aug", "count": 7 }, { "month": "Sep", "count": 12 }, { "month": "Oct", "count": 16 }, { "month": "Nov", "count": 2 }]

    # return JsonResponse(mon_count_list, safe=False)

    return JsonResponse(response_data)


class IssueViewSet(
    OCCResourceMixin, VotedResourceMixin, HistoryResourceMixin, WatchedResourceMixin,
    ByRefMixin, TaggedResourceMixin, BlockedByProjectMixin, ModelCrudViewSet):
    validator_class = validators.IssueValidator
    queryset = models.Issue.objects.order_by('-id')
    permission_classes = (permissions.IssuePermission, )
    filter_backends = (filters.CanViewIssuesFilterBackend,
                       filters.RoleFilter,
                       filters.OwnersFilter,
                       filters.AssignedToFilter,
                       filters.StatusesFilter,
                       filters.IssueTypesFilter,
                       filters.SeveritiesFilter,
                       filters.PrioritiesFilter,
                       filters.TagsFilter,
                       filters.WatchersFilter,
                       filters.QFilter,
                       filters.CreatedDateFilter,
                       filters.ModifiedDateFilter,
                       filters.FinishedDateFilter,
                       filters.OrderByFilterMixin)
    filter_fields = ("milestone",
                     "project",
                     "type_id",
                     "project__slug",
                     "status__is_closed",
                     "status__name")
    order_by_fields = ("type",
                       "project",
                       "status",
                       "severity",
                       "priority",
                       "created_date",
                       "modified_date",
                       "owner",
                       "assigned_to",
                       "subject",
                       "total_voters")

    def get_serializer_class(self, *args, **kwargs):

        if self.action in ["retrieve", "by_ref"]:
            return serializers.IssueNeighborsSerializer

        if self.action == "list":
            return serializers.IssueListSerializer

        return serializers.IssueSerializer

    def update(self, request, *args, **kwargs):
        self.object = self.get_object_or_none()
        project_id = request.DATA.get('project', None)

        if project_id and self.object and self.object.project.id != project_id:
            try:
                new_project = Project.objects.get(pk=project_id)
                self.check_permissions(request, "destroy", self.object)
                self.check_permissions(request, "create", new_project)

                sprint_id = request.DATA.get('milestone', None)
                if sprint_id is not None and new_project.milestones.filter(pk=sprint_id).count() == 0:
                    request.DATA['milestone'] = None

                status_id = request.DATA.get('status', None)
                if status_id is not None:
                    try:
                        old_status = self.object.project.issue_statuses.get(pk=status_id)
                        new_status = new_project.issue_statuses.get(slug=old_status.slug)
                        request.DATA['status'] = new_status.id
                    except IssueStatus.DoesNotExist:
                        request.DATA['status'] = new_project.default_issue_status.id

                priority_id = request.DATA.get('priority', None)
                if priority_id is not None:
                    try:
                        old_priority = self.object.project.priorities.get(pk=priority_id)
                        new_priority = new_project.priorities.get(name=old_priority.name)
                        request.DATA['priority'] = new_priority.id
                    except Priority.DoesNotExist:
                        request.DATA['priority'] = new_project.default_priority.id

                severity_id = request.DATA.get('severity', None)
                if severity_id is not None:
                    try:
                        old_severity = self.object.project.severities.get(pk=severity_id)
                        new_severity = new_project.severities.get(name=old_severity.name)
                        request.DATA['severity'] = new_severity.id
                    except Severity.DoesNotExist:
                        request.DATA['severity'] = new_project.default_severity.id

                type_id = request.DATA.get('type', None)
                if type_id is not None:
                    try:
                        old_type = self.object.project.issue_types.get(pk=type_id)
                        new_type = new_project.issue_types.get(name=old_type.name)
                        request.DATA['type'] = new_type.id
                    except IssueType.DoesNotExist:
                        request.DATA['type'] = new_project.default_issue_type.id

            except Project.DoesNotExist:
                return response.BadRequest(_("The project doesn't exist"))

        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        type = self.request.QUERY_PARAMS.get('type_id', None)
        q1 = self.request.QUERY_PARAMS.get('issue_cat', None)
        q2 = self.request.QUERY_PARAMS.get('issue_sub', None)
        start_date = self.request.QUERY_PARAMS.get('start_date', None)
        end_date = self.request.QUERY_PARAMS.get('end_date', None)
        params = self.request.QUERY_PARAMS
        type_name = IssueType.objects.get(id=type)

        qs = super().get_queryset()

        if q1 and q2 and start_date and end_date:
            if type_name.name == "Investigation":
                qs = qs.filter(asset_name=q1, test_name=q2,created_date__date__range=[start_date, end_date])
            else:
                qs = qs.filter(issue_category=q1, issue_subcategory=q2,created_date__date__range=[start_date, end_date])
        elif q1 and start_date and end_date:
            if type_name.name == "Investigation":
                qs = qs.filter(asset_name=q1,created_date__date__range=[start_date, end_date])
            else:
                qs = qs.filter(issue_category=q1,created_date__date__range=[start_date, end_date])
        
        elif start_date and end_date:
            qs = qs.filter(created_date__date__range=[start_date, end_date])
        print(qs.count())
        qs = qs.select_related("owner", "assigned_to", "status", "project")
        include_attachments = "include_attachments" in self.request.QUERY_PARAMS
        qs = attach_extra_info(qs, user=self.request.user,
                               include_attachments=include_attachments,)
        return qs

    def pre_save(self, obj):
        if not obj.id:
            obj.owner = self.request.user

        super().pre_save(obj)

    # def post_save(self, object, created=False):
    #     super().post_save(object, created=created)

    #     if not created:
    #         return
    #     else:
    #         project_id = object.project_id

    #         field_list = ["issue_id","chainage_from","chainage_to","chainage_side","issue_category","issue_subcategory",
    #         "quantity","unit_of_measurement","treatment"]

    #         for field in field_list:
    #             issue_custom_attr = IssueCustomAttribute.objects.get(project_id = project_id, name=field)                

    #             if issue_custom_attr:
    #                 IssueCustomAttributesValues.objects.filter(issue_id=object.pk).update(version=1, attributes_values
    #                 ='{\"'+str(issue_custom_attr.id)+'\":\"Check\" }, {"'+str(issue_custom_attr.id)+'":"Check Now" }')


    def pre_conditions_on_save(self, obj):
        if obj.milestone and obj.milestone.project != obj.project:
            raise exc.PermissionDenied(_("You don't have permissions to set this sprint "
                                         "to this issue."))

        if obj.status and obj.status.project != obj.project:
            raise exc.PermissionDenied(_("You don't have permissions to set this status "
                                         "to this issue."))

        if obj.severity and obj.severity.project != obj.project:
            raise exc.PermissionDenied(_("You don't have permissions to set this severity "
                                         "to this issue."))

        if obj.priority and obj.priority.project != obj.project:
            raise exc.PermissionDenied(_("You don't have permissions to set this priority "
                                         "to this issue."))

        if obj.type and obj.type.project != obj.project:
            raise exc.PermissionDenied(_("You don't have permissions to set this type "
                                         "to this issue."))

        super().pre_conditions_on_save(obj)

    @list_route(methods=["GET"])
    def filters_data(self, request, *args, **kwargs):
        project_id = request.QUERY_PARAMS.get("project", None)
        project = get_object_or_404(Project, id=project_id)

        filter_backends = self.get_filter_backends()
        types_filter_backends = (f for f in filter_backends if f != filters.IssueTypesFilter)
        statuses_filter_backends = (f for f in filter_backends if f != filters.StatusesFilter)
        assigned_to_filter_backends = (f for f in filter_backends if f != filters.AssignedToFilter)
        owners_filter_backends = (f for f in filter_backends if f != filters.OwnersFilter)
        priorities_filter_backends = (f for f in filter_backends if f != filters.PrioritiesFilter)
        severities_filter_backends = (f for f in filter_backends if f != filters.SeveritiesFilter)
        roles_filter_backends = (f for f in filter_backends if f != filters.RoleFilter)

        queryset = self.get_queryset()
        querysets = {
            "types": self.filter_queryset(queryset, filter_backends=types_filter_backends),
            "statuses": self.filter_queryset(queryset, filter_backends=statuses_filter_backends),
            "assigned_to": self.filter_queryset(queryset, filter_backends=assigned_to_filter_backends),
            "owners": self.filter_queryset(queryset, filter_backends=owners_filter_backends),
            "priorities": self.filter_queryset(queryset, filter_backends=priorities_filter_backends),
            "severities": self.filter_queryset(queryset, filter_backends=severities_filter_backends),
            "tags": self.filter_queryset(queryset),
            "roles": self.filter_queryset(queryset, filter_backends=roles_filter_backends),
        }
        return response.Ok(services.get_issues_filters_data(project, querysets))

    @list_route(methods=["GET"])
    def csv(self, request):
        get_data={}
        status_id = []
        # PDF or Excel
        doc_type = request.QUERY_PARAMS.get('doc_type', None)
        uuid = request.QUERY_PARAMS.get("uuid", None)
        start_date = request.QUERY_PARAMS.get('start_date', None)
        end_date = request.QUERY_PARAMS.get('end_date', None)
        type = request.QUERY_PARAMS.get('type', None)
        status = request.QUERY_PARAMS.get('status', None)
        asset = request.QUERY_PARAMS.get('asset_cat', None)
        performance = request.QUERY_PARAMS.get('performance_cat', None)
        photo = request.QUERY_PARAMS.get('photo', None)
        name = request.QUERY_PARAMS.get('type_name', None)
        if status:
            status = status.split(',')
        if uuid is None:
            return response.NotFound()

        project = get_object_or_404(Project, issues_csv_uuid=uuid)

        if asset and performance:
            if status:
                queryset = project.issues.filter(issue_category=asset,issue_subcategory=performance,type__name=type,status__id__in=status, created_date__date__range=[start_date, end_date]).order_by('ref')

            else:
                if type=="Investigation":
                    queryset = project.issues.filter(asset_name=asset,test_name=performance,type__name=type, created_date__date__range=[start_date, end_date]).order_by('ref')
                else:
                    queryset = project.issues.filter(issue_category=asset,issue_subcategory=performance,type__name=type, created_date__date__range=[start_date, end_date]).order_by('ref')
        if asset:
            if status:
                queryset = project.issues.filter(issue_category=asset,type__name=type,status__id__in=status, created_date__date__range=[start_date, end_date]).order_by('ref')

            else:
                if type=="Investigation":
                    queryset = project.issues.filter(asset_name=asset,type__name=type, created_date__date__range=[start_date, end_date]).order_by('ref')
                else:
                    queryset = project.issues.filter(issue_category=asset,type__name=type, created_date__date__range=[start_date, end_date]).order_by('ref')
        else:
            queryset = project.issues.filter(type__name=type,created_date__date__range=[start_date, end_date]).order_by('ref')
        

        data = write_excel.write_excel(project, queryset, type, status, start_date, end_date,asset,performance,photo,doc_type,name)
        

        if doc_type=="excel":
            csv_response = HttpResponse(save_virtual_workbook(data), content_type='application/vnd.ms-excel; charset=utf-8')
            csv_response['Content-Disposition'] = 'attachment; filename="issues.xlsx"'
            return csv_response
            
        if doc_type=="pdf":
            html = HTML(string=data)
            
            
            html.write_pdf(target='/tmp/mypdf.pdf',stylesheets=[CSS(settings.STATIC_ROOT +  '/main.css')], presentational_hints=True);
            # print("=============================")
            # print(html)
            fs = FileSystemStorage('/tmp')
            with fs.open('mypdf.pdf') as pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="mypdf.pdf"'
                return response
            # csv_response = HttpResponse(data, content_type='text/html; charset=utf-8')
            # csv_response['Content-Disposition'] = 'attachment; filename="issues.html"'
            # return csv_response
           

    @list_route(methods=["GET"])
    def new(self, request):
        get_data={}
        status_id = []
        uuid = request.QUERY_PARAMS.get("uuid", None)
        start_date = request.QUERY_PARAMS.get('start_date')
        end_date = request.QUERY_PARAMS.get('end_date')
        type = request.QUERY_PARAMS.get('type')
        status = request.QUERY_PARAMS.get('status')
        asset = request.QUERY_PARAMS.get('asset_cat')
        performance = request.QUERY_PARAMS.get('performance_cat')
        photo = request.QUERY_PARAMS.get('photo')
        get_data['start_date'] = start_date
        get_data['end_date'] = end_date
        get_data['status'] = status
        get_data['type'] = type
        get_data['asset'] = asset
        get_data['performance'] = performance
        get_data['photo'] = photo
        return JsonResponse(get_data)
        

    @list_route(methods=["POST"])
    def bulk_create(self, request, **kwargs):
        validator = validators.IssuesBulkValidator(data=request.DATA)
        if validator.is_valid():
            data = validator.data
            project = Project.objects.get(pk=data["project_id"])
            self.check_permissions(request, 'bulk_create', project)
            if project.blocked_code is not None:
                raise exc.Blocked(_("Blocked element"))

            issues = services.create_issues_in_bulk(
                data["bulk_issues"], milestone_id=data["milestone_id"],
                project=project, owner=request.user,
                status=project.default_issue_status,
                severity=project.default_severity,
                priority=project.default_priority,
                type=project.default_issue_type,
                callback=self.post_save, precall=self.pre_save)

            issues = self.get_queryset().filter(id__in=[i.id for i in issues])
            issues_serialized = self.get_serializer_class()(issues, many=True)

            return response.Ok(data=issues_serialized.data)

        return response.BadRequest(validator.errors)


class AccidentTypeIssue(IssueViewSet):
    
    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     qs = qs.filter(type__name='Accident').select_related("owner", "assigned_to", "status", "project")
    #     return qs

    def create(self, request, *args, **kwargs):

        project_id = request.DATA.get('project', None)

        try:
            type_value = IssueType.objects.get(name='Accident', project_id = project_id)
            request.DATA['type'] = type_value.id
        except IssueType.DoesNotExist:
            request.DATA['type'] = None

        return super().create(request, *args, **kwargs)

    def post_save(self, object, created=False):
        super().post_save(object, created=created)

        if created:
            project_id = object.project_id

            try:
                issue_status_id = IssueStatus.objects.get(project_id = project_id, name = "Open")
            except:
                issue_status_id = None

            if issue_status_id:
                Issue.objects.filter(id = object.id).update(status_id = issue_status_id.id)
        else:
            status_name = self.request.DATA['status_name']
            project = self.request.DATA['project']

            try:
                issue_status_id = IssueStatus.objects.get(project_id = project, name = status_name)
            except:
                issue_status_id = None

            if issue_status_id:
                Issue.objects.filter(id = object.id).update(status_id = issue_status_id.id)

            try:
                type_value_id = IssueType.objects.get(name='Accident', project_id = project)
            except:
                type_value_id = None

            if type_value_id:
                Issue.objects.filter(id = object.id).update(type_id = type_value_id.id)


class InvestigationTypeIssue(IssueViewSet):

    """
    To save investigation issue type.

    :parameter:

        parameters -->

        {
            'project': 'CharField',
            'subject': 'CharField',
            'status_name': 'CharField'
        }

        example -->

        {
            'project': '135',
            'subject': 'This is test issue.',
            'status_name': 'Open'
        }

        response -->

        {

        }

        authorization -->

        Authorization: Bearer ${AUTH_TOKEN}

    """

    def create(self, request, *args, **kwargs):

        project_id = request.DATA.get('project', None)

        try:
            type_value = IssueType.objects.get(name='Investigation', project_id=project_id)
            request.DATA['type'] = type_value.id

        except IssueType.DoesNotExist:
            request.DATA['type'] = None

        return super().create(request, *args, **kwargs)

    def post_save(self, object, created=False):

        super().post_save(object, created=created)

        if created:

            project_id = object.project_id

            try:
                issue_status_id = IssueStatus.objects.get(project_id=project_id, name='Open')
            except:
                issue_status_id = None

            if issue_status_id:
                Issue.objects.filter(id=object.id).update(status_id=issue_status_id)

        else:

            status_name = self.request.DATA['status_name']
            project = self.request.DATA['project']

            try:
                issue_status_id = IssueStatus.objects.get(project_id=project, name=status_name)
            except:
                issue_status_id = None

            if issue_status_id:
                Issue.objects.filter(id=object.id).update(status_id=issue_status_id)

            try:
                type_value_id = IssueType.objects.get(name='Investigation', project_id=project)
            except:
                type_value_id = None

            if type_value_id:
                Issue.objects.filter(id=object.id).update(type_id=type_value_id.id)


class IssueTypeIssue(IssueViewSet):

    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     qs = qs.filter(type__name='Issue', status__name='Open')
    #     return qs

    def create(self, request, *args, **kwargs):
        project_id = request.DATA.get('project', None)
        issues_detail = Issue.objects.filter(type__name='Issue').order_by('id').last()

        project = Project.objects.get(id = project_id)

        if project:
            short_name = str(project.package_no)
        else:
            short_name = ''

        if issues_detail:
            issueidcount = issues_detail.issue_id_count
            if issueidcount:
                request.DATA['issue_id_count'] = issueidcount + 1
            else:
                request.DATA['issue_id_count'] = 1
        else:
            request.DATA['issue_id_count'] = 1

        issue_id_count = str(request.DATA['issue_id_count'])
        now = datetime.datetime.now()
        prev_year = str(now.year -1)
        current_year = str(now.year)

        year = prev_year + "-" + current_year[2:]
        mon = now.strftime("%b")

        request.DATA['formatted_issue_id'] = 'TOT-1/'+short_name+'/'+year+'/'+mon+'/'+issue_id_count+''

        try:
            type_value = IssueType.objects.get(name='Issue', project_id = project_id)
            request.DATA['type'] = type_value.id
        except IssueType.DoesNotExist:
            request.DATA['type'] = None

        return super().create(request, *args, **kwargs)

    def post_save(self, object, created=False, updated=False):
        super().post_save(object, created=created)

        if created:
            project_id = object.project_id

            try:
                issue_status_id = IssueStatus.objects.get(project_id = project_id, name = "Open")
            except:
                issue_status_id = None

            if issue_status_id:
                Issue.objects.filter(id = object.id).update(status_id = issue_status_id.id)

            
        else:
            try:
                issue_status_id = IssueStatus.objects.get(project_id = project, name = status_name)
            except:
                issue_status_id = None

            if issue_status_id:
                Issue.objects.filter(id = object.id).update(status_id = issue_status_id.id)

            try:
                type_value_id = IssueType.objects.get(name='Issue', project_id = project)
            except:
                type_value_id = None

            if type_value_id:
                Issue.objects.filter(id = object.id).update(type_id = type_value_id.id)


class ComplianceTypeIssue(IssueViewSet):
    pass
    # def get_queryset(self):
    #     qs = super().get_queryset()
    #     qs = qs.filter(type__name='Issue', status__name='Closed')
    #     return qs

class IssueVotersViewSet(VotersViewSetMixin, ModelListViewSet):
    permission_classes = (permissions.IssueVotersPermission,)
    resource_model = models.Issue


class IssueWatchersViewSet(WatchersViewSetMixin, ModelListViewSet):
    permission_classes = (permissions.IssueWatchersPermission,)
    resource_model = models.Issue
