import ssl, urllib.request, json
import pandas as pd


def get_url_as_json(url):
    """Retrieve data from url and returns as json

    :param url: url to retrieve data from
    :return: data obtained as json
    """

    context = ssl._create_unverified_context()

    try:
        with urllib.request.urlopen(url, context=context) as url:
            covid_json = json.loads(url.read().decode())
    except Exception as e:
        print("Error occured: ", e)
        covid_json = None

    return covid_json


def read_csv_as_df(filename):
    """Fetch csv as json

    :param fully qualified name of the csv file
    :return: data as pandas dataframe
    """

    try:
        return pd.read_csv(filename)
    except Exception as e:
        print("Error occured: ", e)
        return None
