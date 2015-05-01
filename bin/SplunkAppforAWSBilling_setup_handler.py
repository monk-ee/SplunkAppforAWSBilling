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
        confDict = self.readConf('ServiceNow')
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

        if self.callerArgs.data['url'][0] in [None, '']:
            self.callerArgs.data['url'][0] = ''

        if self.callerArgs.data['endpoint'][0] in [None, '']:
            self.callerArgs.data['endpoint'][0] = ''

        if self.callerArgs.data['release'][0] in [None, '']:
            self.callerArgs.data['release'][0] = ''

        if self.callerArgs.data['proxy_url'][0] in [None, '']:
            self.callerArgs.data['proxy_url'][0] = ''

        self.writeConf('ServiceNow', 'default', self.callerArgs.data)

        input_1 = {'disabled': '1', 'index': 'snowincident', 'interval': '300', 'source': 'SNow_Incident',
                   'sourcetype': 'SNow_Incident', 'passAuth': 'splunk-system-user'}

        input_2 = {'disabled': '1', 'index': 'snoweccqueue', 'interval': '300', 'source': 'SNow_ECC_Queue',
                   'sourcetype': 'SNow_ECC_Queue', 'passAuth': 'splunk-system-user'}

        input_3 = {'disabled': '1', 'index': 'snowsysclustermessage', 'interval': '300',
                   'source': 'SNow_Sys_Cluster_Message',
                   'sourcetype': 'SNow_Sys_Cluster_Message', 'passAuth': 'splunk-system-user'}

        input_4 = {'disabled': '1', 'index': 'snowsysclusterstate', 'interval': '300', 'source': 'SNow_Sys_Cluster_State',
                   'sourcetype': 'SNow_Sys_Cluster_State', 'passAuth': 'splunk-system-user'}

        input_5 = {'disabled': '1', 'index': 'snowsysemail', 'interval': '300', 'source': 'SNow_Sys_Email',
                   'sourcetype': 'SNow_Sys_Email', 'passAuth': 'splunk-system-user'}

        input_6 = {'disabled': '1', 'index': 'snowsysstatus', 'interval': '300', 'source': 'SNow_Sys_Status',
                   'sourcetype': 'SNow_Sys_Status', 'passAuth': 'splunk-system-user'}

        input_7 = {'disabled': '1', 'index': 'snowsysuser', 'interval': '300', 'source': 'SNow_Sys_User',
                   'sourcetype': 'SNow_Sys_User', 'passAuth': 'splunk-system-user'}

        input_8 = {'disabled': '1', 'index': 'snowsyslogtransaction', 'interval': '300',
                   'source': 'SNow_Syslog_Transaction',
                   'sourcetype': 'SNow_Syslog_Transaction', 'passAuth': 'splunk-system-user'}

        input_9 = {'disabled': '1', 'index': 'snowvclusternodes', 'interval': '300', 'source': 'SNow_V_Cluster_Nodes',
                   'sourcetype': 'SNow_V_Cluster_Nodes', 'passAuth': 'splunk-system-user'}

        input_10 = {'disabled': '1', 'index': 'snowvtransaction', 'interval': '300', 'source': 'SNow_V_Transaction',
                    'sourcetype': 'SNow_V_Transaction', 'passAuth': 'splunk-system-user'}

        input_11 = {'disabled': '1', 'index': 'snoweccqueueretryactivity', 'interval': '300', 'source': 'SNow_ECC_Queue_Retry_Activity',
                    'sourcetype': 'SNow_ECC_Queue_Retry_Activity', 'passAuth': 'splunk-system-user'}

        SNOW_FILE = os.path.join(os.environ['SPLUNK_HOME'], 'etc', 'apps', 'ServiceNow', 'bin', 'scripts', 'universal_collector.py incident')
        SNOW_FILE = 'script://' + SNOW_FILE
        self.writeConf('inputs', SNOW_FILE, input_1)

        SNOW_FILE = os.path.join(os.environ['SPLUNK_HOME'], 'etc', 'apps', 'ServiceNow', 'bin', 'scripts', 'universal_collector.py ecc_queue')
        SNOW_FILE = 'script://' + SNOW_FILE
        self.writeConf('inputs', SNOW_FILE, input_2)

        SNOW_FILE = os.path.join(os.environ['SPLUNK_HOME'], 'etc', 'apps', 'ServiceNow', 'bin', 'scripts', 'universal_collector.py sys_cluster_message')
        SNOW_FILE = 'script://' + SNOW_FILE
        self.writeConf('inputs', SNOW_FILE, input_3)

        SNOW_FILE = os.path.join(os.environ['SPLUNK_HOME'], 'etc', 'apps', 'ServiceNow', 'bin', 'scripts', 'universal_collector.py sys_cluster_state')
        SNOW_FILE = 'script://' + SNOW_FILE
        self.writeConf('inputs', SNOW_FILE, input_4)

        SNOW_FILE = os.path.join(os.environ['SPLUNK_HOME'], 'etc', 'apps', 'ServiceNow', 'bin', 'scripts', 'universal_collector.py sys_email')
        SNOW_FILE = 'script://' + SNOW_FILE
        self.writeConf('inputs', SNOW_FILE, input_5)

        SNOW_FILE = os.path.join(os.environ['SPLUNK_HOME'], 'etc', 'apps', 'ServiceNow', 'bin', 'scripts', 'universal_collector.py sys_status')
        SNOW_FILE = 'script://' + SNOW_FILE
        self.writeConf('inputs', SNOW_FILE, input_6)

        SNOW_FILE = os.path.join(os.environ['SPLUNK_HOME'], 'etc', 'apps', 'ServiceNow', 'bin', 'scripts', 'universal_collector.py sys_user')
        SNOW_FILE = 'script://' + SNOW_FILE
        self.writeConf('inputs', SNOW_FILE, input_7)

        SNOW_FILE = os.path.join(os.environ['SPLUNK_HOME'], 'etc', 'apps', 'ServiceNow', 'bin', 'scripts', 'universal_collector.py syslog_transaction')
        SNOW_FILE = 'script://' + SNOW_FILE
        self.writeConf('inputs', SNOW_FILE, input_8)

        SNOW_FILE = os.path.join(os.environ['SPLUNK_HOME'], 'etc', 'apps', 'ServiceNow', 'bin', 'scripts', 'v_cluster_nodes_collector.py')
        SNOW_FILE = 'script://' + SNOW_FILE
        self.writeConf('inputs', SNOW_FILE, input_9)

        SNOW_FILE = os.path.join(os.environ['SPLUNK_HOME'], 'etc', 'apps', 'ServiceNow', 'bin', 'scripts', 'universal_collector.py v_transaction')
        SNOW_FILE = 'script://' + SNOW_FILE
        self.writeConf('inputs', SNOW_FILE, input_10)

        SNOW_FILE = os.path.join(os.environ['SPLUNK_HOME'], 'etc', 'apps', 'ServiceNow', 'bin', 'scripts', 'universal_collector.py ecc_queue_retry_activity')
        SNOW_FILE = 'script://' + SNOW_FILE
        self.writeConf('inputs', SNOW_FILE, input_11)

# initialize the handler
admin.init(ConfigApp, admin.CONTEXT_NONE)
