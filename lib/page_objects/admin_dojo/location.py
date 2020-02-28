import json
import datetime
import dateutil.relativedelta
import dateutil.parser
from urllib.error import HTTPError

STUDENT_OVERVIEW = "https://dojo.code.ninja/api/customerdetailsstudent/{site}/studentoverview/{student_id}"
STUDENT_LICENSE = "https://dojo.code.ninja/api/customerdetailsstudent/{site}/studentLicenses/{student_id}"
STUDENT_USAGE = "https://dojo.code.ninja/api/customerdetailsstudent/{site}/studentusage/{student_id}"
STUDENT_SCAN_INS = "https://dojo.code.ninja/api/employee/{site}/scanins/300"
SEARCH = "https://dojo.code.ninja/api/employee/{site}/search/"
GENERAL_STUDENT_DETAIL = "https://dojo.code.ninja/api/customerdetailsgeneral/{site}/{customer_id}/student/{student_id}"


class AdminDojoAPI:
    """
    Utility to interact with the dojo REST API.
    """

    def __init__(self, requests):
        self.requests = requests

    def fetch_students(self, site, page_size=25):
        """
        Iterate through the customer data to create a iterable generator of student guids
        :param site: The string for your site id. i.e. cn-ma-wellesley
        :param page_size: The amount of customers to fetch at one time
        :return :Iterable of student GUIDS, customer_ids
        """
        params = {"pageNum": 1, "pageSize": page_size}
        resp = self.requests.get(SEARCH.format(site=site), params=params)
        if resp.status_code == 403:
            raise HTTPError(
                SEARCH.format(site=site),
                code=403,
                msg="Invalid or expired creds",
                hdrs="",
                fp="",
            )
        try:
            page = resp.json()
        except json.JSONDecodeError:
            raise EnvironmentError(
                "Site name incorrect should be in format: cn-state-location, got: {}".format(
                    site
                )
            )

        total_records = int(page["recordCount"])
        pages = int((total_records / page_size)) + 1

        for page_number in range(pages):
            page_number += 1  # Offset fo query purposes
            params["pageNum"] = page_number
            page = self.requests.get(SEARCH.format(
                site=site), params=params).json()
            for customer in page["customers"]:
                customer_id = customer["guid"]
                for member in customer["members"]:
                    guid = member.get("guid")
                    if not guid:
                        print(member)
                    yield guid, customer_id

    def sync_ninjas(self, site_name):
        """  
        Gets the current belt information for all the ninjas in the dojo
        :param site_name: The string for your site id. i.e. cn-ma-wellesley
        :return: List of ninja dictionaries
        """
        ninjas = self.fetch_students(site_name)
        active_ninjas = 0
        for ninja_id, customer_id in ninjas:
            ninja = self.get_ninja_info(ninja_id, customer_id, site_name)
            if ninja:
                active_ninjas += 1
                yield ninja
        print(f"Created or updated {active_ninjas} licenses")

    def get_ninja_info(self, guid, customer_id, site_name):
        """
        Pull the needed Student information from the dojo.  This can be expanded
        but right now we are just getting the most current drop in program
        """

        detail = self.requests.get(
            GENERAL_STUDENT_DETAIL.format(
                site=site_name, customer_id=customer_id, student_id=guid
            )
        ).json()
        overview = self.requests.get(
            STUDENT_OVERVIEW.format(site=site_name, student_id=guid)
        ).json()
        ninja = self.ninja_from_license(guid, site_name)
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

    def ninja_from_license(self, guid, site_name):
        ninja = {}
        licenses = self.requests.get(
            STUDENT_LICENSE.format(site=site_name, student_id=guid)
        ).json()
        for program in licenses:
            # Filter out any ninjas that have not be enrolled in the program
            if (
                program["programName"] in [
                    "Drop-in Learning", "Code Ninjas CREATE"]
                and program["isActive"]
            ):
                belt_info = self.requests.get(
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

    def get_ninja_usage(self, guid, site_name):
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
            monthly_usage = self.requests.get(
                STUDENT_USAGE.format(site=site_name, student_id=guid),
                params={"selectedDate": str_date},
            ).json()
            usage.extend(monthly_usage["weeks"])
            date = date - dateutil.relativedelta.relativedelta(months=1)
        usage = self.clean_usage(usage)

        return usage

    @staticmethod
    def clean_usage(usage):
        """
        Remove Duplicate weeks based on the start day of the week
        :param usage:
        :return:
        """
        return list({week["days"][0]["dayDate"]: week for week in usage}.values())

    def get_scan_ins(self, site_name):
        resp = self.requests.get(STUDENT_SCAN_INS.format(site=site_name))
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
