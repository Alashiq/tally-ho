from django.db import models

from libya_tally.libs.models.base_model import BaseModel
from libya_tally.libs.models.enum.form_state import FormState
from libya_tally.libs.models.enum.form_type import FormType


class ResultForm(BaseModel):
    race1 = models.ForeignKey('Race')
    race2 = models.ForeignKey('Race')
    station = models.ForeignKey('Station')

    barcode = models.PositiveIntegerField()
    ballot_number = models.PositiveIntegerField()
    form_type = models.EnumField(FormType)
    number_of_races = models.PositiveSmallIntegerField()
    form_state = models.EnumField(FormState)
