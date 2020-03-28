import socket
import ssl
import tkinter as tk
import json
import base64


class GUI(tk.Tk):

    # set up the environment and frames to be made and displayed
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side='top', fill='both', expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (Login, Doctor, Nurse, Patient, Info, Add):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky=tk.W + tk.E + tk.N + tk.S)

        self.user = None
        self.show_frame(Login)

    # raise and shows the given frame
    def show_frame(self, f):
        self.title(str(f.__name__))
        if f == Doctor or f == Nurse or f == Patient:
            self.user = f
        frame = self.frames[f]
        frame.tkraise()
        frame.event_generate("<<ShowFrame>>")

    # shows the previous frame
    def prev_frame(self):
        self.title(str(self.user.__name__))
        frame = self.frames[self.user]
        frame.tkraise()
        frame.event_generate("<<ShowFrame>>")

    # get the user that has logged in
    def get_user(self):
        return self.user.__name__


class Login(tk.Frame):

    # initialize the login user interface frame and what it shows
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        tk.Label(self, text='Enter your username and password.').grid(row=0, columnspan=3, sticky=tk.W + tk.E + tk.N + tk.S, padx=10, pady=(10, 5))

        tk.Label(self, text='Username:').grid(row=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        tk.Label(self, text='Password:').grid(row=2, sticky=tk.W, padx=(10, 0), pady=(0, 5))

        username = tk.Entry(self)
        password = tk.Entry(self, show="*")

        username.grid(row=1, column=1, columnspan=2, sticky=tk.W, padx=(0, 10), pady=(0, 5))
        password.grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=(0, 10), pady=(0, 5))

        tk.Button(self, text='Enter', command=lambda: self.login(controller, username.get() + ' ' + password.get())).grid(row=3, column=2, sticky=tk.E, padx=(0, 10), pady=(0, 5))

    # send the entered user name and password to the server to be authorized
    def login(self, controller, log):
        text = tk.StringVar()
        tk.Label(self, textvariable=text, fg='red').grid(row=4, columnspan=3, sticky=tk.W + tk.E + tk.N + tk.S, padx=10, pady=(0, 10))

        client.send('login'.encode())
        # encrypts the username and password
        encrypted = base64.b64encode(log.encode())
        client.send(encrypted)
        auth = client.recv(port).decode()

        if auth == 'doctor':
            controller.show_frame(Doctor)
        elif auth == 'nurse':
            controller.show_frame(Nurse)
        elif auth == 'patient':
            controller.show_frame(Patient)
        else:
            text.set(auth)


# display all patient names in a listbox
def display(lb):
    client.send('all_patient_names'.encode())
    names = json.loads(client.recv(port).decode())

    lb.delete(0, tk.END)
    for i in range(len(names)):
        lb.insert(i, names[i][0] + ' ' + names[i][1])


# re enables the view/edit button when a name is selected in the listbox
def activate(btn):
    btn.configure(state=tk.NORMAL)


# find the current id of the selected name
def name_to_id(name):
    if name:
        client.send('name_to_id'.encode())
        client.send(str(name).encode())
        # controller.show_frame(Info)


# removes the selected patient name from the listbox
def remove(lb):
    name_to_id(lb.get(lb.curselection()))
    lb.delete(lb.curselection())
    client.send('remove_patient'.encode())


class Doctor(tk.Frame):

    # initialize the doctor user interface frame and what it shows
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        tk.Label(self, text='Select Patient').pack(padx=10, pady=(10, 5))

        lb = tk.Listbox(self)
        lb.yview()
        lb.pack(pady=(0, 5))

        self.bind("<<ShowFrame>>", lambda event: display(lb))

        tk.Label(self, text='Doctor Options').pack(pady=(0, 5))

        b1 = tk.Button(self, text='View/Edit', state=tk.DISABLED, command=lambda: (name_to_id(lb.get(lb.curselection())), controller.show_frame(Info)))
        b1.pack(pady=(0, 5))

        b2 = tk.Button(self, text='Remove Patient', state=tk.DISABLED, command=lambda: remove(lb))
        b2.pack(pady=(0, 5))

        lb.bind("<<ListboxSelect>>", lambda event: (activate(b1), activate(b2)))

        tk.Button(self, text='Logout', command=lambda: controller.show_frame(Login)).pack(pady=(0, 10))


