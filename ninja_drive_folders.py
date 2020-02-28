import argparse
import os
import shutil

from lib.dojo_requests import DojoRequests
from lib.page_objects.admin_dojo.location import AdminDojoAPI

ACTIVE_NINJA_DIR = r'\\raspberrypi\DojoStorage\Ninjas'
ARCHIVED_NINJA_DIR = r'\\raspberrypi\DojoStorage\.archived'


def get_ninjas(site):
    requests = DojoRequests()

    ln_scanner = AdminDojoAPI(requests)
    users = ln_scanner.sync_ninjas(site)
    for user in users:
        if user.get('username'):
            active_folder_name = os.path.join(
                ACTIVE_NINJA_DIR, user.get('username'))
            archived_folder_name = os.path.join(
                ARCHIVED_NINJA_DIR, user.get('username'))
            is_active_folder = os.path.isdir(active_folder_name)
            if user.get('active'):
                if not is_active_folder:
                    is_inactive_folder = os.path.isdir(archived_folder_name)
                    if is_inactive_folder:
                        shutil.move(archived_folder_name, active_folder_name)
                    else:
                        os.mkdir(active_folder_name)
            else:
                if is_active_folder:
                    shutil.move(active_folder_name, archived_folder_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default=None)

    args = parser.parse_args()

    get_ninjas(args.site)
