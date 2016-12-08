import hashlib
import sys
import os
import json
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
        print "[File Created] Name: %s" % (event.src_path.rstrip())
        self.filesDictionary[event.src_path.rstrip()] = md5(event.src_path.rstrip()) # Adiciona arquivo ao dicionario
        json.dump(self.filesDictionary, open(".metadata", "w+")) # Salva dicionario como json no arquivo de metadados

    # On Modify
    def on_modified(self, event):
        print "[File Modified] Name: %s" % (event.src_path.rstrip())

    # Deleted
    def on_deleted(self, event):
        print "[File Deleted] Name: %s" % (event.src_path.rstrip())

    # Rename
    def on_moved(self, event):
        print "[File Moved] Name: %s - Destination: %s" % (event.src_path.rstrip(), event.dest_path.rstrip())

    # Em qualquer evento
    #def on_any_event(self, event):
        #print "[Any Event] Name: %s" % (event.src_path)

    def getMetadataFile():
        return self.metadataFile

# Utilizamos md5 para verificar diferencas no arquivo entre o cliente e o servidor
def md5(fname):
    hash_md5 = hashlib.md5()
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
