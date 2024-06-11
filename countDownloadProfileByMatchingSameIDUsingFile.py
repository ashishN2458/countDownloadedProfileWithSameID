# Finding out how many times we have downloaded a profile with same ID by matching the data inside the file.
import os
import configparser
import datetime
from datetime import datetime, date
from datetime import timedelta
import linecache  # if get bytes so use lineache
import gzip
import glob
import paramiko
import fnmatch
import shutil
import xlswriter
import csv
import subprocess
import builtins
from ordinal import ordinal
import pandas as pd
from collections import Counter
import numpy as np
import matplotlb.pyplot as plt
import smtplib, socket
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.message import EmailMessage
from email.utils import make_msgid

# define global variable
yesterday = date.today() - timedelta(days=1)  # Get today - 1 day i.e., 2024-04-25
# got date yesterday as per the format
print("The date used is as per format of customApiResponse")
anFileDate = yesterday.strftime("%Y%m%d")
conversionDate: str = anFileDate  # 20240425

# Read config file
print("reading config parser for profile download")
config = configparser.ConfigParser()
config.read('configprofiledownload.properties')

# Get current directory
dirPath = os.path.dirname(__file__)

# --------------------------
# server start
# --------------------------
print("Executing script")
serverIPaddress = config.get("server", "serverIPaddress")
serverPort = config.get("server", "serverPort")
serverUsername = config.get("server", "serverUsername")
serverPassword = config.get("server", "serverPassword")
serverInputPath = config.get("server", "serverInputPath")
print("server config details loaded successfully")

