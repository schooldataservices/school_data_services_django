# Email Scraper and DynamoDB Updater

This Python script scrapes email responses and stores them in an AWS DynamoDB NoSQL database. It's designed to organize and manage email thread data.

## Prerequisites

- Python 3.11
- Required Python packages: `imaplib`, `json`, `pandas`, `email`, `boto3` (for AWS DynamoDB)
- [AWS](https://aws.amazon.com/) account with DynamoDB configured

## Usage

1. Install required Python packages: `pip install imaplib json pandas email boto3`.

2. Customize the script by updating your Gmail IMAP settings, subject lines, and DynamoDB table name.

3. Run the script: `python lambda_function.py`.

4. The script scrapes specified emails, assembles threads, and updates DynamoDB.

## Configuration

- Modify the `process()` function to specify email subject lines you want to scrape.
- Update `update_db()` to match your DynamoDB setup.

