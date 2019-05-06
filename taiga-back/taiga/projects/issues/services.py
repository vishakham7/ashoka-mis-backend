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

import io
import csv
import os
from collections import OrderedDict
from operator import itemgetter
from contextlib import closing

from django.db import connection
from django.utils.translation import ugettext as _

from taiga.base.utils import db, text
from taiga.projects.issues.apps import (
    connect_issues_signals,
    disconnect_issues_signals)
from taiga.projects.votes.utils import attach_total_voters_to_queryset
from taiga.projects.notifications.utils import attach_watchers_to_queryset
from django.conf import settings

from . import models
from taiga.users.models import User
from taiga.projects.attachments.models import Attachment

from datetime import datetime
#####################################################
# Bulk actions
#####################################################

def get_issues_from_bulk(bulk_data, **additional_fields):
    """Convert `bulk_data` into a list of issues.

    :param bulk_data: List of issues in bulk format.
    :param additional_fields: Additional fields when instantiating each issue.

    :return: List of `Issue` instances.
    """
    return [models.Issue(subject=line, **additional_fields)
            for line in text.split_in_lines(bulk_data)]


def create_issues_in_bulk(bulk_data, callback=None, precall=None, **additional_fields):
    """Create issues from `bulk_data`.

    :param bulk_data: List of issues in bulk format.
    :param callback: Callback to execute after each issue save.
    :param additional_fields: Additional fields when instantiating each issue.

    :return: List of created `Issue` instances.
    """
    issues = get_issues_from_bulk(bulk_data, **additional_fields)

    disconnect_issues_signals()

    try:
        db.save_in_bulk(issues, callback, precall)
    finally:
        connect_issues_signals()

    return issues


#####################################################
# CSV
#####################################################

