import argparse
import json
from covid_tracker.utils import get_url_as_json, read_csv_as_df
from covid_tracker.covid_tracker import get_covid_date, get_current_count, get_percent_count


def main(args):
    """Gives the information about corona virus

    :param args: input arguments
    :return: None
    """

    # Config parser
    with open(args.config_file_name) as config_file:
        config = json.load(config_file)

    # Fetch covid and world population data
    covid_json = get_url_as_json(config['covid_data_url'])
    world_pop_df = read_csv_as_df(config['world_pop_csv_filename'])

    type_available = {'c': 'confirmed',
                      'd': 'deaths',
                      'r': 'recovered'}
    format_available = {'p': 'percentage_of_population',
                        'a': 'actual_count'}

    exit_flag = False
    while(not exit_flag):

        input_loop_flag = True
        try_count = 1

        while(input_loop_flag):

            if try_count > 3:
                print("!!!!!! Wrong Input, exiting ......")
                exit(1)

            # Fetch user inputs
            country = str(input(
                'Enter country: '
            ))
            type_input = str(input(
                'Enter count type{0}: '.format(type_available)
            )).lower()
            format_input = str(input(
                'Enter count format{0}: '.format(format_available)
            )).lower()

            # Print the available countries during wrong user input
            if country in covid_json.keys() and \
                    type_input in type_available.keys() and \
                    format_input in format_available:
                input_loop_flag = False
            else:
                print(
                 "\n ------ Wrong input, countries available are:\n\n{0}\n\n"
                 .format([key for key in covid_json.keys()])
                )
                try_count = try_count + 1
            # ############################## End of input loop

        # Set count_type & count format
        count_type = type_available[type_input]
        count_format = format_available[format_input]

        # Fetch the count output
        if count_format == 'percentage_of_population':
            count_out = str(
                get_percent_count(country=country,
                                     count_type=count_type,
                                     covid_json=covid_json,
                                     world_pop_df=world_pop_df)
                ) + '% ' + 'of total population'
        else:
            count_out = format(
                get_current_count(country=country,
                                     count_type=count_type,
                                     covid_json=covid_json),
                ',d')

        # Fetch the updated date of covid data
        covid_date = get_covid_date(country=country, covid_json=covid_json)

        # Display the output
        print("\n```````````````````````````````````````````````````````````")
        print("{0}'s {1} count is {2} on {3}"
              .format(country,
                      count_type.capitalize(),
                      count_out,
                      covid_date.strftime('%A, %b %d %Y')))
        print("\n``````````````````````````````````````````````````````````")

        # Continue?
        if str(input("Do you want to continue(Y/N): ")).upper() in ['N', 'NO']:
            print(" ~~~~~ Thank You! Goodbye!!!")
            exit_flag = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config_file_name',
                        help="name of the config file")
    args = parser.parse_args()
    main(args)
