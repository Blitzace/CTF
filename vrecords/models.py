from django.db import models

# Create your models here.
from django.db import models

IMP_CHOICES = (
    ('1', 'Eligible'),
    ('2', 'Ineligible'),
)

VOTE_CHOICES = (
    ('1', 'Yes'),
    ('2', 'No'),
)
class Voter(models.Model):
    SSN = models.CharField(max_length=200)
    Name = models.CharField(max_length=200)
    add_date = models.DateTimeField('date added')
    status = models.CharField(max_length=10, choices=IMP_CHOICES)
    def get_ssn(self):
        return self.SSN
    def get_name(self):
        return self.Name
    def get_status(self):
        return self.status

class Choice(models.Model):
    US = models.CharField(max_length=200)
    votes = models.CharField(max_length=10, choices=VOTE_CHOICES)
    def get_us(self):
        return self.US
    def get_vote(self):
        return self.votes