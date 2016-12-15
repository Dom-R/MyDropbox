import hashlib
import sys
import os
import json
import time
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler

# Documentacao Watchdog: http://pythonhosted.org/watchdog/

# Class que cuida dos eventos realizados na pasta e sub-pastas do MyDropbox
class MyDropboxFileSystemEventHandler(FileSystemEventHandler):
    # Construtor
    def __init__(self):
        FileSystemEventHandler.__init__(self) # Chamada de construror da superclasse
        self.filesDictionary = json.load(open(".metadata")) if os.path.isfile(".metadata") else {} # Cria/Carrega dicionario com arquivos do sistema. Dados sao guardados atraves de JSON

    # On Create
    def on_created(self, event):
        if not event.src_path.rstrip() == ".\.metadata" and not event.is_directory:
            print "[File Created] Name: %s" % (event.src_path.rstrip())
            self.filesDictionary[event.src_path.rstrip()] = md5(event.src_path.rstrip()) # Adiciona arquivo ao dicionario

    # On Modify
    def on_modified(self, event):
        if not event.src_path.rstrip() == ".\.metadata" and not event.is_directory:
            print "[File Modified] Name: %s" % (event.src_path.rstrip())
            self.filesDictionary[event.src_path.rstrip()] = md5(event.src_path.rstrip()) # Altera valor do md5 do arquivo devido a uma mudanca nele

    # Deleted
    def on_deleted(self, event):
        if not event.src_path.rstrip() == ".\.metadata" and not event.is_directory:
            print "[File Deleted] Name: %s" % (event.src_path.rstrip())
            try:
                del self.filesDictionary[event.src_path.rstrip()] # remove entrada do arquivo no dicionario
                pass

    # Rename
    def on_moved(self, event):
        if not event.src_path.rstrip() == ".\.metadata" and not event.is_directory:
            print "[File Moved] Name: %s - Destination: %s" % (event.src_path.rstrip(), event.dest_path.rstrip())
            try:
                del self.filesDictionary[event.src_path.rstrip()] # remove entrada antiga do dicionario
            except KeyError:
                pass
            self.filesDictionary[event.dest_path.rstrip()] = md5(event.dest_path.rstrip()) # Adiciona nova localizacao do arquivo ao dicionario

    # Em qualquer evento
    def on_any_event(self, event):
        if not event.src_path.rstrip() == ".\.metadata" and not event.is_directory:
            #print "[Any Event] Name: %s" % (event.src_path)
            time.sleep(1) # Espera 1 segundo
            json.dump(self.filesDictionary, open(".metadata", "w+")) # Salva dicionario como json no arquivo de metadados

    def getMetadataFile():
        return self.metadataFile

# Utilizamos md5 para verificar diferencas no arquivo entre o cliente e o servidor
def md5(fname):
    hash_md5 = hashlib.md5()
    #if os.path.isfile(fname):
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

if __name__ == "__main__":
    # Moduleo de monitoramente de arquivos
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = MyDropboxFileSystemEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
