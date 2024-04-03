#This is specific to a csv. 
import os 
import pandas as pd


def read_in():

    df = pd.read_csv(os.getcwd() + '\emailscraper_app\modules\Sending_Emails\KC_Schools.csv')
    df = df.dropna(subset=['School District', 'Level', 'High schools'], how='all')

    column_mapping = {
        'School District': 'SchoolDistrict',
        'Level': 'Level',
        'High schools': 'HighSchools',
        'LOGO': 'LOGO',
        'OUR LOGO': 'OURLOGO',
        'School Search': 'SchoolSearch',
        'PHONE SEARCH': 'PHONESEARCH',
        'Unnamed: 7': 'Unnamed7',
        'Principal': 'Principal',
        'Athletic Director': 'AthleticDirector',
        'Vice-Principal': 'VicePrincipal',
        'Football Coach': 'FootballCoach',
        'Baseball Coach': 'BaseballCoach',
        'Softball Coach': 'SoftballCoach',
        'Basketball Coach': 'BasketballCoach',
        'Soccer Coach': 'SoccerCoach',
        'Address Search': 'AddressSearch',
        'Address': 'Address',
        'Principal.1': 'PrincipalEmail',
        'Athletic Director.1': 'AthleticDirectorEmail',
        'Vice-Principal.1': 'VicePrincipalEmail',
        'Football Coach.1': 'FootballCoachEmail',
        'Baseball Coach.1': 'BaseballCoachEmail',
        'Softball Coach.1': 'SoftballCoachEmail',
        'Basketball Coach.1': 'BasketballCoachEmail',
        'Soccer Coach.1': 'SoccerCoachEmail',
        'Unnamed: 26': 'Unnamed26',
        'email replacement': 'emailreplacement',
        " emails wasn't delivered": 'emailswasntdelivered',
        'yellow did not remove': 'yellowdidnotremove'
    }

    # Rename columns using the mapping
    df = df.rename(columns=column_mapping)

    return(df)


def filter_emails_by_sport(df, list_of_sports):

    all_cols = list(df.columns)
    sports_words = list_of_sports

    main_positions = ['PrincipalEmail', 'AthleticDirector', 'VicePrincipalEmail']
    sports_words.extend(main_positions)	
    
    filtered_columns = [col for col in all_cols if 'Email' in col and any(sport in col for sport in sports_words)]
    
    col_order = ['SchoolDistrict', 'Level', 'HighSchools']
    col_order.extend(filtered_columns)

    df = df[col_order]

    temp = pd.melt(df , id_vars = ['SchoolDistrict', 'Level', 'HighSchools'], var_name = 'Position', value_name = 'email')
    temp = temp.dropna(subset=['email'], how='all')
    temp = temp.reset_index(drop = True)

    return(temp)