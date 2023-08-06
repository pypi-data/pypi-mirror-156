from distutils.log import error
import sys, getopt
import os
import argparse
from telnetlib import STATUS
from unittest import mock
from wsgiref.headers import Headers        
import dotenv 
import requests
import json
import yaml
from tabulate import tabulate
from .log_management import log_management
from .otbctl_main  import otbcli
from .otbctl_mock import mockapi

class testbed():

    def getMocks():
        errorLogger = log_management.get_error_logger()
        infoLogger = log_management.get_info_logger()

        context= otbcli.getContext('otbctl-context')
        try:
            server_url = context +"/mocks"
        except TypeError:

            errorLogger.error("Context must be set first. usage: otbctl setcontext")
            errorLogger.info("-------------------------------------------")
            exit()

        method='get'

        try:
            response = requests.get(server_url)
        except:
            errorLogger.error("Please ensure Docker container is running.")
            exit()

        if response.status_code == 400:
            errorLogger.error(f'400 response from server {response.url}')
            errorLogger.info("-------------------------------------------")
            sys.exit
        elif response.status_code == 200:  
            infoLogger.info('200 OK') 
            responsedata = response.json()
            
            if( responsedata == 0):
                infoLogger.info("No Mocks are registered")
            else:
                mocks_table = []
                for mock in response.json():
                    mock_row = []
                    state = mock['state']['id']
                    path = mock['request']['path']['value']
                    method = mock['request']['method']['value']
                    creation = mock['state']['creation_date']
                    mock_row.extend([state, path, method, creation])
                    mocks_table.append(mock_row)

                infoLogger.info(tabulate(mocks_table, headers=["\nMockID", "\nPath", "\nMethod", "\nCreation"]))

    def getMockbyID(id):
        errorLogger = log_management.get_error_logger()
        infoLogger = log_management.get_info_logger()

        context= otbcli.getContext('otbctl-context')
        server_url = context +"/mocks?id="+id
        method='GET'
        response = requests.get(server_url)

        if response.status_code == 400:
            errorLogger.error(f'Response: 400 Not Found {response.url}')
            errorLogger.info("-------------------------------------------")
            sys.exit
        elif response.status_code == 200:  
            infoLogger.info('Response: 200 OK') 
            responsedata = response.json()
            
            if( responsedata == 0):
                infoLogger.info("No Mocks are registered")
            else:
                infoLogger.info(f'{json.dumps(response.json(), indent=4)}')

    def addMock(config):
        errorLogger = log_management.get_error_logger()
        infoLogger = log_management.get_info_logger()

        context= otbcli.getContext('otbctl-context')
        try:
            server_url = context +"/mocks"
        except TypeError:
            errorLogger.error("Context must be set first. usage: otbctl setcontext")
            errorLogger.info("-------------------------------------------")
            exit()

        method='POST'
       # getdatafromapi='{"access_token":"d6ac8cff-3807-364c-97c5-7b3f312cb054","scope":"am_application_scope default","token_type":"Bearer","expires_in":464}"'
        getdatafromapi = mockapi.mockit(config)
        infoLogger.info(f"Received data from Configured end point {getdatafromapi}")
        
        payload = class_instance.buildPayload(getdatafromapi, config)
        
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request(method, server_url, headers=headers, data=payload)
        infoLogger.info(response.text)

    def buildPayload(self, payload, config):
        infoLogger = log_management.get_info_logger()
        
        replacedString = payload.replace('"','\\"')
        replaceadditional = replacedString.replace('\\\\"','\\"')

        with open(config) as f:
             cfg = yaml.safe_load(f)

        status = cfg['workflows']['flow']['testbed']['request']['status']
        converted_num = f'{status}'
        
        querylist={}
        if(cfg['workflows']['flow']['testbed']['request']['params'] is not None):
            for x in cfg['workflows']['flow']['testbed']['request']['params']:
                querylist.update(x)
        queryParams = str(querylist)
        replacedquery = queryParams.replace('\'','"')

        headerlist={}
        if(cfg['workflows']['flow']['testbed']['request']['headers'] is not None):
            for y in cfg['workflows']['flow']['testbed']['request']['headers']:
                headerlist.update(y)
        replacedHeaders = str(headerlist).replace('\'','"')
     
        if(cfg['workflows']['flow']['testbed']['request']['body'] is not None):
           replacedBody = cfg['workflows']['flow']['testbed']['request']['body'].replace('"','\\"')
           replacedNewLine= replacedBody.replace('\n','\\n')
       
        
        if(cfg['workflows']['flow']['testbed']['request']['method'] =='POST'):
            jsonString ='[{"request": { "method": "'+cfg['workflows']['flow']['testbed']['request']['method']+'","path": "'+cfg['workflows']['flow']['testbed']['request']['path']+'","body":"'+ replacedNewLine+'"},"response": { "status": '+converted_num +',"headers":' + replacedHeaders+',"body": "' +replaceadditional+ '"}}]'
        else:
            jsonString ='[{"request": { "method": "'+cfg['workflows']['flow']['testbed']['request']['method']+'","path": "'+cfg['workflows']['flow']['testbed']['request']['path']+'","query_params":'+replacedquery+'},"response": { "status": '+converted_num +',"headers":' + replacedHeaders+',"body": "' +replaceadditional+ '"}}]'
    
    
        infoLogger.info(jsonString)
        return jsonString

    def load(file):
        infoLogger = log_management.get_info_logger()
        errorLogger = log_management.get_error_logger()
        infoLogger.info(f' Loading Mocks from File -> {file}')
        context= otbcli.getContext('otbctl-context')
        try:
            server_url = context +"/mocks"
        except TypeError:
            errorLogger.error("Context must be set first. usage: otbctl setcontext")
            errorLogger.info("-------------------------------------------")
            exit()

        method='POST'
        file1 = open(file, 'r')
        Lines = file1.readlines()
        count = 0
        # Strips the newline character
        for line in Lines:
            count += 1
            payload = line.strip()
            jsonRe = json.dumps(payload)
            infoLogger.info("Adding Mock to mock server.....", jsonRe)
            headers = {
                'Content-Type': 'application/json'
            }
           # response = requests.request(method, server_url, headers=headers, data=payload)
           # infoLogger.info(response.text)

    def delMocks():
        errorLogger = log_management.get_error_logger()
        infoLogger = log_management.get_info_logger()

        context= otbcli.getContext('otbctl-context')
        try:
            server_url = context +"/reset"
        except TypeError:
            errorLogger.error("Context not set, no mocks to delete. usage: otbctl setcontext")
            errorLogger.info("-------------------------------------------")
            exit()
        response = requests.request("POST", server_url)
        if response.status_code == 400:
            errorLogger.error(f'400 response from server {response.url}')
            errorLogger.info("-------------------------------------------")
            sys.exit
        elif response.status_code == 200:  
            infoLogger.info('200 OK') 
            infoLogger.info(response.text)

class_instance = testbed()