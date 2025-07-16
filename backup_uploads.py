#!/usr/bin/env python3
"""
Script para backup das imagens de uploads
Útil para migração ou backup manual antes de deploys
"""

import os
import shutil
import zipfile
from datetime import datetime
import argparse

def create_backup(source_dir='/app/uploads', backup_dir='backups'):
    """Cria backup das imagens em arquivo ZIP"""
    
    if not os.path.exists(source_dir):
        print(f"❌ Diretório {source_dir} não encontrado")
        return False
    
    # Cria diretório de backup
    os.makedirs(backup_dir, exist_ok=True)
    
    # Nome do arquivo com timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"uploads_backup_{timestamp}.zip"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)
                    print(f"✅ Adicionado: {arcname}")
        
        file_size = os.path.getsize(backup_path) / (1024 * 1024)  # MB
        print(f"🎉 Backup criado: {backup_path} ({file_size:.2f} MB)")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return False

def restore_backup(backup_file, target_dir='/app/uploads'):
    """Restaura backup das imagens"""
    
    if not os.path.exists(backup_file):
        print(f"❌ Arquivo de backup {backup_file} não encontrado")
        return False
    
    try:
        # Cria diretório de destino
        os.makedirs(target_dir, exist_ok=True)
        
        with zipfile.ZipFile(backup_file, 'r') as zipf:
            zipf.extractall(target_dir)
            print(f"✅ Backup restaurado em {target_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao restaurar backup: {e}")
        return False

def list_backups(backup_dir='backups'):
    """Lista backups disponíveis"""
    
    if not os.path.exists(backup_dir):
        print(f"❌ Diretório de backup {backup_dir} não encontrado")
        return
    
    backups = [f for f in os.listdir(backup_dir) if f.endswith('.zip')]
    
    if not backups:
        print("📭 Nenhum backup encontrado")
        return
    
    print("📦 Backups disponíveis:")
    for backup in sorted(backups, reverse=True):
        backup_path = os.path.join(backup_dir, backup)
        size = os.path.getsize(backup_path) / (1024 * 1024)  # MB
        mtime = datetime.fromtimestamp(os.path.getmtime(backup_path))
        print(f"  • {backup} ({size:.2f} MB) - {mtime.strftime('%d/%m/%Y %H:%M')}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Backup/Restore de uploads')
    parser.add_argument('action', choices=['backup', 'restore', 'list'], 
                       help='Ação a executar')
    parser.add_argument('--source', default='/app/uploads', 
                       help='Diretório de origem (padrão: /app/uploads)')
    parser.add_argument('--backup-dir', default='backups', 
                       help='Diretório de backups (padrão: backups)')
    parser.add_argument('--file', help='Arquivo de backup para restaurar')
    
    args = parser.parse_args()
    
    if args.action == 'backup':
        create_backup(args.source, args.backup_dir)
    elif args.action == 'restore':
        if not args.file:
            print("❌ Use --file para especificar o arquivo de backup")
        else:
            restore_backup(args.file, args.source)
    elif args.action == 'list':
        list_backups(args.backup_dir)