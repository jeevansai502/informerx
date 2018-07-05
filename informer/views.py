from django.shortcuts import render
from django.views.generic import TemplateView
import os.path
import json
from django.db import connection
import hashlib
from django.utils import timezone
from django.contrib.auth.signals import user_logged_in
from django.http import HttpResponseRedirect
from django.core.mail import EmailMessage
from django.http import JsonResponse
import json
import urllib.request
import urllib.parse
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os
from informer.models import UserSession
import time
import base64
import urllib
import http.client
import re

# Create your views here.
class IndexPageView(TemplateView):
	def get(self,request):
		return render(request, 'index.html',context=None)

class LoginPageView(TemplateView):

	def get(self,request):
		return render(request, 'login.html',context=None)

	def post(self,request):
		email = request.POST["email"]
		password = request.POST["password"]

		def user_logged_in_handler():
			UserSession.objects.get_or_create( time = timezone.now() , username = email , session_id = request.session.session_key)

		try:
			with connection.cursor() as cursor:
				original = cursor.execute("SELECT password FROM informer_user_login_details WHERE email=%s",(email,))
				corr = original.fetchone()
				
				if corr == None:
					ln = {}
					ln["result"] = "Wrong credentials"
					return render(request, 'login.html',ln)
				
				hash_pass = hashlib.md5(password.encode())
				password = hash_pass.hexdigest()
				if corr[0] == password:

					if not request.session.session_key:
						request.session.save()

					user_logged_in_handler()
					#user_logged_in.connect(user_logged_in_handler)
					return HttpResponseRedirect("/dashboard/")
				else:
					ln = {}
					ln["result"] = "Wrong credentials"
					return render(request, 'login.html',ln)
		except Exception as e:
			print (e)


class RegisterPageView(TemplateView):
	def get(self,request):
		return render(request, 'register.html',context=None)

	def post(self,request):
		username = request.POST["username"].strip()
		password = request.POST["password"].strip()
		email = request.POST["email"].strip()
		mobile = request.POST["mobile"].strip()
		
		reg = {}
		
		if username == "" or password == "" or email == "" or mobile == "":
			reg["result"] = "Please fill all details"
			return render(request, 'register.html',reg)

		hash_pass = hashlib.md5(password.encode())
		password = hash_pass.hexdigest()

		group = request.POST["group"]



		try:
			with connection.cursor() as cursor:
				cursor.execute("INSERT INTO informer_user_login_details(email,password) VALUES (%s,%s)",(email,password))
				cursor.execute("INSERT INTO informer_user_details(email,username,mobile,groupname) VALUES (%s,%s,%s,%s)",(email,username,mobile,group))

			reg["result"] = "Signup success"
			return render(request, 'login.html',reg)
		except Exception as e:
			reg["result"] = "Oops some error occured"
			return render(request, 'register.html',reg)

class LogoutPageView(TemplateView):  

	def get(self,request):
		def delete_user_sessions():
			sid = request.session.session_key
			user_sessions = UserSession.objects.filter(session_id = sid)
			for user_session in user_sessions:
				user_session.delete()
				continue

		delete_user_sessions()
		return HttpResponseRedirect("/login/")

class MainPageView(TemplateView):
	def get(self,request):

		try:
			user_sessions = UserSession.objects.filter(session_id = request.session.session_key)
		except:
			return render(request, 'login.html')

		if len(user_sessions) == 0:
			return render(request, 'login.html')
		else:
			with connection.cursor() as cursor:
				cursor.execute("SELECT DISTINCT groupname FROM informer_user_details ")
				groups = json.loads(json.dumps(cursor.fetchall()))

				cursor.execute("SELECT id,incident_number,region,status,incident_opened_date FROM informer_email_history ORDER BY id DESC LIMIT 10")
				rows = json.loads(json.dumps(cursor.fetchall()))

				ln = {}
				ln["groups"] = groups
				ln["show_email"] = rows
				ln["email_load_more"] = len(rows)

				cursor.execute("SELECT id,message FROM informer_message_history ORDER BY id DESC LIMIT 10")
				rows = json.loads(json.dumps(cursor.fetchall()))

				ln["show_message"] = rows
				ln["msg_load_more"] = len(rows)
				return	render(request, 'main.html',ln)

				






