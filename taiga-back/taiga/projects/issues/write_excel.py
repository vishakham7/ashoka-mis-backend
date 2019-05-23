from openpyxl import *
import openpyxl
import io
import os
from django.utils.translation import ugettext as _
from django.conf import settings
from django.shortcuts import render
from taiga.base.utils import db, text
from taiga.projects.issues.apps import (
    connect_issues_signals,
    disconnect_issues_signals)
from taiga.projects.votes.utils import attach_total_voters_to_queryset
from taiga.projects.notifications.utils import attach_watchers_to_queryset
from datetime import date, datetime, timedelta
from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font
from openpyxl.styles.borders import Border, Side, BORDER_THIN
from openpyxl.utils import get_column_letter
import pandas as pd
from openpyxl.writer.excel import save_virtual_workbook
from django.http import HttpResponse
from xhtml2pdf import pisa 
import pdfkit
import PyPDF2
import urllib3
from openpyxl.drawing.image import Image
from openpyxl.drawing.spreadsheet_drawing import AbsoluteAnchor, OneCellAnchor, AnchorMarker
from openpyxl.utils.units import pixels_to_EMU, cm_to_EMU
from openpyxl.drawing.xdr import XDRPoint2D, XDRPositiveSize2D
from taiga.users.models import User

def style(ws,fieldnames, issue,file_name=None):

    font = Font(name='Calibri',
                size=11,
                bold=True,
                italic=False,
                vertAlign=None,
                underline='none',
                strike=False,
                color='FF000000')
    color = Font(name='Calibri',
                size=11,
                bold=False,
                italic=False,
                vertAlign=None,
                underline='none',
                strike=False,
                color='696969')
    border = Border(
            left=Side(border_style=BORDER_THIN, color='FF000000'),
            right=Side(border_style=BORDER_THIN, color='FF000000'),
            top=Side(border_style=BORDER_THIN, color='FF000000'),
            bottom=Side(border_style=BORDER_THIN, color='FF000000')
        )
    fill=PatternFill(start_color = '00C0C0C0',
            end_color = '00C0C0C0',
            fill_type = 'solid')
    dd = Font(underline='single', color='000000FF')
    row_count = ws.max_row
    column_count = ws.max_column
    print("===========row===========")
    print(row_count)
    for cell in ws['2:2']:
        cell.font = font

    for cell2 in ws['3:3']:
        cell2.fill = fill
        cell2.font = font

    for cell3 in ws['4:4']:
        cell3.fill = fill
        cell3.font = font




    
    for i in range(3,row_count+1):
        ws.row_dimensions[i].height = 50

    
    for row in ws:
        for cell1 in row:
            cell1.border = border
            cell1.alignment = Alignment(wrap_text=True, horizontal='center', vertical='center')
    
    column_widths = []
    for row in fieldnames:
        for i in range(len(row)):
            if len(column_widths) > i:
                if len(row) > column_widths[i]:
                    column_widths[i] = len(row)
            else:
                column_widths += [len(row)]
        for i, column_width in enumerate(column_widths):
            ws.column_dimensions[get_column_letter(i+1)].width = column_width
    


    #////////////////////////// images
    if file_name:
        file_row = []
        for row in range(5,row_count+1):
            file_row.append(row)
        print(file_row)
        l=[]
        for i in range(len(file_row)):
            if len(file_row)==(row_count-4):
                l.append(file_row[i])
        print(l)
        file_name = []
        split = []
        aaa=[]
        val = []
        n=""
        hh=""
        alignment = ['left', 'right','center']
        for new_row in l:
            file = ws.cell(row=new_row, column=7).value
            if file:
                split = file.split('\n')
                if split:
                    aaa.append(split)
                for aa in aaa:
                    for j in range(len(aa)-1):
                        new = aa[j].split('.')
                        doc_name = new[-2].split('/')
                        file_name = doc_name[-1]+'.'+new[-1]
                            

                        name = ws.cell(row=new_row, column=7).value
                        n += name
                        print(aa[j])
                        if new[-1]=="xlsx" or new[-1]=="docx" or new[-1]=="doc" or new[-1]=="pdf":
                            ws.cell(row=new_row, column=7).hyperlink = aa[j]
                        if new[-1]=="svg" or new[-1]=="jpeg" or new[-1]=="jpg" or new[-1]=="png":
                            http = urllib3.PoolManager()
                            # r = http.request('GET', aa[j-(len(aa)-1)])
                            r = http.request('GET', aa[j])
                            image_file = io.BytesIO(r.data)
                        
                            img = Image(image_file)
                            img.height=100
                            img.width =100
                            ws.add_image(img,'G'+str(new_row))
                            ws.cell(row=new_row, column=7).value = "<img scr='"+  aa[j] + "'></img>"
                        if len(n)>180:                
                            ws.row_dimensions[new_row].height = 120
                            if new[-1]=="svg" or new[-1]=="jpeg" or new[-1]=="jpg" or new[-1]=="png":
                                
                                http = urllib3.PoolManager()
                                r = http.request('GET', aa[j-(len(aa)-1)])
                                # r = http.request('GET', aa[j])
                                print(aa[j])
                                image_file = io.BytesIO(r.data)
                                print("0000---------------0000")
                                print(image_file)
                                img = Image(image_file)
                                print("000000000000000000000000")
                                print(img)
                                img.height=100
                                img.width =100
                                ws.add_image(img,'G'+str(new_row))
                                # ws.cell(row=new_row, column=7).value = "<img scr='"+  aa[j] + "'></img>"
                                ws.cell(row=new_row, column=7).value = "<img scr='"+  aa[j-(len(aa)-1)] + "'></img>"
                                

                                # ============================================================
                                # r1 = http.request('GET', aa[0])
                                # # r = http.request('GET', aa[j])
                                # image_file1 = io.BytesIO(r1.data)
                            
                                # img1 = Image(image_file1)
                                # img1.height=100
                                # img1.width =100
                                # ws.add_image(img1,'G'+str(new_row))
                                
                                # ws.cell(row=new_row, column=7).value = "<img scr='"+  aa[j-(len(aa)-1)] + "'></img>"
                                # ws.cell(row=new_row, column=7).value = '<img src="' + aa[0] + '"/>'
                                ws.cell(row=new_row, column=7).alignment = Alignment(wrap_text=True, horizontal='right', vertical='center')
                                ws.cell(row=new_row, column=7).hyperlink = aa[0]
                                ws.cell(row=new_row, column=7).value ="Image"
                                ws.cell(row=new_row, column=7).alignment = Alignment(wrap_text=True, horizontal='right', vertical='center')
                                ws.cell(row=new_row, column=7).font = dd
                                ws.row_dimensions[new_row].height = 150
                            # else:
                            #     ws.cell(row=new_row, column=7).value = ""


                            # ws.cell(row=new_row, column=7).hyperlink = nnn
                        n =""
        # /////////////////////////////////////////
                    # val.append(name)
                    # for i in range(len(val)-1):
                        # print(val[i])

                    # for i in val:
                    #     print(type(i))
                    #     ws.cell(row=new_row, column=7).hyperlink = i
                        # ws.cell(row=new_row, column=7).hyperlink = '\n'.join(aa)
                    # ws.cell(row=new_row, column=7).value = 'attachments'
    # for new_row in l:

        # ws.cell(row=new_row, column=7).hyperlink = aaa

        # for new_split in range(len(split)):
            #     print("=============================")
            #     print(split)
            #     file.append((split))
            
                # ws.cell(row=new_row, column=7).hyperlink = split
            # print(split)

    # for i in file_row:
    #     print(type(i))
        # file = ws.cell(row=i, column=7).value
        # if file:
        #     print("=========================")
        #     print(file)
            # ws.cell(row=i, column=col).value
    # for row in range(3,row_count+1):
        # for col in range():
            # print(col, row)
    #         print(get_column_letter(col))
            # col_name = get_column_letter(col)+str(row)
            # new_col = get_column_letter(col)+str(row+1)
    # for row in ws.iter_rows():
    #     for cell in row:
    #         if cell.value == "Photograph During Inspection":
    #             for i in range(5,row_count+1):
    #                 for col in range(7,8):
    #                     file = ws.cell(row=i, column=col).value
    #                     if file:
    #                         print("==============================")
    #                         print(str(i)+ "+" + str(col) + "=" + file)

                        # if file:
                        #     split = file.split('\n')
                        #     new_file = ""
                        #     for new in range(len(split)):
                        #         print("==========files")
                        #         new_file = split[new]
                        #         print(new_file)
                        #         print("------------new=------------") 
                        #         ws.cell(row=i, column=col).hyperlink = new_file
                                   
                            # 
                            # print(split)
                            # for f in range(len(split)):
                            #     print("==============================")
                            #     print(file[f])
                            #     ws.cell(row=i, column=col).hyperlink = file[f]


                    # for cell_new in i:
                    #     link = []
                    #     value = cell_new.value
                    #     if value:
                    #         l  = value.split("\n")
                    #         for file in range(len(l)):
                    #             if file:
                    #                 # print(l[file])
                    #                 # print("============file123456============")
                    #                 # print(cell_new)
                    #                 # cell_new.hyperlink = l[file]
                    #                 print("========row=========")
                    #                 print(i)
                    #                 print("========cell=========")
                    #                 print(cell_new)
                    
                            
                                    


