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
import warnings
from emailscraper_app.models import RecordingEmailRecipients
warnings.filterwarnings('ignore', category=FutureWarning)



class SendMail:


    def get_smtp_connection(EMAIL_ADDRESS_FROM, EMAIL_PASS):
        # Establish the SMTP connection
        try:
            smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtp.login(EMAIL_ADDRESS_FROM, EMAIL_PASS)
            logging.info('SMTP connection created')
            return(smtp)
        except Exception as e:
            logging.error('Unable to establish SMTP connection due to {e}')
 
    
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
    @staticmethod
    def get_next_50(df, email_config):


        email_contact = email_config['contact_column']

        try:    
            email_history = pd.read_csv(os.getcwd() + '\\output.csv')

            #This always needs to be 'contact_email' to refer to output.csv
            last_email_sent = email_history['contact_email'].iloc[-1]
                
            # Find the index in df where the 'email' column matches the last_email_sent
            index_to_start = df[df[email_contact] == last_email_sent].index.max() + 1

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

        #This can not be configured as a dict, because of SMTP conn and template func
        EMAIL_ADDRESS_FROM = email_config['EMAIL_ADDRESS_FROM']
        EMAIL_PASS = email_config['EMAIL_PASS']
        email_subject_line = email_config['email_subject_line']
        contact_column = email_config['contact_column']
        template = email_config['email_content']

           # Log critical values
        logging.info(f"EMAIL_ADDRESS_FROM: {EMAIL_ADDRESS_FROM}")
        logging.info(f"email_contact (recipient): {email_contact}")
        logging.info(f"contact_column: {contact_column}")
        logging.info(f"email_subject_line: {email_subject_line}")
        logging.info(f"Email content (template): {template}")


        # Check for None or invalid values
        if any(v is None for v in [EMAIL_ADDRESS_FROM, email_contact, email_subject_line, template, SMTP_CONN]):
            logging.error("One or more required parameters are None. Aborting send.")
            return

        if not template.strip():
            logging.error("Template content is empty. Aborting send.")
            return
        
      

    
        #establish the template based on the config file template_str
        # premade_templates = email_config['premade_templates']
        # template_name = f"emailscraper_app.modules.Sending_Emails.html_email_strings.{premade_templates}"
        # module = importlib.import_module(template_name)
        # template = module.get_template
        #if this template_str is empty, then refer to the contents in the HTML box. 
        #For now over-ride the template here by calling it from email_config in a different variable
      

        msg = EmailMessage()
        msg['From'] = EMAIL_ADDRESS_FROM
        msg['To'] = email_contact
        msg['Subject'] = email_subject_line    #This can be formatted to iterate the subject line based on the send with an f string


        # logging.info(f"Sending email: From={msg['From']}, To={msg['To']}, Subject={msg['Subject']}, Body={msg.get_content()}")


          # Set the content as HTML
        try:
            msg.set_content(template, subtype='html')
            logging.info("Content successfully set")
        except Exception as e:
            logging.error(f"Failed to set email content: {str(e)}")
            return


        
        try:
            SMTP_CONN.send_message(msg)
            logging.info(f'Message has been sent to {EMAIL_ADDRESS_FROM}')

        except smtplib.SMTPConnectError as e: #For resetting the connection
            logging.info(f'SMTP Connection Error: {e}')
            time.sleep(10)

            SMTP_CONN_2 = SendMail.get_smtp_connection(EMAIL_ADDRESS_FROM, EMAIL_PASS)

            if SMTP_CONN_2:
                SMTP_CONN_2.send_message(msg)
                
        except smtplib.SMTPRecipientsRefused as e:
            # Handle the specific exception
            print(f"Recipient error for {email_contact}: {e}")

        except Exception as e:
            logging.error('The emails are failing to send due to {e}')



    def test_func(test, df, contact_column):


        if test == True:
            df.at[0, contact_column] = '2015samtaylor@gmail.com'
            df.at[1, contact_column] = 'sammytaylor2006@yahoo.com'
            df.at[2, contact_column] = 'jerrybons2006@gmail.com'
            df = df[:2]
            logging.info(f'Test argument is True, cutting down frame and sending to personal emails, and sending off of the {contact_column}')
        else:
            pass

        return(df)
        

    def provide_formatted_date():
        central_time_zone = pytz.timezone('America/Chicago')
        now_central = datetime.now(central_time_zone)
        formatted_date = now_central.strftime("%Y-%m-%d %H:%M:%S")
        return(formatted_date)



    def process(df, email_config, user, test):
        logging.info(f"Email config dict passed into process: {email_config}")

        EMAIL_ADDRESS_FROM = email_config['EMAIL_ADDRESS_FROM']
        EMAIL_PASS = email_config['EMAIL_PASS']
        contact_column = email_config['contact_column']
        email_campaign_name = email_config['email_campaign_name']
        email_subject_line = email_config['email_subject_line']

        # Establish SMTP connection
        SMTP_CONN = SendMail.get_smtp_connection(EMAIL_ADDRESS_FROM, EMAIL_PASS)

        # Track processed emails to avoid duplicates
        processed_emails = set()
        email_records = []

        # Apply test function if needed
        df = SendMail.test_func(test, df, contact_column)

        # Process rows in DataFrame
        for index, row in df.iterrows():
            email_contact = row[contact_column]

            # Skip already processed emails
            if email_contact in processed_emails:
                logging.info(f"Skipping email to {email_contact} as it has already been processed.")
                continue
            
            # Send email
            try:
                SendMail.send(email_config, email_contact, SMTP_CONN)
                logging.info('Calling SendMail.send method')

                #Only append record to email_records if the send is succesful
                email_record = RecordingEmailRecipients(
                    creator_id=user,
                    email_recipient=email_contact,
                    date_sent=SendMail.provide_formatted_date(),
                    subject=email_subject_line,
                    contact_column=contact_column,
                    from_email=EMAIL_ADDRESS_FROM,
                    email_campaign_tag=email_campaign_name
                )
                email_records.append(email_record)
                print(email_record)


            except Exception as e:
                logging.error(f'Unable to send SendMail.send method due to {e}')

        
            # Mark email as processed
            processed_emails.add(email_contact)

        # Bulk insert records into the database
        if email_records:
            RecordingEmailRecipients.objects.bulk_create(email_records)
            logging.info(f"Bulk inserted {len(email_records)} email records.")

        return processed_emails  # Or return any relevant information




#General Notes

#Sends 1300 emails in 45 mins
#Limit to 1500 emails per day
#Anything over 2000 the entire account gets locked for 24 hours. 
#Limits to 2000 emails per day
# SMTPDataError: (550, b'5.4.5 Daily user sending limit exceeded. For more information on Gmail\n5.4.5 sending limits go to\n5.4.5  https://support.google.com/a/answer/166852 w4-20020a4ae9e4000000b005914f455774sm848190ooc.34 - gsmtp')