try:
    i = 0
    # print("server - initializing connection")
    SSH_Client = paramiko.SSHClient()
    SSH_Client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    SSH_Client.connect(hostname=serverIPaddress, port=serverPort, username=serverUsername, password=serverPassword, look_for_keys=False)
    print('connection established successfully for server')

    statement = " |grep -i 'customApiResponse'"
    filePattern = "cat " + serverInputPath + "*" + conversionDate + "*" + statement
    # print("filePattern", filePattern)

    commandStrForDownload = filePattern

    # execute all line in exec_command
    stdin, stdout, stderr = SSH_Client.exec_command(commandStrForDownload)
    # print("stdout", stdout.readlines())

    # read the each line of file
    getCustomApiResponse = stdout.readlines()  # ['250\n']
    # print("getApiResponse", getApiResponse)

    dataList = {}
    for eachLine in getCustomApiResponse:
        lineInStringFormat = eachLine
        lineInStringFormat = lineInStringFormat.strip()
        eachlineInArrayFormat = lineInStringFormat.split(",")
        # print("eachlineInArrayFormat", eachlineInArrayFormat)

        try:
            getUniqueId = eachlineInArrayFormat[25]
        except IndexError:
            getUniqueId = ""
            print("The index number is out of range.")
        # getImsiId = eachlineInArrayFormat[25] # 521234567

        getProfileStatus = eachlineInArrayFormat[23]  # download profile # active profile

        try:
            getExecutedSuccess = eachlineInArrayFormat[21]
        except IndexError:
            getExecutedSuccess = ""
            print("The index number is out of range.")

        # getExecutedSuccess = eachlineInArrayFormat[21]
        getExecutedSuccess = getExecutedSuccess.strip()  # download profile # active profile

        # print("array >>", eachlineInArrayFormat)
        downloadLinkUrl = eachlineInArrayFormat[18]
        getStartDate = downloadLinkUrl[-21:-2]
        getEndDate = downloadLinkUrl[-21:-2]
        getMessageDate = eachlineInArrayFormat[180]
        getSuccessDate = getMessageDate[-21:-2]
        getLastDate = getMessageDate[-21:-2]

        uniqueObject = {
            "downloadCnt": 0,
            "activeCnt": 0
        }

        # check unique object exist in a list
        if getUniqueId in dataList:
            # unique object already exists in a list so updating existing
            uniqueObject = dataList[getUniqueId]
            # print(uniqueObject)
        else:
            uniqueObject = {
                "downloadCnt": 0,
                "activeCnt": 0
            }

        # adding required properties in an object
        uniqueObject["id"] = getUniqueId

        print("getProfileStatus", getProfileStatus)
        if getProfileStatus == "downloadCustomProfileResponse":
            uniqueObject["downloadProfile"] = getProfileStatus
            uniqueObject["downloadEndDate"] = getEndDate  # 2024-03-04T02:31:47
            uniqueObject["dwlastDate"] = getLastDate  # message date 2024-03-04T02:31:47

            print("adding download count...")
            if "downloadCnt" in uniqueObject:
                uniqueObject["downloadCnt"] = uniqueObject["downloadCnt"] + 1
            else:
                uniqueObject["downloadCnt"] = 1

            # print("downloadStartDate not in uniqueObject", "downloadStartDate" not in uniqueObject)

            if "downloadStartDate" not in uniqueObject:
                uniqueObject["downloadStartDate"] = getStartDate  # 2024-03-04T02:31:47

        if getProfileStatus == "activeCustomProfileResponse" or getProfileStatus == "inactiveCustomProfileResponse":
            print("Checking active status ...")
            if getExecutedSuccess == "EXESUCCESS" or getExecutedSuccess == "EXPIRED" or getExecutedSuccess == "FAILED":
                print("Checking active status complete...")
                uniqueObject["activeProfile"] = getProfileStatus
                uniqueObject["acEndDate"] = getEndDate  # 04-03-2024 # 2024-03-04T02:31:47
                uniqueObject["acsuccessDate"] = getSuccessDate  # message Date

                print("adding active count...")
                if "activeCnt" in uniqueObject:
                    uniqueObject["activeCnt"] = uniqueObject["activeCnt"] + 1
                else:
                    uniqueObject["activeCnt"] = 1

                if "activeStartDate" not in uniqueObject:
                    uniqueObject["activeStartDate"] = getStartDate  # 04-03-2024 # 2024-03-04T02:31:47

            else:
                uniqueObject["activeCnt"] = 1
                print("Checking active status failed...")

        # final updating entry of unique in a list
        dataList[getUniqueId] = uniqueObject

        # forloop end

        # print("dataList", dataList)
        uniqueFinalDataListArray = []
        for uniqueID in dataList:
            row = [dataList[uniqueID]]
            uniqueFinalDataListArray.append(row)
            # print("uniqueFinalDataListArray", uniqueFinalDataListArray)

        finalArray = []
        for uniqueID in dataList:
            newuniqueObj = dataList[uniqueID]
            # print("newuniqueObj", newuniqueObj)

            if "id" in newuniqueObj:
                id = newuniqueObj["id"]
            else:
                id = "NA"

            if "downloadProfile" in newuniqueObj:
                downloadProfile = newuniqueObj["downloadProfile"]
            else:
                downloadProfile = "NA"

            if "downloadEndDate" in newuniqueObj:
                downloadProfile = newuniqueObj["downloadEndDate"]
            else:
                downloadProfile = "NA"

            if "dwlastDate" in newuniqueObj:
                dwlastDate = newuniqueObj["dwlastDate"]
            else:
                dwlastDate = "NA"

            if "downloadCnt" in newuniqueObj:
                downloadCnt = newuniqueObj["downloadCnt"]
            else:
                downloadCnt = 0

            if "downloadStartDate" in newuniqueObj:
                downloadStartDate = newuniqueObj["downloadStartDate"]
            else:
                downloadStartDate = "NA"

            if "activeProfile" in newuniqueObj:
                acdownloadProfile = newuniqueObj["activeProfile"]
            else:
                acdownloadProfile = "NA"

            if "acEndDate" in newuniqueObj:
                acEndDate = newuniqueObj["acEndDate"]
            else:
                acEndDate = "NA"

            if "acsuccessDate" in newuniqueObj:
                acsuccessDate = newuniqueObj["acsuccessDate"]
            else:
                acsuccessDate = "NA"

            if "activeCnt" in newuniqueObj:
                activeCnt = newuniqueObj["activeCnt"]
            else:
                activeCnt = 0

            if "activeStartDate" in newuniqueObj:
                activeStartDate = newuniqueObj["activeStartDate"]
            else:
                activeStartDate = "NA"

            totalCnt = downloadCnt + activeCnt
            # print("downloadCnt, activeCnt, totalCnt", downloadCnt, activeCnt, totalCnt)

            if totalCnt == 0:
                totalCnt = 1

            row = [id, downloadProfile, downloadEndDate, dwlastDate, downloadCnt, downloadStartDate, acdownloadProfile, acEndDate, acsuccessDate, activeCnt, activeStartDate, totalCnt]
            finalArray.append(row)
            # print("finalArray", finalArray)

        htmlDataArray = []
        mergeStr = ""
        for rowDataArray in finalArray:
            print("rowDataArray", rowDataArray)
            getDwlEnbUniqueIdData = rowDataArray[10]
            getUniqueProfileStatus = rowDataArray[11]
            getDwlActTotalAttempt = rowDataArray[12]
            getDwlFirstAttemptDate = rowDataArray[13]
            getActFirstAttemptDate = rowDataArray[14]
            getDwlLastAttemptDate = rowDataArray[15]
            getActLastAttemptDate = rowDataArray[16]
            getDwlSuccessDate = rowDataArray[17]
            getActSuccessDate = rowDataArray[18]
            getActiveEndDate = rowDataArray[19]
            getActstartDate = rowDataArray[20]

            firstAttempt = getDwlFirstAttemptDate
            if firstAttempt == "NA":
                firstAttempt = getActLastAttemptDate

            lastAttemptDate = getActLastAttemptDate
            if lastAttemptDate == "NA":
                lastAttemptDate = getDwlLastAttemptDate

            successDate = getActSuccessDate
            print("successDate", successDate)

            dwlMergeArr = [getDwlActUniqueIdData, getDwlActTotalAttempt, getDwlFirstAttemptDate, getDwlLastAttemptDate, getActSuccessDate]

            actMergeArr = [getDwlActUniqueIdData, getDwlActTotalAttempt, getActiveEndDate, getActSuccessDate, getActSuccessDate]

            finalOutputArr = [getDwlActUniqueIdData, getDwlActTotalAttempt, firstAttempt, lastAttemptDate, successDate]

            htmlDataArray.append(finalOutputArr)

        if len(htmlDataArray) == 0:
            dwmergeStr = "No data found"
            acmergeStr = "No data found"

        # print("htmlDataArray", htmlDataArray)

        SSH_Client.close()
        print("socket connection closed for Server")
    # end remote file
