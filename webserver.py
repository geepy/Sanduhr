import usocket
from uselect import select
from time import sleep

class webserver:
    def __init__(self, draw_time):
        self.draw_time = draw_time;
        self.addr = usocket.getaddrinfo('0.0.0.0', 80)[0][-1]
        self.s = usocket.socket()
        self.s.bind(self.addr)
        self.s.listen(1)

    def client_handler(self, client):
        req = client.recv(1000)
        if req:
            req = ''+str(req, 'utf-8')
            print(req)
            if "?drawTime=" in req:
                new_time = req.substring(req.index('='), 5)
                print('new time is: '+str(new_time, 'utf-8'))

        
        # always return index.html
        client.send('HTTP/1.1 200 OK\n')
        client.send('Content-Type: text/html\n')
        # client.send('Connection: close\n')
        client.send('\n')
        chunksize = 200
        with open ('index.html', 'rb') as f:
            while True:
                read_data = f.read(chunksize)
                if not read_data:
                    break # done
                print(read_data, sep='')
                client.sendall(str(read_data, 'utf-8'))
        client.sendall('\n\n\n\n')
        client.close()

    def run_server(self):
        print('listening on', self.addr)

        while True:
            r, w, err = select((self.s,), (), (), 1)
            if r:
                for readable in r:
                    cl, addr = self.s.accept()
                    print('received request from addr' + str(addr))
                    try:
                        self.client_handler(cl)
                    except OSError as e:
                        print(e)
                        pass
            elif err:
                print(err)
            sleep(1)