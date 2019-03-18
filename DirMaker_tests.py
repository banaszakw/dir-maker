#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import io
import DirMaker
import os
import sys
import unittest
from unittest import mock


class TestAppModel(unittest.TestCase):

    def setUp(self):
        self.m = DirMaker.AppModel()

    def test_verify_top(self):
        with mock.patch('DirMaker.os.path.isdir') as misdir:
            misdir.side_effect = [True, False]
            top = '/home'
            result = self.m.verify_top(top)
            self.assertTrue(result)
            result = self.m.verify_top(top)
            self.assertFalse(result)

    def test_verify_brand(self):
        result = self.m.verify_brand('')
        self.assertFalse(result)
        result = self.m.verify_brand('Test')
        self.assertTrue(result)
        result = self.m.verify_brand(None)
        self.assertFalse(result)

    def test_verify_inp(self):
        result = self.m.verify_inp("  \n  \n  \n  \r\n")
        self.assertFalse(result)
        inp = """ 11957 - Audi_A3_2013_TM40\r\n
                \r\n
                OC0000789 \n
               """
        result = self.m.verify_inp(inp)
        self.assertTrue(result)

    def test_extract_dir_name(self):
        inp = """ AIGG000956 - V11.0_Audi A4_2015\r\n
                ARL005853 - V11.0_Audi A4_2015_Achsantrieb hint...\r\n
                ARL005925 - V6.0_Audi R8_2015_Elektrische Anlage\r\n
                11957 - Audi_A3_2013_TM40\r\n
                \r\n
                OC0000789 \n
                OC0000790 \n
                VRL011916 - V12.0_Golf Sportsvan_2015_6 Gang-Sc...\n
                VRL011917 - V26.0_CC_2010_6 Gang-Schaltgetriebe 02Q\n
                VRL011919 - V5.0_Tiguan_2016_6 Gang-Schaltgetri...\n
                """
        out = ["AIGG000956", "ARL005853", "ARL005925", "11957", "OC0000789",
               "OC0000790", "VRL011916", "VRL011917", "VRL011919"]
        result = self.m.extract_dir_name(inp)
        self.assertListEqual(result, out)

        inp = """  \n  \n  \n  \r\n"""
        out = []
        result = self.m.extract_dir_name(inp)
        self.assertListEqual(result, out)

    def test_add_brand(self):
        dir_list = ["AIGG000956", "ARL005853", "ARL005925", "11957",
                    "OC0000789", "OC0000790"]
        brand = 'Audi'
        out = ["AIGG000956_Audi", "ARL005853_Audi", "ARL005925_Audi",
               "11957_Audi", "OC0000789_Audi", "OC0000790_Audi"]
        result = self.m.add_brand(dir_list, brand)
        self.assertListEqual(result, out)
        brand = None
        out = ["AIGG000956", "ARL005853", "ARL005925", "11957", "OC0000789",
               "OC0000790"]
        result = self.m.add_brand(dir_list)
        self.assertListEqual(result, out)

    def test_make_dir_tree(self):
        top = os.path.normpath('/home')
        topdir = 'VRL011916_VW11'
        basic_tree = [("01_poczatek",),
                      ("rozliczenia_dla_klienta",),
                      ("90_koniec",),]
        calls = [mock.call(os.path.normpath('/home/VRL011916_VW11/01_poczatek'), exist_ok=True),
                 mock.call(os.path.normpath('/home/VRL011916_VW11/rozliczenia_dla_klienta'), exist_ok=True),
                 mock.call(os.path.normpath('/home/VRL011916_VW11/90_koniec'), exist_ok=True)]
        DirMaker.os.makedirs = mock.Mock()
        result = self.m.make_dir_tree(top, topdir, basic_tree)
        DirMaker.os.makedirs.assert_has_calls(calls)
        assert DirMaker.os.makedirs.call_count == 3

    def test_make_file_tree(self):
        top = os.path.normpath('/home')
        topdir = 'VRL011916_VW11'
        in_files = [("02_przygotowanie", "01_DE.pdf"),
                    ("02_przygotowanie", "02_DE-PL.pdf"),
                    ("02_przygotowanie", "03_PL.pdf"),]
        calls = [mock.call(os.path.normpath('/home/VRL011916_VW11/02_przygotowanie/01_DE.pdf'), 'w'),
                 mock.call().close(),
                 mock.call(os.path.normpath('/home/VRL011916_VW11/02_przygotowanie/02_DE-PL.pdf'), 'w'),
                 mock.call().close(),
                 mock.call(os.path.normpath('/home/VRL011916_VW11/02_przygotowanie/03_PL.pdf'), 'w'),
                 mock.call().close()]
        if sys.version_info < (3, 5):
            with mock.patch('builtins.open') as mopen:
                DirMaker.os.path.isfile = mock.Mock(return_value=False)
                self.m.make_file_tree(top, topdir, in_files)
                mopen.assert_has_calls(calls)
        else:
            with mock.patch('DirMaker.open', mock.mock_open(),
                            create=True) as mopen:
                DirMaker.os.path.isfile = mock.Mock(return_value=False)
                self.m.make_file_tree(top, topdir, in_files)
                mopen.assert_has_calls(calls)


