import hashlib
import sys
import os
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler
import requests
import json

# Documentacao Watchdog: http://pythonhosted.org/watchdog/

# Class que cuida dos eventos realizados na pasta e sub-pastas do MyDropbox
class MyDropboxFileSystemEventHandler(FileSystemEventHandler):
    # Construtor
    def __init__(self):
        FileSystemEventHandler.__init__(self) # Chamada de construror da superclasse
        self.filesDictionary = {} # Cria/Carrega dicionario com arquivos do sistema. Dados sao guardados atraves de JSON

    # On Create
    '''def on_created(self, event):
        filename = event.src_path.rstrip().split('\\', 1)[-1]
        if not filename.startswith(".") and not os.path.isdir(event.src_path.rstrip()):
            print "[File Created] Name: %s" % (event.src_path.rstrip())
            self.filesDictionary[event.src_path.rstrip()] = md5(event.src_path.rstrip()) # Adiciona arquivo ao dicionario'''

    # On Modify
    def on_modified(self, event):
        filename = event.src_path.rstrip().split('\\', 1)[-1]
        if not filename.startswith(".") and not os.path.isdir(event.src_path.rstrip()):
            print "[File Modified] Name: %s" % (event.src_path.rstrip())
            self.filesDictionary[event.src_path.rstrip()] = md5(event.src_path.rstrip()) # Altera valor do md5 do arquivo devido a uma mudanca nele

    # Deleted
    def on_deleted(self, event):
        filename = event.src_path.rstrip().split('\\', 1)[-1]
        if not filename.startswith(".") and not os.path.isdir(event.src_path.rstrip()):
            print "[File Deleted] Name: %s" % (event.src_path.rstrip())
            try:
                del self.filesDictionary[event.src_path.rstrip()] # remove entrada do arquivo no dicionario
            except:
                pass

    # Rename
    def on_moved(self, event):
        filename = event.dest_path.rstrip().split('\\', 1)[-1]
        if not filename.startswith(".") and not os.path.isdir(event.dest_path.rstrip()):
            print "[File Moved] Name: %s - Destination: %s" % (event.src_path.rstrip(), event.dest_path.rstrip())
            try:
                del self.filesDictionary[event.src_path.rstrip()] # remove entrada antiga do dicionario
            except KeyError:
                pass
            self.filesDictionary[event.dest_path.rstrip()] = md5(event.dest_path.rstrip()) # Adiciona nova localizacao do arquivo ao dicionario

    # Em qualquer evento
    '''def on_any_event(self, event):
        if not event.src_path.rstrip() == ".\.metadata" and not event.is_directory:
            #print "[Any Event] Name: %s" % (event.src_path)
            time.sleep(1) # Espera 1 segundo
            json.dump(self.filesDictionary, open(".metadata", "w+")) # Salva dicionario como json no arquivo de metadados'''

    def send_metadata_to_server(self):
        print "[Send Metadata] Sending metadata"
        for key, value in self.get_file_dictionary().items():
            print key, value
        response = requests.post('http://127.0.0.1:8080', data=json.dumps(self.get_file_dictionary()))
        print response.text
        for filename in json.loads(response.text):
            self.send_file_to_server(filename)

    def send_file_to_server(self, filepath):
        print "[Uploading to Server] Uploading:", filepath
        with open(filepath, "rb") as f:
            requests.post('http://127.0.0.1:8080', data=f, headers = {'filename': filepath })
        print "[Uploading to Server] Uploading complete:", filepath

    def get_file_dictionary(self):
        return self.filesDictionary

# Utilizamos md5 para verificar diferencas no arquivo entre o cliente e o servidor
def md5(fname):
    hash_md5 = hashlib.md5()
    #if os.path.isfile(fname):
    while True:
        try:
            with open(fname, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            break
        except:
            print "[MD5] Failed to open file. Retrying..."
    return hash_md5.hexdigest()

def scan_folder(basepath, filesDictionary):
    for path, _, filename_array in os.walk(basepath):

        # Remove os arquivos que iniciam com um ponto
        filename_array = [ x for x in filename_array if not x.startswith(".") ]

        for filename in filename_array:
            file_path = os.path.join(path, filename)
            #print file_path, md5(file_path)
            filesDictionary[file_path] = md5(file_path)

if __name__ == "__main__":
    # Moduleo de monitoramente de arquivos
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = MyDropboxFileSystemEventHandler()
    scan_folder(path, event_handler.get_file_dictionary())

    for key, value in event_handler.get_file_dictionary().items():
        print key, value

    event_handler.send_metadata_to_server()
    #event_handler.send_file_to_server("hello.c")

    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
