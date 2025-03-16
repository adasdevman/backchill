import sib_api_v3_sdk
from django.conf import settings
from sib_api_v3_sdk.rest import ApiException

class EmailService:
    def __init__(self):
        self.configuration = sib_api_v3_sdk.Configuration()
        self.configuration.api_key['api-key'] = settings.BREVO_API_KEY
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(self.configuration))

    def send_welcome_email(self, user_email, first_name=''):
        try:
            subject = "Bienvenue sur ChillNow!"
            sender = {"name": "ChillNow", "email": "contact@chillnow.com"}
            to = [{"email": user_email, "name": first_name}]

            html_content = f"""
            <html>
                <body>
                    <h1>Bienvenue sur ChillNow {first_name}!</h1>
                    <p>Nous sommes ravis de vous compter parmi nous.</p>
                    <p>Avec ChillNow, vous pouvez :</p>
                    <ul>
                        <li>Découvrir les meilleurs endroits</li>
                        <li>Réserver vos places</li>
                        <li>Acheter vos tickets d'événements</li>
                    </ul>
                    <p>N'hésitez pas à explorer l'application!</p>
                    <p>L'équipe ChillNow</p>
                </body>
            </html>
            """

            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=to,
                html_content=html_content,
                sender=sender,
                subject=subject
            )

            self.api_instance.send_transac_email(send_smtp_email)
            return True
        except ApiException as e:
            print(f"Exception when sending welcome email: {e}")
            return False 