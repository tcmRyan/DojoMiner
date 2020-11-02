from lib.dojo_requests import DojoRequests
from collections import OrderedDict
import json
import datetime
import dateutil.relativedelta
import dateutil.parser

requests = DojoRequests()

SEARCH = "https://dojo.code.ninja/api/employee/{site}/search/"
STUDENT_OVERVIEW = "https://dojo.code.ninja/api/customerdetailsstudent/{site}/studentoverview/{student_id}"
STUDENT_LICENSE = "https://dojo.code.ninja/api/customerdetailsstudent/{site}/studentLicenses/{student_id}"
STUDENT_BELTS = "https://dojo.code.ninja/api/customerdetailsstudent/{site}/studentbelts/{student_id}"
STUDENT_USAGE = "https://dojo.code.ninja/api/customerdetailsstudent/{site}/studentusage/{student_id}"
GENERAL_STUDENT_DETAIL = 'https://dojo.code.ninja/api/customerdetailsgeneral/{site}/{customer_id}/student/{student_id}'


def get_ninjas_info(site_name):
    """
    Gets the current belt information for all the ninjas in the dojo
    :param site_name: The string for your site id. i.e. cn-ma-wellesley
    :return: List of ninja dictionaries
    """
    ninjas = fetch_students(site_name)
    data = []
    for ninja_id, customer_id in ninjas:
        ninja = get_ninja_info(ninja_id, customer_id, site_name)
        if ninja:
            data.append(ninja)

    return data


def get_ninja_info(guid, customer_id, site_name):
    licenses = requests.get(STUDENT_LICENSE.format(site=site_name, student_id=guid)).json()
    birthday = requests.get(GENERAL_STUDENT_DETAIL.format(site=site_name, customer_id=customer_id, student_id=guid)) \
        .json()['dateOfBirth']
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
            ninja['Birthday'] = birthday
            return ninja


def get_get_ninjas_usage(site_name):
    """
    Get the weekly usage of the ninjas for the last 6 months
    :param site_name: The string for your site id. i.e. cn-ma-wellesley
    :return:
    """
    ninjas = fetch_students(site_name)
    master_report = []
    for ninja_id, customer_id in ninjas:
        ninja = get_ninja_info(ninja_id, customer_id, site_name)
        if not ninja:
            continue
        usage = get_ninja_usage(ninja_id, site_name)
        master_report.append(usage_to_dict(ninja, usage))
    return master_report


def usage_to_dict(ninja, usage):
    name = ninja['name']
    row = OrderedDict()
    usage.sort(key=lambda w: w['days'][0]['dayDate'])
    for week in usage:
        start_date = week['days'][0]['dayDate']
        start_date = dateutil.parser.parse(start_date)
        key = 'Week of {}'.format(start_date.strftime('%b %d'))
        row[key] = week['hoursForWeek']
    row['name'] = name
    row.move_to_end('name', last=False)
    return row


def get_ninja_usage(guid, site_name):
    """
    Get the weekly usage data for a student in the last 6 months
    :param guid: the global unique id (hash) for query student data
    :param site_name: The string for your site id. i.e. cn-ma-wellesley
    :return:
    """
    date = datetime.datetime.now()
    usage = []
    for i in range(6):
        str_date = datetime.datetime.strftime(date, '%m-%d-%Y')
        monthly_usage = requests.get(
            STUDENT_USAGE.format(site=site_name, student_id=guid),
            params={'selectedDate': str_date}).json()
        usage.extend(monthly_usage['weeks'])
        date = date - dateutil.relativedelta.relativedelta(months=1)
    usage = clean_usage(usage)

    return usage


def clean_usage(usage):
    """
    Remove Duplicate weeks based on the start day of the week
    :param usage:
    :return:
    """
    return list({week['days'][0]['dayDate']: week for week in usage}.values())


