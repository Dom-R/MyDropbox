from BaseHTTPServer import BaseHTTPRequestHandler
import os
import json
import hashlib

filesDictionary = {}

class MyDropboxHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.headers.getheader('upload_filename'):
            self.write_file()
        elif self.headers.getheader('download_filename'):
            self.send_file()
        elif self.headers.getheader('remove_filename'):
            self.remove_file()
        else:
            jsondata = self.rfile.read(int(self.headers['Content-Length']))
            clientDic = json.loads(jsondata)
            requestArray, downloadArray = compare(clientDic)

            # Envia resposta
            self.send_response(200) # Sucesso
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(requestArray)) # Envia array com arquivos para enviar para o servidor
            self.wfile.write(json.dumps(downloadArray)) # Envia array com arquivos para enviar para o servidor

    def write_file(self):
        global filesDictionary
        size = long(self.headers['content-length'])
        filename = self.headers['upload_filename']
        modificationTime = self.headers['modification_time']
        print "[Uploading Module] Writing ", filename
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(filename, 'wb') as fh:
            while size > 0:
                if size > 65536:
                    readSize = 65536
                else:
                    readSize = size
                size -= readSize
                line = self.rfile.read(readSize)
                fh.write(line)
        os.utime(filename, (float(modificationTime),float(modificationTime))) # Muda tempo da ultima modificacao
        print "[Uploading Module] Done writing", filename
        filesDictionary[filename] = md5(filename)
        self.send_response(200) # Sucesso

    def send_file(self):
        filename = self.headers['download_filename']
        print "[Downloading Module] Sending ", filename
        self.send_response(200) # Sucesso
        self.send_header('Content-Type', 'application/zip')
        self.send_header('modification_time', str(os.path.getmtime(filename)))
        self.end_headers()
        with open(filename, 'rb') as fh:
            for line in fh:
                self.wfile.write(line)
        print "[Downloading Module] Done sending ", filename

    def remove_file(self):
        global filesDictionary
        filename = self.headers['remove_filename']
        print "[Removing Module] Removing ", filename
        if os.path.exists(filename):
            if not os.path.isdir(filename):
                os.remove(filename)
                del filesDictionary[filename]
            else:
                os.rmdir(filename)
            print "[Removing Module] Done removing ", filename
            self.send_response(200) # Sucesso
        else:
            self.send_response(409) # Failure

def compare(clientDictionary):
    missingArray = []
    downloadArray = []

    missingArray, downloadArray, differentArray, sameArray = dict_compare(clientDictionary, filesDictionary)
    print "[Compare] Client has to Upload", missingArray
    print "[Compare] Client has to Download", downloadArray
    print "[Compare] Different", differentArray
    print "[Compare] Same", sameArray

    # compara os arquivos diferentes. Ganha aquele que foi modificado por ultimo
    for filename in differentArray:
        clientFile = clientDictionary[filename].split('#')[1]
        serverFile = filesDictionary[filename].split('#')[1]

        if serverFile > clientFile:
            print "[Compare] Server Wins:", filename
            downloadArray.append(filename)
        elif clientFile > serverFile:
            print "[Compare] Client Wins:", filename
            missingArray.append(filename)

    return missingArray, downloadArray

def dict_compare(d1, d2):
    d1_keys = set(d1.keys())
    d2_keys = set(d2.keys())
    intersect_keys = d1_keys.intersection(d2_keys)
    added = d1_keys - d2_keys
    removed = d2_keys - d1_keys
    modified = {o : (d1[o], d2[o]) for o in intersect_keys if d1[o] != d2[o]}
    same = set(o for o in intersect_keys if d1[o] == d2[o])
    return list(added), list(removed), list(modified), list(same)

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
    return hash_md5.hexdigest() + "#" + str(os.path.getmtime(fname))

def scan_folder(filesDictionary):
    for path, _, filename_array in os.walk("."):

        # Remove os arquivos que iniciam com um ponto
        filename_array = [ x for x in filename_array if not x.startswith(".") ]

        for filename in filename_array:
            file_path = os.path.join(path, filename)
            #print file_path, md5(file_path)
            filesDictionary[file_path] = md5(file_path)

if __name__ == '__main__':
    from BaseHTTPServer import HTTPServer
    server = HTTPServer(('0.0.0.0', 8080), MyDropboxHandler)

    scan_folder(filesDictionary)

    for key, value in filesDictionary.items():
        print key, value

    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()
