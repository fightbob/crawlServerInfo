import urllib2  
import os
import time
import smtplib  
import string
from email.mime.text import MIMEText  

def getId(server):
	servers = {'qa1':'https://ultra-qa1.int.bbpd.io/', 'stg':'https://saas-stg.int.bbpd.io/', 
	           'demo':'https://ultra-demo.int.bbpd.io/'}
	baseURL = servers[server]
	print(baseURL)
	buildId = ''
	commitId = ''
	UIVTime = ''
	UIV = ''
	try:   	
		for n in range(10):
			rawInfo = urllib2.urlopen(baseURL + 'ultra/').read()
			if rawInfo[1:9] == '!DOCTYPE':
				UIV = rawInfo.split('href')[2].split('ultra/')[1].split('/">\n')[0]
				UIVTime = UIV[3:22]
				print('got the raw information')
				break
		commitUrl = baseURL + 'ultra/' + UIV + '/build-info.json'
		buildInfo = urllib2.urlopen(baseURL).info()
		buildId = buildInfo['X-Blackboard-product'].split(';')[1].lstrip()
		commitInfo = urllib2.urlopen(commitUrl).read()
		commitId = commitInfo.replace('\n',"").split(',')[2].split(':')[1].replace('"',"").replace(' ',"")
	except Exception, e:
		print e
	return (buildId, commitId, UIVTime)

def saveId(server,dir):
	ISOTIMEFORMAT='%Y-%m-%d_%H:%M:%S'
	localtime = time.strftime(ISOTIMEFORMAT, time.localtime(time.time()))
	date = localtime[0:10]
	currentTime = localtime[11:19]
	id = getId(server)
	files = os.listdir(dir)
	fileName = localtime + '.txt'
	file = open(os.path.join(dir, fileName), 'w')
	latestBuildId = id[0]
	latestCommitId = id[1]
	UIVTime = id[2]
	dateInFileName = ''
	updateStatus = 0
	buildInfo = ''
	commitInfo = ''
	oldBuildTime = date
	oldCommitTime = date
	if UIVTime == '':
		file.write('The server is down.')
	else:	   
		if len(files) > 0:
			for n in range(len(files)+1):
				lastFile = open(dir + ''.join(files[-(n+1):][0]), 'r')
				textContent = lastFile.readline().split('\t')
				if textContent[0] != 'The server is down.' and textContent[0] != '':
					if latestBuildId != textContent[0]:
						break
					oldBuildTime = textContent[1]
				print oldBuildTime
			for n in range(len(files)+1):
				lastFile = open(dir + ''.join(files[-(n+1):][0]), 'r')
				textContent = lastFile.readline().split('\t')
				if textContent[0] != 'The server is down.' and textContent[0] != '':
					if latestCommitId != textContent[2]:
						break
					oldCommitTime = textContent[3]

			dateInFileName = files[-1:][0][0:10]
			lastFile = open(dir + ''.join(files[-1:][0]), 'r')
			textContent = lastFile.readline().split('\t')
			print('list files')
			lastFile.close()
			if textContent[0] != 'The server is down.':
				buildInfo = textContent[0]
				commitInfo = textContent[2]
		print oldBuildTime
		file.write(latestBuildId + '\t' + oldBuildTime + '\t' + latestCommitId + '\t' + oldCommitTime + '\t' + UIVTime + '\n')
	file.close()
	buildUpdateStatus = 1 if latestBuildId == buildInfo else 0
	commitUpdateStatus = 1 if latestCommitId == commitInfo else 0
	updateStatus = buildUpdateStatus + commitUpdateStatus
	sendMail = True if updateStatus != 2 or cmp(date, dateInFileName) != 0 else False
	return (latestBuildId, oldBuildTime, latestCommitId, oldCommitTime, UIVTime, sendMail)

