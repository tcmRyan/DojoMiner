from lib.dojo_requests import DojoRequests
import csv

requests = DojoRequests()

SEARCH = "https://dojo.code.ninja/api/employee/{site}/search/"
STUDENT_OVERVIEW = "https://dojo.code.ninja/api/customerdetailsstudent/{site}/studentoverview/{student_id}"
STUDENT_LICENSE = "https://dojo.code.ninja/api/customerdetailsstudent/{site}/studentLicenses/{student_id}"
STUDENT_BELTS = "https://dojo.code.ninja/api/customerdetailsstudent/{site}/studentbelts/{student_id}"


def get_ninja_info(guid, site_name):
    licenses = requests.get(STUDENT_LICENSE.format(site=site_name, student_id=guid)).json()
    ninja = {}
    for program in licenses:
        if program['programName'] == 'Drop-in Learning':
            # Filter out any ninjas that have not be enrolled in the program
            ninja['First Name'] = program['firstName']
            ninja['Last Name'] = program['lastName']
            ninja['Is Active'] = program['isActive']
            ninja['Is Frozen'] = program['isFrozen']
            belt_info = requests.get(STUDENT_OVERVIEW.format(site=site_name, student_id=guid)).json()
            ninja['Current Belt'] = belt_info['currentBelt']['beltName']
            return ninja


def fetch_students(site, page_size=10):
    params = {
        'pageNum': 1,
        'pageSize': page_size
    }
    page = requests.get(SEARCH.format(site=site), params=params).json()
    total_records = int(page['recordCount'])
    pages = int((total_records/page_size)) + 1
    data = []

    for page_number in range(pages):
        page_number += 1  # Offset fo query purposes
        page_data = []
        params['pageNum'] = page_number
        page = requests.get(SEARCH.format(site=site), params=params).json()
        for customer in page['customers']:
            for member in customer['members']:
                ninja = get_ninja_info(member['guid'], site)
                if ninja:
                    page_data.append(ninja)
        data.extend(page_data)

    return data
