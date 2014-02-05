from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import TemplateView

from libya_tally.apps.tally.models.result_form import ResultForm
from libya_tally.apps.tally.models.station import Station
from libya_tally.libs.models.enums.form_state import FormState
from libya_tally.libs.permissions import groups
from libya_tally.libs.views import mixins


class DashboardView(mixins.GroupRequiredMixin, TemplateView):
    group_required = groups.SUPER_ADMINISTRATOR
    template_name = "tally/super_admin/home.html"

    def get(self, *args, **kwargs):
        return self.render_to_response(self.get_context_data())


class CenterListView(mixins.GroupRequiredMixin, TemplateView):
    group_required = groups.SUPER_ADMINISTRATOR
    template_name = "tally/super_admin/centers.html"

    def get(self, *args, **kwargs):
        station_list = Station.objects.all()
        paginator = Paginator(station_list, 100)
        page = self.request.GET.get('page')

        try:
            stations = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            stations = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page.
            stations = paginator.page(paginator.num_pages)

        return self.render_to_response(self.get_context_data(
            stations=stations))


class FormListView(mixins.GroupRequiredMixin, TemplateView):
    group_required = groups.SUPER_ADMINISTRATOR
    template_name = "tally/super_admin/forms.html"

    def get(self, *args, **kwargs):
        form_list = ResultForm.objects.all()
        paginator = Paginator(form_list, 100)
        page = self.request.GET.get('page')

        try:
            forms = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            forms = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page.
            forms = paginator.page(paginator.num_pages)

        return self.render_to_response(self.get_context_data(
            forms=forms))


class FormProgressView(mixins.GroupRequiredMixin, TemplateView):
    group_required = groups.SUPER_ADMINISTRATOR
    template_name = "tally/super_admin/form_progress.html"

    def get(self, *args, **kwargs):
        form_list = ResultForm.objects.exclude(
            form_state=FormState.UNSUBMITTED)
        paginator = Paginator(form_list, 100)
        page = self.request.GET.get('page')

        try:
            forms = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            forms = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page.
            forms = paginator.page(paginator.num_pages)

        return self.render_to_response(self.get_context_data(
            forms=forms))