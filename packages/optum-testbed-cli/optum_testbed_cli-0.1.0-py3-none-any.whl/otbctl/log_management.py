import os
import time
import logging.config

class log_management():

    def remove_files_by_path(path, days):
        infoLogger = class_instance.get_info_logger_inside_class()
        files_count = 0
        deleted_files_count = 0

        # If user gives no amount of days, then 7 is the default
        if type(days) == type(None):
            days = "7"

        seconds = int(days) * 24 * 60 * 60

        infoLogger.info(f"Starting process to remove files from: {path}")
        # Checking to see if the path given was found
        if os.path.exists(path):
            # Retrieving all the files and looping through each one
            for file in os.listdir(path):
                # Ignoring the .gitkeep files
                if file.startswith('.gitkeep'):
                    continue
                else:
                    files_count += 1
                    file_path = os.path.join(path, file)

                    # Determining if the file should get deleted
                    if class_instance.get_file_age(file_path) > seconds:
                        class_instance.remove_file(file_path)
                        deleted_files_count += 1

        else:
            infoLogger.info(f'"{path}" is not found')

        if files_count > 0:
            infoLogger.info(f"Total log files: {files_count}")
            infoLogger.info(f"Total log files deleted: {deleted_files_count}")
        else:
            infoLogger.info("No files found")
        infoLogger.info("-------------------------------------------")

    def get_file_age(self, path):
        # Getting file age: time that has passed - creation time of the file
        file_age = time.time() - os.stat(path).st_ctime
        return file_age

    def remove_file(self, path):
        infoLogger = class_instance.get_info_logger_inside_class()

        if not os.remove(path):
            infoLogger.info(f"{path} is removed successfully")

        else:
            infoLogger.info(f"Unable to delete the {path}")

    # This will be used inside this class
    def get_info_logger_inside_class(self):
        log_config_file = f"{os.path.expanduser('~')}/.otbctl/config/logging.conf"
        logging.config.fileConfig(log_config_file)
        return logging.getLogger('info')

    # These will be used outside this class
    def get_info_logger():
        log_config_file = f"{os.path.expanduser('~')}/.otbctl/config/logging.conf"
        logging.config.fileConfig(log_config_file)
        return logging.getLogger('info')

    def get_error_logger():
        log_config_file = f"{os.path.expanduser('~')}/.otbctl/config/logging.conf"
        logging.config.fileConfig(log_config_file)
        return logging.getLogger('error')

class_instance = log_management()