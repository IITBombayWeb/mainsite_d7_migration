import numpy as np
import pandas as pd
import argparse
from datetime import datetime





def parse_and_convert_date(date_str):
    if not date_str:
        return ''
    datetime_object = datetime.strptime(date_str, '%A, %B %d, %Y')
    conv_str = datetime_object.strftime("%Y-%m-%d %H:%M:%S")
    return conv_str

def convert_dates(dataframe, col_name):
    dataframe[col_name] = dataframe[col_name].apply(parse_and_convert_date)
    return dataframe


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file',  help='Path to input csv', required=True)
    parser.add_argument('--output_file_path',  help='Path to output csv', required=True)
    parser.add_argument('-f', '--field_list', help='delimited list input', type=str, required=True)
    
    

    args = parser.parse_args()
    print(args.field_list)
    print(args.input_file)
    print(args.output_file_path)


    dataframe = pd.read_csv(args.input_file, header=[0])
    dataframe.fillna('', inplace=True)

    for field in args.field_list.split(","):
        dataframe = convert_dates(dataframe, field)
    
    dataframe.to_csv(args.output_file_path, index=False)  



# Example

# python convert_dates.py --input_file '/Users/abisekrk/Downloads/migration-division-functionary-content-original.csv' --output_file '/Users/abisekrk/Downloads/migration-division-functionary-content-edited.csv' -f 'period_of_active_position_start,period_of_active_position_end'