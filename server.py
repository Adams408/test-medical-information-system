import socket
import threading
import time

import sqlite3
import json


class ClientThread(threading.Thread):

    def __init__(self, _socket, client_addr):
        threading.Thread.__init__(self)

        self._socket = _socket
        print("connected to client:", client_addr)

    def run(self):
        try:
            while True:
                data = self._socket.recv(port).decode()
                if not data:
                    break
                print("[%s] %s" % (time.ctime(), data))

                if data == 'login':
                    log = self._socket.recv(port).decode().split(' ')
                    u.execute('SELECT ID, Access_Privilege FROM "user" WHERE Username = "%s" and Password = "%s";' % (log[0], log[1]))
                    q_data = u.fetchone()
                    if q_data is None:
                        self._socket.send('Invalid username and password.'.encode())
                    else:
                        _id = q_data[0]
                        self._socket.send(q_data[1].encode())

                if data == 'all_patient_names':
                    p.execute('SELECT First_Name, Last_Name FROM patient;')
                    self._socket.send(json.dumps(p.fetchall()).encode())

                if data == 'name_to_id':
                    name = self._socket.recv(port).decode().split(' ')
                    p.execute('SELECT ID FROM patient WHERE First_Name = "%s", Last_Name = "%s";' % (name[0], name[1]))
                    _id = p.fetchone()[0]

                if data == 'patient_info':
                    p.execute('SELECT * FROM patient WHERE ID = "%s";' % _id)
                    self._socket.send(json.dumps(p.fetchall()).encode())

                if data == 'get_patient_fields':
                    p.execute('PRAGMA table_info(PATIENT)')
                    self._socket.send(json.dumps(p.fetchalll()).encode())

                if data == 'add_patient':
                    info = json.loads(self._socket.recv(port).decode())
                    u.execute('INSERT INTO "user"(Username, Password, Access_Privilege) VALUES ("%s", "%s", patient);' % (info[0], info[1]))
                    conn_u.commit()

                    u.execute('SELECT ID FROM "user" WHERE Username = "%s" and Password = "%s";' % (info[0], info[1]))
                    _id = u.fetchone()
                    p.execute('INSERT INTO patient(ID, First_Name, Last_Name, Address, Phone_Number, Balance) VALUES ("%s", "%s", "%s", "%s", "%s", "%s");' % (_id, info[2], info[3], info[4], info[5], info[6]))
                    conn_p.commit()

                if data == 'remove_patient':
                    u.execute('DELETE * FROM "user" WHERE ID = "%s";' % _id)
                    conn_u.commit()

                    p.execute('DELETE * FROM patient WHERE ID = "%s";' % _id)
                    conn_p.commit()

                if data == 'save':
                    info = json.loads(self._socket.recv(port).decode())
                    p.execute('UPDATE patient SET First_Name = "%s", Last_Name = "%s", Address = "%s", Phone_Number = "%s" WHERE ID = "%s";' % (info[0], info[1], info[2], info[3], _id))
                    conn_p.commit()

                if data == 'pay':
                    pay = self._socket.recv(port).decode()
                    p.execute('UPDATE patient SET Balance = "%s" WHERE ID = "%s";' % (pay, _id))
                    conn_p.commit()

                if data == 'disconnect':
                    break

        except Exception as e:
            print(e)

        print("client at", addr, "disconnected...")


if __name__ == '__main__':

    conn_u = sqlite3.connect('./database/user_information.db')
    conn_p = sqlite3.connect('./database/patient_information.db')

    u = conn_u.cursor()
    p = conn_p.cursor()

    host = 'localhost'
    port = 9999

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))

    while True:
        server.listen(1)
        client, addr = server.accept()
        thread = ClientThread(client, addr)
        thread.start()