class Nurse(tk.Frame):

    # initialize the nurse user interface frame and what it shows
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        tk.Label(self, text='Select Patient').pack(padx=10, pady=(10, 5))

        lb = tk.Listbox(self, selectmode=tk.SINGLE)
        lb.yview()
        lb.pack(pady=(0, 5))

        self.bind("<<ShowFrame>>", lambda event: display(lb))

        tk.Label(self, text='Nurse Options').pack(pady=(0, 5))

        b1 = tk.Button(self, text='View/Edit', state=tk.DISABLED, command=lambda: (name_to_id(lb.get(lb.curselection())), controller.show_frame(Info)))
        b1.pack(pady=(0, 5))

        tk.Button(self, text='Add Patient', command=lambda: controller.show_frame(Add)).pack(pady=(0, 5))

        b2 = tk.Button(self, text='Remove Patient', state=tk.DISABLED, command=lambda: remove(lb))
        b2.pack(pady=(0, 5))

        lb.bind("<<ListboxSelect>>", lambda event: (activate(b1), activate(b2)))

        tk.Button(self, text='Logout', command=lambda: controller.show_frame(Login)).pack(pady=(0, 10))


class Patient(tk.Frame):

    # initialize the patient user interface frame and what it shows
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        tk.Label(self, text='Patient Options').pack(padx=10, pady=(10, 5))

        tk.Button(self, text='View Balance', command=lambda: controller.show_frame(Info)).pack(pady=(0, 5))
        tk.Button(self, text='Logout', command=lambda: controller.show_frame(Login)).pack(pady=(0, 10))


# save any changes done to the patient info by the doctor or nurse
def save(entries):
    ent = []
    for i in range(len(entries)):
        ent.append(entries[i].get())

    client.send('save'.encode())
    client.send(json.dumps(ent).encode())


# take away or add to balance based on the visit
def pay(controller, amount, balance):
    try:
        sign = amount[:1]
        price = amount[1:].strip()
        if sign == '-':
            total = float(balance) - float(price)
        elif sign == '+':
            total = float(balance) + float(price)
        else:
            total = float(balance) + float(amount)

        client.send('pay'.encode())
        client.send(str(total).encode())
        controller.show_frame(Info)

    except Exception as ex:
        print(ex)


class Info(tk.Frame):

    # initialize the info user interface frame and what it shows
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.bind("<<ShowFrame>>", lambda event: self.display(controller))

    # when frame is displayed it will get the selected patient info from the server and displays it
    def display(self, controller):

        tk.Label(self, text='Information').grid(row=0, columnspan=3, sticky=tk.W + tk.E + tk.N + tk.S, padx=10, pady=(10, 5))
        loc = 1

        client.send('patient_info'.encode())
        info = json.loads(client.recv(port).decode())
        fields = ['ID', 'First_Name', 'Last_Name', 'Address', 'Phone_Number', 'Balance']
        entries = []

        if controller.get_user() != 'Patient':
            for field in fields:
                if field != 'ID':
                    tk.Label(self, text=field.replace('_', ' ') + ':').grid(row=loc, sticky=tk.W, padx=(10, 0), pady=(0, 5))
                    if field == 'Balance':
                        tk.Label(self, text=info[0][loc - 1]).grid(row=loc, column=1, columnspan=2, sticky=tk.W, padx=(0, 10), pady=(0, 5))
                    else:
                        ent = tk.Entry(self)
                        ent.insert(0, info[0][loc - 1])
                        ent.grid(row=loc, column=1, columnspan=2, sticky=tk.W, padx=(0, 10), pady=(0, 5))
                        entries.append(ent)
                loc += 1

            tk.Label(self, text='Account Charge:').grid(row=loc, sticky=tk.W, padx=(10, 0), pady=(0, 5))
            amount = tk.Entry(self)
            amount.grid(row=loc, column=1, columnspan=2, sticky=tk.W, padx=(0, 10), pady=(0, 5))
            loc += 1

            tk.Button(self, text='Save', command=lambda: save(entries)).grid(row=loc, column=2, sticky=tk.E, padx=(0, 10), pady=(0, 5))
            tk.Button(self, text='Update Balance', command=lambda: pay(controller, amount.get(), info[0][len(info[0]) - 1])).grid(row=loc + 1, column=2, sticky=tk.E, padx=(0, 10), pady=(0, 5))
            loc += 2
        else:
            tk.Label(self, text='Balance:').grid(row=loc, sticky=tk.W, padx=(10, 0), pady=(0, 5))
            tk.Label(self, text=info[0][len(info[0]) - 1]).grid(row=loc, column=1, columnspan=2, sticky=tk.W, padx=(0, 10), pady=(0, 5))
            loc += 1

        tk.Button(self, text='Back', command=lambda: controller.prev_frame()).grid(row=loc, column=2, sticky=tk.E, padx=(0, 10), pady=(0, 10))


