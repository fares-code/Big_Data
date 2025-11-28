import pandas as pd
import numpy as np

df = pd.read_csv('./dirty_cafe_sales.csv')

clean = df.copy()
invalid_tokens = ['ERROR','UNKNOWN','None','NONE','none','nan','NaN']
clean.replace(invalid_tokens, np.nan, inplace=True)

str_cols = clean.select_dtypes(include='object').columns.tolist()
for c in str_cols:
    clean[c] = clean[c].astype(str).str.strip().replace({'nan': np.nan})

clean['Item'] = clean['Item'].where(clean['Item'].notna(), np.nan)
clean.loc[clean['Item'].notna(), 'Item'] = clean.loc[clean['Item'].notna(), 'Item'].str.title()

clean['Payment Method'] = clean['Payment Method'].astype(str).str.strip().replace({'nan': np.nan})
clean['Payment Method'] = clean['Payment Method'].str.upper()
payment_map = {'CASH':'Cash','CREDIT CARD':'Credit Card','DIGITAL WALLET':'Digital Wallet','MOBILE PAY':'Digital Wallet'}
clean['Payment Method'] = clean['Payment Method'].map(payment_map).fillna(clean['Payment Method'])
clean['Payment Method'] = clean['Payment Method'].where(clean['Payment Method'].notna(), np.nan)

clean['Location'] = clean['Location'].where(clean['Location'].notna(), np.nan)
clean.loc[clean['Location'].notna(), 'Location'] = clean.loc[clean['Location'].notna(), 'Location'].str.title()

clean['Quantity_raw'] = clean['Quantity']
clean['Price Per Unit_raw'] = clean['Price Per Unit']
clean['Total Spent_raw'] = clean['Total Spent']

clean['Quantity'] = pd.to_numeric(clean['Quantity'], errors='coerce')
clean['Price Per Unit'] = pd.to_numeric(clean['Price Per Unit'], errors='coerce')
clean['Total Spent'] = pd.to_numeric(clean['Total Spent'], errors='coerce')

clean['Transaction Date_raw'] = clean['Transaction Date']
clean['Transaction Date'] = pd.to_datetime(clean['Transaction Date'], errors='coerce', dayfirst=False)

mask_calc = clean['Total Spent'].isna() & clean['Quantity'].notna() & clean['Price Per Unit'].notna()
clean.loc[mask_calc, 'Total Spent'] = clean.loc[mask_calc, 'Quantity'] * clean.loc[mask_calc, 'Price Per Unit']

calc = clean['Quantity'] * clean['Price Per Unit']
mask_inconsistent = clean['Total Spent'].notna() & clean['Quantity'].notna() & clean['Price Per Unit'].notna() & ((clean['Total Spent'] - calc).abs() > 0.01)
clean.loc[mask_inconsistent, 'Total Spent_issue_corrected'] = True
clean.loc[mask_inconsistent, 'Total Spent_before_correction'] = clean.loc[mask_inconsistent, 'Total Spent']
clean.loc[mask_inconsistent, 'Total Spent'] = calc.loc[mask_inconsistent]

cols_for_dup = ['Transaction ID','Item','Quantity','Price Per Unit','Total Spent','Payment Method','Location','Transaction Date']
clean = clean.drop_duplicates(subset=cols_for_dup, keep='first').reset_index(drop=True)

outlier_qty_mask = (clean['Quantity'].notna()) & ((clean['Quantity'] <= 0) | (clean['Quantity'] > 100))
outlier_price_mask = (clean['Price Per Unit'].notna()) & ((clean['Price Per Unit'] <= 0) | (clean['Price Per Unit'] > 500))

clean.loc[outlier_qty_mask, 'Quantity_outlier'] = True
clean.loc[outlier_qty_mask, 'Quantity_before'] = clean.loc[outlier_qty_mask, 'Quantity']
clean.loc[outlier_qty_mask, 'Quantity'] = np.nan

clean.loc[outlier_price_mask, 'Price_outlier'] = True
clean.loc[outlier_price_mask, 'Price_before'] = clean.loc[outlier_price_mask, 'Price Per Unit']
clean.loc[outlier_price_mask, 'Price Per Unit'] = np.nan

final_cols = ['Transaction ID','Item','Quantity','Price Per Unit','Total Spent','Payment Method','Location','Transaction Date']
final = clean[final_cols].copy()

final['Quantity'] = pd.to_numeric(final['Quantity'], errors='coerce')
final['Price Per Unit'] = pd.to_numeric(final['Price Per Unit'], errors='coerce')
final['Total Spent'] = pd.to_numeric(final['Total Spent'], errors='coerce')
final['Transaction Date'] = pd.to_datetime(final['Transaction Date'], errors='coerce')

final.to_csv('./cafe_sales_cleaned.csv', index=False)
print('./cafe_sales_cleaned.csv saved')
