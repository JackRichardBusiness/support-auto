from googlevoice import Voice
import sys
import BeautifulSoup
from time import sleep
waitingList = []
inProgress = []
inProgress1 = []
inProgress2 = []
ignore = []
ignore2 = []
def extractsms(htmlsms) :
    msgitems = []										# accum message items here
    #	Extract all conversations by searching for a DIV with an ID at top level.
    tree = BeautifulSoup.BeautifulSoup(htmlsms)			# parse HTML into tree
    conversations = tree.findAll("div",attrs={"id" : True},recursive=False)
    for conversation in conversations :
        #	For each conversation, extract each row, which is one SMS message.
        rows = conversation.findAll(attrs={"class" : "gc-message-sms-row"})
        for row in rows :								# for all rows
            #	For each row, which is one message, extract all the fields.
            msgitem = {"id" : conversation["id"]}		# tag this message with conversation ID
            spans = row.findAll("span",attrs={"class" : True}, recursive=False)
            for span in spans :							# for all spans in row
                cl = span["class"].replace('gc-message-sms-', '')
                msgitem[cl] = (" ".join(span.findAll(text=True))).strip()	# put text in dict
            msgitems.append(msgitem)					# add msg dictionary to list
    return msgitems
username, password = "jackrichardbusiness@gmail.com", "Guineas14"
voice = Voice()
voice.login("jackrichardbusiness@gmail.com", "Guineas14")
print("Logged in.")
voice.sms()
current = len(extractsms(voice.sms.html))
initialList = []
for message in extractsms(voice.sms.html):
    initialList.append(str(message))
while True:
    try:
        voice.sms()
        new = len(extractsms(voice.sms.html))
        if not new == current:
            newList = []
            for message in extractsms(voice.sms.html):
                newList.append(str(message))
            newMsg = str([x for x in newList if x not in initialList][0])
            print newMsg
            fromNum = newMsg.split("""'from': u'""")[1].split("'")[0].replace(':', '')
            inList = False
            for person in waitingList:
                if person == fromNum:
                    inList = True
            if not fromNum == "Me" and not inList and not fromNum in inProgress and not fromNum in inProgress1 and not fromNum in inProgress2:
                print "Message recieved."
                voice.send_sms(fromNum, "Hi! We've added you to our waiting list, please wait.")
                waitingList.append(fromNum)
                print "Added "+fromNum+" to the waiting list."
                sleep(2)
                voice.send_sms(fromNum, "Hello, thanks for opting to test our automated system. It will try it's best to help you, if it can't help, call us at (508) 306-1254. Thanks.")                
                waitingList.remove(fromNum)
                inProgress.append(fromNum)
            elif fromNum in inProgress1:
                voice.send_sms(fromNum, "Ok, so which of our products is this?")
                inProgress1.remove(fromNum)
                inProgress2.append(fromNum)
                fileReport = open(fromNum+"_report.txt", "w")
                fileReport.write(newMsg)
                fileReport.close()
            elif fromNum in inProgress2:
                voice.send_sms(fromNum, "Got it, we'll send the info over. Thanks for chatting!")
                inProgress2.remove(fromNum)
                ignore.append(fromNum)
                fileReport = open(fromNum+"_report.txt", "r+")
                fileReport.write(fileReport.read()+newMsg)
                fileReport.close()
            elif fromNum in ignore:
                voice.send_sms(fromNum, "Have a wonderful day.")
                ignore.remove(fromNum)
                ignore2.append(fromNum)
            elif fromNum in ignore2:
                voice.send_sms(fromNum, "Thank you!")
            else:
                if inList and not fromNum == "Me":
                    voice.send_sms(fromNum, "Sit tight. We'll be with you soon.")
            current = new
            initialList = newList
        else:
            current = new
            from random import randint
            assistants = ["Fred", "Andrew", "Diane", "Wilma", "Bruce"]
            for person in inProgress:
                voice.send_sms(person, "Hi! I'm "+assistants[randint(0, len(assistants)-1)]+". What problem are you having with your product?")
                inProgress.remove(person)
                inProgress1.append(person)
    except Exception as e:
        print e
        print("An error occured. Cleaning messages...")
        voice = Voice()
        voice.login(username, password)
        for message in voice.sms().messages:
            if message.isRead:
                message.delete()
        voice = Voice()
        voice.login(username, password)
        current = new
        initialList = newList
