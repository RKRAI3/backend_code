import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

# Your data
data = {
    'product_name': {0: 'Photograph', 1: 'Photocopy', 2: 'Form Filling', 3: 'Application Support Service', 4: 'Photocopy', 5: 'Photocopy', 6: 'Photograph', 7: 'Form Filling', 8: 'Form Filling', 9: 'Photocopy', 10: 'Photograph', 11: 'Form Filling', 12: 'Application Support Service', 13: 'Application Support Service', 14: 'Form Filling', 15: 'Application Support Service', 16: 'Photograph', 17: 'Photograph', 18: 'Photocopy', 19: 'Form Filling', 20: 'Application Support Service', 21: 'Photocopy', 22: 'Photograph', 23: 'Application Support Service', 24: 'Form Filling', 25: 'Photograph', 26: 'Photocopy', 27: 'Application Support Service', 28: 'Photograph', 29: 'Form Filling', 30: 'Application Support Service', 31: 'Scan', 32: 'Form Filling', 33: 'Photocopy', 34: 'Application Support Service', 35: 'Application Support Service', 36: 'Form Filling', 37: 'Scan', 38: 'Photograph', 39: 'Photocopy', 40: 'Form Filling', 41: 'Application Support Service', 42: 'Photograph', 43: 'Photograph', 44: 'Application Support Service', 45: 'Form Filling', 46: 'Photograph', 47: 'Form Filling', 48: 'Form Filling', 49: 'Application Support Service', 50: 'Photocopy', 51: 'Photograph', 52: 'Form Filling', 53: 'Photocopy', 54: 'Application Support Service', 55: 'Photograph', 56: 'Photograph', 57: 'Form Filling', 58: 'Application Support Service', 59: 'Application Support Service', 60: 'Form Filling', 61: 'Photograph', 62: 'Photocopy', 63: 'Form Filling', 64: 'Photograph', 65: 'Full Package', 66: 'Full Package', 67: 'Full Package', 68: 'Full Package', 69: 'Full Package', 70: 'Full Package', 71: 'Full Package'},
    'std_price': {0: 100.0, 1: 5.0, 2: 300.0, 3: 9091.0, 4: 5.0, 5: 5.0, 6: 100.0, 7: 300.0, 8: 300.0, 9: 5.0, 10: 100.0, 11: 300.0, 12: 9091.0, 13: 9091.0, 14: 300.0, 15: 9091.0, 16: 100.0, 17: 100.0, 18: 5.0, 19: 300.0, 20: 9091.0, 21: 5.0, 22: 100.0, 23: 9091.0, 24: 300.0, 25: 100.0, 26: 5.0, 27: 9091.0, 28: 100.0, 29: 300.0, 30: 9091.0, 31: 5.0, 32: 300.0, 33: 5.0, 34: 9091.0, 35: 9091.0, 36: 300.0, 37: 5.0, 38: 100.0, 39: 5.0, 40: 300.0, 41: 9091.0, 42: 100.0, 43: 100.0, 44: 9091.0, 45: 300.0, 46: 100.0, 47: 300.0, 48: 300.0, 49: 9091.0, 50: 5.0, 51: 100.0, 52: 300.0, 53: 5.0, 54: 9091.0, 55: 100.0, 56: 100.0, 57: 300.0, 58: 9091.0, 59: 9091.0, 60: 300.0, 61: 100.0, 62: 5.0, 63: 300.0, 64: 100.0, 65: 1000.0, 66: 1000.0, 67: 1000.0, 68: 1000.0, 69: 1000.0, 70: 1000.0, 71: 1000.0},
    'vend_price': {0: 100.0, 1: 5.0, 2: 300.0, 3: 9091.0, 4: 5.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 300.0, 9: 0.0, 10: 0.0, 11: 0.0, 12: 0.0, 13: 9091.0, 14: 300.0, 15: 9091.0, 16: 100.0, 17: 100.0, 18: 5.0, 19: 300.0, 20: 9091.0, 21: 0.0, 22: 0.0, 23: 0.0, 24: 300.0, 25: 100.0, 26: 5.0, 27: 9091.0, 28: 200.0, 29: 305.0, 30: 0.0, 31: 0.0, 32: 0.0, 33: 0.0, 34: 0.0, 35: 9091.0, 36: 300.0, 37: 5.0, 38: 100.0, 39: 5.0, 40: 300.0, 41: 9091.0, 42: 100.0, 43: 0.0, 44: 0.0, 45: 0.0, 46: 100.0, 47: 300.0, 48: 0.0, 49: 0.0, 50: 0.0, 51: 0.0, 52: 300.0, 53: 5.0, 54: 9091.0, 55: 100.0, 56: 100.0, 57: 300.0, 58: 9091.0, 59: 9091.0, 60: 300.0, 61: 100.0, 62: 5.0, 63: 300.0, 64: 100.0, 65: 1000.0, 66: 1000.0, 67: 1000.0, 68: 1000.0, 69: 1000.0, 70: 1000.0, 71: 1000.0},
    'quantity': {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 8.0, 5: 1.0, 6: 4.0, 7: 3.0, 8: 1.0, 9: 1.0, 10: 1.0, 11: 1.0, 12: 1.0, 13: 3.0, 14: 2.0, 15: 1.0, 16: 5.0, 17: 2.0, 18: 3.0, 19: 2.0, 20: 2.0, 21: 3.0, 22: 2.0, 23: 2.0, 24: 3.0, 25: 1.0, 26: 2.0, 27: 1.0, 28: 1.0, 29: 1.0, 30: 1.0, 31: 1.0, 32: 1.0, 33: 1.0, 34: 1.0, 35: 1.0, 36: 1.0, 37: 1.0, 38: 1.0, 39: 1.0, 40: 1.0, 41: 1.0, 42: 1.0, 43: 1.0, 44: 1.0, 45: 1.0, 46: 1.0, 47: 1.0, 48: 1.0, 49: 1.0, 50: 1.0, 51: 1.0, 52: 1.0, 53: 1.0, 54: 1.0, 55: 1.0, 56: 1.0, 57: 1.0, 58: 1.0, 59: 1.0, 60: 1.0, 61: 1.0, 62: 1.0, 63: 1.0, 64: 1.0, 65: 1.0, 66: 1.0, 67: 1.0, 68: 1.0, 69: 1.0, 70: 1.0, 71: 1.0},
    'total_std_price': {0: 100.0, 1: 5.0, 2: 300.0, 3: 9091.0, 4: 40.0, 5: 5.0, 6: 400.0, 7: 900.0, 8: 300.0, 9: 5.0, 10: 100.0, 11: 300.0, 12: 9091.0, 13: 27273.0, 14: 600.0, 15: 9091.0, 16: 500.0, 17: 200.0, 18: 15.0, 19: 600.0, 20: 18182.0, 21: 15.0, 22: 200.0, 23: 18182.0, 24: 900.0, 25: 100.0, 26: 10.0, 27: 9091.0, 28: 100.0, 29: 300.0, 30: 9091.0, 31: 5.0, 32: 300.0, 33: 5.0, 34: 9091.0, 35: 9091.0, 36: 300.0, 37: 5.0, 38: 100.0, 39: 5.0, 40: 300.0, 41: 9091.0, 42: 100.0, 43: 100.0, 44: 9091.0, 45: 300.0, 46: 100.0, 47: 300.0, 48: 300.0, 49: 9091.0, 50: 5.0, 51: 100.0, 52: 300.0, 53: 5.0, 54: 9091.0, 55: 100.0, 56: 100.0, 57: 300.0, 58: 9091.0, 59: 9091.0, 60: 300.0, 61: 100.0, 62: 5.0, 63: 300.0, 64: 100.0, 65: 1000.0, 66: 1000.0, 67: 1000.0, 68: 1000.0, 69: 1000.0, 70: 1000.0, 71: 1000.0},
    'total_vend_price': {0: 100.0, 1: 5.0, 2: 300.0, 3: 9091.0, 4: 40.0, 5: 0.0, 6: 0.0, 7: 0.0, 8: 300.0, 9: 0.0, 10: 0.0, 11: 0.0, 12: 0.0, 13: 27273.0, 14: 600.0, 15: 9091.0, 16: 500.0, 17: 200.0, 18: 15.0, 19: 600.0, 20: 18182.0, 21: 0.0, 22: 0.0, 23: 0.0, 24: 900.0, 25: 100.0, 26: 10.0, 27: 9091.0, 28: 200.0, 29: 305.0, 30: 0.0, 31: 0.0, 32: 0.0, 33: 0.0, 34: 0.0, 35: 9091.0, 36: 300.0, 37: 5.0, 38: 100.0, 39: 5.0, 40: 300.0, 41: 9091.0, 42: 100.0, 43: 0.0, 44: 0.0, 45: 0.0, 46: 100.0, 47: 300.0, 48: 0.0, 49: 0.0, 50: 0.0, 51: 0.0, 52: 300.0, 53: 5.0, 54: 9091.0, 55: 100.0, 56: 100.0, 57: 300.0, 58: 9091.0, 59: 9091.0, 60: 300.0, 61: 100.0, 62: 5.0, 63: 300.0, 64: 100.0, 65: 1000.0, 66: 1000.0, 67: 1000.0, 68: 1000.0, 69: 1000.0, 70: 1000.0, 71: 1000.0},
    'created_at': {0: '29-09-2025', 1: '29-09-2025', 2: '29-09-2025', 3: '29-09-2025', 4: '29-09-2025', 5: '29-09-2025', 6: '29-09-2025', 7: '29-09-2025', 8: '29-09-2025', 9: '26-09-2025', 10: '26-09-2025', 11: '26-09-2025', 12: '26-09-2025', 13: '26-09-2025', 14: '26-09-2025', 15: '26-09-2025', 16: '26-09-2025', 17: '26-09-2025', 18: '26-09-2025', 19: '26-09-2025', 20: '26-09-2025', 21: '26-09-2025', 22: '26-09-2025', 23: '26-09-2025', 24: '26-09-2025', 25: '26-09-2025', 26: '26-09-2025', 27: '26-09-2025', 28: '16-09-2025', 29: '16-09-2025', 30: '16-09-2025', 31: '16-09-2025', 32: '16-09-2025', 33: '16-09-2025', 34: '16-09-2025', 35: '16-09-2025', 36: '16-09-2025', 37: '16-09-2025', 38: '16-09-2025', 39: '16-09-2025', 40: '16-09-2025', 41: '16-09-2025', 42: '16-09-2025', 43: '16-09-2025', 44: '16-09-2025', 45: '16-09-2025', 46: '16-09-2025', 47: '15-09-2025', 48: '15-09-2025', 49: '15-09-2025', 50: '15-09-2025', 51: '15-09-2025', 52: '15-09-2025', 53: '15-09-2025', 54: '15-09-2025', 55: '15-09-2025', 56: '07-09-2025', 57: '07-09-2025', 58: '07-09-2025', 59: '07-09-2025', 60: '07-09-2025', 61: '07-09-2025', 62: '07-09-2025', 63: '07-09-2025', 64: '07-09-2025', 65: '29-09-2025', 66: '26-09-2025', 67: '26-09-2025', 68: '16-09-2025', 69: '16-09-2025', 70: '16-09-2025', 71: '15-09-2025'},
    'receipt_number': {0: 'IN-29092025-857C3087', 1: 'IN-29092025-857C3087', 2: 'IN-29092025-857C3087', 3: 'IN-29092025-857C3087', 4: 'IN-29092025-C2C4752B', 5: 'IN-29092025-D113E79D', 6: 'IN-29092025-D113E79D', 7: 'IN-29092025-D113E79D', 8: 'IN-29092025-B92DE680', 9: 'IN-26092025-1B176AE9', 10: 'IN-26092025-1B176AE9', 11: 'IN-26092025-1B176AE9', 12: 'IN-26092025-1B176AE9', 13: 'IN-26092025-26ADD46D', 14: 'IN-26092025-6ED35007', 15: 'IN-26092025-2C8E6697', 16: 'IN-26092025-2C8E6697', 17: 'IN-26092025-95AA197C', 18: 'IN-26092025-95AA197C', 19: 'IN-26092025-95AA197C', 20: 'IN-26092025-95AA197C', 21: 'IN-26092025-D353C63E', 22: 'IN-26092025-D353C63E', 23: 'IN-26092025-D353C63E', 24: 'IN-26092025-FD4B3C3F', 25: 'IN-26092025-FD4B3C3F', 26: 'IN-26092025-FD4B3C3F', 27: 'IN-26092025-FD4B3C3F', 28: 'IN-16092025-463B3847', 29: 'IN-16092025-463B3847', 30: 'IN-16092025-C8385414', 31: 'IN-16092025-C8385414', 32: 'IN-16092025-C8385414', 33: 'IN-16092025-C8385414', 34: 'IN-16092025-0523F0D1', 35: 'IN-16092025-F66CDB18', 36: 'IN-16092025-F66CDB18', 37: 'IN-16092025-F66CDB18', 38: 'IN-16092025-F66CDB18', 39: 'IN-16092025-F66CDB18', 40: 'IN-16092025-AFBDDCB5', 41: 'IN-16092025-AFBDDCB5', 42: 'IN-16092025-AFBDDCB5', 43: 'IN-16092025-E726CE77', 44: 'IN-16092025-E726CE77', 45: 'IN-16092025-E726CE77', 46: 'IN-16092025-672B6B19', 47: 'IN-15092025-F782DBA9', 48: 'IN-15092025-7C45B8F1', 49: 'IN-15092025-7C45B8F1', 50: 'IN-15092025-7C45B8F1', 51: 'IN-15092025-7C45B8F1', 52: 'IN-15092025-AC313FB3', 53: 'IN-15092025-AC313FB3', 54: 'IN-15092025-AC313FB3', 55: 'IN-15092025-AC313FB3', 56: 'IN-07092025-A477B388', 57: 'IN-07092025-A477B388', 58: 'IN-07092025-A477B388', 59: 'IN-07092025-8A3745D2', 60: 'IN-07092025-37BD72A5', 61: 'IN-07092025-37BD72A5', 62: 'IN-07092025-37BD72A5', 63: 'IN-07092025-2B95ADEE', 64: 'IN-07092025-2B95ADEE', 65: 'IN-29092025-D113E79D', 66: 'IN-26092025-1B176AE9', 67: 'IN-26092025-D353C63E', 68: 'IN-16092025-C8385414', 69: 'IN-16092025-0523F0D1', 70: 'IN-16092025-E726CE77', 71: 'IN-15092025-7C45B8F1'},
    'package': {0: 'Standard', 1: 'Standard', 2: 'Standard', 3: 'Standard', 4: 'Standard', 5: 'Full Package', 6: 'Full Package', 7: 'Full Package', 8: 'Standard', 9: 'Full Package', 10: 'Full Package', 11: 'Full Package', 12: 'Full Package', 13: 'Standard', 14: 'Standard', 15: 'Standard', 16: 'Standard', 17: 'Standard', 18: 'Standard', 19: 'Standard', 20: 'Standard', 21: 'Full Package', 22: 'Full Package', 23: 'Full Package', 24: 'Standard', 25: 'Standard', 26: 'Standard', 27: 'Standard', 28: 'Standard', 29: 'Standard', 30: 'Full Package', 31: 'Full Package', 32: 'Full Package', 33: 'Full Package', 34: 'Full Package', 35: 'Standard', 36: 'Standard', 37: 'Standard', 38: 'Standard', 39: 'Standard', 40: 'Standard', 41: 'Standard', 42: 'Standard', 43: 'Full Package', 44: 'Full Package', 45: 'Full Package', 46: 'Standard', 47: 'Standard', 48: 'Full Package', 49: 'Full Package', 50: 'Full Package', 51: 'Full Package', 52: 'Standard', 53: 'Standard', 54: 'Standard', 55: 'Standard', 56: 'Standard', 57: 'Standard', 58: 'Standard', 59: 'Standard', 60: 'Standard', 61: 'Standard', 62: 'Standard', 63: 'Standard', 64: 'Standard', 65: 'Full Package', 66: 'Full Package', 67: 'Full Package', 68: 'Full Package', 69: 'Full Package', 70: 'Full Package', 71: 'Full Package'}
}

