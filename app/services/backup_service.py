"""
Backup and restore functionality for MEKPAIE database.
"""
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
from app.database import DB_FILE
from app.paths import BACKUP_DIR


class BackupService:
    """Handle database backups and restoration."""
    
    def __init__(self):
        self.backup_dir = BACKUP_DIR
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = DB_FILE
    
    def create_backup(self) -> Optional[Path]:
        """
        Create a backup of the database.
        
        Returns:
            Path to backup file or None if failed
        """
        try:
            if not self.db_path.exists():
                raise FileNotFoundError("Base de données non trouvée")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"MEKPAIE_backup_{timestamp}.db"
            
            shutil.copy2(self.db_path, backup_file)
            
            return backup_file
        except Exception as e:
            raise Exception(f"Erreur lors de la sauvegarde: {str(e)}")
    
    def restore_backup(self, backup_path: Path) -> bool:
        """
        Restore database from backup.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not backup_path.exists():
                raise FileNotFoundError(f"Fichier de sauvegarde non trouvé: {backup_path}")
            
            # Create a backup of current database first
            if self.db_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = self.backup_dir / f"MEKPAIE_before_restore_{timestamp}.db"
                shutil.copy2(self.db_path, backup_file)
            
            # Restore from backup
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_path, self.db_path)
            
            return True
        except Exception as e:
            raise Exception(f"Erreur lors de la restauration: {str(e)}")
    
    def list_backups(self) -> list:
        """
        List all available backups.
        
        Returns:
            List of backup file paths sorted by date (newest first)
        """
        if not self.backup_dir.exists():
            return []
        
        backups = sorted(
            self.backup_dir.glob("MEKPAIE_backup_*.db"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        return backups
    
    def delete_backup(self, backup_path: Path) -> bool:
        """
        Delete a backup file.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if successful
        """
        try:
            if backup_path.exists():
                backup_path.unlink()
                return True
            return False
        except Exception as e:
            raise Exception(f"Erreur lors de la suppression: {str(e)}")
    
    def auto_cleanup_backups(self, keep_count: int = 10):
        """
        Automatically delete old backups keeping only the most recent ones.
        
        Args:
            keep_count: Number of backups to keep
        """
        backups = self.list_backups()
        
        if len(backups) > keep_count:
            for backup in backups[keep_count:]:
                try:
                    backup.unlink()
                except:
                    pass
