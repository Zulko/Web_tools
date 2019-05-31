import sys
import pydent as pd

from db.models import Plate


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
    # sample = conn.Sample.find(1)
    sample = conn.Sample.find_by_name('primer_connector_1')
    plasmid = conn.SampleType.find(5)
    plates = conn.Collection.find(1)
    # sample = conn.Sample.find('1')
    # print(plasmid)
    print(plates)
    print(sample)
    return sample


# conn = connect_db()
# get_sample(conn, 'pYTK096')
all_plates = Plate.objects.all()

for plate in all_plates:
    print(plate.name)