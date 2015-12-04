# -*- coding: utf-8 -*-
__author__ = 'Monkee Magic <magic.monkee.magic@gmail.com>'
__author__ = "monkee"
__license__ = "GPLv3.0"
__version__ = "2.0.7"
__maintainer__ = "monk-ee"
__email__ = "magic.monkee.magic@gmail.com"
__status__ = "Production"

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
            for arg in ['proxy_url', 'proxy_port', 'proxy_user', 'proxy_pass']:
                self.supportedArgs.addOptArg(arg)

    '''
    Read the initial values of the parameters from the custom file
        SplunkAppforAWSBilling.conf, and write them to the setup screen.

    If the app has never been set up,
        uses .../<appname>/default/SplunkAppforAWSBilling.conf.

    If app has been set up, looks at
        .../local/SplunkAppforAWSBilling.conf first, then looks at
    .../default/SplunkAppforAWSBilling.conf only if there is no value for a field in
        .../local/SplunkAppforAWSBilling.conf

    For text fields, if the conf file says None, set to the empty string.
    '''

    def handleList(self, confInfo):
        confDict = self.readConf('SplunkAppforAWSBilling')
        if confDict is not None:
            for stanza, settings in confDict.items():
                for key, val in settings.items():
                    if key in ['proxy_url', 'proxy_port', 'proxy_user', 'proxy_pass'] and val in [None, '']:
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

        if self.callerArgs.data['proxy_port'][0] in [None, '']:
            self.callerArgs.data['proxy_port'][0] = ''

        if self.callerArgs.data['proxy_user'][0] in [None, '']:
            self.callerArgs.data['proxy_user'][0] = ''

        if self.callerArgs.data['proxy_pass'][0] in [None, '']:
            self.callerArgs.data['proxy_pass'][0] = ''

        self.writeConf('SplunkAppforAWSBilling', 'default', self.callerArgs.data)

        input_1 = {'disabled': '0', 'index': 'aws-bill', 'interval': '10800', 'source': 'SplunkAppforAWSBilling_Import',
                   'sourcetype': 'SplunkAppforAWSBilling_Processor', 'passAuth': 'splunk-system-user'}

        INPUT_FILE = os.path.join(os.environ['SPLUNK_HOME'], 'etc', 'apps', 'SplunkAppforAWSBilling', 'bin', 'ProcessDetailedReport.py')
        INPUT_FILE = 'script://' + INPUT_FILE
        self.writeConf('inputs', INPUT_FILE, input_1)



# initialize the handler
admin.init(ConfigApp, admin.CONTEXT_NONE)
