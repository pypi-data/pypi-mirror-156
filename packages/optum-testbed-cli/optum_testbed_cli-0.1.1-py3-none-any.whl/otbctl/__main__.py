from cgi import test
from multiprocessing import context
import sys, getopt
import argparse
import os
from .otbctl_main  import otbcli
from .otbctl_server import testbed
from .log_management import log_management
from .yaml_validate import validate_config

def main():
    args = sys.argv[1:]
    otbctl_parsers(args)

def otbctl_parsers(args):

        parser = argparse.ArgumentParser(description='Optum Testbed CLI')
        subparsers = parser.add_subparsers(dest='subparser')

        parser_context = subparsers.add_parser('setcontext')
        parser_context.add_argument(
            '-s', '--server', dest='host', help='Set the context of the Optum TestBed Server e.g localhost:8080')

        parser_context = subparsers.add_parser('getcontext')
        parser_context.add_argument(
            dest='current', help='Get the current of the Optum TestBed Server e.g localhost:8080')

        parser_get = subparsers.add_parser('get')
        parser_get.add_argument(
            '-g', '--getmocks', dest='getmocks', help='Get the list of all the mocks')
        
        parser_init = subparsers.add_parser('add')
        parser_init.add_argument(
            '-f', '--filename', dest='config_yaml', help='Init Mock on server for a given config.yaml')
        
        parser_init = subparsers.add_parser('load')
        parser_init.add_argument(
            '-f', '--filename', dest='mock_data', help='Load Mock into server from the Data file')

        parser_init = subparsers.add_parser('reset')
        parser_init.add_argument(
            dest='all', help='Reset and Empty Mock Data from Optum TestBed Server e.g localhost:8080')

        parser_init = subparsers.add_parser('removelogs')
        parser_init.add_argument(
            dest='folder', help='Choose which logs to remove e.g. otbctl removelogs info -d 7')
        parser_init.add_argument(
            '-d', '--days-old', dest='days', help='Optional: choose the files to delete based on age e.g. delete files older than 7 days')

        kwargs = vars(parser.parse_args())
        globals()[kwargs.pop('subparser')](**kwargs)

def load(mock_data):
    errorLogger = log_management.get_error_logger()

    if(mock_data is None):

        errorLogger.error(' Please provide valid mock data file with -f option, refer documentation for data format')
        errorLogger.info("-------------------------------------------")
    else:
        testbed.load(mock_data)

def setcontext(host):
    infoLogger = log_management.get_info_logger()
    errorLogger = log_management.get_error_logger()

    if( host is None):

        errorLogger.error(' Please provide server name with the -s option e.g otbctl setcontext -s http://localhost:8080')
        errorLogger.info("-------------------------------------------")
    else:
        infoLogger.info(' Setting context...')
        otbcli.setContext(host)
        infoLogger.info(f' otbctl context set to -> {otbcli.getContext("otbctl-context")}')
        infoLogger.info("-------------------------------------------")
         

def getcontext(current):
    infoLogger = log_management.get_info_logger()

    infoLogger.info(' Getting context...')
    infoLogger.info(f' otbctl context set to -> {otbcli.getContext("otbctl-context")}')
    infoLogger.info("-------------------------------------------")


def get(getmocks):
    infoLogger = log_management.get_info_logger()

    if getmocks is not None:
        infoLogger.info(f'Getting Mock by ID -> {getmocks}')
        testbed.getMockbyID(getmocks)
    else:
        infoLogger.info('Getting Mocks...')
        testbed.getMocks()

    infoLogger.info("-------------------------------------------")


def add(config_yaml):
    infoLogger = log_management.get_info_logger()
    errorLogger = log_management.get_error_logger()

    if config_yaml is not None:
        validate_config(config_yaml)
        infoLogger.info('Adding Mock...')
        testbed.addMock(config_yaml)
        infoLogger.info("-------------------------------------------")
    else:
        errorLogger.error("Please provide config yaml with -f option ")
        errorLogger.info("-------------------------------------------")


def reset(all):
    # keyword all presently required in command, 
    # i.e. `obtctl reset all`
    infoLogger = log_management.get_info_logger()

    infoLogger.info('Resetting and emptying mock data from test bed server...')
    testbed.delMocks()

    infoLogger.info("-------------------------------------------")

def removelogs(folder, days):
    path = f"otbctl/logs/{folder}"
    log_management.remove_files_by_path(path, days)

if __name__ == '__main__':
    main()