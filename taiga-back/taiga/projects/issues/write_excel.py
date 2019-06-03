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
# from PIL import Image


def style(ws,fieldnames, issue,file_name=None,Compliance_file_name=None):
    font = Font(name='Calibri',
                size=11,
                bold=True,
                italic=False,
                vertAlign=None,
                underline='none',
                strike=False,
                color='FF000000')
    font2 = Font(name='Calibri',
                size=11,
                bold=True,
                italic=False,
                vertAlign=None,
                underline='none',
                strike=False,
                color='FFFFFF')
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

    ws.row_dimensions[2].height = 40
    ws.row_dimensions[1].height = 40
    
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


    #////////////////////////// working images
    if file_name:
        file_row = []
        for row in range(5,row_count+1):
            file_row.append(row)
        l=[]
        for i in range(len(file_row)):
            if len(file_row)==(row_count-4):
                l.append(file_row[i])
        
        file_name = []
        split = []
        aaa=[]
        val = []
        n=""
        hh=""
        for new_row in l:
            ws.row_dimensions[new_row].height = 140
            ws.column_dimensions[get_column_letter(6)].width = 50
            file = ws.cell(row=new_row, column=6).value
            if file:
                split = file.split('\n')
                if split:
                    aaa.append(split)
                for aa in aaa:

                    for j in range(len(aa)-1):
                        
                        new = aa[j].split('.')
                        doc_name = new[-2].split('/')
                        file_name = doc_name[-1]+'.'+new[-1]
        
                        name = ws.cell(row=new_row, column=6).value
                        n += name
                        
                        if new[-1]=="jpeg" or new[-1]=="png" or new[-1]=="jpg":
                            if len(aa) == 4:
                                http = urllib3.PoolManager()
                                r = http.request('GET',aa[0])
                                image_file = io.BytesIO(r.data)
                                
                                if image_file:

                                    img = Image(image_file)

                                    img.height=120
                                    img.width =120
                                   
                                    if img:
                                        c2e = cm_to_EMU
                                        p2e = pixels_to_EMU

                                        h, w = img.height, img.width
                                        # Calculated number of cells width or height from cm into EMUs
                                        # celh = [1,8,16]
                                        # celw = [0.09,0.01,0.01]
                                        # cellh = 0
                                        # cellw = 0
                                        cellh = lambda x: c2e((x * 1))
                                        cellw = lambda x: c2e((x *0.09))
                                        # cellw = cellzw
                                        # print(cellw, cellh)
                                        # Want to place image in row 5 (6 in excel), column 2 (C in excel)
                                        # Also offset by half a column.
                                        column = 5
                                        # colof = [28000]
                                        coloffset = cellh(0.5)
                                        # coloffset = 2880000
                                        row = new_row-1
                                        rowoffset = cellw(0.03)
                                        rowpp = [107,197]
                                

                                        print(coloffset, rowoffset)
                                        size = XDRPositiveSize2D(p2e(h), p2e(w))
                                        marker = AnchorMarker(col=column, colOff=coloffset, row=row, rowOff=rowoffset)
                                        img.anchor = OneCellAnchor(_from=marker, ext=size)
                                        
                                        ws.add_image(img)
                                        
                                        # ws.cell(row=new_row, column=6).value = "<img src='"+ aa[0] + "' height=100 width=70/><br>"

                                        # ws.cell(row=new_row, column=6).font = font2
                                http = urllib3.PoolManager()
                                r = http.request('GET',aa[1])
                                image_file = io.BytesIO(r.data)
                                
                                if image_file:

                                    img = Image(image_file)

                                    img.height=200
                                    img.width =200
                                   
                                    if img:
                                        c2e = cm_to_EMU
                                        p2e = pixels_to_EMU

                                        h, w = img.height, img.width
                                        # Calculated number of cells width or height from cm into EMUs
                                        # celh = [1,8,16]
                                        # celw = [0.09,0.01,0.01]
                                        # cellh = 0
                                        # cellw = 0
                                        cellh = lambda x: c2e((x * 8))
                                        cellw = lambda x: c2e((x *0.01))
                                        # cellw = cellzw
                                        # print(cellw, cellh)
                                        # Want to place image in row 5 (6 in excel), column 2 (C in excel)
                                        # Also offset by half a column.
                                        column = 5
                                        # colof = [28000]
                                        coloffset = cellh(0.5)
                                        # coloffset = 2880000
                                        row = new_row-1
                                        rowoffset = cellw(0.03)
                                        rowpp = [107,197]
                                

                                        print(coloffset, rowoffset)
                                        size = XDRPositiveSize2D(p2e(h), p2e(w))
                                        marker = AnchorMarker(col=column, colOff=coloffset, row=row, rowOff=rowoffset)
                                        img.anchor = OneCellAnchor(_from=marker, ext=size)
                                        
                                        ws.add_image(img)
                                        
                                        # ws.cell(row=new_row, column=6).value = "<img src='"+ aa[1] + "' height=100 width=70/><br>"

                                        # ws.cell(row=new_row, column=6).font = font2
                                http = urllib3.PoolManager()
                                r = http.request('GET',aa[0])
                                image_file = io.BytesIO(r.data)
                                
                                if image_file:

                                    img = Image(image_file)

                                    img.height=120
                                    img.width =120
                                   
                                    if img:
                                        c2e = cm_to_EMU
                                        p2e = pixels_to_EMU

                                        h, w = img.height, img.width
                                        # Calculated number of cells width or height from cm into EMUs
                                        # celh = [1,8,16]
                                        # celw = [0.09,0.01,0.01]
                                        # cellh = 0
                                        # cellw = 0
                                        cellh = lambda x: c2e((x * 16))
                                        cellw = lambda x: c2e((x *0.01))
                                        # cellw = cellzw
                                        # print(cellw, cellh)
                                        # Want to place image in row 5 (6 in excel), column 2 (C in excel)
                                        # Also offset by half a column.
                                        column = 5
                                        # colof = [28000]
                                        coloffset = cellh(0.5)
                                        # coloffset = 2880000
                                        row = new_row-1
                                        rowoffset = cellw(0.03)
                                        rowpp = [107,197]
                                

                                        print(coloffset, rowoffset)
                                        size = XDRPositiveSize2D(p2e(h), p2e(w))
                                        marker = AnchorMarker(col=column, colOff=coloffset, row=row, rowOff=rowoffset)
                                        img.anchor = OneCellAnchor(_from=marker, ext=size)
                                        
                                        ws.add_image(img)
                                        
                                        ws.cell(row=new_row, column=6).value = "<img src='"+ aa[2] + "' height=100 width=70/><br><img src='"+ aa[1] + "' height=100 width=70/><br><img src='"+ aa[0] + "' height=100 width=70/>"

                                        ws.cell(row=new_row, column=6).font = font2
                            if len(aa) == 3:
                                print("00000000000000000000000000")
                                print(len(aa))
                                http = urllib3.PoolManager()
                                r = http.request('GET',aa[0])
                                image_file = io.BytesIO(r.data)
                                
                                if image_file:

                                    img = Image(image_file)

                                    img.height=120
                                    img.width =120
                                   
                                    if img:
                                        c2e = cm_to_EMU
                                        p2e = pixels_to_EMU

                                        h, w = img.height, img.width
                                        # Calculated number of cells width or height from cm into EMUs
                                        # celh = [1,8,16]
                                        # celw = [0.09,0.01,0.01]
                                        # cellh = 0
                                        # cellw = 0
                                        cellh = lambda x: c2e((x * 1))
                                        cellw = lambda x: c2e((x *0.09))
                                        # cellw = cellzw
                                        # print(cellw, cellh)
                                        # Want to place image in row 5 (6 in excel), column 2 (C in excel)
                                        # Also offset by half a column.
                                        column = 5
                                        # colof = [28000]
                                        coloffset = cellh(0.5)
                                        # coloffset = 2880000
                                        row = new_row-1
                                        rowoffset = cellw(0.03)
                                        rowpp = [107,197]
                                

                                        print(coloffset, rowoffset)
                                        size = XDRPositiveSize2D(p2e(h), p2e(w))
                                        marker = AnchorMarker(col=column, colOff=coloffset, row=row, rowOff=rowoffset)
                                        img.anchor = OneCellAnchor(_from=marker, ext=size)
                                        
                                        ws.add_image(img)
                                        
                                        # ws.cell(row=new_row, column=6).value = "<img src='"+ aa[1] + "' height=100 width=70/><br>"

                                        # ws.cell(row=new_row, column=6).font = font2
                                http = urllib3.PoolManager()
                                r = http.request('GET',aa[1])
                                image_file = io.BytesIO(r.data)
                                
                                if image_file:

                                    img = Image(image_file)

                                    img.height=120
                                    img.width =120
                                   
                                    if img:
                                        c2e = cm_to_EMU
                                        p2e = pixels_to_EMU

                                        h, w = img.height, img.width
                                        # Calculated number of cells width or height from cm into EMUs
                                        # celh = [1,8,16]
                                        # celw = [0.09,0.01,0.01]
                                        # cellh = 0
                                        # cellw = 0
                                        cellh = lambda x: c2e((x * 8))
                                        cellw = lambda x: c2e((x *0.01))
                                        # cellw = cellzw
                                        # print(cellw, cellh)
                                        # Want to place image in row 5 (6 in excel), column 2 (C in excel)
                                        # Also offset by half a column.
                                        column = 5
                                        # colof = [28000]
                                        coloffset = cellh(0.5)
                                        # coloffset = 2880000
                                        row = new_row-1
                                        rowoffset = cellw(0.03)
                                        rowpp = [107,197]
                                

                                        print(coloffset, rowoffset)
                                        size = XDRPositiveSize2D(p2e(h), p2e(w))
                                        marker = AnchorMarker(col=column, colOff=coloffset, row=row, rowOff=rowoffset)
                                        img.anchor = OneCellAnchor(_from=marker, ext=size)
                                        
                                        ws.add_image(img)
                                        
                                        ws.cell(row=new_row, column=6).value = "<img src='"+ aa[1] + "' height=100 width=70/><br><img src='"+ aa[0] + "' height=100 width=70/><br>"

                                        ws.cell(row=new_row, column=6).font = font2
                                    
                            if len(aa) == 2:
                                http = urllib3.PoolManager()
                                r = http.request('GET',aa[0])
                                image_file = io.BytesIO(r.data)
                                
                                if image_file:

                                    img = Image(image_file)

                                    img.height=120
                                    img.width =120
                                   
                                    if img:
                                        c2e = cm_to_EMU
                                        p2e = pixels_to_EMU

                                        h, w = img.height, img.width
                                        # Calculated number of cells width or height from cm into EMUs
                                        # celh = [1,8,16]
                                        # celw = [0.09,0.01,0.01]
                                        # cellh = 0
                                        # cellw = 0
                                        cellh = lambda x: c2e((x * 1))
                                        cellw = lambda x: c2e((x *0.09))
                                        # cellw = cellzw
                                        # print(cellw, cellh)
                                        # Want to place image in row 5 (6 in excel), column 2 (C in excel)
                                        # Also offset by half a column.
                                        column = 5
                                        # colof = [28000]
                                        coloffset = cellh(0.5)
                                        # coloffset = 2880000
                                        row = new_row-1
                                        rowoffset = cellw(0.03)
                                        rowpp = [107,197]
                                

                                        print(coloffset, rowoffset)
                                        size = XDRPositiveSize2D(p2e(h), p2e(w))
                                        marker = AnchorMarker(col=column, colOff=coloffset, row=row, rowOff=rowoffset)
                                        img.anchor = OneCellAnchor(_from=marker, ext=size)
                                        
                                        ws.add_image(img)
                                        
                                        ws.cell(row=new_row, column=6).value = "<img src='"+ aa[0] + "' height=100 width=70/><br>"

                                        ws.cell(row=new_row, column=6).font = font2

                                
                        if new[-1]=="xlsx" or new[-1]=="docx" or new[-1]=="doc" or new[-1]=="pdf":
                            ws.cell(row=new_row, column=6).hyperlink = aa[j]
                            ws.cell(row=new_row, column=6).value = file_name


