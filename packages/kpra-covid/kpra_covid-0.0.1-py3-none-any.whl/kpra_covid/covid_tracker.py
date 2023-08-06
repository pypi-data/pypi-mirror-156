import pandas as pd
from datetime import datetime


def get_percent_count(country, count_type, covid_json, world_pop_df):
    """Returns the percentage count of given country and type

    :param country: country for which covid data is needed
    :param count_type: type of covid count ['confirmed', 'deaths', 'recovered']
    :param covid_json: covid data json
    :world_pop_df: pandas dataframe with world population details
    :return: percentage of covid count for the given country and type
    """

    covid_value = covid_json[country][-1][count_type]
    population_value = world_pop_df[
                        world_pop_df['Country'] == country].Pop.mean()
    percent_count = covid_value / population_value * 100

    return round(percent_count, 5)


def get_current_count(country, count_type, covid_json):
    """Returns the actual count of given country and type

    :param country: country for which covid data is needed
    :param count_type: type of covid count ['confirmed', 'deaths', 'recovered']
    :param covid_json: covid data json
    :return: covid count for the given country and type
    """

    covid_value = covid_json[country][-1][count_type]
    return covid_value


def get_covid_date(country, covid_json):
    """Returns the latest date of covid data

    :param country: country for which covid data is needed
    :param covid_json: covid data json
    :return: latest date of the covid data as date object
    """

    covid_date = datetime.strptime(
        covid_json[country][-1]['date'], '%Y-%m-%d')
    return covid_date
