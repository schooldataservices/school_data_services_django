from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from users.models import Profile
from .models import RequestConfig


@receiver(pre_save, sender=Profile)
def _cache_old_acronym(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
            instance._old_acronym = old.school_acronym or ''
        except sender.DoesNotExist:
            instance._old_acronym = ''
    else:
        instance._old_acronym = ''

#Changing reference tags of existing RequestConfig objects when a user's school_acronym changes
@receiver(post_save, sender=Profile)
def _cascade_reference_tags(sender, instance, created, **kwargs):
    if created:
        return
    old_acr = getattr(instance, '_old_acronym', '')
    new_acr = (instance.school_acronym or '').strip()
    if old_acr == new_acr:
        return
    new_acr = new_acr or 'GEN'
    qs = RequestConfig.objects.filter(creator=instance.user).only('id', 'reference_tag')
    to_update = []
    for rc in qs:
        desired = f"{new_acr}-{rc.id}"
        if rc.reference_tag != desired:
            rc.reference_tag = desired
            to_update.append(rc)
    if to_update:
        RequestConfig.objects.bulk_update(to_update, ['reference_tag'])