def write_excel(project, queryset, type, status,start_date, end_date,asset, performance, photo,doc_type,name,request):
    wb = Workbook()
    ws1 = wb.active
    ws2 = wb.active
    ws3 = wb.active
    ws4 = wb.active
    ws5 = wb.active
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
    if type == 'Issue' and photo=="with photo" and status==None:
        ws1.title = "Inspection Report"
        ws1['A1'] = "R01: For External Parties:  IE and NHAI-PD or RO"
        ws1['A2'] = "R01.1 : Inspection Report with Photogragh"
        fieldnames = ["Ref.No.", "Project Name", "Chainage","" , "Direction", "Description of Issue",
                              "Photograph During Inspection", "Asset Type", "Performance Parameter (Type of Issue)",
                              "Issue Raised On (Date)", "Issue Raised By (Name of Concessionaire)",
                              "Issue Raised To (Assignee Name Max Upto 3 Persons)"]
        ws1.append(fieldnames)
        ws1.merge_cells('A3:A4')
        ws1.merge_cells('B3:B4')
        ws1.merge_cells('C3:D3')
        # ws1.merge_cells('C4:D4')
        n1 = ws1.cell(row=4,column=3)
        n2 = ws1.cell(row=4,column=4)
        n1.value = "From (In Km)"
        n2.value = "To (In Km)"
        # ws1.merge_cells('D3:D4')
        # n3 = ws1.cell(row=3,column=5)
        # n3.value="Direction"
        ws1.merge_cells('E3:E4')
        ws1.merge_cells('F3:F4')
        ws1.merge_cells('G3:G4')
        ws1.merge_cells('H3:H4')
        ws1.merge_cells('I3:I4')
        ws1.merge_cells('J3:J4')
        ws1.merge_cells('K3:K4')
        ws1.merge_cells('L3:L4')
        

    if type == 'Issue' and photo=="without photo" and status==None:

        ws5.title = "Inspection Reportssssss"
        ws5['A1'] = "R01: For External Parties:  IE and NHAI-PD or RO"
        ws5['A2'] = "R01.1 : Inspection Report with Photogragh"
        fieldnames = ["Ref.No.", "Project Name", "Chainage","" , "Direction", "Description of Issue",
                              "Asset Type", "Performance Parameter (Type of Issue)",
                              "Issue Raised On (Date)", "Issue Raised By (Name of Concessionaire)",
                              "Issue Raised To (Assignee Name Max Upto 3 Persons)"]
        ws5.append(fieldnames)
    
        ws5.merge_cells('A3:A4')
        ws5.merge_cells('B3:B4')
        ws5.merge_cells('C3:D3')
        # ws1.merge_cells('C4:D4')
        n1 = ws5.cell(row=4,column=3)
        n2 = ws5.cell(row=4,column=4)
        n1.value = "From (In Km)"
        n2.value = "To (In Km)"
        # ws1.merge_cells('D3:D4')
        # n3 = ws1.cell(row=3,column=5)
        # n3.value="Direction"
        ws5.merge_cells('E3:E4')
        ws5.merge_cells('F3:F4')
        ws5.merge_cells('G3:G4')
        ws5.merge_cells('H3:H4')
        ws5.merge_cells('I3:I4')
        ws5.merge_cells('J3:J4')
        ws5.merge_cells('K3:K4')
        # ws1.merge_cells('L3:L4')
    if type == 'Issue' and name=="comp" and photo=="with photo" and status:

        wb = Workbook()
        ws2 = wb.active
    
        ws2.title = "Manitenance Report"
        ws2['A1'] = "For External Parties:  IE and NHAI-PD or RO"
        ws2['A2'] = "Maintenance Report"
        
        fieldnames = ["Ref.No.", "Project Name", "Chainage","", "Direction", "Description of Issue",
                          "Photograph During Inspection", "Asset Type", "Performance Parameter\n (Type of Issue)",
                          "Issue Raised On (Date)", "Issue Raised By\n (Name of Concessionaire)",
                          "Issue Raised To\n (Assignee Name Max Upto 3 Persons)" , "Max Time limit for Rectification/Repair",
                          "", "Action Taken",
                          "", "", "Issue Closed By",
                          "Photograph Post Compliance", "Remark", "Current Status","Description Of Compliance" ]
        ws2.append(fieldnames)
        ws2.merge_cells('A3:A4')
        ws2.merge_cells('B3:B4')
        ws2.merge_cells('C3:D3')
        # ws1.merge_cells('C4:D4')
        n1 = ws2.cell(row=4,column=3)
        n2 = ws2.cell(row=4,column=4)
        n1.value = "From (In Km)"
        n2.value = "To (In Km)"
        # ws1.merge_cells('D3:D4')
        # n3 = ws1.cell(row=3,column=5)
        # n3.value="Direction"
        ws2.merge_cells('E3:E4')
        ws2.merge_cells('F3:F4')
        ws2.merge_cells('G3:G4')
        ws2.merge_cells('H3:H4')
        ws2.merge_cells('I3:I4')
        ws2.merge_cells('J3:J4')
        ws2.merge_cells('K3:K4')
        ws2.merge_cells('L3:L4')
        ws2.merge_cells('M3:N3')
        n1 = ws2.cell(row=4,column=13)
        n2 = ws2.cell(row=4,column=14)
        n1.value = "Timeline\n (As per  Schedule F)"
        n2.value = "Target Date\n(As per  Schedule F)"
        # ws2.merge_cells('M3:M4')
        # ws2.merge_cells('N3:N4')
        ws2.merge_cells('O3:Q3')
        n1 = ws2.cell(row=4,column=15)
        n2 = ws2.cell(row=4,column=16)
        n3 = ws2.cell(row=4,column=17)
        n1.value = "Status\n(Open/Closed/Under Rectification)"
        n2.value = "Issue Closed On Date\n(If Closed)"
        n3.value = "Complianced\n (Yes/No)"


        ws2.merge_cells('R3:R4')
        ws2.merge_cells('S3:S4')
        ws2.merge_cells('T3:T4')
        ws2.merge_cells('U3:U4')
        ws2.merge_cells('V3:V4')

    if type=='Issue' and name=="comp" and photo=="without photo" and status:
    
        ws4.title = "Manitenance Report"
        ws4['A1'] = "For External Parties:  IE and NHAI-PD or RO"
        ws4['A2'] = "Maintenance Report"
        fieldnames = ["Ref.No.", "Project Name", "Chainage","", "Direction", "Description of Issue",
                          "Asset Type", "Performance Parameter\n (Type of Issue)",
                          "Issue Raised On (Date)", "Issue Raised By\n (Name of Concessionaire)",
                          "Issue Raised To\n (Assignee Name Max Upto 3 Persons)" , "Max Time limit for Rectification/Repair",
                          "", "Action Taken",
                          "", "", "Issue Closed By",
                          "Photograph Post Compliance", "Remark", "Current Status","Description Of Compliance" ]
        ws4.append(fieldnames)
        ws4.merge_cells('A3:A4')
        ws4.merge_cells('B3:B4')
        ws4.merge_cells('C3:D3')
        # ws1.merge_cells('C4:D4')
        n1 = ws4.cell(row=4,column=3)
        n2 = ws4.cell(row=4,column=4)
        n1.value = "From (In Km)"
        n2.value = "To (In Km)"
        # ws1.merge_cells('D3:D4')
        # n3 = ws1.cell(row=3,column=5)
        # n3.value="Direction"
        ws4.merge_cells('E3:E4')
        ws4.merge_cells('F3:F4')
        ws4.merge_cells('G3:G4')
        ws4.merge_cells('H3:H4')
        ws4.merge_cells('I3:I4')
        ws4.merge_cells('J3:J4')
        ws4.merge_cells('K3:K4')
        ws4.merge_cells('L3:M3')
        n1 = ws4.cell(row=4,column=12)
        n2 = ws4.cell(row=4,column=13)
        n1.value = "Timeline\n (As per  Schedule F)"
        n2.value = "Target Date\n(As per  Schedule F)"
        
        ws4.merge_cells('N3:P3')
        
        n1 = ws4.cell(row=4,column=14)
        n2 = ws4.cell(row=4,column=15)
        n3 = ws4.cell(row=4,column=16)
        n1.value = "Status\n(Open/Closed/Under Rectification)"
        n2.value = "Issue Closed On Date\n(If Closed)"
        n3.value = "Complianced\n (Yes/No)"

        ws4.merge_cells('Q3:Q4')
        ws4.merge_cells('R3:R4')
        ws4.merge_cells('S3:S4')
        ws4.merge_cells('T3:T4')
        ws4.merge_cells('U3:U4')


    if type == 'Investigation':
        
        ws3.title = "Test Report"
        ws3['A1'] = ""
        ws3['A2'] = "Test Report"
        fieldnames = ["Ref.No.", "Project Name", "Chainage","", "Direction", "Description of Issue",
                          "Photograph During Inspection", "Asset Type", "Performance Parameter(Type of Issue)",
                          "Issue Raised On", "Name of Test", "Testing Method", "Standard References for testing",
                          "Test Carried Out Date", "Testing Carried Out By(Name)", "Remark", "Outcome Report"]
        
        ws3.append(fieldnames)
        ws3.merge_cells('A3:A4')
        ws3.merge_cells('B3:B4')
        ws3.merge_cells('C3:D3')
        # ws1.merge_cells('C4:D4')
        n1 = ws3.cell(row=4,column=3)
        n2 = ws3.cell(row=4,column=4)
        n1.value = "From (In Km)"
        n2.value = "To (In Km)"
        # ws1.merge_cells('D3:D4')
        # n3 = ws1.cell(row=3,column=5)
        # n3.value="Direction"
        ws3.merge_cells('E3:E4')
        ws3.merge_cells('F3:F4')
        ws3.merge_cells('G3:G4')
        ws3.merge_cells('H3:H4')
        ws3.merge_cells('I3:I4')
        ws3.merge_cells('J3:J4')
        ws3.merge_cells('K3:K4')
        ws3.merge_cells('L3:L4')
        ws3.merge_cells('M3:M4')
        ws3.merge_cells('N3:N4')
        ws3.merge_cells('O3:O4')
        ws3.merge_cells('P3:P4')
        ws3.merge_cells('Q3:Q4')



    if type == 'Accident':
       
        ws4.title = "Summary of Accident"
        ws4['A1'] = "Report Name : Summary of Accident Report"
        ws4['A2'] = "Date:\n From: "+start_date+ '\t To: ' +end_date
        

        fieldnames = ["Ref.No.", "Description","Up to previous month","","During this month","",
                        "Up to this month", ""]

        ws4.append(fieldnames)
        ws4.merge_cells('A3:A4')
        ws4.merge_cells('B3:B4')
        ws4.merge_cells('C3:D3')
        n1 = ws4.cell(row=4,column=3)
        n2 = ws4.cell(row=4,column=4)
        n1.value = "No of Accidents"
        n2.value = "No of Peoples affected"
        ws4.merge_cells('E3:F3')
        n1 = ws4.cell(row=4,column=5)
        n2 = ws4.cell(row=4,column=6)
        n1.value = "No of Accidents"
        n2.value = "No of Peoples affected"
        ws4.merge_cells('G3:H3')
        n1 = ws4.cell(row=4,column=7)
        n2 = ws4.cell(row=4,column=8)
        n1.value = "No of Accidents"
        n2.value = "No of Peoples affected"
    
    wwww = []  
        
    for issue in queryset:
        if issue.type.name=='Issue'  and photo=="with photo" and status==None:
            qqq = issue.watchers
            watchers = []
            new_watcher_list =  ""
            watcher_username =""
            if issue.assigned_to:
                watcher_username = '1. '+issue.assigned_to.full_name 
            for i in qqq:
                sql = User.objects.get(id=int(i))
                watchers.append(sql.full_name)
            for j in range(len(watchers)):
                watcher_username = str(j+2)+'. '+watchers[j] +','+ watcher_username
            
            split = watcher_username.split(',')

            for i in range(len(split)):
                new_watcher_list = split[i] + new_watcher_list
            if issue.type.name == type:
                if issue.attachments:
                    file_name ="" 
                    files = []

                    file = issue.attachments.filter(project__id=issue.project.id).values_list('attached_file')
                    for i in file:
                        files.extend(i)
                    #     for j in len(file):
                    #         files.append(file[j])
                    for j in files:
                        file_name += os.path.join(settings.MEDIA_URL,str(j)) +"\n"
                        
                
               
                        # file_name.append(os.path.join(settings.MEDIA_URL,str(j)))
                else:
                    file_name=""

                if file_name:
                    wwww.append(file_name.split('\n'))
                Raised_date = datetime.strftime(issue.created_date.date(),"%d-%m-%Y")
                issue_data = [[
                    issue.ref,
                    issue.project.name,
                    issue.chainage_from,
                    issue.chainage_to,
                    issue.chainage_side,
                    issue.description,
                    file_name if issue.attachments else None,
                    issue.issue_category,
                    issue.issue_subcategory,
                    Raised_date,
                    issue.owner.full_name if issue.owner else None,
                    new_watcher_list,
                ]]
                for data in issue_data:
                    ws1.append(data)
                wb.save("table.xlsx")
                wb.close()

                wb = load_workbook('table.xlsx')
                ws1 = wb['Inspection Report']



                style(ws1,fieldnames, file_name, issue)


        if issue.type.name == 'Issue' and photo=="without photo" and status==None:
            qqq = issue.watchers
            watchers = []
            new_watcher_list =  ""
            watcher_username =""
            if issue.assigned_to:
                watcher_username = '1. '+issue.assigned_to.full_name 
            for i in qqq:
                sql = User.objects.get(id=int(i))
                watchers.append(sql.full_name)
            for j in range(len(watchers)):
                watcher_username = str(j+2)+'. '+watchers[j] +','+ watcher_username
            
            split = watcher_username.split(',')

            for i in range(len(split)):
                new_watcher_list = split[i] + new_watcher_list
                
            Raised_date = datetime.strftime(issue.created_date.date(),"%d-%m-%Y")
            issue_data = [[
                issue.ref,
                issue.project.name,
                issue.chainage_from,
                issue.chainage_to,
                issue.chainage_side,
                issue.description,
                issue.issue_category,
                issue.issue_subcategory,
                Raised_date,
                issue.owner.full_name if issue.owner else None,
                new_watcher_list,
            ]]

            for data in issue_data:
                ws5.append(data)
            wb.save("table.xlsx")
            wb.close()

            wb = load_workbook('table.xlsx')
            ws5 = wb['Inspection Reportssssss']
            style(ws5,fieldnames, issue)

    

        if issue.type.name=='Issue' and name=="comp" and photo=="with photo" and status:
            for issue in queryset:
                qqqq = issue.watchers
                watchers = []
                new_watcher_list =  ""
                watcher_username =""
                if issue.assigned_to:
                    watcher_username = '1. '+issue.assigned_to.full_name
                for i in qqqq:
                    sql = User.objects.get(id=int(i))
                    watchers.append(sql.full_name)
                for j in range(len(watchers)):
                    watcher_username = str(j+2)+'. '+watchers[j] +','+ watcher_username
                
                split = watcher_username.split(',')

                for i in range(len(split)):
                    new_watcher_list = split[i] +'\n'+ new_watcher_list 
                    a = issue.created_date.date()
                    b = datetime.strptime(issue.target_date,"%d/%m/%Y").date()
                    timeline = b-a
                    target_date = datetime.strftime(b,"%d-%m-%Y")
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
                    status_name = []
                    status_names =  project.issues.filter(status__id__in=status)
                    new_status_name =[]
                    for name in status_names:
                        
                        if str(name.status) == 'Closed':
                            new_status_name.append('Open')
                            # new_status_name += 'Open'
                             
                        elif str(name.status) == 'Maintenance Closed':
                            # new_status_name += 'Closed'
                            new_status_name.append('Closed')
                            
                        elif str(name.status) == 'Maintenance Pending':
                            # new_status_name += 'Pending'
                            new_status_name.append('Pending')
                    if new_status_name:
                        new =""
                        for i in new_status_name:
                            new = i
                    issue_data = [[
                            issue.ref,
                            issue.project.name,
                            issue.chainage_from,
                            issue.chainage_to,
                            issue.chainage_side,
                            issue.description,
                            file_name,
                            issue.issue_category,
                            issue.issue_subcategory,
                            issue.created_date.date(),
                            issue.owner.full_name if issue.owner else None,
                            new_watcher_list,
                            timeline,
                            target_date,
                            new if issue.status else None,
                            issue.finished_date if status_name=='Closed' else None,
                            'Yes' if issue.compliance_is_update==True else 'No',
                            issue.assigned_to.full_name if issue.assigned_to else None,
                            issue.compliance_description,
                            issue.attachments.name,
                            "",
                            new if issue.status else None,
                        ]]
                    for data in issue_data:
                        ws2.append(data)
                wb.save("table.xlsx")
                wb.close()

                wb = load_workbook('table.xlsx')
                ws2 = wb['Manitenance Report']
                style(ws2,fieldnames, file_name, issue)


        if issue.type.name=='Issue' and name=="comp" and photo=="without photo" and status:
            for issue in queryset:
                qqqq = issue.watchers
                watchers = []
                new_watcher_list =  ""
                watcher_username =""
                if issue.assigned_to:
                    watcher_username = '1. '+issue.assigned_to.full_name
                for i in qqqq:
                    sql = User.objects.get(id=int(i))
                    watchers.append(sql.full_name)
                for j in range(len(watchers)):
                    watcher_username = str(j+2)+'. '+watchers[j] +','+ watcher_username
                
                split = watcher_username.split(',')

                for i in range(len(split)):
                    new_watcher_list = split[i] +'\n'+ new_watcher_list 
                    a = issue.created_date.date()
                    b = datetime.strptime(issue.target_date,"%d/%m/%Y").date()
                    timeline = b-a
                    target_date = datetime.strftime(b,"%d-%m-%Y")
                    
                    status_name = []
                    status_names =  project.issues.filter(status__id__in=status)
                    new_status_name =[]
                    for name in status_names:
                        
                        if str(name.status) == 'Closed':
                            new_status_name.append('Open')
                            # new_status_name += 'Open'
                             
                        elif str(name.status) == 'Maintenance Closed':
                            # new_status_name += 'Closed'
                            new_status_name.append('Closed')
                            
                        elif str(name.status) == 'Maintenance Pending':
                            # new_status_name += 'Pending'
                            new_status_name.append('Pending')
                    if new_status_name:
                        new =""
                        for i in new_status_name:
                            new = i
                    issue_data = [[
                            issue.ref,
                            issue.project.name,
                            issue.chainage_from,
                            issue.chainage_to,
                            issue.chainage_side,
                            issue.description,
                            issue.issue_category,
                            issue.issue_subcategory,
                            issue.created_date.date(),
                            issue.owner.full_name if issue.owner else None,
                            new_watcher_list,
                            timeline,
                            target_date,
                            new if issue.status else None,
                            issue.finished_date if status_name=='Closed' else None,
                            'Yes' if issue.compliance_is_update==True else 'No',
                            issue.assigned_to.full_name if issue.assigned_to else None,
                            issue.compliance_description,
                            issue.attachments.name,
                            "",
                            new if issue.status else None,
                        ]]
                    for data in issue_data:
                        ws4.append(data)
                wb.save("table.xlsx")
                wb.close()

                wb = load_workbook('table.xlsx')
                ws4 = wb['Manitenance Report']
                style(ws4,fieldnames, issue)
        

        if issue.type.name == 'Investigation':
            issue_data = [[
                issue.ref,
                issue.project.name,
                issue.investigation_chainage_from,
                issue.investigation_chainage_to,
                issue.investigation_chainage_side,
                issue.investigation_description,
                issue.asset_name,
                issue.test_name,
                "",
                "",
                "",
                "",
                issue.assigned_to.username if issue.assigned_to else None,
                "",
                "",
            ]]
            for data in issue_data:
                ws3.append(data)


            wb.save("table.xlsx")
            wb.close()

            wb = load_workbook('table.xlsx')
        
            ws3 = wb['Test Report']
            style(ws3,fieldnames, issue)


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
            issue_data = [[
                issue.ref,
                issue.accident_classification,
                project.issues.filter(type__name='Accident',created_date__date__range=[previous_month,Previous_last_date]).count(),
                sum(new_list_last),
                project.issues.filter(type__name='Accident',created_date__date__range=[first_date,current_date]).count(),
                sum(new_list_current),
                project.issues.filter(type__name='Accident').count(),
                sum(new_list_upto),

            ]]
            for data in issue_data:
                ws4.append(data)


            wb.save("table.xlsx")
            wb.close()

            wb = load_workbook('table.xlsx')
        
            ws4 = wb['Summary of Accident']
            style(ws4,fieldnames, issue)

    if doc_type=="pdf":
        new = pd.read_excel('table.xlsx',na_filter=False,header=None, names="",skiprows=[0,1])
    
        # for i in wwww:
        #  
        pd.set_option('display.max_colwidth', 500)   # FOR TABLE <th>

        html = new.to_html(escape=False).replace('&lt;','<').replace('&gt;', '>')
        pisa_context = pisa.CreatePDF(html)
        response = pisa_context.dest.getvalue()
        return html
        # return response

    return wb