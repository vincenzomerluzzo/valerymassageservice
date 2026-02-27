#!/usr/bin/env python3
import ftplib, sys, os

if len(sys.argv) < 7:
    print("Uso: ftp_deploy.py <host> <port> <user> <pass> <local_dir> <remote_dir> [backup_dir]")
    sys.exit(1)

host = sys.argv[1]
port = int(sys.argv[2])
user = sys.argv[3]
passwd = sys.argv[4]
local_dir = sys.argv[5]
remote_dir = sys.argv[6]
backup_dir = sys.argv[7] if len(sys.argv) > 7 else 'remote-backup'

os.makedirs(backup_dir, exist_ok=True)

ftp = ftplib.FTP()
print(f"Connessione a {host}:{port}...")
ftp.connect(host, port, timeout=30)
ftp.login(user, passwd)
ftp.set_pasv(True)
print("Connesso, inizio backup remoto...")

# Helper to ensure local directory exists

def ensure_local_dir(path):
    os.makedirs(path, exist_ok=True)

# Recursively download remote path into local backup

def download_remote(curr_remote, curr_local):
    ensure_local_dir(curr_local)
    try:
        entries = ftp.nlst(curr_remote)
    except ftplib.error_perm as e:
        # Directory empty or no permission
        entries = []
    for entry in entries:
        name = os.path.basename(entry)
        if name in ('.', '..'):
            continue
        remote_path = entry if curr_remote == '.' else f"{curr_remote}/{name}" if curr_remote.endswith('/') is False else f"{curr_remote}{name}"
        local_path = os.path.join(curr_local, name)
        # Decide if it's a dir by trying to cwd
        try:
            ftp.cwd(remote_path)
            # It's a directory
            ftp.cwd('/')
            download_remote(remote_path, local_path)
        except Exception:
            # Assume file
            try:
                with open(local_path, 'wb') as f:
                    ftp.retrbinary(f'RETR {remote_path}', f.write)
                print(f'Download: {remote_path} -> {local_path}')
            except Exception as e:
                print(f'Ignorato file (errore): {remote_path} -> {e}')

# Start download from remote_dir
try:
    ftp.cwd(remote_dir)
    # nlst with '.' to list current dir entries with full names
    download_remote('.', os.path.join(os.getcwd(), backup_dir))
except Exception as e:
    print(f'Impossibile accedere a {remote_dir}: {e}')

print('Backup completato. Inizio upload dei file locali...')

# Helper to make remote directories recursively

def ftp_makedirs(path):
    orig = ftp.pwd()
    parts = [p for p in path.split('/') if p]
    for i in range(len(parts)):
        sub = '/' + '/'.join(parts[: i + 1])
        try:
            ftp.cwd(sub)
        except Exception:
            try:
                ftp.mkd(sub)
            except Exception:
                pass
    try:
        ftp.cwd(orig)
    except Exception:
        pass


# Recursively remove a remote directory (files and subdirs)
def remove_remote_dir(path):
    try:
        entries = ftp.nlst(path)
    except Exception:
        return
    for entry in entries:
        name = os.path.basename(entry)
        if name in ('.', '..'):
            continue
        full = path.rstrip('/') + '/' + name
        try:
            ftp.cwd(full)
            # it's a directory
            ftp.cwd('/')
            remove_remote_dir(full)
            try:
                ftp.rmd(full)
                print(f'Remote dir removed: {full}')
            except Exception as e:
                print(f'Could not rmdir {full}: {e}')
        except Exception:
            # assume file
            try:
                ftp.delete(full)
                print(f'Remote file removed: {full}')
            except Exception as e:
                print(f'Could not delete {full}: {e}')

# If a remote node_modules exists from previous uploads, remove it to save space
try:
    remote_nm = remote_dir.rstrip('/') + '/node_modules'
    remove_remote_dir(remote_nm)
except Exception:
    pass

# Upload local_dir contents into remote_dir (overwrite)

for root, dirs, files in os.walk(local_dir, topdown=True):
    rel = os.path.relpath(root, local_dir)
    if rel == '.':
        remote_path = remote_dir
    else:
        remote_path = remote_dir.rstrip('/') + '/' + rel.replace('\\', '/')
    # exclude common heavy or unwanted directories from upload
    exclude_dirs = {'.git', 'node_modules', '__pycache__'}
    dirs[:] = [d for d in dirs if d not in exclude_dirs]

    # ensure remote dir exists
    ftp_makedirs(remote_path)
    try:
        ftp.cwd(remote_path)
    except Exception:
        pass
    for f in files:
        # skip node_modules, .git
        if f in ('.DS_Store',):
            continue
        local_file = os.path.join(root, f)
        remote_file = f
        try:
            with open(local_file, 'rb') as fh:
                ftp.storbinary(f'STOR {remote_file}', fh)
            print(f'Upload: {local_file} -> {remote_path}/{remote_file}')
        except Exception as e:
            print(f'Errore upload {local_file}: {e}')

print('Upload completato.')
ftp.quit()
