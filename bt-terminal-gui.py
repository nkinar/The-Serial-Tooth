import tkinter as tki
import pygatt
import re
from tkinter import messagebox
from threading import Thread, Lock

# DEFINES
adapter = pygatt.BGAPIBackend()
mutex = Lock()
ENABLE_STATE = True
DISABLE_STATE = False
CONNECT_TEXT = '  Connect '
DISCONNECT_TEXT = 'Disconnect'
CHARACTERISTIC_ADDR = 'e7add780-b042-4876-aae1-112855353cc1'

ECHO_STRING = False
PRINT_STRING_TO_TERM = False
DISABLE_TEXT_WHEN_NOT_CONNECTED = False

"""
Bluetooth LE Application to communicate with a Bluetooth device
that implements a serial port
"""


class BTGui:
    def __init__(self):
        """
        Initialize the main frame and the variables
        """
        # MAIN FRAME
        self.root = tki.Tk()

        # create a Frame for the Text and Scrollbar
        txt_frm = tki.Frame(self. root, width=800, height=400)
        txt_frm.pack(fill="both", expand=True)
        # ensure a consistent GUI size
        txt_frm.grid_propagate(False)
        # implement stretchability
        txt_frm.grid_rowconfigure(0, weight=1)
        txt_frm.grid_columnconfigure(0, weight=1)

        # create a Text widget
        self.txt = tki.Text(txt_frm, borderwidth=3, relief="sunken", blockcursor=True)
        self.txt.config(font=("consolas", 12), undo=True, wrap='word')
        self.txt.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.bind_text_event()
        self.enable_disable_text(DISABLE_STATE)

        # create a scrollbar and associate it with the text
        scrollb = tki.Scrollbar(txt_frm, command=self.txt.yview)
        scrollb.grid(row=0, column=1, sticky='nsew')
        self.txt['yscrollcommand'] = scrollb.set

        # Quit button
        self.q_button = tki.Button(self.root,
                        text="Quit",
                        command=quit)
        self.q_button.pack(side=tki.LEFT)

        # Clear button
        self.q_button = tki.Button(self.root,
                                   text="Clear",
                                   command=self.clear_text)
        self.q_button.pack(side=tki.LEFT)

        # name of device
        self.entry_label = tki.Label(self.root, text="Device address: ")
        self.entry_label.pack(side=tki.LEFT)

        # entry to set the name of the device
        self.list_entry_name = tki.Entry(self.root)
        self.list_entry_name.pack(side=tki.LEFT)

        # Connect button
        self.btn_text = tki.StringVar(self.root)
        self.btn_text.set(CONNECT_TEXT)
        self.connect_button = tki.Button(self.root,
                                   textvariable=self.btn_text,
                                   command=self.connect_to_device)
        self.connect_button.pack(side=tki.LEFT)

        # VARS
        self.connected = False
        self.t_read = None
        self.device = None
        self.uuid = None
        self.clear_to_send = True

    def ignore_text_changed(self, value=None):
        """
        Ignore the text changed
        :return:
        """
        pass

    def bind_text_event(self):
        """
        Bind the text event
        :return:
        """
        self.txt.bind('<<Modified>>', self.text_changed)

    def unbind_text_event(self):
        """
        Unbind the text event
        :return:
        """
        self.txt.bind('<<Modified>>', self.ignore_text_changed)

    def clear_txt_box(self):
        """
        Clear the text box
        :return:
        """
        self.txt.delete("1.0", tki.END)

    def str_to_byte_array(self, s):
        """
        Convert a string to byte array
        :param s:
        :return:
        """
        return str.encode(s)

    def send_string_to_module(self, s):
        """
        Send a string to the module
        :param s:
        :return:
        """
        try:
            for c in s:
                ba = self.str_to_byte_array(c)
                self.device.char_write(self.uuid, ba, wait_for_response=True)
        except:
            self.do_disconnect()

    def check_echo_print(self, val):
        if ECHO_STRING:
            self.text_insert(val)
        if PRINT_STRING_TO_TERM:
            print('User input:', val)

    def text_changed(self, value=None):
        """
        Call this function when the text has been changed
        :param value:
        :return:
        """
        flag = self.txt.edit_modified()
        if flag:
            if self.clear_to_send is False:
                self.clear_to_send = True
                self.txt.edit_modified(False)  # important to ensure that event will continue to fire
                return
            input_value = self.txt.get("end-2c", tki.END)
            self.txt.delete("end-2c", tki.END)
            if input_value[-2] == '\r' or input_value[-2] == '\n':
                val = '\r'
            else:
                val = input_value.strip()
            # send the character to the module
            self.check_echo_print(val)
            if self.connected:
                self.send_string_to_module(val)
        # set the edit modified variable
        self.txt.edit_modified(False)
        # DONE

    def text_insert(self, t):
        """
        Insert text to the text edit box.
        NOTE that we need to unbind the text event to prevent an endless loop
        :param t:
        :return:
        """
        self.clear_to_send = False
        self.txt.insert(tki.END, t)
        self.txt.see("end")  # ensure that the textbox scrolls  to the end of the insert


    def check_python_addr(self, x):
        """
        Check the MAC address to ensure that it is of the right format
        https://stackoverflow.com/questions/7629643/how-do-i-validate-the-format-of-a-mac-address
        :param x:
        :return:
        """
        if re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", x.lower()):
            return True
        return False

    def update_connect_button_text(self, caption):
        """
        Update the connect button text
        :param caption:
        :return:
        """
        self.btn_text.set(caption)

    def enable_disable_connect_button(self, state):
        """
        Enable or disable the connect button
        :param state:
        :return:
        """
        if state:
            self.connect_button['state'] = 'normal'
        else:
            self.connect_button['state'] = 'disabled'

    def busy_cursor(self):
        """
        Set the window cursor to the busy state
        :return:
        """
        self.root.config(cursor="wait")

    def normal_cursor(self):
        """
        Set the window cursor to the normal cursor
        :return:
        """
        self.root.config(cursor="arrow")

    def enable_disable_text(self, state):
        """
        Set the text to enable or disable
        :param state:
        :return:
        """
        if not DISABLE_TEXT_WHEN_NOT_CONNECTED:
            return
        if state:
            self.txt.config(state='enabled')
        else:
            self.txt.config(state='disabled')

    def handle_data(self, handle, value):
        """
        Function that is called from the module when the data arrives
        :param handle:
        :param value:
        :return:
        """
        c = value.decode('utf-8')
        self.text_insert(c)
        if PRINT_STRING_TO_TERM:
            print('Module received:', c)

    def do_read(self):
        """
        Do read from the module.  NOTE that to be able to communicate with the module,
        the indication must be True.
        :return:
        """
        while self.connected:
            try:
                self.device.subscribe(CHARACTERISTIC_ADDR, callback=self.handle_data, indication=True)
            except:
                self.connected = False
                self.do_disconnect()
                break

    def setup_read_from_device(self):
        """
        Start the read from the device
        :return:
        """
        self.t_read = Thread(target=self.do_read)
        self.t_read.start()

    def do_connect(self, addr):
        """
        Do the connection to the Bluetooth module
        :param addr:
        :return:
        """
        self.enable_disable_connect_button(DISABLE_STATE)
        self.busy_cursor()
        self.connected = False
        self.uuid = None
        if not self.check_python_addr(addr):
            messagebox.showinfo("Information", "Address is of wrong format")
            self.enable_disable_connect_button(ENABLE_STATE)
            self.normal_cursor()
            return
        try:
            adapter.start()
            self.device = adapter.connect(addr)
            self.device.bond()
            for uuid in self.device.discover_characteristics().keys():
                if str(uuid) == CHARACTERISTIC_ADDR:
                    self.uuid = uuid
                    self.connected = True
                    self.setup_read_from_device()
            if self.uuid is None:
                messagebox.showinfo("Information", "Could not find UUID for device")
        except:
            messagebox.showinfo("Information", "Could not connect to device")
        self.normal_cursor()
        if self.connected:
            self.update_connect_button_text(DISCONNECT_TEXT)
        self.enable_disable_connect_button(ENABLE_STATE)

    def do_disconnect(self):
        """
        Disconnect from the adapter
        :return:
        """
        mutex.acquire()
        try:
            adapter.stop()
        except:
            pass
        finally:
            mutex.release()
        self.uuid = None
        self.connected = False
        self.update_connect_button_text(CONNECT_TEXT)
        self.enable_disable_text(DISABLE_STATE)

    def connect_to_device(self):
        """
        Connect to device
        :return:
        """
        if not self.connected:
            # connect to the device
            addr = self.list_entry_name.get().strip()
            t = Thread(target=self.do_connect, args=(addr,))
            t.start()
        else:  # device is connected, so disconnect
            t = Thread(target=self.do_disconnect)
            t.start()
            self.t_read.join()  # wait until the reading thread is finished

    def clear_text(self):
        """
        Clear the text in the frame
        :return:
        """
        self.txt.delete("1.0", tki.END)


# CREATE THE MAIN APP AND THE MAIN LOOP
app = BTGui()
app.root.title('The Serial Tooth')
app.root.mainloop()
