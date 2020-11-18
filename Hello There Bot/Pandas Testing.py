# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 16:49:25 2020

@author: derph
"""

from PIL import ImageGrab
import win32com.client as win32

excel = win32.gencache.EnsureDispatch('Excel.Application')
workbook = excel.Workbooks.Open('How was your Day.xlsx')

for sheet in workbook.Worksheets:
    for i, shape in enumerate(sheet.Shapes):
        if shape.Name.startswith('Picture'):
            shape.Copy()
            image = ImageGrab.grabclipboard()
            image.save('{}.jpg'.format(i+1), 'jpeg')