def issues_to_csv(project, queryset, type, status):
    csv_data = io.StringIO()
    

    queryset = queryset.prefetch_related("attachments",
                                         "generated_user_stories",
                                         "custom_attributes_values")
    queryset = queryset.select_related("owner",
                                       "assigned_to",
                                       "status",
                                       "project",
                                       "type")
    queryset = attach_total_voters_to_queryset(queryset)
    queryset = attach_watchers_to_queryset(queryset)
    print(type)

    if type == 'Issue':
        fieldnames = ["Sr.No", "Project Name", "Chainage From", "Chainage To", "Direction", "Description of Issue",
                              "Photograph During Inspection", "Asset Type", "Performance Parameter",
                              "Issue Raised On", "Issue Raised By", "description",
                              "Issue Raised To","attached_file"]

    if type == 'Issue' and status== 'Closed':
        fieldnames = ["Sr.No", "Project Name", "Chainage From", "Chainage To", "Direction", "Description of Issue",
                          "Photograph During Inspection", "Asset Type", "Performance Parameter",
                          "Issue Raised On", "Issue Raised By",
                          "Issue Raised To" , "Timeline",
                          "Target Date", "Status",
                          "Issue Closed On Date", "Complianced", "Issue Closed By",
                          "Photograph Post Compliance", "Remark", "Current Status","Description Of Compliance" ]
    if type == 'Investigation':
        fieldnames = ["Sr.No", "Project Name", "Chainage From", "Chainage To", "Direction", "Description of Issue",
                          "Photograph During Inspection", "Asset Type", "Performance Parameter",
                          "Issue Raised On", "Name of Test", "Testing Method", "Standard References for testing",
                          "Test Carried Out Date", "Testing Carried Out By", "Remark", "Outcome Report"]
        

    if type == 'Accident':
        fieldnames = ["Sr.No", "Description","No of Accidents previous month","No of Peoples affected previous month","No of Accidents during this month",
                        "No of Peoples affected during this month", "No of Accidents upto this month", "No of Peoples affected upto this month"]

    custom_attrs = project.issuecustomattributes.all()
        
    for custom_attr in custom_attrs:
        fieldnames.append(custom_attr.name)
    
    writer = csv.DictWriter(csv_data, fieldnames=fieldnames)
    writer.writeheader()

    animals_killed_count = 0
    
    for issue in queryset:
       
        if issue:

            qqq = issue.watchers
            watchers = []
            wathcer_username = issue.assigned_to.full_name + '\n'
            for i in qqq:
                sql = User.objects.get(id=int(i))
                watchers.append(sql.full_name)
            for j in watchers:
                wathcer_username = j +'\n'+ wathcer_username 

            if issue.type.name == type:
                if issue.attachments:
                    file_name = "" 
                    files = []
                    file = issue.attachments.filter(project__id=issue.project.id).values_list('attached_file')
                    for i in file:
                        files.extend(i)
                    #     for j in len(file):
                    #         files.append(file[j])
                    for j in files:
                        file_name = os.path.join(settings.MEDIA_URL,str(j)) +'\n' + file_name
                else:
                    file_name=""
                print(file_name)
                issue_data = {
                    "Sr.No" : issue.ref,
                    "Project Name" : issue.project.name,
                    "Chainage From" : issue.chainage_from,
                    "Chainage To" : issue.chainage_to,
                    "Direction" : issue.chainage_side,
                    "Description of Issue" : issue.description,
                    "Photograph During Inspection" : file_name if issue.attachments else None,
                   
                    "Asset Type" : issue.issue_category,
                    "Performance Parameter" : issue.issue_subcategory,
                    "Issue Raised On" : issue.created_date,
                    "Issue Raised By" : issue.owner.full_name if issue.owner else None,
                    "Issue Raised To" : wathcer_username,
                }
    
        if status:
            if issue.type.name == type and issue.status.name == status:
                qqq = issue.watchers
                watchers = []
                wathcer_username = issue.assigned_to.full_name + '\n'
                for i in qqq:
                    sql = User.objects.get(id=int(i))
                    watchers.append(sql.full_name)
                print(watchers)
                for j in watchers:
                    wathcer_username = j +'\n'+ wathcer_username 
                a = issue.created_date.date()
                b = datetime.strptime(issue.target_date,"%d/%m/%Y").date()
                timeline = b-a

                if issue.attachments:
                    file_name = "" 
                    files = []
                    file = issue.attachments.filter(project_id=issue.project.id).values_list('attached_file')
                    for i in file:
                        files.extend(i)
                    #     for j in len(file):
                    #         files.append(file[j])
                    for j in files:
                        file_name = os.path.join(settings.MEDIA_URL,str(j)) +'\n' + file_name
                else:
                    file_name=""
                print(file_name)
                issue_data = {
                "Sr.No" : issue.ref,
                "Project Name" : issue.project.name,
                "Chainage From" : issue.chainage_from,
                "Chainage To" : issue.chainage_to,
                "Direction" : issue.chainage_side,
                "Description of Issue" : issue.description,
                "Photograph During Inspection" : file_name,
                "Asset Type" : issue.issue_category,
                "Performance Parameter" : issue.issue_subcategory,
                "Issue Raised On" : issue.created_date,
                "Issue Raised By" : issue.owner.full_name if issue.owner else None,
                "Issue Raised To" : wathcer_username,
                "Timeline" : timeline,
                "Target Date" : issue.target_date,
                "Status" : issue.status.name if issue.status else None,
                "Issue Closed On Date" : issue.finished_date if status=='Closed' else None,
                "Complianced" : 'Yes' if issue.compliance_is_update==False else 'No',
                "Issue Closed By" : "",
                "Description Of Compliance": issue.compliance_description,
                "Photograph Post Compliance" : issue.attachments.name,
                "Remark":"",
                # "Current_Status" : "Closed" if issue.status.is_closed==True else "Open",
            }

          
        if issue.type.name == 'Investigation':
            issue_data = {
                "Sr.No" : issue.ref,
                "Project Name" :   issue.project.name,
                "Chainage From" : issue.investigation_chainage_from,
                "Chainage To" : issue.investigation_chainage_to,
                "Direction" : issue.investigation_chainage_side,
                "Description of Issue" : issue.investigation_description,
                "Asset Type" : issue.asset_name,
                "Performance Parameter" : issue.test_name,
                "Name of Test" : "",
                "Testing Method" : "",
                "Standard References for testing" : "",
                "Test Carried Out Date" :"",
                "Testing Carried Out By" :issue.assigned_to.username if issue.assigned_to else None,
                "Outcome Report" : "",
                "Remark" :"",
            }


            

        if issue.type.name == 'Accident':
            last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
            first_date_of_previos_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)
            first_date = date.today().replace(day=1)
            current_date = date.today()
            previous_month = first_date_of_previos_month
            Previous_last_date = last_day_of_prev_month
            animals_killed_last_month = project.issues.filter(created_date__date__range=[previous_month,Previous_last_date],type__name='Accident').values_list('animals_killed', flat=True)
            
            animal_list_last_month = list(animals_killed_last_month)
            new_list_last = []
            
            if animals_killed_last_month:
                for i in animals_killed_last_month:
                    if i:
                        new_list_last.append(int(i))


            animals_killed_cuurent_month = project.issues.filter(created_date__date__range=[first_date,current_date],type__name='Accident').values_list('animals_killed', flat=True)
            animal_list_current_month = list(animals_killed_cuurent_month)
            new_list_current = []
            if animals_killed_cuurent_month:
                for i in animal_list_current_month:
                    if i:
                        new_list_current.append(int(i))


            animals_killed_upto_month = project.issues.filter(type__name='Accident').values_list('animals_killed', flat=True)

            animal_list_upto_month = list(animals_killed_upto_month)
            new_list_upto = []
            if animals_killed_upto_month:
                for i in animal_list_upto_month:
                    if i:
                        new_list_upto.append(int(i))
            
            issue_data = {
                "Sr.No" : issue.ref,
                "Description" : issue.accident_classification,
                "No_of_Accidents_previous_month":project.issues.filter(type__name='Accident',created_date__date__range=[previous_month,Previous_last_date]).count(),
                "No_of_Peoples_affected_previous_month": sum(new_list_last),
                "No_of_Accidents_during_this_month":project.issues.filter(type__name='Accident',created_date__date__range=[first_date,current_date]).count(),
                "No_of_Peoples_affected_during_this_month": sum(new_list_current),
                "No_of_Accidents_upto_this_month":project.issues.filter(type__name='Accident').count(),
                "No_of_Peoples_affected_upto_this_month": sum(new_list_upto),

            }
        for custom_attr in custom_attrs:
            value = issue.custom_attributes_values.attributes_values.get(str(custom_attr.id), None)
            issue_data[custom_attr.name] = value

        writer.writerow(issue_data) 

    return csv_data

    


