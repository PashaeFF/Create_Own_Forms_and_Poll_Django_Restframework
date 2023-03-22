from django.db import models
from django.utils.timezone import now
from auth2.models import User


class Form(models.Model):
    owner_id = models.ForeignKey(User, verbose_name="owner_id", on_delete=models.CASCADE)
    url = models.CharField(max_length=500)
    form_name = models.CharField(max_length=250, unique=True)
    values = models.JSONField(default=dict)
    forms_count = models.IntegerField(default=0)
    image = models.ImageField(null=True, upload_to='media/images/')
    created_at = models.DateTimeField(default=now)

    class Meta:
        db_table = "own_forms"

    def __str__(self):
        return f'Email: {self.email} \nURL: {self.url} \nFullname: {self.fullname} \nForm name: {self.form_name} \nForm values: {self.values}'


class FilledForms(models.Model):
    person_id = models.ForeignKey(User, verbose_name="user_id", on_delete=models.CASCADE)
    filled_form = models.JSONField(default=dict)
    form_id = models.ForeignKey(Form, default=1, verbose_name="own_forms", on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=now)
    counter = models.IntegerField(default=0)

    class Meta:
        db_table = "filled_forms"

    def __str__(self):
        return f'Form id: {self.form_id} \nForm: {self.filled_form}'