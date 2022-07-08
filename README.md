# automail

Python library to simplify automated emails

# Usage

```python
from automail.email import Email, Attachment, SMTPServers, SendStatus

email = Email(
    'username',
    'password',
    SMTPServers.OUTLOOK,
    'sender', # usually username 
    'recipient',
    'subject',
    'this is an automated email',
    Attachment('attachment.txt')
)

def on_progress(status: SendStatus):
    if status == SendStatus.BUILDING:
        print('building email...')
    if status == SendStatus.CONNECTING:
        print('connecting to server...')
    if status == SendStatus.SENDING:
        print(f'sending to {email.recipient}...')
    if status == SendStatus.CLOSING:
        print('closing connection to server...')
    if status == SendStatus.DONE:
        print('email sent!')

email.send(on_progress)
```

If you are using `SMTPServers.GMAIL` with 2FA is enabled then use an app password instead of the actual password: https://security.google.com/settings/security/apppasswords 