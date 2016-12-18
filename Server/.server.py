from BaseHTTPServer import BaseHTTPRequestHandler
import os
import json
import hashlib

filesDictionary = {}

class MyDropboxHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.headers.getheader('filename'):
            self.write_file()
        else:
            jsondata = self.rfile.read(int(self.headers['Content-Length']))
            dic = json.loads(jsondata)
            requestArray, downloadArray = compare(dic)

            # Envia resposta
            self.send_response(200) # Sucesso
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(requestArray)) # Envia array com arquivos para enviar para o servidor
            self.wfile.write(json.dumps(downloadArray)) # Envia array com arquivos para enviar para o servidor

    def write_file(self):
        global filesDictionary
        size = long(self.headers['content-length'])
        filename = self.headers['filename']
        length = self.headers['Content-Length']
        print "[Uploading Module] Writing ", filename
        with open(filename, 'wb') as fh:
            while size > 0:
                if size > 65536:
                    readSize = 65536
                else:
                    readSize = size
                size -= readSize
                line = self.rfile.read(readSize)
                fh.write(line)
        print "[Uploading Module] Done writing", filename
        filesDictionary[filename] = md5(filename)
        self.send_response(200) # Sucesso

def compare(metaDataDictionary):
    missingArray = []
    downloadArray = []

    missingArray, downloadArray, differentArray, sameArray = dict_compare(metaDataDictionary, filesDictionary)
    print "Client has to Upload", missingArray
    print "Client has to Download", downloadArray
    print "Modified", differentArray
    print "Same", sameArray

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
    return hash_md5.hexdigest()

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
    server = HTTPServer(('localhost', 8080), MyDropboxHandler)

    scan_folder(filesDictionary)

    for key, value in filesDictionary.items():
        print key, value

    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()
