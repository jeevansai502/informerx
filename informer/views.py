from django.shortcuts import render
from django.views.generic import TemplateView
import os.path
import json
from django.db import connection
import hashlib
from django.utils import timezone
#import sys
#sys.path.append("informer/src")
#from email import Email
#from message import Message
from django.contrib.auth.signals import user_logged_in
from django.http import HttpResponseRedirect
#from informer.src import message,email
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

		with connection.cursor() as cursor:
			original = cursor.execute("SELECT password FROM informer_user_login_details WHERE email=%s",(email,))
			corr = original.fetchone()
			print (corr)
			
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


class RegisterPageView(TemplateView):
	def get(self,request):
		return render(request, 'register.html',context=None)

	def post(self,request):
		username = request.POST["username"]
		password = request.POST["password"]

		hash_pass = hashlib.md5(password.encode())
		password = hash_pass.hexdigest()

		email = request.POST["email"]
		mobile = request.POST["mobile"]
		group = request.POST["group"]

		reg = {}

		try:
			with connection.cursor() as cursor:
				cursor.execute("INSERT INTO informer_user_login_details VALUES (%s,%s)",(email,password))
				cursor.execute("INSERT INTO informer_user_details VALUES (%s,%s,%s,%s)",(email,username,mobile,group))

			reg["result"] = "Signup success"
			return render(request, 'login.html',reg)
		except Exception as e:
			print (e)

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

		user_sessions = UserSession.objects.filter(session_id = request.session.session_key)
		if len(user_sessions) == 0:
			return render(request, 'login.html')
		else:
			with connection.cursor() as cursor:
				cursor.execute("SELECT DISTINCT groupname FROM informer_user_details ")
				groups = json.loads(json.dumps(cursor.fetchall()))

				cursor.execute("SELECT id,what_happened FROM informer_email_history ORDER BY id DESC LIMIT 1")
				rows = json.loads(json.dumps(cursor.fetchall()))

				ln = {}
				ln["groups"] = groups
				ln["show_email"] = rows
				ln["email_load_more"] = len(rows)

				cursor.execute("SELECT id,message FROM informer_message_history ORDER BY id DESC LIMIT 1")
				rows = json.loads(json.dumps(cursor.fetchall()))

				ln["show_message"] = rows
				ln["msg_load_more"] = len(rows)
				return	render(request, 'main.html',ln)




class EmailPageView(TemplateView):  
	def post(self,request):
		
		data = []
		
		data.append( ["Communication type: " , request.POST["communication_type"] ,1 , 5 ] )
		data.append( ["Incident number: " , request.POST["incident_number"] ,1 ,2 ] )
		data.append( ["Priority: " , request.POST["priority"] ,1 ,2] )
		data.append( ["Region: " , request.POST["region"] ,1,2])		
		data.append( ["Status: " , request.POST["status"] ,1,2])		
		data.append( ["Incident opened: " , request.POST["incident_opened"],1,2] )		
		data.append( ["Incident duration: " , request.POST["incident_duration"],1,2] )		
		data.append( ["What happened: " , request.POST["what_happened"] ,1,5])	
		data.append( ["Business impact: ", request.POST["business_impact"],1,5])	
		data.append( ["Service impact: " , request.POST["service_impact"],1,5] )		
		data.append( ["Key groups and people involved: " , request.POST["key_groups_and_people_involved"],1,5] )		
		data.append( ["What we discovered: " , request.POST["what_we_discovered"],1,5] )	
		data.append( ["What finally fixed the issue: " , request.POST["what_finally_fixed_the_issue"],1,5] )	
		data.append( ["Post recovery action items: " , request.POST["post_recovery_action_items"],1,5] )	
		data.append( ["Design issues: " , request.POST["design_issues"],1,5] )	
		data.append( ["Chronology of the incident: " , request.POST["chronology_of_the_incident"],1,5] )	
		data.append( ["Flagged for Reliability: " , request.POST["flagged_for_reliability"],1,2] )	
		data.append( ["Date and time flagged for reliability: " , request.POST["date_and_time_flagged_for_reliability"],1,2] )	
		data.append( ["Reliability record number: " , request.POST["reliability_record_number"],1,5] )	
		data.append( ["Time down: " , request.POST["time_down"],1,2] )	
		data.append( ["Date and time issue resolved: " , request.POST["date_and_time_issue_resolved"],1,2] )	
		data.append( ["Did we receive an alert: " , request.POST["did_we_receive_an_alert"],1,2] )	
		data.append( ["Date and time alert received: " , request.POST["date_and_time_alert_received"],1,2] )
		
		group = request.POST["hidden_group_email"]
		

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
		m = '<html><head><style>table,td,th{ border: 1px solid black; } tr:hover {background-color: #f5f5f5;} table{ border-collapse: collapse; width: 100%; } td,th{ height: 50px;padding: 10px; } th {background-color: red;color: white;}</style></head><body><div style="overflow-x:auto;"><table>'
		m += '<tr><th scope="col" colspan="6">J&J Major Incident Communication </th></tr>'
				
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
		

		t = {}
		try:
			me = "ibm2014048@iiita.ac.in"
			you = "jeevansai502@gmail.com"

			msg = MIMEMultipart('alternative')
			#msg['Subject'] = "Link"
			msg['From'] = me
			msg['To'] = you
		
			part = MIMEText(m, 'html')
			msg.attach(part)
		
			server = smtplib.SMTP('smtp.gmail.com', 587)
			server.starttls()
			server.login("ibm2014048@iiita.ac.in", "Jeevan123")
			server.sendmail("ibm2014048@iiita.ac.in", "jeevansai502@gmail.com", msg.as_string())
		
			#email = EmailMessage('Incident communication', msg, to = ['jeevansai502@gmail.com'])
			#email.send()

			return JsonResponse({"result": "Email sent successfully"})
		except Exception as e:
			return JsonResponse({"result": "Email sending failed"})


class MsgPageView(TemplateView):  
	def post(self,request):
		data = request.POST["msgdata"]
		group = request.POST["hidden_group_msg"]
		
		msg_data =  {'apikey': '4TCdBKnBuwE-5SbT9KHhtkSzfZ779fkCmFYnvsQ97Y','numbers': '919873997340','message' : 'Good boy', 'sender': 'TXTLCL'}
		
		
		f = urllib.request.urlopen('https://api.textlocal.in/send/?'+ urllib.parse.urlencode(msg_data)) 
		

		#r = requests.post("https://api.textlocal.in/send/", data=msg_data)
		#print (r.url)
		#print (r.status_code)
		#if ret == True:
		t = {}
			#t["result"] = "Message sent successfully"
		return render(request, 'main.html', t)
		#else:
		#	t = {}
		#	t["result"] = "Message sending failed"
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


class UsersPageView(TemplateView):  
	def post(self,request):
		data = request.POST["name"]
		
		with connection.cursor() as cursor:
			cursor.execute("SELECT username FROM informer_user_details WHERE groupname=%s",(data,))	
			users = cursor.fetchall()
		
		return JsonResponse({"data": users})
		
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

		if len(rows) > 0:	
			return JsonResponse({"show_message": rows,"msg_load_more":rows[len(rows)-1][0]})
		else:
			return JsonResponse({"show_message": rows,"msg_load_more": "0"})	