def comp(ws,Compliance_file_name):
    font2 = Font(name='Calibri',
                size=11,
                bold=True,
                italic=False,
                vertAlign=None,
                underline='none',
                strike=False,
                color='FFFFFF')
    if Compliance_file_name:
        row_count = ws.max_row
        column_count = ws.max_column
        file_row = []
        for row in range(5,row_count+1):
            file_row.append(row)
        l=[]
        for i in range(len(file_row)):
            if len(file_row)==(row_count-4):
                l.append(file_row[i])
        
        file_name = []
        split = []
        aaa=[]
        val = []
        n=""
        hh=""
        for new_row in l:
            ws.row_dimensions[new_row].height = 140
            ws.column_dimensions[get_column_letter(7)].width = 50
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
                        
                        if new[-1]=="jpeg" or new[-1]=="png" or new[-1]=="jpg":
                            if len(aa) == 4:
                                http = urllib3.PoolManager()
                                r = http.request('GET',aa[0])
                                image_file = io.BytesIO(r.data)
                                
                                if image_file:

                                    img = Image(image_file)

                                    img.height=120
                                    img.width =120
                                   
                                    if img:
                                        c2e = cm_to_EMU
                                        p2e = pixels_to_EMU

                                        h, w = img.height, img.width
                                        # Calculated number of cells width or height from cm into EMUs
                                        # celh = [1,8,16]
                                        # celw = [0.09,0.01,0.01]
                                        # cellh = 0
                                        # cellw = 0
                                        cellh = lambda x: c2e((x * 1))
                                        cellw = lambda x: c2e((x *0.09))
                                        # cellw = cellzw
                                        # print(cellw, cellh)
                                        # Want to place image in row 5 (6 in excel), column 2 (C in excel)
                                        # Also offset by half a column.
                                        column = 6
                                        # colof = [28000]
                                        coloffset = cellh(0.5)
                                        # coloffset = 2880000
                                        row = new_row-1
                                        rowoffset = cellw(0.03)
                                        rowpp = [107,197]
                                

                                        print(coloffset, rowoffset)
                                        size = XDRPositiveSize2D(p2e(h), p2e(w))
                                        marker = AnchorMarker(col=column, colOff=coloffset, row=row, rowOff=rowoffset)
                                        img.anchor = OneCellAnchor(_from=marker, ext=size)
                                        
                                        ws.add_image(img)
                                        
                                        # ws.cell(row=new_row, column=6).value = "<img src='"+ aa[0] + "' height=100 width=70/><br>"

                                        # ws.cell(row=new_row, column=6).font = font2
                                http = urllib3.PoolManager()
                                r = http.request('GET',aa[1])
                                image_file = io.BytesIO(r.data)
                                
                                if image_file:

                                    img = Image(image_file)

                                    img.height=120
                                    img.width =120
                                   
                                    if img:
                                        c2e = cm_to_EMU
                                        p2e = pixels_to_EMU

                                        h, w = img.height, img.width
                                        # Calculated number of cells width or height from cm into EMUs
                                        # celh = [1,8,16]
                                        # celw = [0.09,0.01,0.01]
                                        # cellh = 0
                                        # cellw = 0
                                        cellh = lambda x: c2e((x * 8))
                                        cellw = lambda x: c2e((x *0.01))
                                        # cellw = cellzw
                                        # print(cellw, cellh)
                                        # Want to place image in row 5 (6 in excel), column 2 (C in excel)
                                        # Also offset by half a column.
                                        column = 6
                                        # colof = [28000]
                                        coloffset = cellh(0.5)
                                        # coloffset = 2880000
                                        row = new_row-1
                                        rowoffset = cellw(0.03)
                                        rowpp = [107,197]
                                

                                        print(coloffset, rowoffset)
                                        size = XDRPositiveSize2D(p2e(h), p2e(w))
                                        marker = AnchorMarker(col=column, colOff=coloffset, row=row, rowOff=rowoffset)
                                        img.anchor = OneCellAnchor(_from=marker, ext=size)
                                        
                                        ws.add_image(img)
                                        
                                        # ws.cell(row=new_row, column=6).value = "<img src='"+ aa[1] + "' height=100 width=70/><br>"

                                        # ws.cell(row=new_row, column=6).font = font2
                                http = urllib3.PoolManager()
                                r = http.request('GET',aa[0])
                                image_file = io.BytesIO(r.data)
                                
                                if image_file:

                                    img = Image(image_file)

                                    img.height=120
                                    img.width =120
                                   
                                    if img:
                                        c2e = cm_to_EMU
                                        p2e = pixels_to_EMU

                                        h, w = img.height, img.width
                                        # Calculated number of cells width or height from cm into EMUs
                                        # celh = [1,8,16]
                                        # celw = [0.09,0.01,0.01]
                                        # cellh = 0
                                        # cellw = 0
                                        cellh = lambda x: c2e((x * 16))
                                        cellw = lambda x: c2e((x *0.01))
                                        # cellw = cellzw
                                        # print(cellw, cellh)
                                        # Want to place image in row 5 (6 in excel), column 2 (C in excel)
                                        # Also offset by half a column.
                                        column = 6
                                        # colof = [28000]
                                        coloffset = cellh(0.5)
                                        # coloffset = 2880000
                                        row = new_row-1
                                        rowoffset = cellw(0.03)
                                        rowpp = [107,197]
                                

                                        print(coloffset, rowoffset)
                                        size = XDRPositiveSize2D(p2e(h), p2e(w))
                                        marker = AnchorMarker(col=column, colOff=coloffset, row=row, rowOff=rowoffset)
                                        img.anchor = OneCellAnchor(_from=marker, ext=size)
                                        
                                        ws.add_image(img)
                                        
                                        ws.cell(row=new_row, column=6).value = "<img src='"+ aa[2] + "' height=100 width=70/><br><img src='"+ aa[1] + "' height=100 width=70/><br><img src='"+ aa[0] + "' height=100 width=70/>"

                                        ws.cell(row=new_row, column=6).font = font2
                            if len(aa) == 3:
                                print("00000000000000000000000000")
                                print(len(aa))
                                http = urllib3.PoolManager()
                                r = http.request('GET',aa[0])
                                image_file = io.BytesIO(r.data)
                                
                                if image_file:

                                    img = Image(image_file)

                                    img.height=120
                                    img.width =120
                                   
                                    if img:
                                        c2e = cm_to_EMU
                                        p2e = pixels_to_EMU

                                        h, w = img.height, img.width
                                        # Calculated number of cells width or height from cm into EMUs
                                        # celh = [1,8,16]
                                        # celw = [0.09,0.01,0.01]
                                        # cellh = 0
                                        # cellw = 0
                                        cellh = lambda x: c2e((x * 1))
                                        cellw = lambda x: c2e((x *0.09))
                                        # cellw = cellzw
                                        # print(cellw, cellh)
                                        # Want to place image in row 5 (6 in excel), column 2 (C in excel)
                                        # Also offset by half a column.
                                        column = 6
                                        # colof = [28000]
                                        coloffset = cellh(0.5)
                                        # coloffset = 2880000
                                        row = new_row-1
                                        rowoffset = cellw(0.03)
                                        rowpp = [107,197]
                                

                                        print(coloffset, rowoffset)
                                        size = XDRPositiveSize2D(p2e(h), p2e(w))
                                        marker = AnchorMarker(col=column, colOff=coloffset, row=row, rowOff=rowoffset)
                                        img.anchor = OneCellAnchor(_from=marker, ext=size)
                                        
                                        ws.add_image(img)
                                        
                                        # ws.cell(row=new_row, column=6).value = "<img src='"+ aa[1] + "' height=100 width=70/><br>"

                                        # ws.cell(row=new_row, column=6).font = font2
                                http = urllib3.PoolManager()
                                r = http.request('GET',aa[1])
                                image_file = io.BytesIO(r.data)
                                
                                if image_file:

                                    img = Image(image_file)

                                    img.height=120
                                    img.width =120
                                   
                                    if img:
                                        c2e = cm_to_EMU
                                        p2e = pixels_to_EMU

                                        h, w = img.height, img.width
                                        # Calculated number of cells width or height from cm into EMUs
                                        # celh = [1,8,16]
                                        # celw = [0.09,0.01,0.01]
                                        # cellh = 0
                                        # cellw = 0
                                        cellh = lambda x: c2e((x * 8))
                                        cellw = lambda x: c2e((x *0.01))
                                        # cellw = cellzw
                                        # print(cellw, cellh)
                                        # Want to place image in row 5 (6 in excel), column 2 (C in excel)
                                        # Also offset by half a column.
                                        column = 6
                                        # colof = [28000]
                                        coloffset = cellh(0.5)
                                        # coloffset = 2880000
                                        row = new_row-1
                                        rowoffset = cellw(0.03)
                                        rowpp = [107,197]
                                

                                        print(coloffset, rowoffset)
                                        size = XDRPositiveSize2D(p2e(h), p2e(w))
                                        marker = AnchorMarker(col=column, colOff=coloffset, row=row, rowOff=rowoffset)
                                        img.anchor = OneCellAnchor(_from=marker, ext=size)
                                        
                                        ws.add_image(img)
                                        
                                        ws.cell(row=new_row, column=7).value = "<img src='"+ aa[1] + "' height=100 width=70/><br><img src='"+ aa[0] + "' height=100 width=70/><br>"

                                        ws.cell(row=new_row, column=7).font = font2
                                    
                            if len(aa) == 2:
                                http = urllib3.PoolManager()
                                r = http.request('GET',aa[0])
                                image_file = io.BytesIO(r.data)
                                
                                if image_file:

                                    img = Image(image_file)

                                    img.height=120
                                    img.width =120
                                   
                                    if img:
                                        c2e = cm_to_EMU
                                        p2e = pixels_to_EMU

                                        h, w = img.height, img.width
                                        # Calculated number of cells width or height from cm into EMUs
                                        # celh = [1,8,16]
                                        # celw = [0.09,0.01,0.01]
                                        # cellh = 0
                                        # cellw = 0
                                        cellh = lambda x: c2e((x * 1))
                                        cellw = lambda x: c2e((x *0.09))
                                        # cellw = cellzw
                                        # print(cellw, cellh)
                                        # Want to place image in row 5 (6 in excel), column 2 (C in excel)
                                        # Also offset by half a column.
                                        column = 6
                                        # colof = [28000]
                                        coloffset = cellh(0.5)
                                        # coloffset = 2880000
                                        row = new_row-1
                                        rowoffset = cellw(0.03)
                                        rowpp = [107,197]
                                

                                        print(coloffset, rowoffset)
                                        size = XDRPositiveSize2D(p2e(h), p2e(w))
                                        marker = AnchorMarker(col=column, colOff=coloffset, row=row, rowOff=rowoffset)
                                        img.anchor = OneCellAnchor(_from=marker, ext=size)
                                        
                                        ws.add_image(img)
                                        
                                        ws.cell(row=new_row, column=7).value = "<img src='"+ aa[0] + "' height=100 width=70/><br>"

                                        ws.cell(row=new_row, column=7).font = font2

                                
                        if new[-1]=="xlsx" or new[-1]=="docx" or new[-1]=="doc" or new[-1]=="pdf" or new[-1]=="svg":
                            ws.cell(row=new_row, column=7).hyperlink = aa[j]
                            ws.cell(row=new_row, column=7).value = file_name
                        
                                    
                        # # if new[-1]=="svg":
                        # #     http = urllib3.PoolManager()
                        # #     # r = http.request('GET', aa[j-(len(aa)-1)])
                        # #     if aa[j]:
                        # #         r = http.request('GET', aa[j])
                        # #         image_file = io.BytesIO(r.data)
                        # #         if image_file:
                        # #             img = Image(image_file)
                        # #             img.height=100
                        # #             img.width =100
                        # #             img.format = new[-1]

                        # #             ws.add_image(img,'F'+str(new_row))
                        # #             ws.row_dimensions[new_row].height = 40
                        # #             # ws.cell(row=new_row, column=7).value = aa[j]
                        # #             # ws.cell(row=new_row, column=7).hyperlink = aa[j]
                        # #             ws.cell(row=new_row, column=6).value = "<img src='"+ aa[j] + "' height=100 width=70/>"

                        # #             ws.cell(row=new_row, column=6).font = font2
                        


                        #     # print(aa[j])
                        #     # print(aa[j-(len(aa))])
                        #     # http = urllib3.PoolManager()
                        #     # # r = http.request('GET', aa[j-(len(aa)-1)])
                        #     # r = http.request('GET', aa[j])
                        #     # image_file = io.BytesIO(r.data)
                        
                        #     # img = Image(image_file)
                        #     # img.height=100
                        #     # img.width =100
                        #     # ws.add_image(img,'G'+str(new_row))
                        #     # # ws.cell(row=new_row, column=7).value = aa[j]
                        #     # # ws.cell(row=new_row, column=7).hyperlink = aa[j]
                        #     # ws.cell(row=new_row, column=7).value = "<img src='"+  aa[j] + "' height=100 width=70/>"
                        # if len(n)>180:                
                        #     ws.row_dimensions[new_row].height = 120
                        #     if new[-1]=="jpeg" or new[-1]=="jpg" or new[-1]=="png":
                        # #         # print(aa[j])
                        #         http = urllib3.PoolManager()
                        #         # r = http.request('GET', aa[j-(len(aa)-1)])
                        #         r = http.request('GET', aa[j])
                        # # #         print(aa[j])
                        #         image_file = io.BytesIO(r.data)
                        # # #         print("0000---------------0000")
                        # # #         print(image_file)
                        #         img = Image(image_file)
                        # # #         print("000000000000000000000000")
                        # # #         print(img)
                        #         img.height=100
                        #         img.width =100
                        #         if img:
                        #             ws.add_image(img,'F'+str(new_row))
                        #     #         # ws.cell(row=new_row, column=7).value = aa[j]
                        #             ws.cell(row=new_row, column=6).value = "<img scr='"+  aa[j] + "'  />"
                        #             ws.cell(row=new_row, column=6).font = font2

                                

                        #         # ============================================================
                        #         # r1 = http.request('GET', aa[0])
                        #         # # r = http.request('GET', aa[j])
                        #         # image_file1 = io.BytesIO(r1.data)
                            
                        #         # img1 = Image(image_file1)
                        #         # img1.height=100
                        #         # img1.width =100
                        #         # ws.add_image(img1,'G'+str(new_row))
                                
                        #         # ws.cell(row=new_row, column=7).value = "<img scr='"+  aa[j-(len(aa)-1)] + "'></img>"
                        #         # ws.cell(row=new_row, column=7).value = '<img src="' + aa[0] + '"/>'
                        #         ws.cell(row=new_row, column=6).alignment = Alignment(wrap_text=True, horizontal='right', vertical='center')
                        #         ws.cell(row=new_row, column=6).hyperlink = aa[0]
                        #         ws.cell(row=new_row, column=6).value ="Image"
                        #         ws.cell(row=new_row, column=6).alignment = Alignment(wrap_text=True, horizontal='right', vertical='center')
                        #         ws.cell(row=new_row, column=6).font = dd
                        #         ws.row_dimensions[new_row].height = 150
                        #     # else:
                        #     #     ws.cell(row=new_row, column=7).value = ""


                        #     # ws.cell(row=new_row, column=7).hyperlink = nnn

                        # n =""
        
                            

