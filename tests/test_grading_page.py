import pytest
import os
import platform
from requests_html import HTMLSession
from requests_file import FileAdapter
from pathlib import WindowsPath, PosixPath
from lib.grading_page import GradingPage
from requests_html import HTML

session = HTMLSession()
session.mount('file://', FileAdapter())


def get():
    path = os.path.sep.join((os.path.dirname(os.path.abspath(__file__)), 'mocked_grading.html'))
    if platform.system() == 'Windows':
        path = WindowsPath(path)
    else:
        path = PosixPath(path)
    url = path.as_uri()

    return session.get(url)


@pytest.fixture
def page():
    return GradingPage(get())


def test_validate_login(page):
    assert page.validate_login() is None


def test_page_count(page):
    assert page.page_count == 4


def test_table_headers(page):
    expected_headers = [
        'Student',
        'Center',
        'Belt - Game',
        'Completed Date',
        'Graded Date',
        'Stars Earned',
        'Play and Grade'
    ]
    assert page.table_headers == expected_headers


def test_row_data(page):
    row_data = '<tr class="graded" data-uts="f4TGigNsjf"><td>Matt Damon</td><td>Wellesley</td>'\
        '<td>White Belt v2 - The Cat and You!</td><td>12/1/2018</td><td>'\
        '<span class="col-graded">12/1/2018 by Jim Mattis</span></td>'\
        '<td><div class="col-stars-earned"><span><i class="fa fa-star"></i><i class="fa fa-star"></i>'\
        '<i class="fa fa-star"></i></span></div></td><td>' \
        '<a href="/Grading/Details/f4Tswersjf" class="btn btn-primary btn-sm">Play &amp; Grade</a></td></tr>'
    html = HTML(html=row_data)
    expected_data = [
        'Matt Damon',
        'Wellesley',
        'White Belt v2 - The Cat and You!',
        '12/1/2018',
        '12/1/2018 by Jim Mattis',
        '3',
        '/Grading/Details/f4Tswersjf'
    ]
    assert page._row_data(html) == expected_data


def test_grades(page):
    expected_grades = [
        {'Student': 'Matt Damon', 'Center': 'Wellesley', 'Belt - Game': 'White Belt v2 - The Cat and You!', 'Completed Date': '12/1/2018', 'Graded Date': '12/1/2018 by Jim Mattis', 'Stars Earned': '3', 'Play and Grade': '/Grading/Details/f4Tswersjf'},
        {'Student': 'John Goodman', 'Center': 'Wellesley', 'Belt - Game': 'White Belt v2 - The Cat and You!', 'Completed Date': '12/1/2018', 'Graded Date': '12/1/2018 by Condoleza Rice', 'Stars Earned': '3', 'Play and Grade': '/Grading/Details/eYLsdf4Tm2'},
        {'Student': 'Jet Lee', 'Center': 'Wellesley', 'Belt - Game': 'White Belt v2 - The Cat and You!', 'Completed Date': '12/1/2018', 'Graded Date': '12/1/2018 by Hugo Boss', 'Stars Earned': '3', 'Play and Grade': '/Grading/Details/rKhsdf2Xrc'}]

    assert page.grades == expected_grades
