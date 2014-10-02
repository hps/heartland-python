"""
    batch.py

    This module defines the batch entity types.

    :copyright: (c) Heartland Payment Systems. All rights reserved.
"""


class HpsBatch(object):
    id = None
    transaction_count = None
    total_amount = None
    sequence_number = None