def write_excel(project, queryset, type, status,start_date, end_date,asset, performance, photo,doc_type,name):
    # print(project.name)

    wb = Workbook()
    ws1 = wb.active
    ws2 = wb.active
    ws3 = wb.active
    ws4 = wb.active
    ws5 = wb.active
    ws6 = wb.active
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
        ws1['A1'] = "Inspection Report with Photogragh"
        ws1['A2'] = "Project Name"
        ws1['B2'] = project.name
        fieldnames = ["Ref.No.", "Chainage","" , "Direction", "Description of Issue",
                              "Photograph During Inspection", "Asset Type", "Performance Parameter",
                              "Issue Raised On", "Issue Raised By",
                              "Issue Raised To"]
        ws1.append(fieldnames)
        ws1.merge_cells('A3:A4')
        ws1.merge_cells('B3:c3')
        # ws1.merge_cells('C3:D3')
        # ws1.merge_cells('C4:D4')
        n1 = ws1.cell(row=4,column=2)
        n2 = ws1.cell(row=4,column=3)
        n1.value = "From (In Km)"
        n2.value = "To (In Km)"
        ws1.merge_cells('D3:D4')
        # n3 = ws1.cell(row=3,column=5)
        # n3.value="Direction"
        ws1.merge_cells('E3:E4')
        ws1.merge_cells('F3:F4')
        ws1.merge_cells('G3:G4')
        ws1.merge_cells('H3:H4')
        ws1.merge_cells('I3:I4')
        ws1.merge_cells('J3:J4')
        ws1.merge_cells('K3:K4')
        # ws1.merge_cells('L3:L4')
        

    if type == 'Issue' and photo=="without photo" and status==None:

        ws5.title = "Inspection Reportssssss"
        ws5['A1'] = "Inspection Report without Photogragh"
        ws5['A2'] = "Project Name"
        ws5['B2'] = project.name
        fieldnames = ["Ref.No.", "Chainage","" , "Direction", "Description of Issue",
                              "Asset Type", "Performance Parameter",
                              "Issue Raised On", "Issue Raised By",
                              "Issue Raised To"]
        ws5.append(fieldnames)
    
        ws1.append(fieldnames)
        ws1.merge_cells('A3:A4')
        ws1.merge_cells('B3:c3')
        # ws1.merge_cells('C3:D3')
        # ws1.merge_cells('C4:D4')
        n1 = ws1.cell(row=4,column=2)
        n2 = ws1.cell(row=4,column=3)
        n1.value = "From (In Km)"
        n2.value = "To (In Km)"
        ws1.merge_cells('D3:D4')
        # n3 = ws1.cell(row=3,column=5)
        # n3.value="Direction"
        ws1.merge_cells('E3:E4')
        ws1.merge_cells('F3:F4')
        ws1.merge_cells('G3:G4')
        ws1.merge_cells('H3:H4')
        ws1.merge_cells('I3:I4')
        ws1.merge_cells('J3:J4')
        # ws1.merge_cells('L3:L4')
    if type == 'Issue' and name=="Compliance" and photo=="with photo" and status:

        wb = Workbook()
        ws2 = wb.active
    
        ws2.title = "Manitenance Report"
        ws2['A1'] = "Maintenance Report with Photograph"
        ws2['A2'] = "Project Name"
        ws2['B2'] = project.name
        
        fieldnames = ["Ref.No.", "Chainage","", "Direction", "Description of Issue",
                          "Photograph During Inspection","Photograph During Maintenance", "Asset Type", "Performance Parameter",
                          "Issue Raised On", "Issue Raised By",
                          "Issue Raised To" , "Max Time limit for Rectification/Repair",
                          "", "Action Taken",
                          "", "", "Issue Closed By","Description Of Compliance",
                          "Photograph Post Compliance", "Remark", "Current Status"]
        ws2.append(fieldnames)
        ws2.merge_cells('A3:A4')
        ws2.merge_cells('B3:C3')
        # ws2.merge_cells('C3:D3')
        # ws1.merge_cells('C4:D4')
        n1 = ws2.cell(row=4,column=2)
        n2 = ws2.cell(row=4,column=3)
        n1.value = "From (In Km)"
        n2.value = "To (In Km)"
        ws2.merge_cells('D3:D4')
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

        # ws2.merge_cells('Q3:Q4')
        ws2.merge_cells('R3:R4')
        ws2.merge_cells('S3:S4')
        ws2.merge_cells('T3:T4')
        ws2.merge_cells('U3:U4')
        ws2.merge_cells('V3:V4')


    if type=='Issue' and name=="Compliance" and photo=="without photo" and status:
    
        ws4.title = "Manitenance Report"
        ws4['A1'] = "Maintenance Report without Photograph"
        ws4['A2'] = "Project Name"
        ws4['B2'] = project.name
        fieldnames = ["Ref.No.", "Chainage","", "Direction", "Description of Issue",
                          "Asset Type", "Performance Parameter",
                          "Issue Raised On", "Issue Raised By",
                          "Issue Raised To" , "Max Time limit for Rectification/Repair",
                          "", "Action Taken",
                          "", "", "Issue Closed By","Description Of Compliance",
                          "Photograph Post Compliance", "Remark", "Current Status"]
        ws4.append(fieldnames)
        ws4.merge_cells('A3:A4')
        ws4.merge_cells('B3:C3')
        # ws2.merge_cells('C3:D3')
        # ws1.merge_cells('C4:D4')
        n1 = ws4.cell(row=4,column=2)
        n2 = ws4.cell(row=4,column=3)
        n1.value = "From (In Km)"
        n2.value = "To (In Km)"
        ws4.merge_cells('D3:D4')
        # n3 = ws1.cell(row=3,column=5)
        # n3.value="Direction"
        ws4.merge_cells('E3:E4')
        ws4.merge_cells('F3:F4')
        ws4.merge_cells('G3:G4')
        ws4.merge_cells('H3:H4')
        ws4.merge_cells('I3:I4')
        ws4.merge_cells('J3:J4')
        # ws4.merge_cells('K3:K4')
        # ws2.merge_cells('L3:L4')
        ws4.merge_cells('K3:L3')
        n1 = ws4.cell(row=4,column=11)
        n2 = ws4.cell(row=4,column=12)
        n1.value = "Timeline\n (As per  Schedule F)"
        n2.value = "Target Date\n(As per  Schedule F)"
        # ws2.merge_cells('M3:M4')
        # ws2.merge_cells('N3:N4')
        ws4.merge_cells('M3:O3')
        n1 = ws4.cell(row=4,column=13)
        n2 = ws4.cell(row=4,column=14)
        n3 = ws4.cell(row=4,column=15)
        n1.value = "Status\n(Open/Closed/Under Rectification)"
        n2.value = "Issue Closed On Date\n(If Closed)"
        n3.value = "Complianced\n (Yes/No)"
        ws4.merge_cells('P3:P4')
        ws4.merge_cells('Q3:Q4')
        ws4.merge_cells('R3:R4')
        ws4.merge_cells('S3:S4')
        ws4.merge_cells('T3:T4')


    if type == 'Investigation' and photo=="with photo":
        
        ws3.title = "Test Report"
        ws3['A1'] = "Test Report"
        ws3['A2'] = "Project Name"
        ws3['B2'] = project.name
        fieldnames = ["Ref.No.","Description of Test/ Investigation", "Chainage","", "Direction",
                          "Asset Type", "Performance Parameter",
                          "Name of Test", "Testing Method", "Standard References for testing",
                          "Test Carried Out Date", "Testing Carried Out By(Name)"]
        
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
  
    if type == 'Investigation' and photo=="without photo":
        
        ws6.title = "Test Report"
        ws6['A1'] = ""
        ws6['A2'] = "Test Report"
        fieldnames = ["Ref.No.","Description of Test/ Investigation", "Chainage","", "Direction",
                          "Asset Type", "Performance Parameter",
                          "Name of Test", "Testing Method", "Standard References for testing",
                          "Test Carried Out Date", "Testing Carried Out By(Name)"]
        
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



    if type == 'Accident':
       
        ws4.title = "Summary of Accident"
        ws4['A1'] = "Summary of Accident Report"
        ws4['A2'] = "Date:\n From: "+start_date+ '\t To: ' +end_date
        ws4['B2'] = "Project Name"
        ws4['C2'] = project.name
        

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
                new_watcher_list = split[i]+'\n' + new_watcher_list
            if issue.attachments:
                file_name = "" 
                files = []
                file = issue.attachments.all().filter(project__id=issue.project.id,description="").values_list('attached_file')
                for i in file:
                    files.extend(i)
                for j in files:
                    file_name = os.path.join(settings.MEDIA_URL,str(j)) +'\n' + file_name
            else:
                file_name=""

            print(file_name)
            
            Raised_date = datetime.strftime(issue.created_date.date(),"%d-%m-%Y")
            issue_data = [[
                issue.ref,
                # issue.project.name,
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
                new_watcher_list = split[i]+'\n' + new_watcher_list
                
            Raised_date = datetime.strftime(issue.created_date.date(),"%d-%m-%Y")
            issue_data = [[
                issue.ref,
                # issue.project.name,
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

    

        if issue.type.name=='Issue' and name=="Compliance" and photo=="with photo" and status:
            for issue in queryset:
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
                    new_watcher_list = split[i]+'\n' + new_watcher_list
                a = issue.created_date.date()
                b = datetime.strptime(issue.target_date,"%d/%m/%Y").date()
                timeline = b-a
                target_date = datetime.strftime(b,"%d-%m-%Y")
                
                if issue.attachments:
                    file_name = "" 
                    files = []
                    Compliance_file_name = "" 
                    Compliance_files = []

                    file = issue.attachments.all().filter(project__id=issue.project.id,description="").values_list('attached_file')
                    for i in file:
                        files.extend(i)
                    for j in files:
                        file_name = os.path.join(settings.MEDIA_URL,str(j)) +'\n' + file_name
                

                    
                    Compliance_file = issue.attachments.all().filter(project__id=issue.project.id,description="Compliances").values_list('attached_file')
                    for k in Compliance_file:
                        Compliance_files.extend(k)
                    for l in Compliance_files:
                        Compliance_file_name = os.path.join(settings.MEDIA_URL,str(l)) +'\n' + Compliance_file_name
                else:
                    file_name=""
                    Compliance_file_name=""

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
                        # issue.project.name,
                        issue.chainage_from,
                        issue.chainage_to,
                        issue.chainage_side,
                        issue.description,
                        file_name,
                        Compliance_file_name,
                        issue.issue_category,
                        issue.issue_subcategory,
                        issue.created_date.date(),
                        issue.owner.full_name if issue.owner else None,
                        new_watcher_list,
                        timeline,
                        target_date,
                        'new' if issue.status else None,
                        issue.finished_date if status_name=='Closed' else None,
                        'Yes' if issue.compliance_is_update==True else 'No',
                        issue.assigned_to.full_name if issue.assigned_to else None,
                        issue.compliance_description,
                        issue.attachments.name,
                        "",
                        'new' if issue.status else None,
                    ]]
                for data in issue_data:
                    ws2.append(data)
            wb.save("table.xlsx")
            wb.close()

            wb = load_workbook('table.xlsx')
            ws2 = wb['Manitenance Report']
            style(ws2,fieldnames, file_name, issue)
            comp(ws2,Compliance_file_name)

        if issue.type.name=='Issue' and name=="Compliance" and photo=="without photo" and status:
            for issue in queryset:
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
                    new_watcher_list = split[i]+'\n' + new_watcher_list
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
                        "new" if issue.status else None,
                        issue.finished_date if status_name=='Closed' else None,
                        'Yes' if issue.compliance_is_update==True else 'No',
                        issue.assigned_to.full_name if issue.assigned_to else None,
                        issue.compliance_description,
                        issue.attachments.name,
                        "",
                        "new" if issue.status else None,
                    ]]
                for data in issue_data:
                    ws4.append(data)
            wb.save("table.xlsx")
            wb.close()

            wb = load_workbook('table.xlsx')
            ws4 = wb['Manitenance Report']
            style(ws4,fieldnames, issue)
            

        if issue.type.name == 'Investigation' and photo=="with photo":
            issue_data = [[
                issue.ref,
                issue.investigation_description,
                issue.investigation_chainage_from,
                issue.investigation_chainage_to,
                issue.investigation_chainage_side,
                issue.asset_name,
                issue.test_name,
                issue.test_name,
                issue.testing_method,
                issue.test_specifications,
                issue.created_date.date(),
                issue.owner.full_name if issue.owner else None,
            ]]
            for data in issue_data:
                ws3.append(data)


            wb.save("table.xlsx")
            wb.close()

            wb = load_workbook('table.xlsx')
        
            ws3 = wb['Test Report']
            style(ws3,fieldnames, issue)

        if issue.type.name == 'Investigation' and photo=="without photo":
            issue_data = [[
                issue.ref,
                issue.investigation_description,
                issue.investigation_chainage_from,
                issue.investigation_chainage_to,
                issue.investigation_chainage_side,
                issue.asset_name,
                issue.test_name,
                issue.test_name,
                issue.testing_method,
                issue.test_specifications,
                issue.created_date.date(),
                issue.owner.full_name if issue.owner else None,
            ]]
            for data in issue_data:
                ws6.append(data)


            wb.save("table.xlsx")
            wb.close()

            wb = load_workbook('table.xlsx')
        
            ws6 = wb['Test Report']
            style(ws6,fieldnames, issue)

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
        new = pd.read_excel('table.xlsx',na_filter=False,header=None, names="",border="0")
    
        # for i in wwww:
        #  
        pd.set_option('display.max_colwidth', 500)   # FOR TABLE <th>

        html = new.to_html(escape=False,index=False,header=False,border="0.5").replace('&lt;','<').replace('&gt;', '>')
        pisa_context = pisa.CreatePDF(html)
        response = pisa_context.dest.getvalue()
        return html
        # return response

    return wb