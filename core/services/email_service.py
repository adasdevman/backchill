import sib_api_v3_sdk
from django.conf import settings
from sib_api_v3_sdk.rest import ApiException

class EmailService:
    def __init__(self):
        self.configuration = sib_api_v3_sdk.Configuration()
        self.configuration.api_key['api-key'] = settings.BREVO_API_KEY
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(self.configuration))
        self.default_sender = {"name": "ChillNow", "email": "no-reply@chillnow-ci.com"}

    def _get_base_template(self, content):
        return f"""
        <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333333;
                        margin: 0;
                        padding: 0;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background-color: #000000;
                        padding: 20px;
                        text-align: center;
                        border-radius: 5px 5px 0 0;
                    }}
                    .content {{
                        background-color: #ffffff;
                        padding: 20px;
                        border-radius: 0 0 5px 5px;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 20px;
                        padding: 20px;
                        font-size: 12px;
                        color: #666666;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 10px 20px;
                        background-color: #FFD700;
                        color: #000000;
                        text-decoration: none;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .stats-container {{
                        background-color: #f8f8f8;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                    }}
                    .stat-item {{
                        margin: 10px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="color: #FFFFFF; margin: 0;">ChillNow</h1>
                    </div>
                    <div class="content">
                        {content}
                    </div>
                    <div class="footer">
                        <p>© {2025} ChillNow. Tous droits réservés.</p>
                        <p>Cet email a été envoyé automatiquement, merci de ne pas y répondre.</p>
                    </div>
                </div>
            </body>
        </html>
        """

    def send_welcome_email(self, user_email, first_name='', role='UTILISATEUR'):
        try:
            subject = "Bienvenue sur ChillNow!"
            content = f"""
                <h2 style="color: #000000;">Bienvenue sur ChillNow {first_name}!</h2>
                <p>Nous sommes ravis de vous accueillir parmi nous.</p>
                <p>Avec ChillNow, vous pouvez :</p>
                <ul>
                    <li>Découvrir les meilleurs endroits pour sortir</li>
                    <li>Réserver vos places en quelques clics</li>
                    <li>Acheter vos tickets d'événements</li>
                    <li>Profiter d'offres exclusives</li>
                </ul>
                <p>Si vous avez des questions, notre équipe est là pour vous aider.</p>
                <p>À très bientôt sur ChillNow!</p>
                <p>L'équipe ChillNow</p>
            """

            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": user_email, "name": first_name}],
                html_content=self._get_base_template(content),
                sender=self.default_sender,
                subject=subject
            )

            self.api_instance.send_transac_email(send_smtp_email)
            return True
        except ApiException as e:
            print(f"Exception when sending welcome email: {e}")
            return False

    def send_booking_confirmation(self, user_email, user_name, booking_details):
        try:
            subject = "Confirmation de votre réservation"
            content = f"""
                <h2>Confirmation de réservation</h2>
                <p>Bonjour {user_name},</p>
                <p>Votre réservation a été confirmée avec succès !</p>
                <div style="background-color: #f8f8f8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>Détails de la réservation :</h3>
                    <p><strong>Établissement :</strong> {booking_details.get('establishment')}</p>
                    <p><strong>Date :</strong> {booking_details.get('date')}</p>
                    <p><strong>Formule :</strong> {booking_details.get('package')}</p>
                    <p><strong>Montant :</strong> {booking_details.get('amount')} FCFA</p>
                </div>
                <p>Nous vous souhaitons un excellent moment !</p>
            """

            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": user_email, "name": user_name}],
                html_content=self._get_base_template(content),
                sender=self.default_sender,
                subject=subject
            )

            self.api_instance.send_transac_email(send_smtp_email)
            return True
        except ApiException as e:
            print(f"Exception when sending booking confirmation: {e}")
            return False

    def send_ticket_confirmation(self, user_email, user_name, ticket_details):
        try:
            subject = "Confirmation de votre achat de ticket"
            content = f"""
                <h2>Confirmation d'achat de ticket</h2>
                <p>Bonjour {user_name},</p>
                <p>Votre achat de ticket a été confirmé avec succès !</p>
                <div style="background-color: #f8f8f8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>Détails du ticket :</h3>
                    <p><strong>Événement :</strong> {ticket_details.get('event')}</p>
                    <p><strong>Date :</strong> {ticket_details.get('date')}</p>
                    <p><strong>Type de ticket :</strong> {ticket_details.get('type')}</p>
                    <p><strong>Montant :</strong> {ticket_details.get('amount')} FCFA</p>
                    <p><strong>Numéro de transaction :</strong> {ticket_details.get('transaction_id')}</p>
                </div>
                <p>Vous pouvez retrouver votre ticket dans votre espace personnel.</p>
                <div style="text-align: center;">
                    <a href="https://chillnow-ci.com/profile" class="button">Voir mon ticket</a>
                </div>
                <p>Nous vous souhaitons un excellent événement !</p>
            """

            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": user_email, "name": user_name}],
                html_content=self._get_base_template(content),
                sender=self.default_sender,
                subject=subject
            )

            self.api_instance.send_transac_email(send_smtp_email)
            return True
        except ApiException as e:
            print(f"Exception when sending ticket confirmation: {e}")
            return False

    def send_event_reminder(self, user_email, user_name, event_details):
        try:
            subject = "Rappel : Votre événement approche !"
            content = f"""
                <h2>Rappel d'événement</h2>
                <p>Bonjour {user_name},</p>
                <p>Nous vous rappelons que vous avez un événement demain !</p>
                <div style="background-color: #f8f8f8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>Détails de l'événement :</h3>
                    <p><strong>Événement :</strong> {event_details.get('event_name')}</p>
                    <p><strong>Date :</strong> {event_details.get('date')}</p>
                    <p><strong>Lieu :</strong> {event_details.get('location')}</p>
                    <p><strong>Type de ticket :</strong> {event_details.get('ticket_type')}</p>
                </div>
                <p>Nous vous souhaitons un excellent moment !</p>
            """
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": user_email, "name": user_name}],
                html_content=self._get_base_template(content),
                sender=self.default_sender,
                subject=subject
            )
            self.api_instance.send_transac_email(send_smtp_email)
            return True
        except ApiException as e:
            print(f"Exception when sending event reminder: {e}")
            return False

    def send_booking_cancellation(self, user_email, user_name, booking_details):
        try:
            subject = "Annulation de votre réservation"
            content = f"""
                <h2>Annulation de réservation</h2>
                <p>Bonjour {user_name},</p>
                <p>Nous vous informons que votre réservation a été annulée.</p>
                <div style="background-color: #f8f8f8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>Détails de la réservation annulée :</h3>
                    <p><strong>Établissement :</strong> {booking_details.get('establishment')}</p>
                    <p><strong>Date :</strong> {booking_details.get('date')}</p>
                    <p><strong>Formule :</strong> {booking_details.get('package')}</p>
                    <p><strong>Montant :</strong> {booking_details.get('amount')} FCFA</p>
                </div>
                <p>Le montant vous sera remboursé dans les plus brefs délais.</p>
            """
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": user_email, "name": user_name}],
                html_content=self._get_base_template(content),
                sender=self.default_sender,
                subject=subject
            )
            self.api_instance.send_transac_email(send_smtp_email)
            return True
        except ApiException as e:
            print(f"Exception when sending booking cancellation: {e}")
            return False

    def send_password_reset(self, user_email, user_name, reset_link):
        try:
            subject = "Réinitialisation de votre mot de passe"
            content = f"""
                <h2>Réinitialisation de mot de passe</h2>
                <p>Bonjour {user_name},</p>
                <p>Vous avez demandé la réinitialisation de votre mot de passe.</p>
                <p>Cliquez sur le lien ci-dessous pour créer un nouveau mot de passe :</p>
                <div style="text-align: center;">
                    <a href="{reset_link}" class="button">Réinitialiser mon mot de passe</a>
                </div>
                <p>Si vous n'êtes pas à l'origine de cette demande, ignorez cet email.</p>
                <p>Ce lien expirera dans 24 heures.</p>
            """
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": user_email, "name": user_name}],
                html_content=self._get_base_template(content),
                sender=self.default_sender,
                subject=subject
            )
            self.api_instance.send_transac_email(send_smtp_email)
            return True
        except ApiException as e:
            print(f"Exception when sending password reset: {e}")
            return False

    def send_new_booking_notification(self, advertiser_email, advertiser_name, booking_details):
        try:
            subject = "Nouvelle réservation reçue !"
            content = f"""
                <h2>Nouvelle réservation</h2>
                <p>Bonjour {advertiser_name},</p>
                <p>Vous avez reçu une nouvelle réservation !</p>
                <div style="background-color: #f8f8f8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>Détails de la réservation :</h3>
                    <p><strong>Client :</strong> {booking_details.get('client_name')}</p>
                    <p><strong>Date :</strong> {booking_details.get('date')}</p>
                    <p><strong>Formule :</strong> {booking_details.get('package')}</p>
                    <p><strong>Montant :</strong> {booking_details.get('amount')} FCFA</p>
                </div>
                <p>Connectez-vous à votre espace pour voir tous les détails.</p>
            """
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": advertiser_email, "name": advertiser_name}],
                html_content=self._get_base_template(content),
                sender=self.default_sender,
                subject=subject
            )
            self.api_instance.send_transac_email(send_smtp_email)
            return True
        except ApiException as e:
            print(f"Exception when sending new booking notification: {e}")
            return False

    def send_daily_booking_summary(self, advertiser_email, advertiser_name, summary_data):
        try:
            subject = "Récapitulatif quotidien des réservations"
            content = f"""
                <h2>Récapitulatif des réservations</h2>
                <p>Bonjour {advertiser_name},</p>
                <p>Voici le récapitulatif de vos réservations du jour :</p>
                <div class="stats-container">
                    <div class="stat-item">
                        <p><strong>Nombre total de réservations :</strong> {summary_data.get('total_bookings')}</p>
                        <p><strong>Montant total :</strong> {summary_data.get('total_amount')} FCFA</p>
                    </div>
                    <h3>Détails par établissement :</h3>
                    {summary_data.get('establishment_details')}
                </div>
            """
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": advertiser_email, "name": advertiser_name}],
                html_content=self._get_base_template(content),
                sender=self.default_sender,
                subject=subject
            )
            self.api_instance.send_transac_email(send_smtp_email)
            return True
        except ApiException as e:
            print(f"Exception when sending daily booking summary: {e}")
            return False

    def send_announcement_status_update(self, advertiser_email, advertiser_name, announcement_details):
        try:
            status = announcement_details.get('status')
            if status == 'APPROVED':
                subject = "Votre annonce a été validée"
                status_message = "a été validée et est maintenant visible sur ChillNow"
            elif status == 'REJECTED':
                subject = "Votre annonce n'a pas été validée"
                status_message = "n'a pas été validée pour la raison suivante"
            else:
                subject = "Votre annonce a été suspendue"
                status_message = "a été suspendue pour la raison suivante"

            content = f"""
                <h2>Mise à jour du statut de votre annonce</h2>
                <p>Bonjour {advertiser_name},</p>
                <p>Votre annonce "{announcement_details.get('title')}" {status_message} :</p>
                <div style="background-color: #f8f8f8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p><strong>Raison :</strong> {announcement_details.get('reason')}</p>
                    {announcement_details.get('additional_info', '')}
                </div>
                <p>{announcement_details.get('next_steps', '')}</p>
            """
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": advertiser_email, "name": advertiser_name}],
                html_content=self._get_base_template(content),
                sender=self.default_sender,
                subject=subject
            )
            self.api_instance.send_transac_email(send_smtp_email)
            return True
        except ApiException as e:
            print(f"Exception when sending announcement status update: {e}")
            return False

    def send_new_advertiser_notification(self, admin_email, advertiser_details):
        try:
            subject = "Nouvelle inscription annonceur"
            content = f"""
                <h2>Nouvel annonceur inscrit</h2>
                <p>Un nouvel annonceur vient de s'inscrire sur la plateforme.</p>
                <div style="background-color: #f8f8f8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>Informations de l'annonceur :</h3>
                    <p><strong>Nom :</strong> {advertiser_details.get('name')}</p>
                    <p><strong>Email :</strong> {advertiser_details.get('email')}</p>
                    <p><strong>Téléphone :</strong> {advertiser_details.get('phone')}</p>
                    <p><strong>Entreprise :</strong> {advertiser_details.get('company_name')}</p>
                </div>
                <p>Veuillez vérifier ces informations et valider le compte.</p>
            """
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": admin_email}],
                html_content=self._get_base_template(content),
                sender=self.default_sender,
                subject=subject
            )
            self.api_instance.send_transac_email(send_smtp_email)
            return True
        except ApiException as e:
            print(f"Exception when sending new advertiser notification: {e}")
            return False

    def send_announcement_validation_request(self, admin_email, announcement_details):
        try:
            subject = "Nouvelle annonce à valider"
            content = f"""
                <h2>Nouvelle annonce en attente de validation</h2>
                <p>Une nouvelle annonce requiert votre validation.</p>
                <div style="background-color: #f8f8f8; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3>Détails de l'annonce :</h3>
                    <p><strong>Titre :</strong> {announcement_details.get('title')}</p>
                    <p><strong>Annonceur :</strong> {announcement_details.get('advertiser_name')}</p>
                    <p><strong>Catégorie :</strong> {announcement_details.get('category')}</p>
                    <p><strong>Description :</strong> {announcement_details.get('description')}</p>
                </div>
                <p>Veuillez examiner cette annonce et la valider ou la rejeter.</p>
            """
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": admin_email}],
                html_content=self._get_base_template(content),
                sender=self.default_sender,
                subject=subject
            )
            self.api_instance.send_transac_email(send_smtp_email)
            return True
        except ApiException as e:
            print(f"Exception when sending announcement validation request: {e}")
            return False

    def send_daily_activity_report(self, admin_email, report_data):
        try:
            subject = "Rapport d'activité quotidien"
            content = f"""
                <h2>Rapport d'activité du {report_data.get('date')}</h2>
                <div class="stats-container">
                    <h3>Nouveaux utilisateurs</h3>
                    <div class="stat-item">
                        <p><strong>Clients :</strong> {report_data.get('new_users')}</p>
                        <p><strong>Annonceurs :</strong> {report_data.get('new_advertisers')}</p>
                    </div>

                    <h3>Activité commerciale</h3>
                    <div class="stat-item">
                        <p><strong>Nouvelles réservations :</strong> {report_data.get('new_bookings')}</p>
                        <p><strong>Tickets vendus :</strong> {report_data.get('tickets_sold')}</p>
                        <p><strong>Chiffre d'affaires :</strong> {report_data.get('revenue')} FCFA</p>
                    </div>

                    <h3>Contenu</h3>
                    <div class="stat-item">
                        <p><strong>Nouvelles annonces :</strong> {report_data.get('new_announcements')}</p>
                        <p><strong>Annonces en attente :</strong> {report_data.get('pending_announcements')}</p>
                    </div>
                </div>
            """
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": admin_email}],
                html_content=self._get_base_template(content),
                sender=self.default_sender,
                subject=subject
            )
            self.api_instance.send_transac_email(send_smtp_email)
            return True
        except ApiException as e:
            print(f"Exception when sending daily activity report: {e}")
            return False

    def send_password_reset_email(self, user_email, user_name, reset_url):
        try:
            subject = "Réinitialisation de votre mot de passe ChillNow"
            content = f"""
                <h2>Réinitialisation de mot de passe</h2>
                <p>Bonjour {user_name},</p>
                <p>Vous avez demandé la réinitialisation du mot de passe de votre compte ChillNow.</p>
                <p>Pour définir un nouveau mot de passe, cliquez sur le bouton ci-dessous :</p>
                <div style="text-align: center;">
                    <a href="{reset_url}" class="button">Réinitialiser mon mot de passe</a>
                </div>
                <p>Si vous n'avez pas demandé cette réinitialisation, vous pouvez ignorer cet email.</p>
                <p>Ce lien de réinitialisation expirera dans 24 heures.</p>
                <p>Pour des raisons de sécurité, nous vous conseillons de :</p>
                <ul>
                    <li>Ne jamais partager ce lien avec quelqu'un</li>
                    <li>Choisir un mot de passe fort et unique</li>
                    <li>Activer l'authentification à deux facteurs si disponible</li>
                </ul>
            """

            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": user_email, "name": user_name}],
                html_content=self._get_base_template(content),
                sender=self.default_sender,
                subject=subject
            )

            self.api_instance.send_transac_email(send_smtp_email)
            return True
        except ApiException as e:
            print(f"Exception when sending password reset email: {e}")
            return False 