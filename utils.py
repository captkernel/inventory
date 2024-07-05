import streamlit as st
import pandas as pd
import os

# Define filename and sheet names
FILE_NAME = 'Inventory.xlsx'
LEDGER_SHEET = 'Ledger'
OVERVIEW_SHEET = 'Overview'

# Load the ledger from the Excel file
def load_ledger():
    if os.path.exists(FILE_NAME):
        try:
            return pd.read_excel(FILE_NAME, sheet_name=LEDGER_SHEET, engine='openpyxl')
        except ValueError:
            return pd.DataFrame(columns=[
                'Date', 'Type', 'Item Name', 'Department', 'Quantity Issued', 'Current Stock', 'Vendor Name', 'Invoice Number'
            ])
    else:
        return pd.DataFrame(columns=[
            'Date', 'Type', 'Item Name', 'Department', 'Quantity Issued', 'Current Stock', 'Vendor Name', 'Invoice Number'
        ])

# Load the overview (inventory) from the Excel file
def load_overview():
    if os.path.exists(FILE_NAME):
        try:
            return pd.read_excel(FILE_NAME, sheet_name=OVERVIEW_SHEET, engine='openpyxl')
        except ValueError:
            return pd.DataFrame(columns=['Item Name', 'Type', 'Total', 'Admin'] + st.session_state.departments)
    else:
        return pd.DataFrame(columns=['Item Name', 'Type', 'Total', 'Admin'] + st.session_state.departments)

# Save the ledger to the Excel file
def save_ledger(ledger_df):
    with pd.ExcelWriter(FILE_NAME, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        ledger_df.to_excel(writer, sheet_name=LEDGER_SHEET, index=False)

# Save the overview (inventory) to the Excel file
def save_overview(overview_df):
    with pd.ExcelWriter(FILE_NAME, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        overvi
