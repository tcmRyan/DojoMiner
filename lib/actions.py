import csv
import os
import xlsxwriter

from setting import config
from .dojo_requests import DojoRequests
from .grading_page import GradingPage
from .belt_scripts import get_ninjas_info, get_get_ninjas_usage


def get_grading_page(session, search_term='', page_num=1, page_size=100, include_graded='true'):
    url = 'https://gdp.code.ninja/Grading/'
    params = {
        'searchTerm': search_term,
        'pageNum': page_num,
        'pageSize': page_size,
        'includeGraded': include_graded,
        'slug': 'undefined',
    }
    return session.get(url, params=params)


def create_csv(headers, data, filename='grades.csv'):
    # if os.path.exists(filename) and not config['file_config']['overwrite']:
    #     name, _ = filename.split('.csv')
    #     now = datetime.datetime.now()
    #     filename = name + now.strftime('%d%B%y-%H:%M') + '.csv'

    with open(filename, 'w', newline='') as f:
        w = csv.DictWriter(f, headers)
        w.writeheader()
        w.writerows(data)


def save_grades(filename, search_term=''):
    session = DojoRequests()
    page = GradingPage(get_grading_page(session, search_term=search_term))
    data = []
    print(page.page_count)
    for page_number in range(page.page_count):
        print(f'Processing pn: {page_number}')
        page_number += 1  # Offset for human counting
        page = GradingPage(get_grading_page(
            session,
            page_num=page_number,
            search_term=search_term)
        )
        data.extend(page.grades)
        

    create_csv(page.table_headers, data, filename=filename)


def save_belts(filename, site_name):
    students = get_ninjas_info(site_name)
    headers = students[0].keys()
    create_csv(headers, students, filename)


def save_usage(filename, site_name, excel_fmt=False):
    """
    Creates a CSV for each month.  If excel mode selected, it will create 1 workbook
    with a sheet per month
    :param filename:
    :param site_name:
    :param excel_fmt: boolean to write in excel format
    :return:
    """
    usages = get_get_ninjas_usage(site_name)
    # if excel_fmt:
    #     if os.path.exists(filename):
    #         os.remove(filename)
    #     wb = xlsxwriter.Workbook(filename)
    #     for key, value in usages.items():
    #         write_excel_ws(wb, key, value[0].keys(), value)
    headers = usages[0].keys()
    create_csv(headers, usages, filename=filename)


def scheduled_work():
    if config['file_config'].get('repeat'):
        save_grades(config['file_config']['name'], config['search_term'])


def write_excel_ws(workbook, name, headers, data):
    ws = workbook.add_worksheet(name)
    write_row(ws, 0, headers)
    for i, row in enumerate(data):
        row_num = i + 1  # Account for the headers
        write_row(ws, row_num, data)


def write_row(worksheet, row, data):
    for i, header in enumerate(data):
        worksheet.write(row, i, data)

