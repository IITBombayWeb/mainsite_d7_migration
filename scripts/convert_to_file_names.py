import numpy as np
import pandas as pd
import argparse
from bs4 import BeautifulSoup as BSHTML


def get_links(data):
    altered_links = []
    if data and (not isinstance(data, float)):
        soup = BSHTML(data)
        images = soup.findAll('img')
        for image in images:
            full_link = image['src']
            split_link = full_link.split("www.iitb7.ac.in/files/")
            rem_link = split_link[-1]
            rem_link = 'public://' + rem_link
            altered_links.append(rem_link)
    result = ",".join(altered_links)
    return result


def get_file_names(data):
    if not data:
        return ''
    current_file_names = data.split(",")
    
    altered_paths = []
    for filename in current_file_names:
        split_path = filename.split("www.iitb7.ac.in/files/")
        rem_path = split_path[-1]
        rem_path = 'public://' + rem_path
        altered_paths.append(rem_path)
    result = ",".join(altered_paths)
    return result


def filter_links(dataframe, col_name):
    dataframe[col_name] = dataframe[col_name].apply(get_links)
    return dataframe

def filter_file_paths(dataframe, col_name):
    dataframe[col_name] = dataframe[col_name].apply(get_file_names)
    return dataframe


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_type',  help='image or file', required=True)
    parser.add_argument('--input_file',  help='Path to input csv', required=True)
    parser.add_argument('--output_file_path',  help='Path to output csv', required=True)
    parser.add_argument('-f', '--field_list', help='delimited list input', type=str, required=True)
    
    

    args = parser.parse_args()
    print(args.field_list)
    print(args.input_file)
    print(args.output_file_path)


    dataframe = pd.read_csv(args.input_file, header=[0])
    dataframe.fillna('', inplace=True)

    if args.file_type == 'image':
        for field in args.field_list.split(","):
            dataframe = filter_links(dataframe, field)
    elif args.file_type == 'file':
        for field in args.field_list.split(","):
            dataframe = filter_file_paths(dataframe, field)

    dataframe.to_csv(args.output_file_path, index=False)  



# Example

# python convert_to_file_names.py --file_type 'file' --input_file '/Users/abisekrk/Downloads/path_cleaned_migrations/migration_annual_report_sorted.csv' --output_file '/Users/abisekrk/Downloads/path_cleaned_migrations/migration_annual_report_sorted.csv' -f 'file_upload,publications'
# python convert_to_file_names.py --file_type 'image' --input_file '/Users/abisekrk/Downloads/path_cleaned_migrations/migration_article_sorted.csv' --output_file '/Users/abisekrk/Downloads/path_cleaned_migrations/migration_article_sorted.csv' -f 'inline_images,photograph'