#####################################################
# Api filter data
#####################################################

def _get_issues_statuses(project, queryset):
    compiler = connection.ops.compiler(queryset.query.compiler)(queryset.query, connection, None)
    queryset_where_tuple = queryset.query.where.as_sql(compiler, connection)
    where = queryset_where_tuple[0]
    where_params = queryset_where_tuple[1]

    extra_sql = """
        WITH counters AS (
                SELECT status_id, count(status_id) count
                  FROM "issues_issue"
            INNER JOIN "projects_project" ON ("issues_issue"."project_id" = "projects_project"."id")
                 WHERE {where}
              GROUP BY status_id
        )

                 SELECT "projects_issuestatus"."id",
                        "projects_issuestatus"."name",
                        "projects_issuestatus"."color",
                        "projects_issuestatus"."order",
                        COALESCE(counters.count, 0)
                   FROM "projects_issuestatus"
        LEFT OUTER JOIN counters ON counters.status_id = projects_issuestatus.id
                  WHERE "projects_issuestatus"."project_id" = %s
               ORDER BY "projects_issuestatus"."order";
    """.format(where=where)

    with closing(connection.cursor()) as cursor:
        cursor.execute(extra_sql, where_params + [project.id])
        rows = cursor.fetchall()

    result = []
    for id, name, color, order, count in rows:
        result.append({
            "id": id,
            "name": _(name),
            "color": color,
            "order": order,
            "count": count,
        })
    return sorted(result, key=itemgetter("order"))


