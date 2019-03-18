#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import logging
import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext


class AppModel:

    def verify_top(self, top):
        """ Checks if a given path exists and is a directory """
        if os.path.isdir(top):
            return True
        return False

    def verify_brand(self, brand):
        """ Checks if a brand is a valid. """
        if brand:
            return True
        return False

    def verify_inp(self, inp):
        """ Checks if a given string contains any alphanumeric
            characters. """
        if re.search('\w', inp):
            return True
        return False

    def extract_dir_name(self, inp):
        """ Constructs a list from an input list. An input list contains
            lines inserted by user. Function extracts only an initial
            alphanumeric string (directory names) and returns it in 
            a new list. In this case such function is more readable than 
            a list coprehension. """
        dir_name = []
        for i in inp.splitlines():
            s = re.search('\w+', i)
            if s:
                dir_name.append(s.group())
        return dir_name

    def add_brand(self, dir_list, brand=None):
        """ Adds a brand suffix preceded by the delimiter to every
            element of input list if the brand suffix is given and
            returns a new list. """
        delimiter = '_'
        topdir_list = []
        for topdir in dir_list:
            if brand and brand != 'Empty':
                topdir += delimiter + brand
            topdir_list.append(topdir)
        return topdir_list

    def make_dir_tree(self, top, topdir, tree):
        """ Creates directory tree in a given path. """
        for d in tree:
            dpath = os.path.join(top, topdir, *d)
            os.makedirs(dpath, exist_ok=True)

    def make_file_tree(self, top, topdir, tree):
        """ Creates files in a given path. """
        for f in tree:
            fpath = os.path.join(top, topdir, *f)
            if not os.path.isfile(fpath):
                open(fpath, 'w').close()


