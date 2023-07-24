import sys

from src.extensions.mail import mail
from flask_mail import Message
from src import logging

__module_name__ = 'src.mail'


def send_mail(app, key, msg):
    recipient = msg['email']
    subject = msg['subject']
    body = msg['template']

    with app.app_context():
        message = Message(recipients=[recipient],
                          html=body,
                          subject=subject)
        try:
            mail.send(message)
            logging.send_log_kafka('INFO', __module_name__, 'send_mail',
                                   f'Mail sent to {recipient}', msg["transaction_id"])
        except Exception as e:
            logging.send_log_kafka('EXCEPTION', __module_name__, 'send_mail',
                                   f'It was not possible to send mail to {recipient}: {e}', msg["transaction_id"])
            sys.exit(1)
