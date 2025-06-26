from pages.base_app_page import BaseAppPage
from pages.base_page import testid_locator


class DayReportPage(BaseAppPage):
    # Navigation
    prev_day_button_locator = testid_locator("prev-day-button")
    next_day_button_locator = testid_locator("next-day-button")
    save_report_button_locator = testid_locator("save-report-button")

    # Form fields
    morning_notes_locator = testid_locator("field-morning-notes")
    daily_plans_locator = testid_locator("field-daily-plans")
    sleep_hours_locator = testid_locator("field-sleep-hours")
    prayer_rating_locator = testid_locator("field-prayer-rating")
    diet_adherence_locator = testid_locator("field-diet-adherence")
    drug_rating_locator = testid_locator("field-drug-rating")
    dyel_locator = testid_locator("field-dyel")
    workout_rpe_locator = testid_locator("field-workout-rpe")
    exercise_notes_locator = testid_locator("field-exercise-notes")
    work_adherence_locator = testid_locator("field-work-adherence")
    work_rpe_locator = testid_locator("field-work-rpe")
    cleaning_adherence_locator = testid_locator("field-cleaning-adherence")
    job_hunt_rpe_locator = testid_locator("field-job-hunt-rpe")
    job_hunt_notes_locator = testid_locator("field-job-hunt-notes")
    gains_locator = testid_locator("field-gains")
    gains_rating_locator = testid_locator("field-gains-rating")
    gratitudes_locator = testid_locator("field-gratitudes")
    notes_locator = testid_locator("field-notes")

    def __init__(self, driver, date=None):
        super().__init__(driver)
        if date:
            self._visit(f"/reports/day/{date}")
        else:
            self._visit("/reports/day")

    def navigate_to_previous_day(self):
        self._click(self.prev_day_button_locator)

    def navigate_to_next_day(self):
        self._click(self.next_day_button_locator)

    def fill_report(self, report_data):
        """
        Fill the report form with provided data.

        Args:
            report_data (dict): Dictionary containing field names and values
        """
        field_mapping = {
            'morning_notes': self.morning_notes_locator,
            'daily_plans': self.daily_plans_locator,
            'sleep_hours': self.sleep_hours_locator,
            'prayer_rating': self.prayer_rating_locator,
            'diet_adherence': self.diet_adherence_locator,
            'drug_rating': self.drug_rating_locator,
            'dyel': self.dyel_locator,
            'workout_rpe': self.workout_rpe_locator,
            'exercise_notes': self.exercise_notes_locator,
            'work_adherence': self.work_adherence_locator,
            'work_rpe': self.work_rpe_locator,
            'cleaning_adherence': self.cleaning_adherence_locator,
            'job_hunt_rpe': self.job_hunt_rpe_locator,
            'job_hunt_notes': self.job_hunt_notes_locator,
            'gains': self.gains_locator,
            'gains_rating': self.gains_rating_locator,
            'gratitudes': self.gratitudes_locator,
            'notes': self.notes_locator
        }

        for field_name, value in report_data.items():
            if field_name in field_mapping and value is not None:
                self._type(field_mapping[field_name], str(value))

    def save_report(self):
        """Save the report and wait for success"""
        self._click(self.save_report_button_locator)