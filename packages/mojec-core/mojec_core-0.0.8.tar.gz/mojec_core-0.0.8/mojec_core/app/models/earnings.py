from django.db import models
from .work_order import WorkOrder
from .transaction import TransactionLog
from .base import BaseModelAbstract


class Earning(BaseModelAbstract, models.Model):
    workOrder = models.ForeignKey(WorkOrder, models.SET_NULL,
                                  blank=True, null=True)
    transactionRef = models.CharField(
        db_column='transactionRef', max_length=255, blank=True, null=True)
    transactionLog = models.ForeignKey(TransactionLog, models.SET_NULL,
                                       blank=True, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=15, default=0)
    balanceBefore = models.DecimalField(decimal_places=2, max_digits=15,
                                        default=0)
    balanceAfter = models.DecimalField(decimal_places=2, max_digits=15,
                                       default=0)

    class Meta:
        db_table = 'Earnings'