except EOFError as e:
    print("Something went wrong for server", e)

# ----------------------------
#   Configure mail
# ----------------------------
# Read config file
print("reading config parser of smtp mail server")
smtpServer = config.get("email", "smtpServer")
emailFROM = config.get("email", "emailFROM")
emailTo = config.get("email", "emailTo")
emailCc = config.get("email", "emailCc")
emailLogo = config.get("email", "emailLogo")

# setup port number and server name
smtp_server = smtpServer
emailFrom = emailFROM
emailTo = emailTo.split(",")
emailCc = emailCc.split(",")
subject = 'Profile Download'

# Textual month, day and year
print("The date used as per format for mail")
mdate = yesterday.strftime("%d")
fromdateOrdinal = ordinal(int(mdate))
dateFormatForMail = datetime.strptime(str(yesterday), '%Y-%m-%d')  # Get today - 1 day i.e, 2023-12-21 00:00:00
print(dateFormatForMail)
fromdateFormat = datetime.strptime(str(dateFormatForMail), '%Y-%m-%d %H:%M:%S').strftime(f"{fromdateOrdinal} %B %Y")


def send_emails(emailTo):
    # make a MIME Object to define parts of the email
    msg = EmailMessage()
    msg['from'] = emailFrom
    msg['to'] = ", ".join(emailTo)
    msg['cc'] = ", ".join(emailCc)
    msg['subject'] = subject

    # update code for email signature--------
    img_path = emailLogo  # Path to img you are appending to the end of the email
    image_id = make_msgid()

    htmlStart = """<html>
                <head></head>
                <body>
                    <p>Dear All,</p>
                    <p>Please find the below details for Profile download """ + str(fromdateFormat) + """</p>"""

    htmlTableStructureFirstRow = """<p style="font-weight: bold;>Download Profile details: </p><br>
                    <table style="background-color:#d9d9d9; border: 1px inset black;white-space: nowrap; cellspacing="3" cellpadding="0">
                        <tr>
                            <th style="background-color: #00008B;text-color: #fff; border: 1px solid #00008;">UniqueID</th>
                            <th style="background-color: #00008B;text-color: #fff; border: 1px solid #00008;">Total Attempt</th>
                            <th style="background-color: #00008B;text-color: #fff; border: 1px solid #00008;">First Attempt Date</th>
                            <th style="background-color: #00008B;text-color: #fff; border: 1px solid #00008;">Last Attempt Date</th>
                            <th style="background-color: #00008B;text-color: #fff; border: 1px solid #00008;">Success Date</th>
                        </tr>"""

    htmlDownloadDetails = ""
    for eachRowDataArray in htmlDataArray:
        htmlTd = ""
        for columndata in eachRowDataArray:
            htmlTd = htmlTd + "<td style='background-color:#FEFEFA;padding: 10px;border: 1px solid #00008B;'>" + str(columndata) + "</td>"
        htmlDownloadDetails = htmlDownloadDetails + "<tr>" + htmlTd + "</tr>"
    # end for loop

    htmlTableStructure = """<table border="0" cellspacing="3" cellpadding="0" width="0">
                    <tbody>
                        <tr>
                            <td width="112" style="width:84.0pt; padding: .75pt .75pt .75pt .75pt;">
                                <u></u>
                                    <img width="102" height="71" src="cid:{image_id}">
                                <u></u>
                            </td>
                            <td>
                                <span></span>
                                <span></span>
                            </td>
                            <td width="272" style="width:204.0pt;border:none;border-left:solid #1486ed 1.5 pt;padding:.75pt .75pt .75pt .75pt">
                                <span style="font-size:9.5pt;font-family:&quot;sans-serif;color:#404040;margin-left:5px;"></span>
                                <span style="font-size:9.5pt;font-family:&quot;sans-serif;color:#404040;margin-left:5px;"></span>
                                <span style="font-size:9.5pt;font-family:&quot;sans-serif;color:#404040;margin-left:5px;"></span>
                                <span style="font-size:9.5pt;font-family:&quot;sans-serif;color:#404040;margin-left:5px;"></span>
                            </td>
                        </tr>
                    </tbody>
                </table>"""

    htmlNoticeTips = """<div style="background-color: yellow; display: inline-block;">Note: This is an automatically generated email by automationScript</div>"""

    htmlEnd = """</body></html>"""

    emailHtml = htmlStart + htmlTableStructureFirstRow + htmlDownloadDetails + htmlTableStructure + htmlNoticeTips + htmlEnd

    msg.add_alternative(emailHtml.format(image_id=image_id[1:-1]), subtype='html')
    # Note that we needed to peel <> off the msg-id for use in the html
    # Now add the related image to the html part.
    with open(img_path, 'rb') as img:
        msg.get_payload()[0].add_related(img.read(), 'image', 'png', cid=image_id)
    # end email signature template----------

    # Cast as string
    try:
        text = msg.as_string()
        print("connecting to server...")
        TIE_server = smtplib.SMTP(smtp_server)
        print("Successfully connected to server :-) ")
        print()
        # send emails to "allEmail" as a list is iterated
        print(f"Sending email To - {emailTo}")
        print(f"Sending email Cc - {emailCc}")
        TIE_server.sendmail(emailFrom, (emailTo + emailCc), text)
        print(f"Email sent To - {emailTo}")
        print(f"Email sent To - {emailCc}")
        print()
        TIE_server.quit()
    except socket.error as errmsg:
        print(errmsg, "Could not connect to server")


send_emails(emailTo)
#   end mail function >>>>>
# countDownloadedProfileWithSameID
# countDownloadedProfileWithSameID