class TestAppController(unittest.TestCase):

    def setUp(self):
        self.c = DirMaker.AppController()
        self.c.init_model()
        self.c.init_view = mock.Mock()
        self.model_patch = mock.patch.multiple('DirMaker.AppModel',
                                               extract_dir_name=mock.DEFAULT,
                                               add_brand=mock.DEFAULT,
                                               make_dir_tree=mock.DEFAULT,
                                               make_file_tree=mock.DEFAULT)
        self.mp = self.model_patch.start()

    def tearDown(self):
        self.model_patch.stop()

    def test_create_dirs_0(self):
        """ Scenario 0:  """
        counter = 3
        inp = list(range(counter))
        self.mp['add_brand'].return_value = inp
        self.mp['extract_dir_name'].return_value = inp
        order = {'top': '/home',
                 'brand': 'VW12',
                 'inp': inp,
                 'make_02': True,
                 'make_pdf': True}
        result = self.c.create_dirs(order)
        assert self.mp['extract_dir_name'].call_count == 1
        assert self.mp['add_brand'].call_count == 1
        assert self.mp['make_dir_tree'].call_count == 2 * counter
        assert self.mp['make_file_tree'].call_count == 2 * counter

    def test_create_dirs_1(self):
        """ Scenaerio 1:  """
        counter = 10
        inp = list(range(counter))
        self.mp['extract_dir_name'].return_value = inp
        self.mp['add_brand'].return_value = inp
        order = {'top': '/home',
                 'brand': 'Audi',
                 'inp': inp,
                 'make_02': False,
                 'make_pdf': False}
        result = self.c.create_dirs(order)
        assert self.mp['extract_dir_name'].call_count == 1
        assert self.mp['add_brand'].call_count == 1
        assert self.mp['make_dir_tree'].call_count == counter
        assert not self.mp['make_file_tree'].called

    def test_create_dirs_2(self):
        """ Scenario 2: """
        counter = 21
        inp = list(range(counter))
        self.mp['add_brand'].return_value = inp
        self.mp['extract_dir_name'].return_value = inp
        order = {'top': '/home',
                 'brand': 'Audi',
                 'inp': inp,
                 'make_02': True,
                 'make_pdf': False}
        result = self.c.create_dirs(order)
        assert self.mp['extract_dir_name'].call_count == 1
        assert self.mp['add_brand'].call_count == 1
        assert self.mp['make_dir_tree'].call_count == 2 * counter
        assert self.mp['make_file_tree'].call_count == counter

    def test_create_dirs_3(self):
        """ Scenario 3: """
        counter = 0
        inp = list(range(counter))
        self.mp['add_brand'].return_value = inp
        self.mp['extract_dir_name'].return_value = inp
        order = {'top': '/home',
                 'brand': 'Audi',
                 'inp': inp,
                 'make_02': True,
                 'make_pdf': True}
        result = self.c.create_dirs(order)
        assert self.mp['extract_dir_name'].call_count == 1
        assert self.mp['add_brand'].call_count == 1
        assert not self.mp['make_dir_tree'].called
        assert not self.mp['make_file_tree'].called


