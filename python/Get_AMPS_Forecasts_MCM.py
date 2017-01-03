#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 08:50:40 2016

@author: Mark Dalberth

This script will download forecasts from the Antarctic Mesoscale Prediction System's
website and save them into the folder e:\AMPSForecasts. Three different grids are
downloaded - 3km, 9km, and 10km. These are then attached to an email and sent to an
email list. The list is in the variable 'toaddr' down below.

I let this run for a while and sometimes the 10km forecasts would not be complete
when the email went out. I asked Kevin Manning at ucar, and he said that there is
a file on the website (METEOGRAMS_ARE_DONE) that will tell you if the meteograms are ready.
I rewrote the script to look for that file.

This version of the script is meant to be started by the Task Scheduler and then
the timing is done by the script itself. This eliminates the need for an external log file
that keeps track of the number of iterations. Also, this way the script can just
end when the files are downloaded.
"""
#The 'requests' module can read url's
import requests
#datetime is used to get dates in various formats
import datetime
#The time module is used for its 'sleep' function.
import time

#This is the path where the forecasts will be saved.
#path = "E:\\AMPSForecasts\\"
path = '/home/markd/www/static/images/'
#this is the network drive
#networkdrive = '\\\\edisto\\charts\\'

#This version of the script replaces the log file with a list (called log).
#Use the time module to time the delay between download attempts.
log = [0,404]

#maxiteration is the max number of times the script will loop.
maxiteration = 10
#delay is the length in seconds that the script will wait before trying again.
delay = 600

#Print this statement so that people looking at PAWS will know why the
#script window is open
print('''This is the script that retrieves the AMPS forecasts for McMurdo. It checks for the \n\r\
meteograms to be complete and then downloads them.\n\n\r\
It will exit after %s minutes if no meteograms are found.\n\n\r''' % ((maxiteration+1)*delay/60))

#404 means that the web page was not found.
while log[1] == 404 :

    #If log[1] is '404' then either this is the first time
    #the script has been run today or the the METOGRAMS_ARE_DONE file
    #did not exist the last time we looked.

    print('Looking to see if 10 km meteograms are done...')
    #Next, I generate two different dates. today1 is used in the url for the forecasts.
    #today2 is used in the text of the email message.
    today1 = datetime.datetime.utcnow().strftime('%Y%m%d')
    today2 = datetime.date.today().isoformat()
    #The following three lines are for testing purposes...
#    testtime = datetime.datetime.utcnow()-datetime.timedelta(hours=16)
#    today1 = testtime.strftime('%Y%m%d')
#    today2 =  testtime.strftime('%Y-%m-%d')



    #Use the url below to check if the meteograms are ready. The 10 km one takes the
    #longest out of the 3km, 9km and 10km. Look for the file METEOGRAMS_ARE_DONE
    url_10km_exist = 'http://www2.mmm.ucar.edu/rt/amps/wrf_plots/'+today1+'00/10km/meteogram/METEOGRAMS_ARE_DONE'
    r_exists = requests.get(url_10km_exist)

    #If r_exists.status_code == 200 then file METEOGRAMS_ARE_DONE exists.
    #We can download the image files
    if r_exists.status_code == 200 :
        print('Meteograms are done. Download files...')
        #set log[1] = 200 to stop the while loop
        log[1] = 200
        log[0] += 1

        #subprocess.call will be used to copy the images onto the network
        #from subprocess import call

#        #Now, import the modules needed to send the email
#        #smtplib actually sends the email
#        import smtplib
#        #The next three MIME packages are used to construct the email.
#        from email.mime.multipart import MIMEMultipart
#        from email.mime.text import MIMEText
#        from email.mime.image import MIMEImage

        #create the function 'get_image'....
        def get_image(url, file):
            "function to go to a url for an image file and save the image to the provided filename"
            r = requests.get(url)
            #Create the file that will hold the image and then save the image into the file
            imagefile = open(file, 'wb')
            for chunk in r.iter_content(100000):
                imagefile.write(chunk)
            imagefile.close()


#        # Set up some variables used in the script...
#        mailserver = 'mail.palmer.usap.gov'
#        fromaddr = 'noreply@usap.gov'
#        toaddr = ['pal.ra@usap.gov',
#            'nandor.kovats.contractor@usap.gov',
#            'PalmerMarineTechnician@usap.gov',
#            'Palmer.CommsTech@usap.gov',
#            'farrysc@hotmail.com',
#            'BPCFX7@gmail.com',
#            'mcateecarrie@gmail.com',
#            'erin.p.pickett@gmail.com',
#            'logan.pallin@gmail.com',
#            'ryanyoung1@usf.edu',
#            'bjbaker@usf.edu',
#            'mamsler@uab.edu']

        #Set up the urls for the 3km, 9km and 10km grid forecasts, and the filenames to store the .png's
        url_3km = 'http://www2.mmm.ucar.edu/rt/amps/wrf_plots/' + today1 +'00/3km/meteogram/mcm.png'
        forecast_3km = 'mcm_3km.png'

        url_10km = 'http://www2.mmm.ucar.edu/rt/amps/wrf_plots/'+today1+'00/10km/meteogram/mcm.png'
        forecast_10km = 'mcm_10km.png'

        print('Getting the images...')
        get_image(url_3km, path+forecast_3km)
        get_image(url_10km, path+forecast_10km)
        print('Done.')

#        #save the .png files to edisto\charts (z:\) so they will appear on the intranet.
#        call(['copy', path+'AMPS*.png', networkdrive], shell = True)
#
#        #Construct the email message...
#        msg = MIMEMultipart()
#        msg['From'] = fromaddr
#        msg['To'] = ', '.join(toaddr)
#        msg['Subject'] = 'AMPS Forecast for ' + today2
#
#        body = "Here are the AMPS forecasts generated for 12:00 UTC " + today2 + \
#        ".\r\nThe 3km forecast goes out 39 hours, 9km 3 days, and 10km 5 days.\n\n\rTalk to the RA to be removed from this email list (pal.ra@usap.gov)." + \
#        "\n\n\rThese will be emailed once per day when the calculations for the 12:00 UTC forecast are complete."
#        msg.attach(MIMEText(body, 'plain'))
#
#        #Read the image for 3km meteogram into 'img', add the header (this sets the filename
#        #of the attachment), then attach img to the message.
#        with open(path+forecast_3km, 'rb') as fp:
#            img = MIMEImage(fp.read())
#        img.add_header('Content-Disposition', 'attachment', filename = forecast_3km)
#        msg.attach(img)
#
#        #Repeat for 9km forecast
#        with open(path+forecast_9km, 'rb') as fp:
#            img = MIMEImage(fp.read())
#        img.add_header('Content-Disposition', 'attachment', filename = forecast_9km)
#        msg.attach(img)
#
#        #Repeat for the 10km meteogram
#        with open(path+forecast_10km, 'rb') as fp:
#            img = MIMEImage(fp.read())
#        img.add_header('Content-Disposition', 'attachment', filename = forecast_10km)
#        msg.attach(img)
#
#        #Now, send the email that was just constructed...
#        print('Sending email...')
#        server = smtplib.SMTP(mailserver)
#        server.send_message(msg)
#        server.quit()
#        print('Done.')
#
#        #Run Get_AMPS_charts.py. This retrieves the weather charts and makes a movie from them.
#        #The exec function executes a series of pythons statements, so this command
#        #opens the file 'Get_AMPS_Charts.py', reads it and then executes the
#        #statements.
#        exec(open('e:\\scripts\\Python\\Get_AMPS_Charts.py').read())

    elif r_exists.status_code == 404:
        print('Meteograms are not done. Wait %s minutes. \titeration= %s\tstatus= %s' % (delay/60, log[0], log[1]))
        #Increment the counter in log
        if log[0] == maxiteration :
            print('The 10 km meteogram is not done after %s iterations. Ending the loop.' % (maxiteration+1 ))
            break
        #increment the counter in the variable log for the next iteration.
        log[0] += 1
        time.sleep(delay)

