# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 16:26:40 2025

@author: RAVI KANT
"""

def transform_receipt_data(original_data):
    # Extract and transform the data
    new_data = {
        'recpt_nmbr': original_data.get('receipt_number'),
        'rcpnt_nm': original_data.get('recipient_name'),
        'rcpnt_mob': original_data.get('recipient_number'),
        'tot_amt': original_data.get('total_amount'),
        'tax_amt': original_data.get('tax_amount'),
        'tot_incl_tax': original_data.get('gross_amount'),
        'recpt_dt': original_data.get('created_at', '').split('T')[0],  # Remove time portion
        'items': []
    }

    # Process each item in the items list
    for item in original_data.get('items', []):
        transformed_item = {
            'service': item.get('product_name'),
            'per_unt': item.get('unit_price'),
            'nos_unt': item.get('quantity'),
            'tot_amt': item.get('total_amount'),
        }
        new_data['items'].append(transformed_item)

    return new_data
    