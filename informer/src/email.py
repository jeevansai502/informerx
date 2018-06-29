import smtplib

class Email():

	def __init__(self):
		self.server = smtplib.SMTP('smtp.gmail.com', 587)
		self.server.login("ibm2014048@iiita.ac.in", "Jeevan123")
		return

	def sendmail(self,msg,toaddresses):
		self.server.sendmail("ibm2014048@iiita.ac.in", "jeevansai502@gmail.com", msg)
		return