class EmailPageView(TemplateView):  
	def post(self,request):
		data = []

		d = {}
		
		group = request.POST["hidden_group_email"]
		li = [group]
		
		data.append( ["Communication type: " , request.POST["communication_type"] ,1 , 5 ] )
		li.append(request.POST["communication_type"])
		data.append( ["Incident number: " , request.POST["incident_number"] ,1 ,2 ] )
		li.append(request.POST["incident_number"])
		data.append( ["Priority: " , request.POST["priority"] ,1 ,2] )
		li.append(request.POST["priority"])
		data.append( ["Region: " , request.POST["region"] ,1,2])	
		li.append(request.POST["region"])	
		data.append( ["Status: " , request.POST["status"] ,1,2])	
		li.append(request.POST["status"])	

		d["incident_opened_date"] = request.POST["incident_opened_date"]
		li.append(request.POST["incident_opened_date"])
		d["incident_opened_time"] = request.POST["incident_opened_time"]
		li.append(request.POST["incident_opened_time"])
		data.append( ["Incident opened: " , d["incident_opened_date"] + " " + d["incident_opened_time"] ,1,2] )


		d["incident_duration_days"] = request.POST["incident_duration_days"]
		li.append(request.POST["incident_duration_days"])
		d["incident_duration_hr"] = request.POST["incident_duration_hr"]
		li.append(request.POST["incident_duration_hr"])
		d["incident_duration_min"] = request.POST["incident_duration_min"]
		li.append(request.POST["incident_duration_min"])
		data.append( ["Incident duration: " , d["incident_duration_days"]+" days "+d["incident_duration_hr"]+" hrs " + d["incident_duration_min"] + " mins" ,1,2] )

		data.append( ["What happened: " , request.POST["what_happened"] ,1,5])	
		li.append(request.POST["what_happened"])
		data.append( ["Business impact: ", request.POST["business_impact"],1,5])	
		li.append(request.POST["business_impact"])
		data.append( ["Service impact: " , request.POST["service_impact"],1,5] )	
		li.append(request.POST["service_impact"])	
		data.append( ["Key groups and people involved: " , request.POST["key_groups_and_people_involved"],1,5] )	
		li.append(request.POST["key_groups_and_people_involved"])	
		data.append( ["What we discovered: " , request.POST["what_we_discovered"],1,5] )
		li.append(request.POST["what_we_discovered"])	
		data.append( ["What finally fixed the issue: " , request.POST["what_finally_fixed_the_issue"],1,5] )	
		li.append(request.POST["what_finally_fixed_the_issue"])
		data.append( ["Post recovery action items: " , request.POST["post_recovery_action_items"],1,5] )	
		li.append(request.POST["post_recovery_action_items"])
		data.append( ["Design issues: " , request.POST["design_issues"],1,5] )	
		li.append(request.POST["design_issues"])
		data.append( ["Chronology of the incident: " , request.POST["chronology_of_the_incident"],1,5] )	
		li.append(request.POST["chronology_of_the_incident"])
		data.append( ["Flagged for Reliability: " , request.POST["flagged_for_reliability"],1,2] )	
		li.append(request.POST["flagged_for_reliability"])

		d["date_and_time_flagged_for_reliability_date"] = request.POST["date_and_time_flagged_for_reliability_date"]
		li.append(request.POST["date_and_time_flagged_for_reliability_date"])
		d["date_and_time_flagged_for_reliability_time"] = request.POST["date_and_time_flagged_for_reliability_time"] 
		li.append(request.POST["date_and_time_flagged_for_reliability_time"])
		data.append( ["Date and time flagged for reliability: " , d["date_and_time_flagged_for_reliability_date"] + " " + d["date_and_time_flagged_for_reliability_time"] ,1,2] )	
		

		data.append( ["Reliability record number: " , request.POST["reliability_record_number"],1,5] )	
		li.append(request.POST["reliability_record_number"])

		d["time_down_date"] = request.POST["time_down_date"]
		li.append(request.POST["time_down_date"])
		d["time_down_time"] = request.POST["time_down_time"] 
		li.append(request.POST["time_down_time"])
		data.append( ["Time down: " , d["time_down_date"] + " " + d["time_down_time"] ,1,2] )	


		d["date_and_time_issue_resolved_date"] = request.POST["date_and_time_issue_resolved_date"]
		li.append(request.POST["date_and_time_issue_resolved_date"])
		d["date_and_time_issue_resolved_time"] = request.POST["date_and_time_issue_resolved_time"] 
		li.append(request.POST["date_and_time_issue_resolved_time"])
		data.append( ["Date and time issue resolved: " , d["date_and_time_issue_resolved_date"] + " " +d["date_and_time_issue_resolved_time"],1,2] )	
		


		data.append( ["Did we receive an alert: " , request.POST["did_we_receive_an_alert"],1,2] )	
		li.append(request.POST["did_we_receive_an_alert"])

		d["date_and_time_alert_received_date"] = request.POST["date_and_time_alert_received_date"]
		li.append(request.POST["date_and_time_alert_received_date"])
		d["date_and_time_alert_received_time"] = request.POST["date_and_time_alert_received_time"] 
		li.append(request.POST["date_and_time_alert_received_time"])
		data.append( ["Date and time alert received: " , d["date_and_time_alert_received_date"] + " " + d["date_and_time_alert_received_time"],1,2] )


		'''
		m = ""
		
		for row in data:
			m += str(row[0]) + "\t" + str(row[1]) + "\n"
		
		<table border="1">
<tr> 

<th scope="col">Header</th>
<th scope="col">Header</th>
<th scope="col" colspan="2">Header</th>


</tr> 
</table>
		
		'''
		m = '<html><head><style>table,td,th{ border: 1px solid black; } tr:hover {background-color: #f5f5f5;} table{ border-collapse: collapse; width: 100%; } td,th{ height: 50px;padding: 10px; }'


		if request.POST["status"] == "New":
			m += 'th {background-color: red;color: white;font-size: 150%;}</style></head><body><div style="overflow-x:auto;"><table>'
		elif request.POST["status"] == "In progress":
			m += 'th {background-color: yellow;color: white;font-size: 150%;}</style></head><body><div style="overflow-x:auto;"><table>'
		elif request.POST["status"] == "Resolved":
			m += 'th {background-color: green;color: white;font-size: 150%;}</style></head><body><div style="overflow-x:auto;"><table>'


		m += '<tr><th scope="col" colspan="6"><h4>J&J Major Incident Communication </h4></th></tr>'
				
		c = 0
		
		for row in data:

			if c == 0:
				m += '<tr>'
			
			if row[2] != 1:
				c += row[2]
				m += '<td scope="col" colspan="' + str(row[2]) + '">' + str(row[0]) + '</td>'
			else:
				c += 1
				m += '<td scope="col" colspan="1">' + str(row[0]) + '</td>'	 
			
			if row[3] != 1:
				c += row[3]
				m += '<td scope="col" colspan="' + str(row[3]) + '">' + str(row[1]) + '</td>'
			else:
				c += 1
				m += '<td scope="col" colspan="1">' + str(row[1]) + '</td>'		
			
			if c == 6:
				m += '</tr>'
				c = 0
		
		m += "</table></div></body></html>"
		
		with connection.cursor() as cursor:
			cursor.execute("SELECT email FROM informer_user_details WHERE groupname=%s",(group,))	
			emails = cursor.fetchall()
		
		emails_list = []
		for row in emails:
			emails_list.append(row[0])
		
		me = "ibm2014048@iiita.ac.in"
		mypass = "Jeevan123"
		msg = MIMEMultipart('alternative')
		#msg['Subject'] = "Link"
		msg['From'] = me
		msg['To'] = ", ".join(emails_list)
		
		part = MIMEText(m, 'html')
		msg.attach(part)
		
		try:
			server = smtplib.SMTP('smtp.gmail.com', 587)
			server.starttls()
			server.login(me, mypass)	
			server.sendmail(me, emails_list , msg.as_string())


			with connection.cursor() as cursor:
				cursor.execute("INSERT INTO informer_email_history(groupname,communication_type,incident_number,priority,region,status,incident_opened_date,incident_opened_time,incident_duration_days,incident_duration_hr,incident_duration_min,what_happened,business_impact,service_impact,key_groups_and_people_involved,what_we_discovered,what_finally_fixed_the_issue,post_recovery_action_items,design_issues,chronology_of_the_incident,flagged_for_reliability,date_and_time_flagged_for_reliability_date,date_and_time_flagged_for_reliability_time,reliability_record_number,time_down_date,time_down_time,date_and_time_issue_resolved_date,date_and_time_issue_resolved_time,did_we_receive_an_alert,date_and_time_alert_received_date,date_and_time_alert_received_time) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",tuple(li))
				
		except Exception as e:
			return JsonResponse({"result": "Email sending failed"})

		return JsonResponse({"result": "Email sent successfully"})
		


