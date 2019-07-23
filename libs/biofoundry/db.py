from db.models import File


def save_file(name_file, script_name, user):
    if name_file is not None:
        new_file = File(name=name_file, script=script_name, author=user, file='docs/'+name_file)
        new_file.save()
        return new_file
    return None