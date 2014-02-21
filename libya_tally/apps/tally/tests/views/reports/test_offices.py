from django.test import RequestFactory

from libya_tally.apps.tally.views.reports import offices
from libya_tally.libs.permissions import groups
from libya_tally.libs.tests.test_base import create_center, \
    create_ballot, create_result_form, TestBase


class TestOffices(TestBase):
    def setUp(self):
        self.factory = RequestFactory()
        self._create_permission_groups()
        self._create_and_login_user()
        self._add_user_to_group(self.user, groups.SUPER_ADMINISTRATOR)

    def test_overview_report_get(self):
        for i in xrange(1, 11):
            center = create_center()
            ballot = create_ballot()
            create_result_form(
                center=center, ballot=ballot,
                station_number=i,
                barcode=i, serial_number=i, form_state=i - 1)

        request = self._get_request()
        view = offices.OfficesReportView.as_view()
        request = self.factory.get('/')
        request.user = self.user
        request.session = {}
        response = view(request)

        self.assertContains(response, 'Per Office')
        self.assertContains(response, 'Tally Centre Progress Report')
        self.assertContains(response, "<td>8</td>")
        self.assertContains(response, "<td>80.0%</td>")
        self.assertContains(response, "<td>Not Received</td>")