class MsgPageView(TemplateView):  
	def post(self,request):
		msgdata = request.POST["msgdata"] + " "
		group = request.POST["hidden_group_msg"]

		t = {}
		try:	
			with connection.cursor() as cursor:
				cursor.execute("SELECT mobile FROM informer_user_details WHERE groupname=%s",(group,))	
				numbers = cursor.fetchall()
				num = []
				for i in numbers:
					num.append(i[0])

				conn = http.client.HTTPConnection("api.msg91.com")
				#payload = '{ "sender": "UPDATE", "route": "4", "country": "91", "sms": [ { "message": "data" , "to": ["9490787967"]} ] }'
				#payload = re.escape(str(payload))

				#payload = '{ "sender": "UPDATE", "route": "4", "country": "91","sms": [ { "message": "' + data  +'" , "to":' + num + '} ] }'
				payload = {}
				payload["sender"] = "UPDATE"	
				payload["route"] = "4"
				payload["country"] = "91"
				payload["sms"] = []
				payload["sms"].append({})
				(payload["sms"][0])["message"] = msgdata
				(payload["sms"][0])["to"] = num
				payload = json.dumps(payload)

				#payload = '{\"sender\": \"UPDATE\", \"country\": \"91\", \"route\": \"4\", \"sms\": [{\"message\": \"\", \"to\": [\"9490787967\"]}]}'
				#print (payload)

				headers = { 'authkey': "223766ARJVWnp0yL5b39fdb9",'content-type': "application/json"}
				conn.request("POST", "/api/v2/sendsms", str(payload), headers)
				res = conn.getresponse()
				data = res.read()
				ret = json.loads( data.decode('utf-8') )["type"]
				#print (data)
				
				if ret == "success":
					t["result"] = "Message sent successfully"
				else:
					t["result"] = "Message sending failed"
					return JsonResponse(t)

				cursor.execute("INSERT INTO informer_message_history(groupname,message) VALUES(%s,%s)",(group,data)) 
				
		except Exception as e:
			t = {}
			t["result"] = "Message sending failed"
			return JsonResponse(t)

		
		#msg_data =  {'apikey': 'WjaljBgU2dg-f4h5q1lJScSjkyIy4SVOJ8mBIS1IS6','numbers': '919873997340','message' : data, 'sender': 'TXTLCL'}
		
		
		#f = urllib.request.urlopen('https://api.textlocal.in/send/?'+ urllib.parse.urlencode(msg_data)) 
		

		#r = requests.post("https://api.textlocal.in/send/", data=msg_data)
		#print (r.url)
		#print (r.status_code)
		
		return JsonResponse(t)

		#	return render(request, 'main.html', t)
				
