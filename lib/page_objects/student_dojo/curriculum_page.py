import time


class CurriculumPage:
    """
    Page to get all the link information for the current belts.
    """

    def __init__(self, page):
        self.page = page
        self.wait_for_loaded()

    def belt_paths(self):
        popups = []
        for i in range(1, 6):
            popups.append(self.page.html.find(f"#belt{i}", first=True))
        return popups

    @property
    def available_belt_links(self):
        print(self.belt_paths())
        return [self.belt_link(belt) for belt in self.belt_paths()]

    def belt_link(self, element):
        selector = "div > div > div > div.col-md-7 > p:nth-child(2) > a"
        belt_anchor = element.find(selector, first=True)
        return belt_anchor.attrs["href"]

    def wait_for_loaded(self):
        time.sleep(3)
