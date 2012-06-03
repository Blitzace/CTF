from vrecords.models import Voter, Choice
from django.contrib import admin

class VoterAdmin(admin.ModelAdmin):
    list_display = ('id', 'SSN', 'Name', 'status')

class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('US', 'votes')

admin.site.register(Voter, VoterAdmin)
admin.site.register(Choice, ChoiceAdmin)