def _get_issues_types(project, queryset):
    compiler = connection.ops.compiler(queryset.query.compiler)(queryset.query, connection, None)
    queryset_where_tuple = queryset.query.where.as_sql(compiler, connection)
    where = queryset_where_tuple[0]
    where_params = queryset_where_tuple[1]

    extra_sql = """
        WITH counters AS (
                SELECT type_id, count(type_id) count
                  FROM "issues_issue"
            INNER JOIN "projects_project" ON ("issues_issue"."project_id" = "projects_project"."id")
                 WHERE {where}
              GROUP BY type_id
        )

                 SELECT "projects_issuetype"."id",
                        "projects_issuetype"."name",
                        "projects_issuetype"."color",
                        "projects_issuetype"."order",
                        COALESCE(counters.count, 0)
                   FROM "projects_issuetype"
        LEFT OUTER JOIN counters ON counters.type_id = projects_issuetype.id
                  WHERE "projects_issuetype"."project_id" = %s
               ORDER BY "projects_issuetype"."order";
    """.format(where=where)

    with closing(connection.cursor()) as cursor:
        cursor.execute(extra_sql, where_params + [project.id])
        rows = cursor.fetchall()

    result = []
    for id, name, color, order, count in rows:
        result.append({
            "id": id,
            "name": _(name),
            "color": color,
            "order": order,
            "count": count,
        })
    return sorted(result, key=itemgetter("order"))


def _get_issues_priorities(project, queryset):
    compiler = connection.ops.compiler(queryset.query.compiler)(queryset.query, connection, None)
    queryset_where_tuple = queryset.query.where.as_sql(compiler, connection)
    where = queryset_where_tuple[0]
    where_params = queryset_where_tuple[1]

    extra_sql = """
        WITH counters AS (
                SELECT priority_id, count(priority_id) count
                  FROM "issues_issue"
            INNER JOIN "projects_project" ON ("issues_issue"."project_id" = "projects_project"."id")
                 WHERE {where}
              GROUP BY priority_id
        )

                 SELECT "projects_priority"."id",
                        "projects_priority"."name",
                        "projects_priority"."color",
                        "projects_priority"."order",
                        COALESCE(counters.count, 0)
                   FROM "projects_priority"
        LEFT OUTER JOIN counters ON counters.priority_id = projects_priority.id
                  WHERE "projects_priority"."project_id" = %s
               ORDER BY "projects_priority"."order";
    """.format(where=where)

    with closing(connection.cursor()) as cursor:
        cursor.execute(extra_sql, where_params + [project.id])
        rows = cursor.fetchall()

    result = []
    for id, name, color, order, count in rows:
        result.append({
            "id": id,
            "name": _(name),
            "color": color,
            "order": order,
            "count": count,
        })
    return sorted(result, key=itemgetter("order"))


def _get_issues_severities(project, queryset):
    compiler = connection.ops.compiler(queryset.query.compiler)(queryset.query, connection, None)
    queryset_where_tuple = queryset.query.where.as_sql(compiler, connection)
    where = queryset_where_tuple[0]
    where_params = queryset_where_tuple[1]

    extra_sql = """
        WITH counters AS (
                SELECT severity_id, count(severity_id) count
                  FROM "issues_issue"
            INNER JOIN "projects_project" ON ("issues_issue"."project_id" = "projects_project"."id")
                 WHERE {where}
              GROUP BY severity_id
        )

                 SELECT "projects_severity"."id",
                        "projects_severity"."name",
                        "projects_severity"."color",
                        "projects_severity"."order",
                        COALESCE(counters.count, 0)
                   FROM "projects_severity"
        LEFT OUTER JOIN counters ON counters.severity_id = projects_severity.id
                  WHERE "projects_severity"."project_id" = %s
               ORDER BY "projects_severity"."order";
    """.format(where=where)

    with closing(connection.cursor()) as cursor:
        cursor.execute(extra_sql, where_params + [project.id])
        rows = cursor.fetchall()

    result = []
    for id, name, color, order, count in rows:
        result.append({
            "id": id,
            "name": _(name),
            "color": color,
            "order": order,
            "count": count,
        })
    return sorted(result, key=itemgetter("order"))


