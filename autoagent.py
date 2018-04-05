try:
    print "Importing requirments..."
    from googlevoice import Voice
    import sys
    import BeautifulSoup
    from time import sleep
    from random import randint
    import os
    print "Logging solutions..."
    solutions = []
    for solution in os.listdir("solutions/"):
        if not ".DS_Store" == solution:
            solutions.append(solution)
            print "Adding "+solution+"..."
    waitingList = []
    inProgress = []
    inProgress1 = []
    inProgress2 = []
    asked = []
    ignore = []
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
    print "Retrieving credentials..."
    username, password = "jackrichardbusiness@gmail.com", ""
    voice = Voice()
    voice.login(username, password)
    print("Successful authentication.")
    voice.sms()
    current = len(extractsms(voice.sms.html))
    initialList = []
    print "Beginning message listening service..."
    for message in extractsms(voice.sms.html):
        initialList.append(str(message))
    print "Service started."
    while True:
        try:
            voice.sms()
            new = len(extractsms(voice.sms.html))
            if not new == current:
                newList = []
                for message in extractsms(voice.sms.html):
                    newList.append(str(message))
                newMsg = str([x for x in newList if x not in initialList][0])
                fromNum = newMsg.split("""'from': u'""")[1].split("'")[0].replace(':', '')
                inList = False
                for person in waitingList:
                    if person == fromNum:
                        inList = True
                if not fromNum == "Me":
                    with open("log.txt", "a") as log:
                        log.write("\n"+str(newMsg))
                if not fromNum == "Me" and not inList and not fromNum in inProgress and not fromNum in inProgress1 and not fromNum in inProgress2 and not fromNum in ignore and not fromNum in asked:
                    print "Message recieved."
                    voice.send_sms(fromNum, "Hi! We've added you to our waiting list, please wait.")
                    waitingList.append(fromNum)
                    print "Added "+fromNum+" to the waiting list."
                    sleep(2)                
                    waitingList.remove(fromNum)
                    inProgress.append(fromNum)
                elif fromNum in inProgress1:
                    newMsg = newMsg.lower()
                    if "sabrina" in newMsg or "companion" in newMsg or "ios" in newMsg or "android" in newMsg or "car" in newMsg or "watch" in newMsg:
                        issue = ["Alright, we're sorry you're having a problem with this. But, what's the issue?", "Ok, what issue are you having with this?", "Ok, what issue are you having?"]
                        with open(fromNum+"_report.txt", "a") as fileReport:
                            if "companion" in newMsg:
                                fileReport.write("Sabrina Companion\n")
                                voice.send_sms(fromNum, issue[randint(0, len(issue)-1)])
                                inProgress1.remove(fromNum)
                                inProgress2.append(fromNum)
                            elif "android" in newMsg:
                                fileReport.write("Sabrina Assistant for Android\n")
                                voice.send_sms(fromNum, issue[randint(0, len(issue)-1)])
                                inProgress1.remove(fromNum)
                                inProgress2.append(fromNum)
                            elif "ios" in newMsg:
                                fileReport.write("Sabrina Assistant for iOS\n")
                                voice.send_sms(fromNum, issue[randint(0, len(issue)-1)])
                                inProgress1.remove(fromNum)
                                inProgress2.append(fromNum)
                            elif "app" in newMsg and not "ios" in newMsg and not "android" in newMsg:
                                voice.send_sms(fromNum, "What operating system are you using (Android, iOS, etc.)?")
                            else:
                                voice.send_sms(fromNum, "I couldn't find any help topics for that product, could you call us at (508) 306-1254?")
                                inProgress1.remove(fromNum)
                                ignore.append(fromNum)
                    else:
                        voice.send_sms(fromNum, "I couldn't find that product...could you try that again?")
                elif fromNum in inProgress2 or fromNum in asked:
                    if not fromNum in asked:
                        solutionFound = 0
                        for solution in solutions:
                            print "Searching in "+solution+"..."
                            if solution.split("-")[1].replace(".txt", "") in newMsg:
                                solutionFound = 1
                                asked.append(fromNum)
                                inProgress2.remove(fromNum)
                                voice.send_sms(fromNum, ("Have you tried%s" % str(open("solutions/"+solution, "r").read()).split("\n")[0]))
                                with open(fromNum+"_report.txt", "a") as myfile:
                                    myfile.write("Tried"+str(open("solutions/"+solution, "r").read()).split("\n")[0].replace("?", ""))
                        if solutionFound == 0:
                            voice.send_sms(fromNum, "Ok, please call us to get a solution to that.")
                            inProgress2.remove(fromNum)
                            ignore.append(fromNum)
                    else:
                        with open(fromNum+"_report.txt", "a") as myfile:
                            if "worked" in newMsg or "work" in newMsg and not "didn't" in newMsg or "not" in newMsg:
                                myfile.write("\nProblem Fixed.")
                                voice.send_sms(fromNum, "Glad I could help today, have a great day!")
                            else:
                                myfile.write("Did not work.")
                elif fromNum in ignore:
                    bye = ["Have a nice day!", "Bye!", "Hope you get your product fixed!"]
                    voice.send_sms(fromNum, bye[randint(0, len(bye)-1)])
                    ignore.remove(fromNum)
                else:
                    if inList and not fromNum == "Me":
                        voice.send_sms(fromNum, "Sit tight. We'll be with you soon.")
                current = new
                initialList = newList
            else:
                current = new
                welcomes = ["Hello! I am %s, here to help you with your Sabrina Technologies questions. What's the product you're having trouble today?", "Hi! My name is %s. What product are you having trouble with?", "Good day! I'm %s with Sabrina Technologies. What product are you having trouble with?"]
                assistants = ["Fred", "Andrew", "Diane", "Wilma", "Bruce"]
                for person in inProgress:
                    print "Helping "+person+"..."
                    helper = assistants[randint(0, len(assistants)-1)]
                    voice.send_sms(person, welcomes[randint(0, len(welcomes)-1)] % helper)
                    inProgress.remove(person)
                    inProgress1.append(person)
                    with open(person+"_report.txt", "w") as fileReport:
                        fileReport.write("Helped by "+helper+"\n")
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
except Exception as e:
    print "\nERROR: "+str(e)+"\nService shutting down..."
