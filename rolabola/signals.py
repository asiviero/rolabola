from django.db.models.signals import post_save
from django.dispatch import receiver
from rolabola.models import *
from django.conf import settings

@receiver(post_save, sender=Match)
def match_post_save(sender, **kwargs):
    print("AQUI!")
