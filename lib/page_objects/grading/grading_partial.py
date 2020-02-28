class GradingPartial:
    """
    Turns the grading partial, containing the detail information about grading in
    the dojo into a page object
    """

    def __init__(self, page):
        self.page = page

    @property
    def table(self):
        return self.page.html.find(".table", first=True)

    @property
    def student_name(self):
        selector = "tr:nth-child(1) > td:nth-child(2)"
        return self.table.find(selector, first=True).text

    @property
    def completed(self):
        selector = "tr:nth-child(3) > td:nth-child(2) > span"
        return self.table.find(selector, first=True).attrs.get("data-date")

    @property
    def graded(self):
        selector = "tr:nth-child(4) > td:nth-child(2) > span"
        return self.table.find(selector, first=True).attrs.get("data-date")

    @property
    def game_url(self):
        btn = self.page.html.find(".btn.btn-default", first=True)
        if not btn:
            print("Student has not shared url")
            return None
        return btn.attrs.get("href")

    @property
    def grader(self):
        selector = "tr:nth-child(5) > td:nth-child(2)"
        return self.table.find(selector, first=True).text

    @property
    def grade_form_action(self):
        return self.page.html.find("#grade-form", first=True).attrs.get("action")

    @property
    def user_trek_scene_id(self):
        selector = "#UserTrekSceneId"
        return self.page.html.find(selector, first=True).attrs.get("value")
