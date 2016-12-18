from BaseHTTPServer import BaseHTTPRequestHandler
import os
import json
import hashlib

class MyDropboxHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        print self.headers.items()
        if self.headers.getheader('filename'):
            self.write_file()
        else:
            jsondata = self.rfile.read(int(self.headers['Content-Length']))
            dic = json.loads(jsondata)
            requestArray = compare(dic)

            # Envia resposta
            self.send_response(200) # Sucesso
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(requestArray)) # Envia array com arquivos para enviar para o servidor

    def write_file(self):
        size = long(self.headers['content-length'])
        filename = self.headers['filename']
        length = self.headers['Content-Length']
        with open(filename, 'wb') as fh:
            while size > 0:
                if size > 65536:
                    readSize = 65536
                else:
                    readSize = size
                size -= readSize
                line = self.rfile.read(readSize)
                fh.write(line)
        print "Done"
        self.send_response(200) # Sucesso

def compare(metaDataDictionary):
    missingArray = []
    for filePath, fileMD5 in metaDataDictionary.items():
        #print filePath, fileMD5

        if not os.path.isfile(filePath):
            print filePath, "does not exist here!"
            missingArray.append(filePath)
            continue

        if fileMD5 != md5(filePath):
            print filePath, "has different md5!"
            continue
    print "Done checking"
    return missingArray

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

if __name__ == '__main__':
    from BaseHTTPServer import HTTPServer
    server = HTTPServer(('localhost', 8080), MyDropboxHandler)
    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()
