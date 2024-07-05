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
        overview_df.to_excel(writer, sheet_name=OVERVIEW_SHEET, index=False)

# Update inventory based on the ledger
def update_inventory(ledger_df):
    inventory = pd.DataFrame(columns=['Item Name', 'Type', 'Total', 'Admin'] + st.session_state.departments)
    for index, row in ledger_df.iterrows():
        if row['Item Name'] not in inventory['Item Name'].values:
            new_row = {'Item Name': row['Item Name'], 'Type': row['Type'], 'Total': 0, 'Admin': 0}
            for dept in st.session_state.departments:
                new_row[dept] = 0
            inventory = pd.concat([inventory, pd.DataFrame([new_row])], ignore_index=True)
        
        item_row = inventory[inventory['Item Name'] == row['Item Name']].index[0]
        
        if row['Department'] == 'Admin':
            inventory.at[item_row, 'Admin'] += row['Quantity Issued']
        elif row['Department'] in st.session_state.departments:
            inventory.at[item_row, row['Department']] += row['Quantity Issued']
            inventory.at[item_row, 'Admin'] -= row['Quantity Issued']
        
        inventory.at[item_row, 'Total'] = inventory.at[item_row, 'Admin'] + sum(inventory.loc[item_row, st.session_state.departments])
    
    return inventory