class TestValidateData(unittest.TestCase):
    """ Class doc """

    def setUp(self):
        self.c = DirMaker.AppController()
        self.c.init_model()
        self.c.init_view()
        self.mockshowerr = mock.patch('DirMaker.AppView.showerr')
        self.model_patch = mock.patch.multiple('DirMaker.AppModel',
                                               verify_top=mock.DEFAULT,
                                               verify_brand=mock.DEFAULT,
                                               verify_inp=mock.DEFAULT)
        self.order = {'top': None,
                      'brand': None,
                      'inp': None,
                      'make_02': None,
                      'make_pdf': None}
        # self.cp = self.contr_patch.start()
        self.mshowerr = self.mockshowerr.start()
        self.mp = self.model_patch.start()

    def tearDown(self):
        self.mockshowerr.stop()
        self.model_patch.stop()

    def test_validate_data_0(self):
        """ Scenario 0: All of three verifications are passed. """
        self.mp['verify_top'].return_value = True
        self.mp['verify_brand'].return_value = True
        self.mp['verify_inp'].return_value = True
        result = self.c.validate_data(self.order)
        assert self.mshowerr.call_count == 0
        self.assertTrue(result)

    def test_validate_data_1(self):
        """ Scenario 1: """
        self.mp['verify_top'].return_value = False
        self.mp['verify_brand'].return_value = True
        self.mp['verify_inp'].return_value = True
        result = self.c.validate_data(self.order)
        assert self.mshowerr.call_count == 1
        self.mshowerr.assert_called_once_with(self.c.validerr['top'])
        self.assertFalse(result)

    def test_validate_data_2(self):
        """ Scenario 2: """
        self.mp['verify_top'].return_value = True
        self.mp['verify_brand'].return_value = False
        self.mp['verify_inp'].return_value = True
        result = self.c.validate_data(self.order)
        assert self.mshowerr.call_count == 1
        self.mshowerr.assert_called_once_with(self.c.validerr['brand'])
        self.assertFalse(result)

    def test_validate_data_3(self):
        """ Scenario 3: """
        self.mp['verify_top'].return_value = True
        self.mp['verify_brand'].return_value = False
        self.mp['verify_inp'].return_value = False
        result = self.c.validate_data(self.order)
        assert self.mshowerr.call_count == 2
        calls = [mock.call(self.c.validerr['brand']),
                 mock.call(self.c.validerr['inp'])]
        self.mshowerr.assert_has_calls(calls)
        self.assertFalse(result)


