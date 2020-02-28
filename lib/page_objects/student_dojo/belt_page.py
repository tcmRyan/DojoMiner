import time


class NinjaBeltPage:
    """
    The page containing all the lessons for the belt.  This is intended for 
    us to be able to bring in belt changes that get pushed so that there
    is no manual updates
    """

    def __init__(self, page):
        self.page = page
        self.wait_for_loaded()

    @property
    def belt_name(self):
        selector = "body > div.body-content > div:nth-child(2) > div.row.header-row.full-screen.clearfix > div.col-md-3.bg-blue.text-nowrap > h2"
        title = self.page.html.find(selector, first=True)
        return title.text

    @property
    def lessons(self):
        selector = "#scenes > li"
        lesson_header_selector = (
            "div > div.col-md-10.bg-dark-orange.text-nowrap.padding-top-1 > h3"
        )
        lesson_elements = self.page.html.find(selector)
        lessons = [
            lesson.find(lesson_header_selector, first=True).text
            for lesson in lesson_elements
        ]
        return lessons

    @property
    def description(self):
        selector = "body > div.body-content > div:nth-child(2) > div.row.margin-top-3.padding-left-3.padding-right-3 > div.col-md-3.padding-left-0 > div.margin-top-10.text-justify > h5"
        return self.page.html.find(selector, first=True).text

    def wait_for_loaded(self):
        """
        Overly simple syncronization technique, TODO: use more sophisticated
        methods when appropriate
        """
        time.sleep(3)

    @property
    def belt_id(self):
        url = self.page.url
        return url.split("/")[-1]