def sendMail():
	data = ['', '', '']
	data[0] = saveId('qa1','/Users/boliu/crawlServerInfo/ultra-qa1/')
	data[1] = saveId('stg','/Users/boliu/crawlServerInfo/stg/')
	data[2] = saveId('demo','/Users/boliu/crawlServerInfo/demo/')
	if data[0][5] or data[1][5] or data[2][5]:
		sender = 'Bob.Liu@blackboard.com'  
		receivers = ('Bob.Liu@blackboard.com')
		# smtpserver = 'outlook.office365.com'  
		username = 'Bob.Liu@blackboard.com'  
		password = 'Fight*9'  
		
		date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
		alertFlag = ['','','','','','']
		dateInfo = ['', '', '', '', '', '']
		for n in range(len(data)):
			 if data[n][1] == date:
			 	alertFlag[2*n] = ''
			 	dateInfo[2*n] = ''
			 else:
			 	alertFlag[2*n] = '#EA0000'
			 	dateInfo[2*n] = data[n][1]
			  
  			 if data[n][3] == date:
				alertFlag[2*n+1] = ''
				dateInfo[2*n+1] = ''
  			 else:
  			  	alertFlag[2*n+1] = '#EA0000'
  			  	dateInfo[2*n+1] = data[n][3]
		qa1Report = """
		            Server: https://ultra-qa1.int.bbpd.io<br />
		            Build: %s<br />
		            Commit: %s
		            """%(data[0][0],data[0][2]) if data[0][0] !='' and data[0][2] !='' else """ """
		stgReport = """
            Server: https://saas-stg.int.bbpd.io<br />
            Build: %s<br />
            Commit: %s
            """%(data[1][0],data[1][2]) if data[1][0] !='' and data[1][2] !='' else """ """ 
		demoReport = """
			Server: https://ultra-demo.int.bbpd.io<br />
            Build: %s<br />
            Commit: %s
            """%(data[2][0],data[2][2]) if data[2][0] !='' and data[2][2] !='' else """ """  
		msgReport = """
            		<p text-align="left">
						%s<br>%s<br>%s
					</p>
					"""%(qa1Report, stgReport, demoReport)

		qa1Info = """
				<tr>
		     	 <td>ultra-qa1</td>
		     	 <td>%s<br />
		     	 <font color=%s>%s</font>
		     	 </td>
				 <td>%s<br />
				 <font color=%s>%s</font>
				 </td>
		     	</tr>
				"""%(data[0][0], alertFlag[0], dateInfo[0], data[0][2], alertFlag[1], dateInfo[1]) if data[0][0] !='' and data[0][2] !='' else """
				<tr>
				 <td>ultra-qa1</td>
				 <td colspan="2"><font color="#EA0000" align="center">server is down!</font></td>
				</tr>
				"""
		saasInfo = """
				<tr>
		     	 <td>saas-stg</td>
		     	 <td>%s<br />
		     	 <font color=%s>%s</font>
		     	 </td>
				 <td>%s<br />
				 <font color=%s>%s</font>
				 </td>
		     	</tr>
				"""%(data[1][0], alertFlag[2], dateInfo[2], data[1][2], alertFlag[3], dateInfo[3]) if data[1][0] !='' and data[1][2] !='' else """
				<tr>
				 <td>saas-stg</td>
				 <td colspan="2"><font color="#EA0000" text-align="center">server is down!</font></td>
				</tr>
				"""
		demoInfo = """
				<tr>
		     	 <td>ultra-demo</td>
		     	 <td>%s<br />
		     	 <font color=%s>%s</font>
		     	 </td>
				 <td>%s<br />
				 <font color=%s>%s</font>
				 </td>
		     	</tr>
				"""%(data[2][0], alertFlag[4], dateInfo[4], data[2][2], alertFlag[5], dateInfo[5]) if data[2][0] !='' and data[2][2] !='' else """
				<tr>
				 <td>ultra-demo</td>
				 <td colspan="2"><font color="#EA0000">server is down!</font></td>
				</tr>
				"""
		jiraFormat = """
					||server||environment||status||<br>
					|ultra-qa1|%s|work well|<br>
					|saas-stg|%s|work well|<br>
					|demo|%s|work well|
					"""%(qa1Report, stgReport, demoReport)
		dateSend = time.strftime('%Y.%m.%d  %H:%M:%S', time.localtime(time.time()))
		msg = MIMEText("""
			<p><center><h3>Time:  %s</h3></center></p><br>
			<table width="1000" border="1" cellspacing="0" cellpadding="4">
			  <tr>
				<th>server</th>
				<th>commit id</th>
				<th>build id</th>
			  </tr>
		     %s
		     %s
             %s
		    </table><br><br>%s<br>%s"""%(dateSend, qa1Info, saasInfo, demoInfo, msgReport, jiraFormat), "html", "utf-8")

		msg['subject'] = 'Server information'
		smtp = smtplib.SMTP()  
		smtp.connect('outlook.office365.com','submission')
		smtp.starttls()  
		smtp.ehlo() 
		smtp.login(username, password)  
		smtp.sendmail(sender, receivers, msg.as_string())  
		smtp.quit()  

sendMail()