class CallPageView(TemplateView):  
	def post(self,request):
		data = request.POST["calldata"]
		group = request.POST["hidden_group_call"]
		return JsonResponse({"data": "1"})
		'''
		print ("WWWWWWWWWW")

		#client = plivo.RestClient(auth_id='MAZWU1NTRJYZJMMGMYYT', auth_token='Zjc3NmY5OTU3MmFjZmMxMTBjYzBkOGJhNzYyNWU4')
		#call_made = client.calls.create(from_='+917396730773',to_='+919490787967',answer_url='https://a.rokket.space/ckvrad.xml',answer_method="GET")
		call_url = 'https://callingapi.sinch.com/v1/callouts'


		to = '460000000002'
		fr = '+919490787967'

		app_key = "f2af6934-3fc4-4305-a517-daa7cedd3e5b"
		app_secret = "RleTrmSl0EuafsJJod4lmg=="

		values = base64.b64encode({ "method":"ttsCallout", "ttsCallout": { "cli":"46000000000", "destination":{"type":"number","endpoint":"460000000001"}, "domain":"pstn", "locale":"en-US","text":"Helloworld"})
		val = b64bytes.decode('ascii')

		b64bytes = base64.b64encode(('Application:%s:%s' % (app_key, app_secret)).encode())
		_auth = 'basic %s' % b64bytes.decode('ascii')

		a = {}

		url = call_url

		#json_data = json.dumps(urllib.parse.urlencode(values))
		request = urllib.request.Request(url, val)
		request.add_header('content-type', 'application/json')
		request.add_header('authorization', _auth)
		connection = urllib.request.urlopen(request)
		response = connection.read()
		connection.close()

		try:
			result = json.loads(response.decode())
			print (result)
		except ValueError as exception:
			print (str(exception))


		#if ret == True:
		t = {}
			#t["result"] = "Message sent successfully"
		return render(request, 'main.html', t)
		#else:
		#	t = {}
		#	t["result"] = "Message sending failed"
		#	return render(request, 'main.html', t)
		'''