class TestRun(unittest.TestCase):

    def setUp(self):
        self.c = DirMaker.AppController()
        self.c.init_model()
        self.c.init_view = mock.Mock()
        self.c.view = mock.Mock()
        self.c.config = configparser.ConfigParser()
        self.controller_patch = mock.patch.multiple('DirMaker.AppController',
                                                    get_top=mock.DEFAULT,
                                                    get_make_02=mock.DEFAULT,
                                                    get_make_pdf=mock.DEFAULT,
                                                    get_input=mock.DEFAULT,
                                                    get_brand=mock.DEFAULT)
        self.model_patch = mock.patch.multiple('DirMaker.AppModel',
                                               extract_dir_name=mock.DEFAULT,
                                               add_brand=mock.DEFAULT,
                                               make_dir_tree=mock.DEFAULT,
                                               make_file_tree=mock.DEFAULT)
        self.order = {'top': '/home',
                      'brand': 'Audi',
                      'inp': 'OC0000789\nOC0000790',
                      'make_02': False,
                      'make_pdf': True}
        self.cp = self.controller_patch.start()
        self.mp = self.model_patch.start()

    def tearDown(self):
        self.controller_patch.stop()
        self.model_patch.stop()

    def test_create_order_dict(self):
        self.cp['get_top'].return_value = self.order['top']
        self.cp['get_brand'].return_value = self.order['brand']
        self.cp['get_input'].return_value = self.order['inp']
        self.cp['get_make_02'].return_value = self.order['make_02']
        self.cp['get_make_pdf'].return_value = self.order['make_pdf']
        result = self.c.create_order_dict()
        self.assertDictEqual(result, self.order)

    def test_write_config_0(self):
        """ Scenario 0:  """
        self.c.configfile = io.StringIO()
        self.c.appdir = os.path.normpath('/test')
        key, val = ('top', '/home')
        calls = [mock.call().write("[user_options]\n"),
                 mock.call().write("top = /home\n"),
                 mock.call().write("\n")]
        m = mock.mock_open()
        # DirMaker.os.path.dirname = mock.Mock()
        # DirMaker.os.path.exists = mock.Mock(return_value=True)
        DirMaker.os.path.isdir = mock.Mock(return_value=True)
        DirMaker.os.makedirs = mock.Mock()
        if sys.version_info < (3, 5):
            mopen = mock.patch('builtins.open', m, create=True)
        else:
            mopen = mock.patch('DirMaker.open', m)
        mopen.start()
        # if sys.version_info < (3, 5):
        #     print("Py 3.4")
        #     with mock.patch('builtins.open',  m, create=True) as mopen:
        #         self.c.write_config(key, val)
        #         m.assert_called_once_with(self.c.configfile, 'w+')
        #         assert m().write.call_count == 3
        #         m.assert_has_calls(calls)
        #         assert not DirMaker.os.makedirs.called
        # else:
        #     print("Py 3.5")
        #     with mock.patch('DirMaker.open', m):
        #         self.c.write_config(key, val)
        #         m.assert_called_once_with(self.c.configfile, 'w+')
        #         assert m().write.call_count == 3
        #         m.assert_has_calls(calls)
        #         assert not DirMaker.os.makedirs.called
        self.c.write_config(key, val)
        m.assert_called_once_with(self.c.configfile, 'w+')
        assert m().write.call_count == 3
        m.assert_has_calls(calls)
        assert not DirMaker.os.makedirs.called
        mopen.stop()

    def test_write_config_1(self):
        """ Scenario 1:  """
        self.c.configfile = io.StringIO()
        self.c.appdir = os.path.normpath('/test')
        key, val = ('top', '/home')
        calls = [mock.call().write("[user_options]\n"),
                 mock.call().write("top = /home\n"),
                 mock.call().write("\n")]
        m = mock.mock_open()
        DirMaker.os.path.isdir = mock.Mock(return_value=False)
        DirMaker.os.makedirs = mock.Mock(return_value=None)
        if sys.version_info < (3, 5):
            mopen = mock.patch('builtins.open', m, create=True)
        else:
            mopen = mock.patch('DirMaker.open', m)
        mopen.start()
        self.c.write_config(key, val)
        m.assert_called_once_with(self.c.configfile, 'w+')
        assert m().write.call_count == 3
        m.assert_has_calls(calls)
        DirMaker.os.makedirs.assert_called_once_with(os.path.normpath('/test'),
                                                     exist_ok=True)
        mopen.stop()

    def test_run_0(self):
        """ Scenario 0: controller.validate_data returns False"""
        self.c.create_order_dict = mock.Mock(return_value=self.order)
        self.c.write_config = mock.Mock()
        self.c.create_dirs = mock.Mock()
        self.c.create_dirs = mock.Mock()
        self.c.view.set_statusmsg = mock.Mock()
        self.c.validate_data = mock.Mock(return_value=False)
        self.c.run()
        assert self.c.create_order_dict.call_count == 1
        assert not self.c.write_config.called
        assert not self.c.create_dirs.called
        assert not self.c.view.set_statusmsg.called

    def test_run_1(self):
        """ Scenario 1: controller.validate_data returns True"""
        self.c.create_order_dict = mock.Mock(return_value=self.order)
        self.c.write_config = mock.Mock()
        self.c.create_dirs = mock.Mock()
        self.c.view.set_statusmsg = mock.Mock()
        self.c.validate_data = mock.Mock(return_value=True)
        self.c.run()
        assert self.c.create_order_dict.call_count == 1
        assert self.c.write_config.call_count == 1
        assert self.c.create_dirs.call_count == 1
        self.c.view.set_statusmsg.assert_called_once_with("Done!")


