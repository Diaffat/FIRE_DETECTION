from flask import Flask, render_template, Response, stream_with_context, url_for, request
import cv2         # Library for openCV
import threading   # Library for threading -- which allows code to run in backend
import playsound   # Library for alarm sound
import smtplib     # Library for email sending
import imutils
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import os

app = Flask(__name__)
# To access xml file which includes positive and negative images of fire. (Trained images)
fire_cascade = cv2.CascadeClassifier('fire_detection_cascade_model.xml')


# To start camera this command is used "0" for laptop inbuilt camera and "1" for USB attahed camera for pc
runOnce = False  # created boolean

def SendIp(request):
   ip=request.POST
   return ip
 
video = cv2.VideoCapture(0)

def play_alarm_sound_function():  # defined function to play alarm post fire detection using threading
    # to play alarm # mp3 audio file is also provided with the code.
    playsound.playsound('Alarm Sound.mp3', True)
    print("Fire alarm end")  # to print in console


def send_mail_function():  # defined function to send mail post fire detection using threading

    recipientmail = "fatoumatasoukouradiassana18@gmail.com"  # recipients mail
    recipientmail = recipientmail.lower()  # To lower case mail

    try:
        filename = "fire.png"
        with open(filename, 'rb') as f:
            img = f.read()
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        msg = MIMEMultipart()
        text = MIMEText(
            "Fire signalisation !!!")
        msg.attach(text)
        image = MIMEImage(img, name=os.path.basename(filename))
        msg.attach(image)
        server.login("fatoumatasoukouradiassana18@gmail.com",
                     'raoe pzrh tkvo bizo')  # Senders mail ID and password
        server.sendmail('f.diassana@edu.umi.ma.ac', recipientmail,
                        msg.as_string())  # recipients mail with mail message
        # to print in consol to whome mail is sent
        print("Alert mail sent sucessfully to {}".format(recipientmail))

        server.close()  # To close server

    except Exception as e:
        print(e)  # To print error if any


def gen(video):
    global outputFrame, lock
    while(True):
        Alarm_Status = False
        ret, frame =video.read()  # Value in ret is True # To read video frame
        if not ret:
            break
        else:
            frame = imutils.resize(frame, width=400)
            # To convert frame into gray color
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            fire = fire_cascade.detectMultiScale(
                frame, 1.2, 5)  # to provide frame resolution

            # to highlight fire with square
            for (x, y, w, h) in fire:
                cv2.rectangle(frame, (x-20, y-20),
                              (x+w+20, y+h+20), (255, 0, 0), 2)
                cv2.putText(frame, "FIRE", (x, y-10), cv2.FONT_HERSHEY_PLAIN,
                            3, color=(0, 0, 255), thickness=2)
                cv2.imwrite("fire.png", frame)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]

                print("Fire alarm initiated")
                # To call alarm thread
                threading.Thread(target=play_alarm_sound_function).start()
                global runOnce
                if runOnce == False:
                    print("Mail send initiated")
                    # To call alarm thread
                    threading.Thread(target=send_mail_function).start()
                    runOnce = True
                if runOnce == True:
                    print("Mail is already sent once")
                    runOnce = True
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield(b'--frame\r\n'
                  b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    video.release()
    cv2.destroyAllWindows()
def close(video):
    video.release() 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed/')
def video_feed():
    video
    return Response(gen(video),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=2204, threaded=True)
