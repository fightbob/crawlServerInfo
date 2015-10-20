import urllib2  
import os
import time
import smtplib  
import string
from email.mime.text import MIMEText  
# from email.header import Header 

def getId(server):
	servers = {'qa1':'https://ultra-qa.int.bbpd.io/', 'stg':'https://saas-stg.int.bbpd.io/', 
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
				if textContent[0] != 'The server is down.' and latestBuildId != textContent[0]:
				    break
				oldBuildTime = textContent[1]
				print oldBuildTime
			for n in range(len(files)+1):
				lastFile = open(dir + ''.join(files[-(n+1):][0]), 'r')
				textContent = lastFile.readline().split('\t')
				if textContent[0] != 'The server is down.' and latestCommitId != textContent[2]:
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
	data[0] = saveId('qa1','/Users/boliu/takeParam/ultra-qa1/')
	data[1] = saveId('stg','/Users/boliu/takeParam/stg/')
	data[2] = saveId('demo','/Users/boliu/takeParam/demo/')
	if data[0][5] or data[1][5] or data[2][5]:
		sender = 'Bob.Liu@blackboard.com'  
		receivers = ('Bob.Liu@blackboard.com')
		# smtpserver = 'outlook.office365.com'  
		username = 'Bob.Liu@blackboard.com'  
		password = 'Fight*9'  
		
		date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
		alertFlag = ['','','','','','']
		for n in range(len(data)):
			alertFlag[2*n] = '' if data[n][1] == date else '#00FFFF'
			alertFlag[2*n+1] = '' if data[n][3] == date else '#00FFFF'
		qa1Report = """
		            <p text-align="left">
		            Server: https://ultra-qa1.int.bbpd.io<br />
		            Build: %s<br />
		            Commit: %s<br /><br />
		            </p>
		            """%(data[0][0],data[0][2])
		            if data[0][0] !='' and data[0][2] !='' else
                    """"""
		stgReport = """
            <p text-align="left">
            Server: https://saas-stg.int.bbpd.io<br />
            Build: %s<br />
            Commit: %s<br /><br />
            </p>
            """%(data[1][0],data[1][2])
            if data[1][0] !='' and data[1][2] !='' else
            """""" 
		demoReport = """
            <p text-align="left">
            Server: https://ultra-demo.int.bbpd.io<br />
            Build: %s<br />
            Commit: %s<br /><br />
            </p>
            """%(data[2][0],data[2][2])
            if data[2][0] =='' and data[2][2] =='' else
            """"""  
		msgReport = """%s%s%s"""%(qa1Report, stgReport, demoReport)

		qa1Info = """
				<tr>
		     	 <td>ultra-qa1</td>
		     	 <td>%s<font color=%s>(%s)</font></td>
				 <td>%s<font color=%s>(%s)</font></td>
		     	</tr>
				"""%(alertFlag[0], data[0][0], data[0][1], alertFlag[1], data[0][2], data[0][3], data[0][4])
				if data[0][0] !='' and data[0][2] !='' else
				"""
				<tr>
				 <td>ultra-qa1</td>
				 <td colspan="2"><font color="#EA0000">server is down!</font></td>
				</tr>
				"""

		msg = MIMEText("""
			<table width="1000" border="1" cellspacing="0" cellpadding="4">
		     <tr>
		      <th>server</th>
		      <th>buildID</th>
		      <th>commitID</th>
		     </tr>
		     <tr>
		      <td>ultra-qa1</td>
		      <td bgcolor=%s>%s(%s)</td>
		      <td bgcolor=%s>%s(%s)</td>
		      <td>%s</td>
		     </tr>
		     <tr>
		      <td>saas-stg</td>
		      <td bgcolor=%s>%s(%s)</td>
		      <td bgcolor=%s>%s(%s)</td>
		      <td>%s</td>
		    </tr>
		    <tr>
		     <td>ultra-demo</td>
		      <td bgcolor=%s>%s(%s)</td>
		      <td bgcolor=%s>%s(%s)</td>
		      <td>%s</td>
		    </tr>
		    </table><br><br>%s"""%(alertFlag[0], data[0][0], data[0][1], alertFlag[1], data[0][2], data[0][3], data[0][4],
		    	         alertFlag[2], data[1][0], data[1][1], alertFlag[3], data[1][2], data[1][3], data[1][4],
		    	         alertFlag[4], data[2][0], data[2][1], alertFlag[5], data[2][2], data[2][3], data[2][4], msgReport),
		    	         "html","utf-8")

		msg['subject'] = 'this is a test'
		smtp = smtplib.SMTP()  
		smtp.connect('outlook.office365.com','submission')
		smtp.starttls()  
		smtp.ehlo() 
		smtp.login(username, password)  
		smtp.sendmail(sender, receivers, msg.as_string())  
		smtp.quit()  

sendMail()