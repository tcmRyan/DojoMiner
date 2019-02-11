import csv
import os

from .dojo_requests import DojoRequests
from .grading_page import GradingPage


def get_grading_page(session, search_term='', page_num=1, page_size=100, include_graded='true'):
    url = 'https://gdp.code.ninja/Grading/'
    params = {
        'searchTerm': search_term,
        'pageNum': page_num,
        'pageSize': page_size,
        'includeGraded': include_graded,
    }
    return session.get(url, params=params)


def create_csv(headers, data, filename='grades.csv'):
    if os.path.exists(filename):
        pass

    with open(filename, 'w', newline='') as f:
        w = csv.DictWriter(f, headers)
        w.writeheader()
        w.writerows(data)


def save_grades(filename, search_term=''):
    session = DojoRequests()
    page = GradingPage(get_grading_page(session, search_term=''))
    data = []
    for page_number in range(page.page_count):
        page_number += 1  # Offset for human counting
        page = GradingPage(get_grading_page(
            session,
            page_num=page_number,
            search_term=search_term)
        )
        data.extend(page.grades)

    create_csv(page.table_headers, data, filename=filename)

