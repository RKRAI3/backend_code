# -*- coding: utf-8 -*-
"""
Created on Thu Jul 24 16:26:40 2025

@author: RAVI KANT
"""
from datetime import datetime, timedelta


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
        'pmnt_mode': original_data.get('payment_mode', 'CASH'),
        'trnsaction_nmbr': original_data.get('transaction_number'),
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

def transform_pre_generated_receipts_list(receipts):
    # Extract and transform the data
    new_data = [{
        'recpt_id': rcpt.to_dict().get('receipt_id'),
        'recpt_nmbr': rcpt.to_dict().get('receipt_number'),
        'rcpnt_nm': rcpt.to_dict().get('recipient_name'),
        'rcpnt_mob': rcpt.to_dict().get('recipient_number'),
        'tot_incl_tax': rcpt.to_dict().get('gross_amount'),
        'recpt_dt': rcpt.to_dict().get('created_at', '').split('T')[0],
        'pmnt_mode': rcpt.to_dict().get('payment_mode', 'CASH'),
        'trnsaction_nmbr': rcpt.to_dict().get('transaction_number'),
        } for rcpt in receipts.items]
    return new_data

def transform_dashboard_data(receipts_data):
    # # Extract and transform the data
    # yesterday = datetime.now() - timedelta(days=1)
    # # Format as 'YYYY-MM-DD'
    # yesterday = yesterday.strftime('%Y-%m-%d')
    keys_to_remove = ["created_at", "id", "prod_id", "receipt_id"]
    rename_map = {"receipt_id":"recpt_id",
                  "receipt_number":"recpt_nmbr",
                  "recipient_name":"rcpnt_nm",
                  "recipient_number":"rcpnt_mob",
                  "receipt_dt":"recpt_dt",
                  "total_amount": "tot_amt",
                  "tax_amount": "tax_amt",
                  "payment_mode": "pmnt_mode",
                  "transaction_number": "transaction_nmbr",
                  }
    itms_rename = {"product_name":"service",
                   "unit_price": "per_unt",
                   "quantity": "nos_unt",
                   "total_amount": "tot_amt"
                   }
    # receipts_lst=[]
    # receipts={"receipts":[]}
    
    for receipts in receipts_data:
        for rcpt in receipts['receipts']:
            for item in rcpt["items"]:
                for key in keys_to_remove:
                    item.pop(key, None)
                for old_key, new_key in itms_rename.items():
                        if old_key in item:
                            item[new_key] = item.pop(old_key) 
            if "created_at" in rcpt:
                rcpt["created_at"] = rcpt.get('created_at', '').split('T')[0]
                rcpt["recpt_dt"] = rcpt.pop("created_at") 
                # date_obj = datetime.strptime(rcpt["recpt_dt"], '%Y-%m-%d')
                # rcpt["recpt_dt"] = date_obj.strftime('%d-%m-%Y')
            if "updated_at" in rcpt:
                rcpt.pop("updated_at", None)
            for old_key, new_key in rename_map.items():
                if old_key in rcpt:
                    rcpt[new_key] = rcpt.pop(old_key) 

            # receipts["receipts"].append(rcpt)
        # receipts_lst.append(receipts)
    return receipts_data
    