from django.test import RequestFactory
from django.utils import timezone

from tally_ho.libs.permissions import groups
from tally_ho.apps.tally.views.reports import staff_performance_metrics
from tally_ho.apps.tally.templatetags.app_filters import\
    forms_processed_per_hour
from tally_ho.libs.models.enums.form_state import FormState
from tally_ho.libs.tests.test_base import create_result_form,\
    create_result_form_stats, create_tally, TestBase


class TestStaffPerformanceMetrics(TestBase):
    def setUp(self):
        self.factory = RequestFactory()
        self._create_permission_groups()
        self._create_and_login_user()
        self._add_user_to_group(self.user, groups.TALLY_MANAGER)

    def test_staff_perfomance_metrics_get(self):
        tally = create_tally()
        tally.users.add(self.user)

        result_form =\
            create_result_form(
                name="Example",
                tally=tally,
                form_state=FormState.AUDIT)
        start_time = timezone.now()
        minutes = 65.5
        end_time = start_time + timezone.timedelta(minutes=minutes)

        form_processing_time_in_seconds =\
            (end_time - start_time).total_seconds()

        create_result_form_stats(
            processing_time=form_processing_time_in_seconds,
            user=self.user,
            result_form=result_form,
            approved_by_supervisor=True
        )

        request = self._get_request()
        view = staff_performance_metrics.StaffPerformanceMetricsView.as_view()
        request = self.factory.get('/')
        request.user = self.user
        response = view(
            request,
            tally_id=tally.pk,
            group_name=groups.TALLY_MANAGER)

        total_forms_processed = 1
        processed_forms_per_hour =\
            forms_processed_per_hour(
                total_forms_processed,
                form_processing_time_in_seconds)

        self.assertContains(
            response,
            f'{groups.TALLY_MANAGER}s Performance Report')
        self.assertContains(response, "<th>Staff Name</th>")
        self.assertContains(response, "<th>Forms Processed Per Hour</th>")
        self.assertContains(response, f'<td>{self.user.username}</td>')
        self.assertContains(response, f'<td>{processed_forms_per_hour}</td>')

    def test_surpervisors_approvals_get(self):
        tally = create_tally()
        tally.users.add(self.user)

        result_form =\
            create_result_form(
                name="Example",
                tally=tally,
                form_state=FormState.AUDIT)
        start_time = timezone.now()
        minutes = 65.5
        end_time = start_time + timezone.timedelta(minutes=minutes)

        form_processing_time_in_seconds =\
            (end_time - start_time).total_seconds()

        # Audit supervisor audit review
        audit_supervisor_user =\
            self._create_user('audit_supervisor', 'password')
        self._add_user_to_group(audit_supervisor_user,
                                groups.AUDIT_SUPERVISOR)
        create_result_form_stats(
            processing_time=form_processing_time_in_seconds,
            user=audit_supervisor_user,
            result_form=result_form,
            reviewed_by_supervisor=True,
            approved_by_supervisor=True
        )

        request = self._get_request()
        view = staff_performance_metrics.SupervisorsApprovalsView.as_view()
        request = self.factory.get('/')
        request.user = self.user
        response = view(request, tally_id=tally.pk,)

        self.assertContains(
            response,
            "<h1>Supervisors Approvals Rate Report</h1>")
        self.assertContains(
            response,
            "<h3>Audit Supervisors Approval Rate</h3>")
        self.assertContains(
            response,
            "<h3>Tally Managers Approval Rate</h3>")
        self.assertContains(response, "<th>Number of Approved Forms</th>")
        self.assertContains(
            response,
            "<th>Number of Forms Sent For Review</th>")
        self.assertContains(
            response,
            "<th>Approval Rate</th>")
        self.assertContains(response, f'<td>1</td>')
        self.assertContains(response, f'<td>100.0%</td>')