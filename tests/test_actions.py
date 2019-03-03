from lib import actions
from unittest.mock import patch
from copy import deepcopy

grade_data = [
    {
        'Student': 'Matt Damon',
        'Center': 'Wellesley',
        'Belt - Game': 'White Belt v2 - The Cat and You!',
        'Completed Date': '12/1/2018',
        'Graded Date': '12/1/2018 by Ben Affleck',
        'Stars Earned': '3',
        'Play and Grade': '/Grading/Details/f4TGsdfjf'
    },
    {
        'Student': 'Willie Wonka',
        'Center': 'Wellesley',
        'Belt - Game': 'White Belt v2 - The Cat and You!',
        'Completed Date': '12/1/2018',
        'Graded Date': '12/1/2018 by Umpa Loopa',
        'Stars Earned': '3',
        'Play and Grade': '/Grading/Details/eYsdfBZ8Tm2'},
    {
        'Student': 'Sam Huff',
        'Center': 'Wellesley',
        'Belt - Game': 'White Belt v2 - The Cat and You!',
        'Completed Date': '12/1/2018',
        'Graded Date': '12/1/2018 by Bill Parcels',
        'Stars Earned': '3',
        'Play and Grade': '/Grading/Details/rKhsdffEc'}
    ]


@patch('lib.actions.DojoRequests')
@patch('lib.actions.GradingPage')
@patch('lib.actions.create_csv')
def test_save_grades_no_search(mock_dojo_requests, mock_grading_page, mock_create_csv):
    mock_page = mock_grading_page.return_value
    mock_page.page_count = 1
    mock_page.grades = grade_data
    mock_page.table_headers = grade_data[0].keys()

    actions.save_grades('test.csv')
    actions.create_csv.assert_called_with(grade_data[0].keys(), grade_data, filename='test.csv')


@patch('lib.actions.DojoRequests')
@patch('lib.actions.GradingPage')
@patch('lib.actions.create_csv')
def test_save_grades_iteration(mock_dojo_requests, mock_grading_page, mock_create_csv):
    mock_page = mock_grading_page.return_value
    mock_page.page_count = 2
    mock_page.grades = grade_data
    mock_page.table_headers = grade_data[0].keys()
    grades = deepcopy(grade_data)
    grades.extend(grades)
    actions.save_grades('test.csv')
    actions.create_csv.assert_called_with(grade_data[0].keys(), grades, filename='test.csv')
