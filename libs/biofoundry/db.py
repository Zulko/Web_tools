
from db.models import File
from django.contrib.auth.models import User


def save_file(name_file, script_name):
    if name_file is not None:
        new_file = File(name=name_file, script=script_name, author=User.first_name, file='docs/'+name_file)
        new_file.save()