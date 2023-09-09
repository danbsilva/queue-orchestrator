import sys

from src.extensions.mail import mail
from flask_mail import Message
from src.logging import Logger
from src import messages

__module_name__ = 'src.callbacks'


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
            Logger().dispatch('INFO', __module_name__, 'send_mail',
                                    messages.MAIL_SENT.format(recipient),
                                    msg["transaction_id"])
        except Exception as e:
            Logger().dispatch('ERROR', __module_name__, 'send_mail',
                                    messages.MAIL_NOT_SENT.format(recipient, e.args[0]),  
                                    msg["transaction_id"])
            sys.exit(1)
