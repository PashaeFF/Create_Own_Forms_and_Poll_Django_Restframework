from django.db import models
from django.utils.timezone import now
from auth2.models import User


class Poll(models.Model):
    owner_id = models.ForeignKey(User, verbose_name="owner_id", on_delete=models.CASCADE)
    poll_name = models.CharField(max_length=250, unique=True)
    answers = models.JSONField(default=dict)
    anonimouse = models.BooleanField(default=False)
    more_answers = models.BooleanField(default=False)
    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=now)

    class Meta:
        db_table = "poll"

    def __str__(self):
        return f'Poll Name: {self.poll_name}'


class PollAnswers(models.Model):
    person_id = models.ForeignKey(User, verbose_name="user_id", on_delete=models.CASCADE)
    poll_id = models.ForeignKey(Poll, verbose_name="poll", on_delete=models.CASCADE)
    answers = models.JSONField(default=dict)
    counter = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=now)

    class Meta:
        db_table = "poll_answers"
    
    def __str__(self):
        return f'Answer: {self.answers}'
