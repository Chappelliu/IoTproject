#modified from lesson2 socket server and rpi_spreadsheet
# server part of the system
from tkinter import *
import json
import sys
import gspread
import psutil
import subprocess
from oauth2client.service_account import ServiceAccountCredentials
import socket
import datetime, time

#global variable
dat = ''
part = ''
module = ''
node = ''
addr = {}
addr[0] = 'UNCONNECTED'
#function part
def server_main():
    correct_module = 0
    correct_part = 0
    node1_prev = 0
    node2_prev = 0
    node3_inti = 0
    finished_num = 0
    effective = 0
    time_int = 5
    HOST = ''                 # Symbolic name meaning all available interfaces
    PORT = 50007              # Arbitrary non-privileged port
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)
    while 1:
        print_to_status('Ready to accepting new data...')
        conn, addr = s.accept()
        print('Connected by', addr)
        data = conn.recv(1024)
        if not data: break
        conn.sendall(data)
        update_addr(addr[0])
        print_to_status('Accepting...')
        data = repr(data)
        module,part,node,dat = data.split(',')
        part = part[1:]
        module = module[2:]
        dat = dat[1:-2]
        node = node[1:6]
        #check if the assembly line is too fast
        if node == 'Node1':
            if node1_prev == 0:
                node1_prev = time.time()
                #print_to_gui("time settled")
            else:
                time_int = time.time() - node1_prev
                node1_prev = time.time()
            if time_int < 5:
                print_to_status('Node1 is too fast')
        if node == 'Node2':
            if node2_prev == 0:
                node2_prev = time.time()
            else:
                time_int = time.time() - node2_prev
                node2_prev = time.time()
            if time_int < 5:
                print_to_status('Node2 is too fast')
        #check if the module or part is wrong on the assembly line
        if correct_module == 0:
            correct_module = module
            correct_part = part
        elif module != correct_module:
            msg = 'Module is wrong, the correct one should be ' + correct_module
            print_to_status('Stop')
            print(msg)
            warningmsg(msg)
            break
        elif part != correct_part:
            msg = 'Part is wrong, the correct one should be ' + correct_part
            print_to_status('Stop')
            print(msg)
            warningmsg(msg)
            break
        #compute the efficiency
        if node == 'Node3':
            if node3_inti == 0:
                node3_inti = time.time()
                finished_num = finished_num + 1
            else:
                finished_num = finished_num + 1
                time_dif = time.time() - node3_inti
                effective = finished_num/time_dif

        print('{0},{1},{2},{3}.'.format(module,part,node,dat))
        GDOCS_OAUTH_JSON       = 'AssemblyLine-d0c856e4b131.json'
        GDOCS_SPREADSHEET_NAME = 'AssemblyLine'
        FREQUENCY_SECONDS      = 10
        def login_open_sheet(oauth_key_file, spreadsheet):
            try:
                credentials = ServiceAccountCredentials.from_json_keyfile_name(oauth_key_file,
                              scopes = ['https://spreadsheets.google.com/feeds',
                                        'https://www.googleapis.com/auth/drive'])
                gc = gspread.authorize(credentials)
                worksheet = gc.open(spreadsheet).sheet1
                return worksheet
            except Exception as ex:
                print('Unable to login and get spreadsheet. Check OAuth credentials, spreadsheet name, and')
                print('make sure spreadsheet is shared to the client_email address in the OAuth .json file!')
                print('Google sheet login failed with error:', ex)
                sys.exit(1)
        worksheet = None
        if worksheet is None:
            worksheet = login_open_sheet(GDOCS_OAUTH_JSON, GDOCS_SPREADSHEET_NAME)
        #print(dat)
        #print(part)
        #print(module)
        #print(node)
        try:
            worksheet.append_row((dat,part, module, node, effective))
        #        worksheet.append_row((dat, cpu, tmp))
        # gspread==0.6.2
        # https://github.com/burnash/gspread/issues/511
        except:
            print_to_gui('Append error, logging in again')
            worksheet = None
            continue
        #print('Wrote a row to {0}'.format(GDOCS_SPREADSHEET_NAME))
    conn.close()

#print the result to gui
def print_to_status(text_string):
    statusbar.config(text=text_string)
    # Force the GUI to update
    app.update()

def update_addr(conn_addr_text):
    conn_addr_entry.config(text=conn_addr_text)
    app.update()

def warningmsg(msg):
    popup = Tk()
    popup.title("!")
    warning_label = Label(popup, text=msg, font= ('bold', 14))
    warning_label.pack(side="top", fill="x", pady=10)
    B1 = Button(popup, text="Ok, I know",width = 20, font= ('bold', 14), command = popup.destroy)
    B1.pack()
    popup.mainloop()

#gui
app = Tk()

#button
add_btn = Button(app, text='Start Demo!', width=12, command=server_main)
add_btn.pack()

#Alert log
conn_addr_text = StringVar()
conn_addr_text.set(addr[0])
conn_addr_label = Label(app, text='Connected Nodes', font=('bold', 14))
conn_addr_label.pack()
conn_addr_entry = Label(app, text = 'UNCONNECTED')
conn_addr_entry.pack()

app.title('ASL Monitoring Simulator')
app.geometry('400x200')
#status bar
statusbar = Label(app, text="Ready to Start…", bd = 1, relief=SUNKEN, anchor=W)
statusbar.pack(side = BOTTOM, fill =X)

app.mainloop()