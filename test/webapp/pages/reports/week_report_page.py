from pages.base_app_page import BaseAppPage
from pages.base_page import testid_locator


class WeekReportPage(BaseAppPage):
    # Navigation
    prev_week_button_locator = testid_locator("prev-week-button")
    next_week_button_locator = testid_locator("next-week-button")
    save_report_button_locator = testid_locator("save-report-button")

    # Planning section fields
    weekly_goals_locator = testid_locator("field-weekly-goals")
    goals_rationale_locator = testid_locator("field-goals-rationale")
    start_notes_locator = testid_locator("field-start-notes")

    # Review section fields
    goals_achieved_rating_locator = testid_locator("field-goals-achieved-rating")
    course_corrections_locator = testid_locator("field-course-corrections")
    end_notes_locator = testid_locator("field-end-notes")

    def __init__(self, driver, date=None):
        super().__init__(driver)
        if date:
            self._visit(f"/reports/week/{date}")
        else:
            self._visit("/reports/week")

    def navigate_to_previous_week(self):
        self._click(self.prev_week_button_locator)

    def navigate_to_next_week(self):
        self._click(self.next_week_button_locator)

    def fill_report(self, report_data):
        """
        Fill the weekly report form with provided data.

        Args:
            report_data (dict): Dictionary containing field names and values
        """
        field_mapping = {
            'weekly_goals': self.weekly_goals_locator,
            'goals_rationale': self.goals_rationale_locator,
            'start_notes': self.start_notes_locator,
            'goals_achieved_rating': self.goals_achieved_rating_locator,
            'course_corrections': self.course_corrections_locator,
            'end_notes': self.end_notes_locator
        }

        for field_name, value in report_data.items():
            if field_name in field_mapping and value is not None:
                self._type(field_mapping[field_name], str(value))

    def save_report(self):
        """Save the report"""
        self._click(self.save_report_button_locator)