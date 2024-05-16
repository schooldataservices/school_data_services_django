import smtplib
from email.message import EmailMessage
import logging
import pandas as pd
import numpy as np
import time
import os
from datetime import datetime
import pytz
import time
import base64
import importlib
import ast 
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)



class SendMail:


    def get_smtp_connection(EMAIL_ADDRESS_FROM, EMAIL_PASS):
        # Establish the SMTP connection
        smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp.login(EMAIL_ADDRESS_FROM, EMAIL_PASS)
        logging.info('SMTP connection created')
        return(smtp)
    
    def pass_in_png(png_path):
            # Read the PNG file as binary data and encode it g base64
        png_file_path = f'PNGs/{png_path}.png'
        try:
            with open(png_file_path, 'rb') as f:
                image_data = f.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')
        except FileNotFoundError:
            image_base64 = ''

        return(image_base64)


# -------------------------------------------------------------------------------------------

    #Different logic, output.csv is not created yet. It is at the point of blasting the first 5-. 
    #get next 50 is modified with a try except where the except simply gets the first 50. 
    #Attempts to read from the output.csv everytime   

    def get_next_50(df):

        try:    
            email_history = pd.read_csv(os.getcwd() + '\\output.csv')

            last_email_sent = email_history['contact_email'].iloc[-1]
                
            # Find the index in df where the 'email' column matches the last_email_sent
            index_to_start = df[df['email'] == last_email_sent].index.max() + 1

            if np.isnan(index_to_start):    #So if index_to_start is nan. Then let df be itself. 
                print('Could not match last email sent to master frame, proceeding with original frame')
                df_remaining = df
            else:
                print("Matched last email sent to master frame, proceding from last email sent")
                # # Process df starting from the index_to_start
                df_remaining = df.loc[index_to_start: index_to_start + 50]

        except FileNotFoundError:
            print('Output is not created, first run of 50 emails preparing to be sent')
            logging.info('Output is not created, first run of 50 emails preparing to be sent')

            #Process df starting from the index_to_start
            df_remaining = df.iloc[0:50]

        except TypeError:
            
            #email where final send was left off can not be matched up in the original df
            print('Email where final send was left off can not be matched up in the original df. Frame is empty')
            logging.info('Email where final send was left off can not be matched up in the original df. Frame is empty')
            #create empty frame to return
            df_remaining = pd.DataFrame()

        return(df_remaining)
    # ------------------------------------------------------


    def send(email_config, email_contact, SMTP_CONN,  **kwargs):

        print(f"here is the email_config dict passed in {email_config}")

        #This can not be configured as a dict, because of SMTP conn and template func
        EMAIL_ADDRESS_FROM = email_config['EMAIL_ADDRESS_FROM']
        EMAIL_PASS = email_config['EMAIL_PASS']
        email_subject_line = email_config['email_subject_line']
    
        #establish the template based on the config file template_str
        premade_templates = email_config['premade_templates']
        template_name = f"emailscraper_app.modules.Sending_Emails.html_email_strings.{premade_templates}"
        module = importlib.import_module(template_name)
        template = module.get_template

        #if this template_str is empty, then refer to the contents in the HTML box. 

        #For now over-ride the template here by calling it from email_config in a different variable
        template = email_config['email_content']
        print(template)


        msg = EmailMessage()
        msg['From'] = EMAIL_ADDRESS_FROM
        msg['To'] = email_contact
        msg['Subject'] = email_subject_line    #This can be formatted to iterate the subject line based on the send with an f string

        #kwargs adds in additional adlibs columns into the template if specified in config variable
        # body = template(**kwargs) 
        body = template

        # Set the content as HTML
        msg.set_content(body, subtype='html')

        try:
            SMTP_CONN.send_message(msg)

        except smtplib.SMTPConnectError as e:
            print(f'SMTP Connection Error: {e}')
            time.sleep(10)

            SMTP_CONN_2 = SendMail.get_smtp_connection(EMAIL_ADDRESS_FROM, EMAIL_PASS)

            if SMTP_CONN_2:
                SMTP_CONN_2.send_message(msg)
                
        except smtplib.SMTPRecipientsRefused as e:
            # Handle the specific exception
            print(f"Recipient error for {email_contact}: {e}")



    def test_func(test, df):


        if test == True:
            df.at[0, 'email'] = '2015samtaylor@gmail.com'
            df.at[1, 'email'] = 'sammytaylor2006@yahoo.com'
            df.at[2, 'email'] = 'jerrybons2006@gmail.com'
            df = df[:2]
            logging.info('Test argument is True, cutting down frame and sending to personal emails')
            print('Test argument is True, cutting down frame and sending to personal emails')
        else:
            pass

        return(df)
        


    def process(df, email_config, test=False):

        print(f"here is the email_config dict passed into process {email_config}")

        #next 50 must be passed in as the df, otherwise it will keep running

        EMAIL_ADDRESS_FROM = email_config['EMAIL_ADDRESS_FROM']
        EMAIL_PASS = email_config['EMAIL_PASS']
        contact_column = email_config['contact_column']
        sport = email_config['sport']
        email_campaign_name = email_config['email_campaign_name']
        email_subject_line = email_config['email_subject_line']
        optional_iterated_columns_str = email_config['optional_iterated_columns']
        optional_iterated_columns = ast.literal_eval(optional_iterated_columns_str)

        #establish SMTP conn based on variables in config, passed into send function. Lasts throughout send. If fails re-configures within send
        SMTP_CONN = SendMail.get_smtp_connection(EMAIL_ADDRESS_FROM, EMAIL_PASS) #Established in view click button

        #create the test right here with a True False flag. 
        #Then limit it to two. And send to self
        data_list = []
        processed_emails = set()

        #returns subsidized portion of the df if arg it True
        df = SendMail.test_func(test, df)

        #Limit df itterrows to test
        for index, row in df.iterrows():

            #Establish concrete args
            central_time_zone = pytz.timezone('America/Chicago')
            now_central = datetime.now(central_time_zone)
            formatted_date = now_central.strftime("%m/%d/%Y")
            email_contact = row[contact_column] #should always be 'email' column name
    
            # Check if the email has already been processed once
            if email_contact in processed_emails:
                print(f"Skipping email to {email_contact} as it has already been processed.")
                continue
            
            #There four columns are necessary, everything else is for the send. Mark email as processed
            data = [email_contact, sport, formatted_date]
            data_list.append(data)
            processed_emails.add(email_contact)


            kwargs = {'sport': sport}
            if optional_iterated_columns:
                # Iterate through optional_iterated_columns and add them to kwargs
                for column_name in optional_iterated_columns:

                    if column_name in row: #check if column name exists in the row data

                        kwargs[column_name] = row[column_name]

                    else:
                        print(f'Column {column_name} does not exist in the DataFrame row')

                    #optional kwargs get passed into send, which are passed into template. Then are called upon through dict format

            SendMail.send(email_config, email_contact, SMTP_CONN, **kwargs)

        
        #contact_email is how the get_next_50 finds where it left off
        
        data_list = pd.DataFrame(data_list, columns=['Contact', 'Sport', 'Date_Sent'])

        data_list.rename(columns = {'Contact': 'contact_email', 'Date_Sent': 'date_sent', 'Sport': 'sport'}, inplace = True)
        data_list['date'] = data_list['date_sent'].astype(str)

        #Adding in additional columns from the config class
        data_list['subject'] = email_subject_line
        data_list['position'] = contact_column
        data_list['from'] = EMAIL_ADDRESS_FROM
        data_list['email_campaign_tag'] = email_campaign_name
        data_list['date'] = now_central.strftime("%Y-%m-%d %H:%M:%S")

        #This is present in case the process breaks it knows where to resume
        data_list.to_csv('output.csv', index=False)

        return(data_list)





#General Notes

#Sends 1300 emails in 45 mins
#Limit to 1500 emails per day
#Anything over 2000 the entire account gets locked for 24 hours. 
#Limits to 2000 emails per day
# SMTPDataError: (550, b'5.4.5 Daily user sending limit exceeded. For more information on Gmail\n5.4.5 sending limits go to\n5.4.5  https://support.google.com/a/answer/166852 w4-20020a4ae9e4000000b005914f455774sm848190ooc.34 - gsmtp')

