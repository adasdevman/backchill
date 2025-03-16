from django.core.management.base import BaseCommand
from utils.css_backup import CSSBackupManager

class Command(BaseCommand):
    help = 'Gère les sauvegardes du fichier CSS du dashboard'

    def add_arguments(self, parser):
        parser.add_argument('action', type=str, choices=['backup', 'restore', 'list'],
                          help='Action à effectuer (backup/restore/list)')
        parser.add_argument('--file', type=str, help='Fichier de sauvegarde spécifique à restaurer')

    def handle(self, *args, **options):
        backup_manager = CSSBackupManager()
        action = options['action']

        if action == 'backup':
            backup_manager.create_backup()
            self.stdout.write(self.style.SUCCESS('Sauvegarde créée avec succès'))

        elif action == 'list':
            self.stdout.write('Liste des sauvegardes disponibles :')
            backup_manager.list_backups()

        elif action == 'restore':
            if options['file']:
                success = backup_manager.restore_backup(options['file'])
            else:
                success = backup_manager.restore_backup()

            if success:
                self.stdout.write(self.style.SUCCESS('Restauration effectuée avec succès'))
            else:
                self.stdout.write(self.style.ERROR('Échec de la restauration')) 