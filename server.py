import socket
import ssl
import threading
import time

import sqlite3
import json


class ClientThread(threading.Thread):

    def __init__(self, _socket, client_addr):
        threading.Thread.__init__(self)

        self._socket = _socket
        print('connected to client:', client_addr)

    def run(self):

        # connect to the database
        conn_u = sqlite3.connect("./database/user_information.db")
        conn_p = sqlite3.connect("./database/patient_information.db")

        u = conn_u.cursor()
        p = conn_p.cursor()

        while True:
            # receive data from the server
            data = self._socket.recv(port).decode()
            if not data:
                break
            print('[%s] %s' % (time.ctime(), data))

            # using the sqlite it will query the table and will authorize if the username and password are correct
            if data == 'login':
                auth = self._socket.recv(port).decode()
                u.execute('SELECT ID, Access_Privilege FROM "user" WHERE "Authorization" = "%s";' % auth)
                q_data = u.fetchone()
                if q_data is None:
                    self._socket.send('Invalid username and password.'.encode())
                else:
                    _id = q_data[0]
                    self._socket.send(q_data[1].encode())

            # it will query the table and will get the names of every one in the database
            if data == 'all_patient_names':
                p.execute('SELECT First_Name, Last_Name FROM patient;')
                self._socket.send(json.dumps(p.fetchall()).encode())

            # it will query the table and will get the id of the entered name
            if data == 'name_to_id':
                name = self._socket.recv(port).decode().split(' ')
                p.execute('SELECT ID FROM patient WHERE First_Name = "%s" and Last_Name = "%s";' % (name[0], name[1]))
                _id = p.fetchone()[0]

            # it will query the table and will get all the information based of off the id
            if data == 'patient_info':
                p.execute('SELECT * FROM patient WHERE ID = "%s";' % _id)
                self._socket.send(json.dumps(p.fetchall()).encode())

            # it will insert the received data into the table
            if data == 'add_patient':
                info = json.loads(self._socket.recv(port).decode())
                u.execute('INSERT INTO "user"(Username, "Authorization", Access_Privilege) VALUES ("%s", "%s", "%s");' % (info[0], info[1], 'patient'))
                conn_u.commit()

                u.execute('SELECT ID FROM "user" WHERE Username = "%s" and Password = "%s";' % (info[0], info[1]))
                _id = u.fetchone()[0]
                p.execute('INSERT INTO patient(ID, First_Name, Last_Name, Address, Phone_Number, Balance) VALUES ("%s", "%s", "%s", "%s", "%s", "%s");' % (_id, info[2], info[3], info[4], info[5], info[6]))
                conn_p.commit()

            # it will remove the selected patients data from both tables
            if data == 'remove_patient':
                u.execute('DELETE FROM "user" WHERE ID = "%s";' % _id)
                conn_u.commit()

                p.execute('DELETE FROM patient WHERE ID = "%s";' % _id)
                conn_p.commit()

            # it will insert the received data into the table
            if data == 'save':
                info = json.loads(self._socket.recv(port).decode())
                p.execute('UPDATE patient SET First_Name = "%s", Last_Name = "%s", Address = "%s", Phone_Number = "%s" WHERE ID = "%s";' % (info[0], info[1], info[2], info[3], _id))
                conn_p.commit()

            # it will update the tables balance with the data in the location of the patients id
            if data == 'pay':
                pay = self._socket.recv(port).decode()
                p.execute('UPDATE patient SET Balance = "%s" WHERE ID = "%s";' % (pay, _id))
                conn_p.commit()

            # disconnect client from server
            if data == 'disconnect':
                break

        print("client at", addr, "disconnected...")


if __name__ == '__main__':

    host = 'localhost'
    port = 9999

    # creates the socket to make the server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind the address and the port to the socket
    server.bind((host, port))

    while True:
        try:
            # listen for any connections
            server.listen(1)
            client, addr = server.accept()
            ssl_server = ssl.wrap_socket(client, server_side=True, ca_certs="./certificate/client.pem", certfile="./certificate/server.pem", keyfile="./certificate/server.key", cert_reqs=ssl.CERT_REQUIRED, ssl_version=ssl.PROTOCOL_TLSv1_2)

            # creates a new thread for each connected client
            thread = ClientThread(client, addr)
            thread.start()
        except Exception as e:
            print(e)