class TestConfigAndLog(unittest.TestCase):

    def setUp(self):
        self.c = DirMaker.AppController()
        self.c.config = configparser.ConfigParser()
        self.c.configfile = 'test.ini'
        self.c.logger = mock.Mock()
        self.c.set_top = mock.Mock()

    def test_create_appdir(self):
        DirMaker.os.makedirs = mock.Mock()
        self.c.appname = os.path.normpath('testapp')
        self.c.userdir = os.path.normpath('/home/user')
        out = os.path.normpath('/home/user/.woffice/.testapp')
        self.c.create_appdir()
        DirMaker.os.makedirs.assert_called_once_with(out, exist_ok=True)

    def test_init_config(self):
        self.c.load_config = mock.Mock()
        self.c.appdir = os.path.normpath('/home/user/.woffice/.testapp')
        out = os.path.normpath('/home/user/.woffice/.testapp/.settings.ini')
        self.c.init_config()
        self.assertEqual(self.c.configfile, out)
        assert self.c.load_config.called

    def test_load_config_0(self):
        """ Scenario 0:
            - the config file doesn't exists - os.path.isfile: False,
            - ConfigParser raises KeyError,
            - set_top loads default value,
            - logger writes two messages to the log file.
        """
        # DirMaker.os.path.exists = mock.Mock(return_value=False)
        DirMaker.os.path.isfile = mock.Mock(return_value=False)
        self.c.config.read = mock.Mock()
        with self.assertRaises(KeyError):
            DirMaker.configparser.ConfigParser()['user_options']
        self.c.load_config()
        calls = [mock.call.warning(self.c.configerr['nofile']),
                 mock.call.warning(self.c.configerr['keyerr'])]
        assert not self.c.config.read.called
        self.c.logger.assert_has_calls(calls)
        self.c.set_top.assert_called_once_with(self.c.userdir)

    def test_load_config_1(self):
        """ Scenario 1:
            - the config file exists - os.path.isfile: True
            - the config file is read successfully,
            - set_top loads value from the config file,
            - logger doesn't write any messages to the log file.
        """
        self.c.config.read_dict({'user_options': {'top': '/home/test'}})
        # DirMaker.os.path.exists = mock.Mock(return_value=True)
        DirMaker.os.path.isfile = mock.Mock(return_value=True)
        self.c.config.read = mock.Mock()
        self.c.load_config()
        assert self.c.config.read.call_count == 1
        assert not self.c.logger.warning.called
        self.c.set_top.assert_called_once_with('/home/test')

    def test_load_config_2(self):
        """ Scenario 2:
            - the config file exists - os.path.isfile: True,
            - parsing config file failed,
            - set_top loads default value,
            - logger writes two messages to the log file.
        """
        self.c.config.read = mock.Mock(side_effect=configparser.ParsingError('None'))
        DirMaker.os.path.isfile = mock.Mock(return_value=True)
        with self.assertRaises(configparser.ParsingError):
            self.c.config.read()
        self.c.config.read_dict({'': {'': ''}})
        self.c.load_config()
        self.c.set_top.assert_called_once_with(self.c.userdir)
        calls = [mock.call.warning(self.c.configerr['parse']),
                 mock.call.warning(self.c.configerr['keyerr'])]
        assert self.c.logger.warning.call_count == 2
        self.c.logger.assert_has_calls(calls)


if __name__ == '__main__':
    unittest.main()
