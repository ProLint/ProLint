from celery import uuid
from django import forms
from django.db import models
from django.conf import settings
from multiselectfield import MultiSelectField
from django.utils.translation import gettext as _

# This is a hacky way of doing things and it needs to be improved eventually,
# but for the purpose of the docker container this works quite nicely.
G, C = True, True
def user_directory_path(instance, filename):
    global task_id; global C

    if G and C:
        task_id = uuid()
        C = False
    else:
        C = True

    instance.task_id = task_id
    return '{0}/{1}/{2}/{3}'.format('user-data', 'prolint', task_id, filename)


# This has to be this convoluted in order to get the
# two column alignment of the options in the submission form.
SHORT_RADII = (
    ('3.0', _("3.0 Å")),
    ('3.5', _("3.5 Å")),
    ('4.0', _("4.0 Å")),
    ('5.0', _("5.0 Å")),
    ('5.5', _("5.5 Å")),
)
LONG_RADII = (
    ('6.0', _("6.0 Å")),
    ('6.5', _("6.5 Å")),
    ('7.0', _("7.0 Å")),
    ('7.5', _("7.5 Å")),
    ('8.0', _("8.0 Å")),
)
# Radii choices options
RADII_CHOICES = (
    (_("short"), SHORT_RADII),
    (_("long"), LONG_RADII),
)

# Resolution choices options
RESOLUTION_CHOICES = (
    ('martini', 'The Martini Model'),
    ('atomistic', 'Atomistic Models')
)

# Application choices options
APP_CHOICES = (
    ('contacts', 'Conctact-based'),
    ('densities', 'Density-based'),
    ('thickcurv', 'Physical-properties'),
)


class FileMD(models.Model):
    # user = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.CASCADE,
    # )
    title = models.CharField(max_length=100)
    prot_name = models.CharField(max_length=100, null=False, blank=False, default="Protein")
    traj = models.FileField(upload_to=user_directory_path, null=True, blank=False)
    coor = models.FileField(upload_to=user_directory_path, null=True, blank=False)
    group = models.BooleanField(null=False, default=True)
    lipids = models.CharField(max_length=300, null=True, blank=True, default="")
    task_id = models.CharField(max_length=40, default=uuid())
    status = models.CharField(max_length=12, default="PENDING")
    radii = MultiSelectField(choices=RADII_CHOICES)
    resolution = models.CharField(max_length=25, choices=RESOLUTION_CHOICES, default="martini")
    chains = models.BooleanField(null=False, default=True)
    apps = MultiSelectField(choices=APP_CHOICES)

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        self.status = "DELETED"
        self.save()
        return None
