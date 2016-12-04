import hashlib
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, FileSystemEventHandler

# Documentacao Watchdog: http://pythonhosted.org/watchdog/

# Class que cuida dos eventos realizados na pasta e sub-pastas do MyDropbox
class MyDropboxFileSystemEventHandler(FileSystemEventHandler):
    # On Create
    def on_created(self, event):
        print "[File Created] Name: %s" % (event.src_path.rstrip())

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

# Utilizamos md5 para verificar diferencas no arquivo
def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

if __name__ == "__main__":
    #logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = MyDropboxFileSystemEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
