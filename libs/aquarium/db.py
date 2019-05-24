import sys
import pydent as pd


def connect_db():
    try:
        connection = pd.AqSession('flavia', 'genomefoundry', 'http://0.0.0.0:8080/')
    except:
        try:
            connection = pd.AqSession('root', 'aSecretAquarium', '172.19.0.3')
        except:
            print('Not possible to connect to the database')
            sys.exit()
    print("connect successful!!")
    return connection


def get_sample(conn, sample):
    sample = conn.Sample.find(sample)
    print(sample)
    return sample


conn = connect_db()
get_sample(conn, 'pYTK096')