class AppController:
    
    def __init__(self):
        self.appname = "DirMaker"
        self.version = "1.0"
        self.userdir = os.path.expanduser('~')
        self.basic_dirs = [("01_poczatek",),
                           ("rozliczenia_dla_klienta",),
                           ("90_koniec",)]
        self.dirs_02 = [("02_przygotowanie", "01_sdlxliff_orig"),
                        ("02_przygotowanie", "02_sdlxliff_trans")]
        self.files_02 = [("02_przygotowanie", "01_DE.pdf"),
                         ("02_przygotowanie", "02_DE-PL.pdf"),
                         ("02_przygotowanie", "03_PL.pdf")]
        self.no_pdf = [("rozliczenia_dla_klienta",
                        "brak_pliku_PDF.txt")]
        self.validerr = {'top': "Invalid directory!",
                         'brand': "Brand is not selected!",
                         'inp': "Empty input!"}
        self.configerr = {'nofile': "Configuration file not found.",
                          'parse': "Configuration file parsing error.",
                          'keyerr': " ".join(
                              """Requested value not found 
                              in the configuration file. 
                              Default value is used instead: {}.
                              """.format(self.userdir).split())}

    def init_model(self):
        """ Initialises the Application Model. """
        self.model = AppModel()

    def init_view(self):
        """ Only initialises the Application View. """
        self.view = AppView()

    def create_view(self):
        """ Creates View's widgets. """
        self.view.create_gui()
        self.view.root.title(self.appname)
        self.view.set_statusmsg(" ".join((self.appname, 
                                          'ver.',
                                          self.version)))
        self.view.register(self)

    def show_view(self):
        self.view.mainloop()

    def init_config(self):
        """ Initialise a ConfigParser object, creates a config file 
            path, calls a function loading values from a config 
            file. """
        self.config = configparser.ConfigParser()
        self.configfile = os.path.join(self.appdir, '.settings.ini')
        self.load_config()
        
    def create_appdir(self):
        """ Create a hidden application directory used by a config file
            and log files. """
        self.appdir = os.path.join(self.userdir, 
                                   r'.woffice',
                                   r'.' + self.appname)
        os.makedirs(self.appdir, exist_ok=True)
        
    def create_log(self):
        """ Initialise a logging object and creates a log file. """
        logfile = os.path.join(self.appdir, 
                               ''.join(('.', self.appname, '.log')))
        logging.basicConfig(filename=logfile,
                            filemode='w',
                            format='%(asctime)s - %(message)s', 
                            datefmt='%Y-%m-%d %H:%M:%S')
        self.logger = logging.getLogger(__name__)
        
    def write_config(self, key, val):
        """ Writes data to a config file. """
        self.config['user_options'] = {key: val}
        if not os.path.isdir(self.appdir):
            os.makedirs(self.appdir, exist_ok=True)
        with open(self.configfile, 'w+') as fw:
            self.config.write(fw)

    def load_config(self):
        """ Checks if a configuration file exists, parses and loads 
            data from it to the View. """
        if os.path.isfile(self.configfile):
            try:
                self.config.read(self.configfile)
            except configparser.ParsingError:
                self.logger.warning(self.configerr['parse'])
        else:    
            self.logger.warning(self.configerr['nofile'])
        try:
            top = self.config['user_options']['top']
        except KeyError:
            self.logger.warning(self.configerr['keyerr'])
            top = self.userdir
        self.set_top(top)

    def set_top(self, d):
        """ Calls View's function setting a top path. """
        self.view.set_top(d)

    def get_top(self):
        return self.view.get_top()

    def get_input(self):
        return self.view.get_input()

    def get_brand(self):
        return self.view.get_brand()

    def get_make_02(self):
        return self.view.get_make_02()

    def get_make_pdf(self):
        return self.view.get_make_pdf()

    def create_order_dict(self):
        """ Creates a dictionary object containing data inserted by
            an user. """
        return {
            'top': self.get_top(),
            'brand': self.get_brand(),
            'inp': self.get_input(),
            'make_02': self.get_make_02(),
            'make_pdf': self.get_make_pdf()
            }

    def validate_data(self, order):
        """ Chcecks all values inserted by an user. """
        data_tuple = [
            (self.model.verify_top(order['top']),
             self.validerr['top']),
            (self.model.verify_brand(order['brand']),
             self.validerr['brand']),
            (self.model.verify_inp(order['inp']),
             self.validerr['inp'])]
        verified = []
        for v, msg in data_tuple:
            if not v:
                self.view.showerr(msg)
            verified.append(v)
        if all(verified):
            return True
        return False

    def create_dirs(self, order):
        """ Creates a directory tree according the selected options. """
        inp = self.model.extract_dir_name(order['inp'])
        topdir_list = self.model.add_brand(inp,
                                           order['brand'])
        for topdir in topdir_list:
            self.model.make_dir_tree(order['top'],
                                     topdir,
                                     self.basic_dirs)

            if order['make_02']:
                self.model.make_dir_tree(order['top'],
                                         topdir,
                                         self.dirs_02)
                self.model.make_file_tree(order['top'],
                                          topdir,
                                          self.files_02)
            if order['make_pdf']:
                self.model.make_file_tree(order['top'],
                                          topdir,
                                          self.no_pdf)

    def run(self):
        """ Main function of the Controller. """
        order = self.create_order_dict()
        if self.validate_data(order):
            self.write_config('top', order['top'])
            self.create_dirs(order)
            self.view.set_statusmsg("Done!")


