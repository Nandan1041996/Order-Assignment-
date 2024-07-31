import pandas as pd
import numpy as np
from exception import MissingColumnError


def validate_columns(df, df_name, required_columns):
    """
    Validate if DataFrame `df` contains all `required_columns`.

    Args:
    - df (pd.DataFrame): DataFrame to validate.
    - df_name (str): Name of the DataFrame (for error messages).
    - required_columns (list): List of column names that must be present in `df`.

    Raises:
    - ValueError: If any required column is missing in `df`.
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    print('misssing column',missing_columns)
    if missing_columns:
        raise   ValueError(f"{df_name} is missing the following required columns: {', '.join(missing_columns)}")


def fraight_rate_calculation(current_fraight_file,dest_dict_file,perc_increase):
    try:
        # to read excel file "Current Freight Rate.XLSX"
        current_freight_df = pd.read_excel(current_fraight_file)
        # print('current_freight_df :',current_freight_df.columns)
        c_frt_not_avail_col_lst =[]
        required_cols = ['Plant','Final Destination','Dest. Desc.','MODE','Direct Road Freight','Market Freight']
        for col in required_cols:
            if not col in  current_freight_df.columns:
                c_frt_not_avail_col_lst.append(col)

        if len(c_frt_not_avail_col_lst) !=0:
            raise MissingColumnError(c_frt_not_avail_col_lst,'Current Freight Rate File')
        # current_freight_df = pd.read_excel("Current Freight Rate.XLSX")
        # get unique final destinations
        lst = current_freight_df['Final Destination'].unique()

        # read excel file "Destination Distance.XLSX"
        dest_dict_df = pd.read_excel(dest_dict_file)

        dest_frt_not_avail_col_lst =[]
        required_cols = ['Direct Road Freight Rate','Description','Plant','Mode of Transport','Distance in KM']
        for col in required_cols:
            if not col in  dest_dict_df.columns:
                dest_frt_not_avail_col_lst.append(col)

        if len(dest_frt_not_avail_col_lst) !=0:
            raise MissingColumnError(dest_frt_not_avail_col_lst,'Destination Freight Rate File')

        # merge Two df to calculate the operation 
        final_df = current_freight_df.merge(dest_dict_df,left_on=['Final Destination','Dest. Desc.','Plant','MODE'],right_on=['Direct Road Freight Rate','Description','Plant','Mode of Transport'])

        # took required columns 
        final_df1 = final_df[['Plant','Dest. Desc.','Final Destination','MODE','Distance in KM','Direct Road Freight','Market Freight']]
        final_df1['Distance in KM'] = round(final_df1['Distance in KM'],0)
        final_df1['Distance in KM'] =  final_df1['Distance in KM'].astype(int)
        # to get per Km Price
        final_df1['Per Km Price'] =final_df1['Direct Road Freight']/final_df1['Distance in KM']
        final_df1['Per Km Price'] = round(final_df1['Per Km Price'],2)
        final_df1['Proposed Price'] = final_df1['Direct Road Freight']+((final_df1['Direct Road Freight']* perc_increase)/100)
        final_df1['Proposed Price'] = round(final_df1['Proposed Price'],2)
        final_df1['Proposed Price'] =  final_df1['Proposed Price'].astype(int)

        final_df1['Proposed Price /KM'] = final_df1['Proposed Price']/final_df1['Distance in KM']
        final_df1['Proposed Price /KM'] = round(final_df1['Proposed Price /KM'],2)

        final_df1['Diff B/W Old And Propose Rate'] = final_df1['Proposed Price'] - final_df1['Direct Road Freight']
        print('final_cols:',final_df1.columns)

        return final_df1
    except MissingColumnError as e:
        return e