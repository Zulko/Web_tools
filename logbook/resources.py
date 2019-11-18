from import_export import resources, fields, widgets
from .models import LogBook
from db.models import Project


class LogBookResource(resources.ModelResource):
    project = fields.Field(
        column_name='project',
        attribute='project',
        widget=widgets.ManyToManyWidget(Project, field='name')
    )

    class Meta:
        model = LogBook
        fields = ('user', 'supervisor', 'time_used', 'comments', 'machine')