# add new patient based in the inputted data
def add(controller, entries, text):
    ent = [entries[0].get(), base64.b64encode(entries[1].get().encode()).decode()]
    for i in range(2, len(entries)):
        ent.append(entries[i].get())

    if '' in ent:
        text.set('Please set a value all fields. Enter 0 for \nbalance if there is no account balance.')
    else:
        client.send('add_patient'.encode())
        client.send(json.dumps(ent).encode())
        controller.show_frame(Add)


class Add(tk.Frame):

    # initialize the add user interface frame and what it shows
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.sv = tk.StringVar()

        self.bind("<<ShowFrame>>", lambda event: self.display(controller))

    # when frame is displayed it will display a blank form for a new patient
    def display(self, controller):
        tk.Label(self, text='Add New Patient').grid(row=0, columnspan=3, sticky=tk.W + tk.E + tk.N + tk.S, padx=10, pady=(10, 5))
        loc = 1

        fields = ['Username', 'Password', 'First_Name', 'Last_Name', 'Address', 'Phone Number', 'Balance']
        entries = []

        for field in fields:
            tk.Label(self, text=field.replace('_', ' ') + ':').grid(row=loc, sticky=tk.W, padx=(10, 0), pady=(0, 5))
            ent = tk.Entry(self)
            ent.grid(row=loc, column=1, columnspan=2, sticky=tk.W, padx=(0, 10), pady=(0, 5))
            entries.append(ent)
            loc += 1

        text = tk.StringVar()

        tk.Button(self, text='Add', command=lambda: add(controller, entries, text)).grid(row=loc, column=2, sticky=tk.E, padx=(0, 10), pady=(0, 5))
        tk.Button(self, text='Cancel', command=lambda: controller.prev_frame()).grid(row=loc + 1, column=2, sticky=tk.E, padx=(0, 10), pady=(0, 5))

        tk.Label(self, textvariable=text, fg='red').grid(row=loc + 2, columnspan=3, sticky=tk.W + tk.E + tk.N + tk.S, padx=10, pady=(0, 10))


if __name__ == '__main__':

    host = 'localhost'
    port = 9999

    # creates the socket to make the client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # connects to the server
    client.connect((host, port))
    print("connected")

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.verify_mode = ssl.CERT_REQUIRED

    context.load_verify_locations("./certificate/server.pem")
    context.load_cert_chain(certfile="./certificate/client.pem", keyfile="./certificate/client.key")
    
    if ssl.HAS_SNI:
        ssl_client = context.wrap_socket(client, server_side=False, server_hostname=host)
    else:
        ssl_client = context.wrap_socket(client, server_side=False)

    try:
        # run the gui
        GUI().mainloop()
        client.send('disconnect'.encode())

    except Exception as e:
        print(e)

    # ssl_client.close()
    client.close()
