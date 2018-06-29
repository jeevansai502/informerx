import urllib.request
import http.cookiejar
import httplib2
import random

class Message():
	def __init__(self):
		return
	
	def send_sms(self,numbers, message):
	    server_list = ['site1', 'site2', 'site3', 'site4', 'site5', 'site6']
	    server = server_list[random.randint(0, len(server_list) - 1)]
	    
	    AUTH_URL = 'http://' + server + '.way2sms.com:80/auth.cl'
	    SMS_URL = 'http://' + server + '.way2sms.com/FirstServletsms?custid='
	    
	    http_conn = httplib2.Http()
	    
	    headers = {'Content-type': 'application/x-www-form-urlencoded',
		       'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)'}
	    body = {'username': "7396730773", 'password': "jeevansai", 'login': 'Login'}
	    
	    try:
	    	response, content = http_conn.request(AUTH_URL, 'POST', headers=headers, body=urllib.urlencode(body))
	    except:
	    	print ('Authentication failed, check your login details again.')
	    	return False
	    else:
	    	print ('Were hooked on to the Way2SMS server!')
	    	
	    headers = {'Content-type': 'application/x-www-form-urlencoded',
		       'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)',
		       'Cookie': response['set-cookie']}
	    
	    for number in numbers:
	    	body = {'custid': 'undefined','HiddenAction': 'instantsms','Action': 'sa65sdf656fdfd','login': '','pass': '','MobNo': number,'textArea': message}
	    
	    	try:
	    		response, content = http_conn.request(SMS_URL, 'POST', headers=headers, body=urllib.urlencode(body))
	    	except:
	    		print ('Failed to send to', number)
	    		return False
	    
	    	if content.find('successfully') == -1:
	    		print ('Message sent to', number)
	    	else:
	    		print ('Failed to send to', number)

	
	
	def sendMessage(self,message,number):
		username = "7396730773"
		passwd = "jeevansai"

		message = "+".join(message.split())
		
		url = 'http://site24.way2sms.com/Login1.action?'
		data = 'username='+username+'&password='+passwd+'&Submit=Sign+in'
		
		cj = http.cookiejar.CookieJar()
		opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
		opener.addheaders=[('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120')]

		try:
		    print ("A")		
		    usock = opener.open(url,data.encode("utf-8"))
		    print ("B")
		except:
		    return False

		session_id = str(cj).split('~')[1].split()[0]
		send_sms_url = 'http://site24.way2sms.com/smstoss.action?'
		send_sms_data = 'ssaction=ss&Token=' + session_id + '&mobile=' + number + '&message=' + message + '&msgLen='+str(len(message))
		opener.addheaders=[('Referer', 'http://site25.way2sms.com/sendSMS?Token='+session_id)]
		
		try:
		    print ("C")
		    sms_sent_page = opener.open(send_sms_url,send_sms_data.encode('utf-8'))
		    print ("D")
		except:
		    return False  
		    
		return True    	