df = pd.DataFrame(data)

# Get unique products
all_products = sorted([p for p in df['product_name'].unique() if p != 'Full Package'])
all_products.append('Full Package')

# Process data by receipt
grouped = df.groupby(['created_at', 'receipt_number', 'package'])
report_data = []

for (date, receipt, package), group in grouped:
    row = {'Date': date, 'Receipt Number': receipt, 'Package': package}
    
    for product in all_products:
        row[f'{product}_Qty'] = ''
        row[f'{product}_Std'] = ''
        row[f'{product}_Vend'] = ''
        row[f'{product}_TotStd'] = ''
        row[f'{product}_TotVend'] = ''
    
    if package != 'Standard' and 'Full Package' in group['product_name'].values:
        full_pkg = group[group['product_name'] == 'Full Package'].iloc[0]
        pkg_amt = full_pkg['std_price']
        item_count = len(group[group['product_name'] != 'Full Package'])
        
        row['Full Package_Qty'] = item_count
        row['Full Package_Std'] = pkg_amt
        row['Full Package_Vend'] = pkg_amt
        row['Full Package_TotStd'] = pkg_amt
        row['Full Package_TotVend'] = pkg_amt
    else:
        for _, item in group.iterrows():
            product = item['product_name']
            if product != 'Full Package':
                row[f'{product}_Qty'] = item['quantity'] if row[f'{product}_Qty'] == '' else row[f'{product}_Qty'] + item['quantity']
                row[f'{product}_Std'] = item['std_price']
                row[f'{product}_Vend'] = item['vend_price']
                row[f'{product}_TotStd'] = item['total_std_price'] if row[f'{product}_TotStd'] == '' else row[f'{product}_TotStd'] + item['total_std_price']
                row[f'{product}_TotVend'] = item['total_vend_price'] if row[f'{product}_TotVend'] == '' else row[f'{product}_TotVend'] + item['total_vend_price']
    
    row['Total_Std'] = sum([row[f'{p}_TotStd'] for p in all_products if row[f'{p}_TotStd'] != ''])
    row['Total_Vend'] = sum([row[f'{p}_TotVend'] for p in all_products if row[f'{p}_TotVend'] != ''])
    report_data.append(row)

report_df = pd.DataFrame(report_data)
report_df['date_sort'] = pd.to_datetime(report_df['Date'], format='%d-%m-%Y')
report_df = report_df.sort_values('date_sort').drop('date_sort', axis=1)

# Create Excel with simple approach using pandas
with pd.ExcelWriter('Sales_Report_September_2025.xlsx', engine='openpyxl') as writer:
    report_df.to_excel(writer, sheet_name='Sales Report', index=False)
    
print("Excel file 'Sales_Report_September_2025.xlsx' created successfully!")
print(f"Total rows: {len(report_df)}")