
from cv2 import preCornerDetect


def reminder(name,product,expiry,email,phone):
    message = "Hello %s!\nYour product %s is about to expire on %s\n This is a reminder to use it in time." % (name,product,expiry)
    emails = [email]
    numbers = [phone]

    for i in numbers:
        import requests
        url = "https://www.fast2sms.com/dev/bulk"
        payload = "sender_id=FSTSMS&message="+message+"&language=english&route=p&numbers=" + str(i)
        headers = {
        'authorization': "zOt4BpJjlwbdV805h62IUgHnACxQXrmTPSevRauE1ycs9WoY7LsQS5khPmERgdCaqvboDXUuBrLl207f",
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "no-cache",
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        print(response.text)


    for i in emails:
        # Python code to illustrate Sending mail from
        # your Gmail account
        import smtplib

        # creates SMTP session
        s = smtplib.SMTP('smtp.gmail.com', 587)

        # start TLS for security
        s.starttls()

        # Authentication
        s.login("plaser.reminders@gmail.com", "penguinputhige")

        # message to be sent
        # message = "Message_you_need_to_send"

        # sending the mail
        s.sendmail("plaser.reminders@gmail.com", i, message)

        # terminating the session
        s.quit()
