import socket
import tkinter as tk
import json


class GUI(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        container = tk.Frame(self)

        container.pack(side='top', fill='both', expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (Login, Doctor, Nurse, Patient, Add, Info):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky=tk.W + tk.E + tk.N + tk.S)

        self.user = None
        self.show_frame(Login)

    def show_frame(self, f):
        self.title(str(f.__name__))
        if f == Doctor or f == Nurse or f == Patient:
            self.user = f
        frame = self.frames[f]
        frame.tkraise()
        frame.event_generate("<<ShowFrame>>")

    def get_user(self):
        return self.user.__name__

    def prev_frame(self):
        self.title(str(self.user.__name__))
        frame = self.frames[self.user]
        frame.tkraise()
        frame.event_generate("<<ShowFrame>>")


class Login(tk.Frame):

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

    def login(self, controller, log):
        text = tk.StringVar()
        tk.Label(self, textvariable=text, fg='red').grid(row=4, columnspan=3, sticky=tk.W + tk.E + tk.N + tk.S, padx=10, pady=(0, 10))

        if log:
            client.send('login'.encode())
            client.send(log.encode())
            access = client.recv(port).decode()

            if access == 'patient':
                controller.show_frame(Patient)
            elif access == 'nurse':
                controller.show_frame(Nurse)
            elif access == 'doctor':
                controller.show_frame(Doctor)
            else:
                text.set(access)
        else:
            text.set('You are required to \nenter a username and password.')


def display(lb):
    client.send('all_patient_names'.encode())
    names = json.loads(client.recv(port).decode())

    lb.delete(0, tk.END)
    for i in range(len(names)):
        lb.insert(i, names[i][0])


def activate(btn):
    btn.configure(state=tk.NORMAL)


def name_to_id(controller, name):
    if name:
        client.send('name_to_id'.encode())
        client.send(str(name).encode())
        controller.show_frame(Info)


class Doctor(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        tk.Label(self, text='Select Patient').pack(padx=10, pady=(10, 5))

        lb = tk.Listbox(self)
        lb.yview()
        lb.pack(pady=(0, 5))

        self.bind("<<ShowFrame>>", lambda event: display(lb))

        tk.Label(self, text='Doctor Options').pack(pady=(0, 5))

        btn = tk.Button(self, text='View/Edit', state=tk.DISABLED, command=lambda: name_to_id(controller, lb.get(lb.curselection())))
        btn.pack(pady=(0, 5))

        lb.bind("<<ListboxSelect>>", lambda event: activate(btn))

        tk.Button(self, text='Logout', command=lambda: controller.show_frame(Login)).pack(pady=(0, 10))


def remove(controller, lb):
    lb.delete(lb.curselection())
    name_to_id(controller, lb.get(lb.curselection()))
    client.send('remove_patient'.encode())


class Nurse(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        tk.Label(self, text='Select Patient').pack(padx=10, pady=(10, 5))

        lb = tk.Listbox(self, selectmode=tk.SINGLE)
        lb.yview()
        lb.pack(pady=(0, 5))

        self.bind("<<ShowFrame>>", lambda event: display(lb))

        tk.Label(self, text='Nurse Options').pack(pady=(0, 5))

        b = tk.Button(self, text='View/Edit', state=tk.DISABLED, command=lambda: name_to_id(controller, lb.get(lb.curselection())))
        b.pack(pady=(0, 5))

        lb.bind("<<ListboxSelect>>", lambda event: activate(b))

        tk.Button(self, text='Add Patient', command=lambda: controller.show_frame(Add)).pack(pady=(0, 5))
        tk.Button(self, text='Remove Patient', command=lambda: remove(controller, lb)).pack(pady=(0, 5))
        tk.Button(self, text='Logout', command=lambda: controller.show_frame(Login)).pack(pady=(0, 10))


class Patient(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        tk.Label(self, text='Patient Options').pack(padx=10, pady=(10, 5))

        tk.Button(self, text='View Balance', command=lambda: controller.show_frame(Info)).pack(pady=(0, 5))
        tk.Button(self, text='Logout', command=lambda: controller.show_frame(Login)).pack(pady=(0, 10))


def add(controller, entries, text):
    ent = []
    for i in range(len(entries)):
        ent.append(entries[i].get())

    if '' in ent:
        text.set('Please set a value all fields. Enter 0 for \nbalance if there is no account balance.')
    else:
        client.send('add_patient'.encode())
        client.send(json.dumps(ent).encode())
        controller.show_frame(Add)


class Add(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.sv = tk.StringVar()

        self.bind("<<ShowFrame>>", lambda event: self.display(controller))

    def display(self, controller):
        tk.Label(self, text='Add New Patient').grid(row=0, columnspan=3, sticky=tk.W + tk.E + tk.N + tk.S, padx=10, pady=(10, 5))
        loc = 1

        # client.send('get_patient_fields'.encode())
        # info = json.loads(client.recv(port).decode())
        info = ['Username', 'Password', 'First_Name', 'Last_Name', 'Address', 'Phone Number', 'Balance']
        entries = []

        for item in info:
            tk.Label(self, text=item + ':').grid(row=loc, sticky=tk.W, padx=(10, 0), pady=(0, 5))
            ent = tk.Entry(self)
            ent.grid(row=loc, column=1, columnspan=2, sticky=tk.W, padx=(0, 10), pady=(0, 5))
            entries.append(ent)
            loc += 1

        text = tk.StringVar()

        tk.Button(self, text='Add', command=lambda: add(controller, entries, text)).grid(row=loc, column=2, sticky=tk.E, padx=(0, 10), pady=(0, 5))
        tk.Button(self, text='Cancel', command=lambda: controller.prev_frame()).grid(row=loc + 1, column=2, sticky=tk.E, padx=(0, 10), pady=(0, 5))

        tk.Label(self, textvariable=text, fg='red').grid(row=loc + 2, columnspan=3, sticky=tk.W + tk.E + tk.N + tk.S, padx=10, pady=(0, 10))


def save(entries):
    ent = []
    for i in range(len(entries)):
        ent.append(entries[i].get())

    client.send('save'.encode())
    client.send(json.dumps(ent).encode())


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

    except Exception as e:
        print(e)


class Info(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.bind("<<ShowFrame>>", lambda event: self.display(controller))

    def display(self, controller):

        tk.Label(self, text='Information').grid(row=0, columnspan=3, sticky=tk.W + tk.E + tk.N + tk.S, padx=10, pady=(10, 5))
        loc = 1

        client.send('patient_info'.encode())
        info = json.loads(client.recv(port).decode())
        fields = ['First Name', 'Last Name', 'Address', 'Phone Number', 'Balance']
        entries = []

        if controller.get_user() != 'Patient':
            for field in fields:
                if field != 'ID':
                    if field == 'Balance':
                        tk.Label(self, text=field + ':').grid(row=loc, sticky=tk.W, padx=(10, 0), pady=(0, 5))
                        tk.Label(self, text=info[0][loc - 1]).grid(row=loc, column=1, columnspan=2, sticky=tk.W, padx=(0, 10), pady=(0, 5))
                    else:
                        tk.Label(self, text=field + ':').grid(row=loc, sticky=tk.W, padx=(10, 0), pady=(0, 5))
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
            tk.Button(self, text='Update Balance', command=lambda: pay(controller, amount.get(), info[0][len(info[0]) - 1])).grid(row=loc + 1, column=2, sticky=tk.E, padx=(0, 10),
                                                                                                                                  pady=(0, 5))
            loc += 2
        else:
            tk.Label(self, text='Balance:').grid(row=loc, sticky=tk.W, padx=(10, 0), pady=(0, 5))
            tk.Label(self, text=info[0][len(info[0]) - 1]).grid(row=loc, column=1, columnspan=2, sticky=tk.W, padx=(0, 10), pady=(0, 5))
            loc += 1

        tk.Button(self, text='Back', command=lambda: controller.prev_frame()).grid(row=loc, column=2, sticky=tk.E, padx=(0, 10), pady=(0, 10))


if __name__ == '__main__':

    host = 'localhost'
    port = 9999

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    print("connected")

    try:
        GUI().mainloop()
        client.send('disconnect'.encode())

    except Exception as e:
        print(e)

    client.close()
