# -*- coding: utf-8 -*-
__author__ = 'Monkee Magic <magic.monkee.magic@gmail.com>'
__version__ = '2.0.0'

import splunk.admin as admin
import splunk.entity as en
import os
import re
import platform
# import your required python modules

'''
Copyright (C) 2005 - 2010 Splunk Inc. All Rights Reserved.
Description:  This skeleton python script handles the parameters in the configuration page.

      handleList method: lists configurable parameters in the configuration page
      corresponds to handleractions = list in restmap.conf

      handleEdit method: controls the parameters and saves the values
      corresponds to handleractions = edit in restmap.conf

'''


class ConfigApp(admin.MConfigHandler):
    '''
    Set up supported arguments
    '''

    def setup(self):
        if self.requestedAction == admin.ACTION_EDIT:
            for arg in ['url', 'endpoint', 'release', 'proxy_url']:
                self.supportedArgs.addOptArg(arg)

    '''
    Read the initial values of the parameters from the custom file
        ServiceNow.conf, and write them to the setup screen.

    If the app has never been set up,
        uses .../<appname>/default/ServiceNow.conf.

    If app has been set up, looks at
        .../local/ServiceNow.conf first, then looks at
    .../default/ServiceNow.conf only if there is no value for a field in
        .../local/ServiceNow.conf

    For text fields, if the conf file says None, set to the empty string.
    '''

    def handleList(self, confInfo):
        confDict = self.readConf('SplunkAppforAWSBilling')
        if confDict is not None:
            for stanza, settings in confDict.items():
                for key, val in settings.items():
                    if key in ['url', 'endpoint', 'release', 'proxy_url'] and val in [None, '']:
                        val = ''
                    confInfo[stanza].append(key, val)

    '''
    After user clicks Save on setup screen, take updated parameters,
    normalize them, and save them somewhere
    '''

    def handleEdit(self, confInfo):
        name = self.callerArgs.id
        args = self.callerArgs

        if self.callerArgs.data['proxy_url'][0] in [None, '']:
            self.callerArgs.data['proxy_url'][0] = ''

        self.writeConf('SplunkAppforAWSBilling', 'default', self.callerArgs.data)

        input_1 = {'disabled': '1', 'index': 'aws-bill', 'interval': '300', 'source': '',
                   'sourcetype': '', 'passAuth': 'splunk-system-user'}

        input_2 = {'disabled': '1', 'index': 'snoweccqueue', 'interval': '300', 'source': 'SNow_ECC_Queue',
                   'sourcetype': 'SNow_ECC_Queue', 'passAuth': 'splunk-system-user'}



        INPUT_FILE = os.path.join(os.environ['SPLUNK_HOME'], 'etc', 'apps', 'SplunkAppforAWSBilling', 'bin', 'scripts', 'fetch_detailed_report.py')
        INPUT_FILE = 'script://' + INPUT_FILE
        self.writeConf('inputs', INPUT_FILE, input_1)

        SNOW_FILE = os.path.join(os.environ['SPLUNK_HOME'], 'etc', 'apps', 'SplunkAppforAWSBilling', 'bin', 'scripts', 'universal_collector.py ecc_queue')
        SNOW_FILE = 'script://' + SNOW_FILE
        self.writeConf('inputs', SNOW_FILE, input_2)



# initialize the handler
admin.init(ConfigApp, admin.CONTEXT_NONE)
