STARS_EARNED_COL = 5
DETAILS_COL = 6


class GradingPage:
    """
    The Grading Page is a page object representation of the grading page in the dojo.
    This means that you can access the elements of the GDP as if you were accessing the
    properties of a class.
    """

    def __init__(self, page):
        self.page = page
        self.validate_login()

    def validate_login(self):
        login_selector = "div.container-fluid:nth-child(2) > h2:nth-child(1)"
        if (
            self.page.html.find(login_selector, first=True)
            or self.page.url == "https://gdp.code.ninja/Account/Login"
        ):
            raise EnvironmentError("Browser Not Authenticated")

    @property
    def page_count(self):
        pagination_selector = (
            "body > div.body-content > div:nth-child(2) > div:nth-child(2) > ul"
        )
        pagination = self.page.html.find(pagination_selector, first=True)
        page_count = len(pagination.find("a"))
        return page_count

    @property
    def table(self):
        table_selector = "/html/body/div[2]/div[2]/div[3]/table"
        table = self.page.html.xpath(table_selector, first=True)
        return table

    @property
    def table_headers(self):
        headers_selector = "thead > tr > th"
        headers_html = self.table.find(headers_selector)
        return [
            header.text if header.text else "Play and Grade" for header in headers_html
        ]

    def _row_data(self, row_html):
        td_tags = row_html.find("td")
        row_data = []
        for i, td in enumerate(td_tags):
            if i == STARS_EARNED_COL:
                row_data.append(self._handle_star_td(td))
            elif i == DETAILS_COL:
                row_data.append(self._get_details_link(td))
            else:
                row_data.append(td.text)
        return row_data

    def _handle_star_td(self, td):
        if td.text == "Not Graded":
            return td.text
        else:
            star_selector = "div > span > i.fa-star"
            earned_stars = td.find(star_selector)
            return str(len(earned_stars))

    def _get_details_link(self, td):
        anchor = td.find("a", first=True)
        return anchor.attrs["href"]

    @property
    def grading_rows(self):
        row_selectors = "tbody > tr"
        rows = self.table.find(row_selectors)
        return [self._row_data(row_html) for row_html in rows]

    @property
    def grades(self):
        return [dict(zip(self.table_headers, row)) for row in self.grading_rows]