'''
class UsersPageView(TemplateView):  
	def post(self,request):
		data = request.POST["name"]
		
		with connection.cursor() as cursor:
			cursor.execute("SELECT username FROM informer_user_details WHERE groupname=%s",(data,))	
			users = cursor.fetchall()
		
		return JsonResponse({"data": users})
'''	

class EmailData(TemplateView):  
	def post(self,request):
		id1 = request.POST["id"]

		with connection.cursor() as cursor:
			cursor.execute("SELECT * FROM informer_email_history WHERE id=%s",(id1,))	
			data = cursor.fetchall()
			data = list(data[0])
			data.pop(0)
			group = data.pop()

		return JsonResponse({"data": data,"group":group})



class MsgData(TemplateView):  
	def post(self,request):
		id1 = request.POST["id"]

		with connection.cursor() as cursor:
			cursor.execute("SELECT * FROM informer_msg_history WHERE id=%s",(id1,))	
			data = cursor.fetchall()
			data = list(data[0])
			data.pop(0)
			group = data.pop()
			msg = data.pop()

		return JsonResponse({"data": msg,"group":group})

class CallData(TemplateView):  
	def post(self,request):
		id1 = request.POST["id"]

		with connection.cursor() as cursor:
			cursor.execute("SELECT * FROM informer_call_history WHERE id=%s",(id1,))	
			data = cursor.fetchall()
			data = list(data[0])
			data.pop(0)
			group = data.pop()
			msg = data.pop()

		return JsonResponse({"data": msg,"group":group})		


class EmailLoad(TemplateView):
	def post(self,request):

		lim = int(request.POST["lim"])

		if lim == 0:
			return JsonResponse({"show_email": [],"email_load_more":"0"})
		
		with connection.cursor() as cursor:
			cursor.execute("SELECT id,what_happened FROM informer_email_history WHERE id>%s ORDER BY id DESC LIMIT 10",(lim,))
			rows = json.loads(json.dumps(cursor.fetchall()))

		if len(rows) > 0:
			return JsonResponse({"show_email": rows,"email_load_more":lim+len(rows)})
		else:
			return JsonResponse({"show_email": rows,"email_load_more" : "0"})


class MsgLoad(TemplateView):
	def post(self,request):

		lim = int(request.POST["lim"])
		
		if lim == 0:
			return JsonResponse({"show_message": [],"msg_load_more":"0"})

		with connection.cursor() as cursor:
			cursor.execute("SELECT id,message FROM informer_message_history WHERE id>%s ORDER BY id DESC LIMIT 10",(lim,))
			rows = json.loads(json.dumps(cursor.fetchall()))

			l = len(rows)
			for i in range(l):
				s = rows[i][1]
				rows[i][1] = s[0:50]

		if len(rows) > 0:	
			return JsonResponse({"show_message": rows,"msg_load_more":rows[len(rows)-1][0]})
		else:
			return JsonResponse({"show_message": rows,"msg_load_more": "0"})	

class CallLoad(TemplateView):
	def post(self,request):

		lim = int(request.POST["lim"])
		
		if lim == 0:
			return JsonResponse({"show_call": [],"call_load_more":"0"})

		with connection.cursor() as cursor:
			cursor.execute("SELECT id,message FROM informer_call_history WHERE id>%s ORDER BY id DESC LIMIT 10",(lim,))
			rows = json.loads(json.dumps(cursor.fetchall()))

			l = len(rows)
			for i in range(l):
				s = rows[i][1]
				rows[i][1] = s[0:50]

		if len(rows) > 0:	
			return JsonResponse({"show_call": rows,"call_load_more":rows[len(rows)-1][0]})
		else:
			return JsonResponse({"show_call": rows,"call_load_more": "0"})	
