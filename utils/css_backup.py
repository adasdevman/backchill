import os
import shutil
from datetime import datetime

class CSSBackupManager:
    def __init__(self):
        self.css_file = 'chillnowback/static/css/dashboard.css'
        self.backup_dir = 'chillnowback/static/css/backups'
        self.max_backups = 5  # Nombre maximum de sauvegardes à conserver

    def create_backup(self):
        """Crée une sauvegarde du fichier CSS"""
        # Créer le dossier de backup s'il n'existe pas
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

        # Générer le nom du fichier de backup avec la date
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(self.backup_dir, f'dashboard_{timestamp}.css')

        # Copier le fichier
        shutil.copy2(self.css_file, backup_file)
        print(f"Backup créé : {backup_file}")

        # Nettoyer les anciennes sauvegardes
        self._cleanup_old_backups()

    def restore_backup(self, backup_file=None):
        """Restaure une sauvegarde spécifique ou la plus récente"""
        if not os.path.exists(self.backup_dir):
            print("Aucune sauvegarde trouvée")
            return False

        if backup_file is None:
            # Obtenir la sauvegarde la plus récente
            backups = self._get_backups()
            if not backups:
                print("Aucune sauvegarde trouvée")
                return False
            backup_file = backups[-1]

        backup_path = os.path.join(self.backup_dir, backup_file)
        if not os.path.exists(backup_path):
            print(f"Fichier de sauvegarde non trouvé : {backup_file}")
            return False

        # Créer une sauvegarde du fichier actuel avant restauration
        self.create_backup()

        # Restaurer la sauvegarde
        shutil.copy2(backup_path, self.css_file)
        print(f"Sauvegarde restaurée : {backup_file}")
        return True

    def list_backups(self):
        """Liste toutes les sauvegardes disponibles"""
        if not os.path.exists(self.backup_dir):
            print("Aucune sauvegarde trouvée")
            return []

        backups = self._get_backups()
        for i, backup in enumerate(backups, 1):
            timestamp = backup.split('_')[1].split('.')[0]
            date = datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
            print(f"{i}. {backup} - {date.strftime('%d/%m/%Y %H:%M:%S')}")
        return backups

    def _get_backups(self):
        """Retourne la liste des fichiers de backup triés par date"""
        backups = [f for f in os.listdir(self.backup_dir) if f.startswith('dashboard_')]
        return sorted(backups)

    def _cleanup_old_backups(self):
        """Supprime les anciennes sauvegardes si le nombre maximum est dépassé"""
        backups = self._get_backups()
        while len(backups) > self.max_backups:
            oldest_backup = os.path.join(self.backup_dir, backups[0])
            os.remove(oldest_backup)
            print(f"Ancienne sauvegarde supprimée : {backups[0]}")
            backups = self._get_backups() 