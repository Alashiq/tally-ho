from collections import OrderedDict
import csv

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy

from libya_tally.apps.tally.models.ballot import Ballot
from libya_tally.libs.models.enums.entry_version import EntryVersion
from libya_tally.libs.models.enums.form_state import FormState

OUTPUT_PATH = 'results/candidate_votes.csv'


def distinct_forms(ballot):
    return ballot.resultform_set.filter(center__isnull=False).distinct(
        'center__id', 'station_number', 'ballot__id')


def get_votes(candidate):
    """Return the active results for this candidate that are for archived
    result forms."""
    results = candidate.results.filter(
        entry_version=EntryVersion.FINAL,
        active=True, result_form__form_state=FormState.ARCHIVED).all()

    return [len(results), sum([r.votes for r in results])]


class Command(BaseCommand):
    help = ugettext_lazy("Export candidate votes list.")

    def handle(self, *args, **kwargs):
        self.export_candidate_votes()

    def export_candidate_votes(self):
        header = ['ballot number',
                  'stations',
                  'stations completed',
                  'stations percent completed']

        max_candidates = 0
        for ballot in Ballot.objects.all():
            if ballot.candidates.count() > max_candidates:
                max_candidates = ballot.candidates.count()

        for i in xrange(1, max_candidates + 1):
            header.append('candidate %s name' % i)
            header.append('candidate %s votes' % i)

        with open(OUTPUT_PATH, 'wb') as f:
            # BOM, Excel needs it to open UTF-8 file properly
            f.write(u'\ufeff'.encode('utf8'))
            w = csv.DictWriter(f, header)
            w.writeheader()

            for ballot in Ballot.objects.all():
                forms = distinct_forms(ballot)

                if not forms:
                    forms = distinct_forms(
                        ballot.sc_component.all()[0].ballot_general)

                num_stations = forms.count()
                num_stations_completed = forms.filter(
                    form_state=FormState.ARCHIVED).count()

                percent_complete = round(
                    100 * num_stations_completed / num_stations, 3)

                output = OrderedDict({
                    'ballot number': ballot.number,
                    'stations': num_stations,
                    'stations completed': num_stations_completed,
                    'stations percent completed': percent_complete})

                num_results_ary = []
                candidates_to_votes = {}

                for candidate in ballot.candidates.all():
                    num_results, votes = get_votes(candidate)
                    candidates_to_votes[candidate.full_name] = votes
                    num_results_ary.append(num_results)

                assert len(set(num_results_ary)) <= 1

                for num_results in num_results_ary:
                    assert num_stations_completed == num_results

                candidates_to_votes = OrderedDict((sorted(
                    candidates_to_votes.items(), key=lambda t: t[1],
                    reverse=True)))

                for i, item in enumerate(candidates_to_votes.items()):
                    candidate, votes = item

                    output['candidate %s name' % (i + 1)] = candidate
                    output['candidate %s votes' % (i + 1)] = votes

                w.writerow({k: v.encode('utf8') if isinstance(v, basestring)
                            else v for k, v in output.items()})