def fetch_students(site, page_size=10):
    """
    Iterate through the customer data to create a iterable generator of student guids
    :param site: The string for your site id. i.e. cn-ma-wellesley
    :param page_size: The amount of customers to fetch at one time
    :return: Generator of student GUIDS
    """
    params = {
        'pageNum': 1,
        'pageSize': page_size
    }
    try:
        page = requests.get(SEARCH.format(site=site), params=params).json()
    except json.JSONDecodeError:
        raise EnvironmentError('Site name incorrect should be in format: cn-state-location, got: {}'.format(site))
    print(page)
    total_records = int(page['recordCount'])
    pages = int((total_records/page_size)) + 1

    for page_number in range(pages):
        page_number += 1  # Offset fo query purposes
        params['pageNum'] = page_number
        page = requests.get(SEARCH.format(site=site), params=params).json()
        for customer in page['customers']:
            customer_id = customer['guid']
            for member in customer['members']:
                guid = member.get('guid')
                if not guid:
                    print(member)
                yield guid, customer_id

def sync_ninjas(site_name):
    """  
    Gets the current belt information for all the ninjas in the dojo
    :param site_name: The string for your site id. i.e. cn-ma-wellesley
    :return: List of ninja dictionaries
    """
    ninjas = fetch_students(site_name)
    active_ninjas = 0
    for ninja_id, customer_id in ninjas:
        ninja = get_ninja_info(ninja_id, customer_id, site_name)
        if ninja:
            active_ninjas += 1
            yield ninja
    print(f"Created or updated {active_ninjas} licenses")

def get_ninja_info(guid, customer_id, site_name):
    """
    Pull the needed Student information from the dojo.  This can be expanded
    but right now we are just getting the most current drop in program
    """

    detail = requests.get(
        GENERAL_STUDENT_DETAIL.format(
            site=site_name, customer_id=customer_id, student_id=guid
        )
    ).json()
    overview = requests.get(
        STUDENT_OVERVIEW.format(site=site_name, student_id=guid)
    ).json()
    ninja = ninja_from_license(guid, site_name)
    if ninja:
        birthday = detail["dateOfBirth"]
        try:
            last_login = overview["currentBelt"]["lastVisitDate"]
            ninja["last_login"] = dateutil.parser.parse(last_login)
        except KeyError:
            name = ninja["name"]
            print(f"Ninja {name} has never scanned in")
        ninja["birthday"] = birthday
        return ninja

def ninja_from_license(guid, site_name):
    ninja = {}
    licenses = requests.get(
        STUDENT_LICENSE.format(site=site_name, student_id=guid)
    ).json()
    for program in licenses:
        # Filter out any ninjas that have not be enrolled in the program
        if (
            program["programName"] in ["Drop-in Learning", "Code Ninjas CREATE"]
            and program["isActive"]
        ):
            belt_info = requests.get(
                STUDENT_OVERVIEW.format(site=site_name, student_id=guid)
            ).json()
            ninja["fzid"] = guid
            ninja["name"] = "{} {}".format(
                program["firstName"], program["lastName"]
            )
            ninja["active"] = program["isActive"]
            ninja["frozen"] = program["isFrozen"]
            ninja["current_lesson_plan"] = belt_info["currentBelt"]["beltName"]
            ninja["roles"] = ["ninja"]
            ninja["username"] = program["username"]

            return ninja
    if not ninja:
        print(f"NO ACTIVE DROP IN LICENSES FOR {guid}")

def get_ninja_usage(guid, site_name):
    """
    Get the weekly usage data for a student in the last 6 months
    :param guid: the global unique id (hash) for query student data
    :param site_name: The string for your site id. i.e. cn-ma-wellesley
    :return:
    """
    date = datetime.datetime.now()
    usage = []
    for i in range(6):
        str_date = datetime.datetime.strftime(date, "%m-%d-%Y")
        monthly_usage = requests.get(
            STUDENT_USAGE.format(site=site_name, student_id=guid),
            params={"selectedDate": str_date},
        ).json()
        usage.extend(monthly_usage["weeks"])
        date = date - dateutil.relativedelta.relativedelta(months=1)
    usage = clean_usage(usage)

    return usage

def clean_usage(usage):
    """
    Remove Duplicate weeks based on the start day of the week
    :param usage:
    :return:
    """
    return list({week["days"][0]["dayDate"]: week for week in usage}.values())

def get_scan_ins(site_name):
    resp = requests.get(STUDENT_SCAN_INS.format(site=site_name))
    if resp.status_code < 202:
        return resp.json()["scanIns"]
    if resp.status_code == 403:
        raise HTTPError(
            SEARCH.format(site=site_name),
            code=403,
            msg="Invalid or expired creds",
            hdrs="",
            fp="",
        )
    return []
