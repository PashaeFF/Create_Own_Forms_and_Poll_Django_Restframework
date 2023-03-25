from django.db import models
from django.utils.timezone import now
from auth2.models import User


class Pull(models.Model):
    owner_id = models.ForeignKey(User, verbose_name="owner_id", on_delete=models.CASCADE)
    pull_name = models.CharField(max_length=250, unique=True)
    answers = models.JSONField(default=dict)
    anonimouse = models.BooleanField(default=False)
    more_answers = models.BooleanField(default=False)
    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=now)

    class Meta:
        db_table = "pull"

    def __str__(self):
        return f'Pull Name: {self.pull_name}'