def _get_issues_assigned_to(project, queryset):
    compiler = connection.ops.compiler(queryset.query.compiler)(queryset.query, connection, None)
    queryset_where_tuple = queryset.query.where.as_sql(compiler, connection)
    where = queryset_where_tuple[0]
    where_params = queryset_where_tuple[1]

    extra_sql = """
        WITH counters AS (
                SELECT assigned_to_id,  count(assigned_to_id) count
                  FROM "issues_issue"
            INNER JOIN "projects_project" ON ("issues_issue"."project_id" = "projects_project"."id")
                 WHERE {where} AND "issues_issue"."assigned_to_id" IS NOT NULL
              GROUP BY assigned_to_id
        )

                SELECT  "projects_membership"."user_id" user_id,
                        "users_user"."full_name",
                        "users_user"."username",
                        COALESCE("counters".count, 0) count
                   FROM projects_membership
        LEFT OUTER JOIN counters ON ("projects_membership"."user_id" = "counters"."assigned_to_id")
             INNER JOIN "users_user" ON ("projects_membership"."user_id" = "users_user"."id")
                  WHERE "projects_membership"."project_id" = %s AND "projects_membership"."user_id" IS NOT NULL

        -- unassigned issues
        UNION

                 SELECT NULL user_id, NULL, NULL, count(coalesce(assigned_to_id, -1)) count
                   FROM "issues_issue"
             INNER JOIN "projects_project" ON ("issues_issue"."project_id" = "projects_project"."id")
                  WHERE {where} AND "issues_issue"."assigned_to_id" IS NULL
               GROUP BY assigned_to_id
    """.format(where=where)

    with closing(connection.cursor()) as cursor:
        cursor.execute(extra_sql, where_params + [project.id] + where_params)
        rows = cursor.fetchall()

    result = []
    none_valued_added = False
    for id, full_name, username, count in rows:
        result.append({
            "id": id,
            "full_name": full_name or username or "",
            "count": count,
        })

        if id is None:
            none_valued_added = True

    # If there was no issue with null assigned_to we manually add it
    if not none_valued_added:
        result.append({
            "id": None,
            "full_name": "",
            "count": 0,
        })

    return sorted(result, key=itemgetter("full_name"))


def _get_issues_owners(project, queryset):
    compiler = connection.ops.compiler(queryset.query.compiler)(queryset.query, connection, None)
    queryset_where_tuple = queryset.query.where.as_sql(compiler, connection)
    where = queryset_where_tuple[0]
    where_params = queryset_where_tuple[1]

    extra_sql = """
        WITH counters AS (
                SELECT "issues_issue"."owner_id" owner_id,  count("issues_issue"."owner_id") count
                  FROM "issues_issue"
            INNER JOIN "projects_project" ON ("issues_issue"."project_id" = "projects_project"."id")
                 WHERE {where}
              GROUP BY "issues_issue"."owner_id"
        )

                 SELECT "projects_membership"."user_id" id,
                        "users_user"."full_name",
                        "users_user"."username",
                        COALESCE("counters".count, 0) count
                   FROM projects_membership
        LEFT OUTER JOIN counters ON ("projects_membership"."user_id" = "counters"."owner_id")
             INNER JOIN "users_user" ON ("projects_membership"."user_id" = "users_user"."id")
                  WHERE "projects_membership"."project_id" = %s AND "projects_membership"."user_id" IS NOT NULL

        -- System users
        UNION

                 SELECT "users_user"."id" user_id,
                        "users_user"."full_name" full_name,
                        "users_user"."username",
                        COALESCE("counters".count, 0) count
                   FROM users_user
        LEFT OUTER JOIN counters ON ("users_user"."id" = "counters"."owner_id")
                  WHERE ("users_user"."is_system" IS TRUE)
    """.format(where=where)

    with closing(connection.cursor()) as cursor:
        cursor.execute(extra_sql, where_params + [project.id])
        rows = cursor.fetchall()

    result = []
    for id, full_name, username, count in rows:
        if count > 0:
            result.append({
                "id": id,
                "full_name": full_name or username or "",
                "count": count,
            })
    return sorted(result, key=itemgetter("full_name"))