class AppView:

    def __init__(self):
        self.controller = None

    def create_gui(self):
        self.root = tk.Tk()
        self.top = tk.StringVar()
        self.brand = tk.StringVar()
        self.make_02 = tk.BooleanVar()
        self.make_pdf = tk.BooleanVar()
        self.statusmsg = tk.StringVar()
        self.create_inputfield()
        self.create_top_selector()
        self.create_option_selector()
        self.create_brand_selector()
        self.create_button()
        self.create_statusbar()

    def register(self, controller):
        self.controller = controller

    def mainloop(self):
        self.root.mainloop()

    def create_top_selector(self):
        frame = ttk.Frame(self.root, padding=5)
        ttk.Button(frame,
                   command=self.ask_top,
                   text="Browse...").pack(side=tk.LEFT)
        ttk.Entry(frame,
                  textvariable=self.top,
                  width=50).pack(expand=1,
                                 fill=tk.X)
        frame.pack(expand=0, fill=tk.BOTH, side=tk.TOP)

    def set_top(self, d):
        self.top.set(d)

    def ask_top(self):
        d = filedialog.askdirectory(initialdir=self.get_top())
        if d:
            self.set_top(d)

    def get_top(self):
        return self.top.get()

    def create_option_selector(self):
        frame = ttk.Frame(self.root, padding=5)
        ttk.Checkbutton(frame,
                        text="Utwórz katalog \\02_przygotowanie",
                        variable=self.make_02).pack(side=tk.LEFT,
                                                    padx=(0, 10))
        ttk.Checkbutton(frame,
                        text="Brak pliku PDF w GOCAT",
                        variable=self.make_pdf).pack(side=tk.LEFT,
                                                     padx=(0, 10))
        frame.pack(expand=0, fill=tk.BOTH, side=tk.TOP)

    def create_brand_selector(self):
        frame = ttk.Frame(self.root, padding=5)
        brands = ['Audi', 'Seat', 'Skoda', 'VW11', 'VW12', 'VW51', 
                  'VW66', 'Empty']
        for brand in brands:
            ttk.Radiobutton(frame,
                            text=brand,
                            value=brand, 
                            variable=self.brand).pack(side=tk.LEFT,
                                                      padx=(0, 10))
        frame.pack(expand=0, fill=tk.BOTH, side=tk.TOP)

    def showerr(self, msg):
        messagebox.showerror(title='Error', message=msg)

    def get_brand(self):
        return self.brand.get()

    def get_input(self):
        inp = self.scrolltext.get('1.0', tk.END)
        return inp

    def get_make_02(self):
        return self.make_02.get()

    def get_make_pdf(self):
        return self.make_pdf.get()

    def create_inputfield(self):
        frame = ttk.Frame(self.root, padding=5)
        ttk.Label(frame, text="Insert text:").pack(fill=tk.X,
                                                   pady=(10, 0))
        self.scrolltext = tk.scrolledtext.ScrolledText(frame,
                                                       height=15,
                                                       width=45,
                                                       wrap=tk.WORD)
        self.scrolltext.pack(expand=1, fill=tk.BOTH)
        frame.pack(expand=1, fill=tk.BOTH, side=tk.TOP)

    def create_button(self):
        frame = ttk.Frame(self.root, padding=5)
        ttk.Button(frame,
                   command=self._quit,
                   text='Cancel',
                   width=10).pack(side=tk.RIGHT)
        ttk.Button(frame,
                   command=self.run,
                   text='OK',
                   width=10).pack(side=tk.RIGHT)
        frame.pack(expand=0, fill=tk.BOTH, side=tk.TOP)

    def create_statusbar(self):
        frame = ttk.Label(self.root, padding=5)
        ttk.Label(frame,
                  borderwidth=1,
                  relief=tk.SUNKEN,
                  textvariable=self.statusmsg).pack(expand=1,
                                                    fill=tk.BOTH)
        frame.pack(expand=0, fill=tk.BOTH, side=tk.TOP)

    def set_statusmsg(self, msg):
        self.statusmsg.set(msg)

    def run(self):
        self.controller.run()

    def _quit(self):
        self.root.quit()
        self.root.destroy()


def main():
    controller = AppController()
    controller.init_model()
    controller.init_view()
    controller.create_view()
    controller.create_appdir()
    controller.create_log()
    controller.init_config()
    controller.show_view()


if __name__ == '__main__':
    main()
