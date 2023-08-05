"""
This is the class that will handle all of the operations.
We are going to make it so that this will work very nicely in a pipeline.

Everything that is generalizable will be in here and called in
the pipeline.

Everything that is custom will have to be created for the pipeline.

TODO test... obviously!!
TODO make into a package
"""

import pandas as pd
import numpy as np
import logging

class Excel_Automation_Operations:
    
    def __init__(self, log_location, mode='a', custom_format='%(asctime)s - %(levelname)s - %(message)s'):
        """Inits the logger
        
        Args:
            log_location (str): path to log
            mode (str, optional): write mode for the log file
            custom_format (str, optional): custom formatting for log line headers
        """
        # initialize the log
		logging.basicConfig(
			filename='{}.log'.format(log_location),
			filemode=mode,
		    format=custom_format)
		logging.info("Starting the script.")

	def verify_zips(self, zip_column, sheet):
        """Make sure that the zip codes are formatted properly
        ZIP codes are all stored as strings

        Args:
            zip_column (str): name of the column containing the zip codes
            sheet (df): dataframe representing the excel sheet
        """
        if sheet[zip_column].dtype != 'str':
            sheet[zip_column] = sheet[zip_column].astype('str')

        # check to make sure everything is 5 digits.
        # check none over 5
        if len(sheet[sheet[zip_column].map(len) > 5]) > 0:
            logging.error("ZIP code has more than 5 digits")
            logging.error(sheet[sheet[zip_column].map(len) > 5])
            sys.exit()

    	def zero_pad_zip(zip):
            # pad a 0 if the zip code is less than 5 digits
            if len(zip) < 5:
    	        zero_pad = '0'
    	        return zero_pad + zip
    	    return zip    

    # if anything has less than 5 digits append a leading zero
    if len(sheet[sheet[zip_column].map(len) < 5]) > 0:
        logging.warning("Zip Codes have less than 5 digits")
        logging.warning(sheet[sheet[zip_column].map(len) < 5])
        sheet[zip_column] = sheet[zip_column].map(zero_pad_zip)

    return sheet

    def verify_columns_has_specified_fields(self, d, sheet):
        """takes a dict where key is the column name and entries
        is a list of the allowed entries.
        returns True if all good and False if theres offending entries.
        
        Args:
            d (list): key is column to be checked

        """

        # sort the allowed entries in the dict
        # list comparison checks sort order also
        for column in d.keys():
            d[column] = np.sort(d[column])

        for column in d.keys():
            if list(np.sort(sheet[column].unique())) != d[column]:
                logging.error("There is an issue with {}".format(column))
                logging.error("entries in sheet:\n{}".format(np.sort(sheet[column].unique())))
                logging.error("Allowed entries:\n{}".format(d[column]))
                return False
        return True

    def format_date(self, sheet, date_column, date_format):
        """Formats a given date column with the given format.
        Supported types (more can be added obviously):
        short form : 14-Mar
        
        Args:
            sheet (TYPE): Description
            date_column (TYPE): Description
            date_format (str): "short form"
        
        Returns:
            df: pandas df representing the excel sheet
        """
        if date_format == "short form":
            format_str = '%d-%b'
        else:
            logging.error("An invalid date format was supplied to format_date")
            logging.error("Valid formats:")
            logging.error("short form")

        sheet[date_column] = sheet[date_column].dt.strftime(format_str)
        return sheet

    def remove_columns(self, sheet, nix_list):
        """Remove the columns given in nix_list
        
        Args:
            sheet (df): pandas df representing the excel sheet
            nix_list (list): list of column names to remove
        
        Returns:
            df: pandas df representing the excel sheet
        """
        cols = list(sheet.columns)
        cols = list(filter(lambda x : x not in nix_list, cols))
        sheet = sheet[cols]
        return sheet

    def create_data_table(self, sheet, dest, excluded_columns=None):
        """Save a data table as a csv. Can exclude columns.
        
        Args:
            sheet (df): pandas df representing excel file
            dest (str): where to save the csv
            excluded_columns (list, optional): list of column names to exclude
        """
        if excluded_columns:
            sheet = self.remove_columns(sheet, excluded_columns)
        
        # TODO this could give errors that we will need to handle
        sheet.to_csv(dest, index=False)


    def create_topn_data_table(self, sheet, dest, sort_value, n, excluded_columns=None):
        """Save a data table as a csv. Can exclude columns.
        
        Args:
            sheet (df): pandas df representing excel file
            dest (str): where to save the csv
            sort_value (str): string to sort on for ranking
            n (int): top n to keep
            excluded_columns (list, optional): list of column names to exclude
        """
        sheet = sheet.sort_values(sort_value).head(n)

        if excluded_columns:
            sheet = self.remove_columns(sheet, excluded_columns)

        # TODO this could give errors that we will need to handle
        sheet.to_csv(dest, index=False)