def _get_issues_roles(project, queryset):
    compiler = connection.ops.compiler(queryset.query.compiler)(queryset.query, connection, None)
    queryset_where_tuple = queryset.query.where.as_sql(compiler, connection)
    where = queryset_where_tuple[0]
    where_params = queryset_where_tuple[1]

    extra_sql = """
     WITH "issue_counters" AS (
         SELECT DISTINCT "issues_issue"."status_id" "status_id",
                         "issues_issue"."id" "issue_id",
                         "projects_membership"."role_id" "role_id"
                    FROM "issues_issue"
              INNER JOIN "projects_project"
                      ON ("issues_issue"."project_id" = "projects_project"."id")
         LEFT OUTER JOIN "projects_membership"
                      ON "projects_membership"."user_id" = "issues_issue"."assigned_to_id"
                   WHERE {where}
            ),
             "counters" AS (
                  SELECT "role_id" as "role_id",
                         COUNT("role_id") "count"
                    FROM "issue_counters"
                GROUP BY "role_id"
            )

                 SELECT "users_role"."id",
                        "users_role"."name",
                        "users_role"."order",
                        COALESCE("counters"."count", 0)
                   FROM "users_role"
        LEFT OUTER JOIN "counters"
                     ON "counters"."role_id" = "users_role"."id"
                  WHERE "users_role"."project_id" = %s
               ORDER BY "users_role"."order";
    """.format(where=where)

    with closing(connection.cursor()) as cursor:
        cursor.execute(extra_sql, where_params + [project.id])
        rows = cursor.fetchall()

    result = []
    for id, name, order, count in rows:
        result.append({
            "id": id,
            "name": _(name),
            "color": None,
            "order": order,
            "count": count,
        })
    return sorted(result, key=itemgetter("order"))

def _get_issues_tags(project, queryset):
    compiler = connection.ops.compiler(queryset.query.compiler)(queryset.query, connection, None)
    queryset_where_tuple = queryset.query.where.as_sql(compiler, connection)
    where = queryset_where_tuple[0]
    where_params = queryset_where_tuple[1]

    extra_sql = """
        WITH "issues_tags" AS (
                    SELECT "tag",
                           COUNT("tag") "counter"
                      FROM (
                                SELECT UNNEST("issues_issue"."tags") "tag"
                                  FROM "issues_issue"
                            INNER JOIN "projects_project"
                                    ON ("issues_issue"."project_id" = "projects_project"."id")
                                 WHERE {where}
                           ) "tags"
                  GROUP BY "tag"),
             "project_tags" AS (
                    SELECT reduce_dim("tags_colors") "tag_color"
                      FROM "projects_project"
                     WHERE "id"=%s)

      SELECT "tag_color"[1] "tag",
             "tag_color"[2] "color",
             COALESCE("issues_tags"."counter", 0) "counter"
        FROM project_tags
   LEFT JOIN "issues_tags" ON "project_tags"."tag_color"[1] = "issues_tags"."tag"
    ORDER BY "tag"
    """.format(where=where)

    with closing(connection.cursor()) as cursor:
        cursor.execute(extra_sql, where_params + [project.id])
        rows = cursor.fetchall()

    result = []
    for name, color, count in rows:
        result.append({
            "name": name,
            "color": color,
            "count": count,
        })
    return sorted(result, key=itemgetter("name"))


def get_issues_filters_data(project, querysets):
    """
    Given a project and an issues queryset, return a simple data structure
    of all possible filters for the issues in the queryset.
    """
    data = OrderedDict([
        ("types", _get_issues_types(project, querysets["types"])),
        ("statuses", _get_issues_statuses(project, querysets["statuses"])),
        ("priorities", _get_issues_priorities(project, querysets["priorities"])),
        ("severities", _get_issues_severities(project, querysets["severities"])),
        ("assigned_to", _get_issues_assigned_to(project, querysets["assigned_to"])),
        ("owners", _get_issues_owners(project, querysets["owners"])),
        ("tags", _get_issues_tags(project, querysets["tags"])),
        ("roles", _get_issues_roles(project, querysets["roles"])),
    ])

    return data
