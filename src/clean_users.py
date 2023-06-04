import pandas as pd
from unidecode import unidecode
import os

USERS_DATA_PATH = os.path.join(os.pardir, 'data', 'users.csv')

# All data treatment is in one single function that is applied to the dataset using "apply()", so we only have to iterate the dataset once.
def clean_users(s):
    return unidecode(s).casefold()


if __name__ == '__main__':
    df_users = pd.read_csv(USERS_DATA_PATH)
    df_users = df_users.dropna(axis=0, subset=['name']) #Deletes user that has no name
    df_users['name'] = df_users['name'].apply(clean_users)
    df_users.to_csv(os.path.join(os.pardir, 'data', 'users_clean.csv'), index=False)