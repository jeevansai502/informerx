from django.db import models
from django.contrib.sessions.models import Session
from django.conf import settings

# Create your models here.
class User_Login_Details(models.Model):
    email = models.CharField(max_length=256,primary_key=True)
    password = models.CharField(max_length=30)
   
class User_Details(models.Model):
    email = models.CharField(max_length=256,primary_key=True)
    username = models.CharField(max_length=30)
    mobile = models.CharField(max_length=20)

class User_Groups(models.Model):
    email = models.CharField(max_length=256)
    groupname = models.CharField(max_length=256)

class Email_History(models.Model):
    groupname = models.CharField(max_length=256)
    communication_type = models.CharField(max_length=256)
    incident_number = models.CharField(max_length=256)
    priority = models.CharField(max_length=256)
    region = models.CharField(max_length=256)
    status = models.CharField(max_length=256)
    incident_opened_date = models.CharField(max_length=256)
    incident_opened_time = models.CharField(max_length=256)
    incident_duration_days = models.CharField(max_length=256)
    incident_duration_hr = models.CharField(max_length=256)
    incident_duration_min = models.CharField(max_length=256)
    what_happened = models.CharField(max_length=256)
    business_impact = models.CharField(max_length=256)
    service_impact = models.CharField(max_length=256)
    key_groups_and_people_involved = models.CharField(max_length=256)
    what_we_discovered = models.CharField(max_length=256)
    what_finally_fixed_the_issue = models.CharField(max_length=256)
    post_recovery_action_items = models.CharField(max_length=256)
    design_issues = models.CharField(max_length=256)
    chronology_of_the_incident = models.CharField(max_length=256)
    flagged_for_reliability = models.CharField(max_length=256)
    date_and_time_flagged_for_reliability_date = models.CharField(max_length=256)
    date_and_time_flagged_for_reliability_time = models.CharField(max_length=256)
    reliability_record_number = models.CharField(max_length=256)
    time_down_date = models.CharField(max_length=256)
    time_down_time = models.CharField(max_length=256)
    date_and_time_issue_resolved_date = models.CharField(max_length=256)
    date_and_time_issue_resolved_time= models.CharField(max_length=256)
    did_we_receive_an_alert = models.CharField(max_length=256)
    date_and_time_alert_received_date = models.CharField(max_length=256)
    date_and_time_alert_received_time = models.CharField(max_length=256)
	  

class Message_History(models.Model):
    groupname = models.CharField(max_length=256)
    message = models.CharField(max_length=256)

class Call_History(models.Model):
    groupname = models.CharField(max_length=256)
    message = models.CharField(max_length=256)

class UserSession(models.Model):
    time = models.DateTimeField(primary_key=True)
    username = models.CharField(max_length=256)
    session = models.ForeignKey(Session,on_delete=models.CASCADE)

