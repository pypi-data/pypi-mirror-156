# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals
from django.dispatch import receiver
from django.db.models.signals import pre_save
from . import models
import logging
log = logging.getLogger('django')

try:
    from xyz_common.signals import to_save_version

    @receiver(pre_save, sender=models.Measure)
    def save_measure_version(sender, **kwargs):
        to_save_version.send_robust(sender, instance=kwargs['instance'])


    @receiver(pre_save, sender=models.Report)
    def save_report_version(sender, **kwargs):
        to_save_version.send_robust(sender, instance=kwargs['instance'])
except:
    import traceback
    log.warn('try to build up to_save_version signals error: %s', traceback.format_exc())
