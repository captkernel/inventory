import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Define filename and sheet names
FILE_NAME = 'Inventory.xlsx'
LEDGER_SHEET = 'Ledger'
OVERVIEW_SHEET = 'Overview'

# Initialize session state for data persistence
if 'ledger' not in st.session_state:
    st.session_state.ledger = pd.DataFrame(columns=[
        'Date', 'Type', 'Item Name', 'Department', 'Quantity Issued', 'Current Stock', 'Vendor Name', 'Invoice Number'
    ])
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=['Item Name', 'Type', 'Total', 'Admin', 'Sports', 'Boys Hostel', 'Canteen', 'Girls Hostel', 'Personal'])
if 'departments' not in st.session_state:
    st.session_state.departments = ['Sports', 'Boys Hostel', 'Canteen', 'Girls Hostel', 'Personal']
if 'page' not in st.session_state:
    st.session_state.page = 'Overview'

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
    if not os.path.exists(FILE_NAME):
        with pd.ExcelWriter(FILE_NAME, engine='openpyxl', mode='w') as writer:
            ledger_df.to_excel(writer, sheet_name=LEDGER_SHEET, index=False)
    else:
        with pd.ExcelWriter(FILE_NAME, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            ledger_df.to_excel(writer, sheet_name=LEDGER_SHEET, index=False)

# Save the overview (inventory) to the Excel file
def save_overview(overview_df):
    if not os.path.exists(FILE_NAME):
        with pd.ExcelWriter(FILE_NAME, engine='openpyxl', mode='w') as writer:
            overview_df.to_excel(writer, sheet_name=OVERVIEW_SHEET, index=False)
    else:
        with pd.ExcelWriter(FILE_NAME, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            overview_df.to_excel(writer, sheet_name=OVERVIEW_SHEET, index=False)

# Initialize data from files
if 'ledger_initialized' not in st.session_state:
    st.session_state.ledger = load_ledger()
    st.session_state.ledger_initialized = True
if 'inventory_initialized' not in st.session_state:
    st.session_state.inventory = load_overview()
    st.session_state.inventory_initialized = True

# Helper functions
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

def add_transaction(date, item_type, item_name, department, quantity, vendor_name, invoice_number):
    if item_name not in st.session_state.inventory['Item Name'].values:
        new_row = {'Item Name': item_name, 'Type': item_type, 'Total': 0, 'Admin': 0}
        for dept in st.session_state.departments:
            new_row[dept] = 0
        st.session_state.inventory = pd.concat([st.session_state.inventory, pd.DataFrame([new_row])], ignore_index=True)
    
    current_stock = st.session_state.inventory.loc[st.session_state.inventory['Item Name'] == item_name, 'Admin'].values[0]
    
    if department != 'Admin' and quantity > current_stock:
        st.error(f"Not enough {item_name} in inventory to issue. Available: {current_stock}")
        return
    
    new_entry = {
        'Date': date,
        'Type': item_type,
        'Item Name': item_name,
        'Department': department,
        'Quantity Issued': quantity,
        'Current Stock': current_stock - quantity if department != 'Admin' else current_stock + quantity,
        'Vendor Name': vendor_name,
        'Invoice Number': invoice_number
    }
    st.session_state.ledger = pd.concat([st.session_state.ledger, pd.DataFrame([new_entry])], ignore_index=True)
    st.session_state.inventory = update_inventory(st.session_state.ledger)
    save_ledger(st.session_state.ledger)
    save_overview(st.session_state.inventory)

# Sidebar
st.sidebar.title("Navigation")
if st.sidebar.button("Overview"):
    st.session_state.page = "Overview"
if st.sidebar.button("Ledger"):
    st.session_state.page = "Ledger"
if st.sidebar.button("Add Stock"):
    st.session_state.page = "Add Stock"
if st.sidebar.button("Issue Items"):
    st.session_state.page = "Issue Items"
if st.sidebar.button("Manage Departments"):
    st.session_state.page = "Manage Departments"

# Streamlit app
st.title('School Housekeeping Inventory Management')

if st.session_state.page == "Overview":
    st.header('Inventory Overview')
    inventory = st.session_state.inventory.copy()
    st.dataframe(inventory)
    
elif st.session_state.page == "Ledger":
    st.header('Transaction Ledger')
    st.write(st.session_state.ledger)

elif st.session_state.page == "Add Stock":
    st.header('Add New Stock')
    with st.form("add_stock_form"):
        date = st.date_input("Date")
        item_type = st.selectbox("Item Type", ["Asset", "Consumable"])
        item_name = st.text_input("Item Name")
        quantity = st.number_input("Quantity", min_value=1, step=1)
        vendor_name = st.text_input("Vendor Name")
        invoice_number = st.text_input("Invoice Number")
        submitted = st.form_submit_button("Add Stock")
        
        if submitted:
            add_transaction(date.strftime("%Y-%m-%d"), item_type, item_name, 'Admin', quantity, vendor_name, invoice_number)
            st.success(f"Added {quantity} units of {item_name} to Admin inventory")

elif st.session_state.page == "Issue Items":
    st.header('Issue Items to Departments')
    
    item_type = st.selectbox("Item Type", ["Asset", "Consumable"])
    item_names = st.session_state.inventory[st.session_state.inventory['Type'] == item_type]['Item Name'].unique()
    
    with st.form("issue_items_form"):
        date = st.date_input("Date")
        item_name = st.selectbox("Item Name", item_names)
        department = st.selectbox("Department", st.session_state.departments)
        quantity = st.number_input("Quantity", min_value=1, step=1)
        submitted = st.form_submit_button("Issue Items")
        
        if submitted:
            current_stock = st.session_state.inventory.loc[st.session_state.inventory['Item Name'] == item_name, 'Admin'].values[0]
            if quantity <= current_stock:
                add_transaction(date.strftime("%Y-%m-%d"), item_type, item_name, department, quantity, "", "")
                st.success(f"Issued {quantity} units of {item_name} to {department}")
            else:
                st.error(f"Not enough {item_name} in inventory to issue. Available: {current_stock}")

elif st.session_state.page == "Manage Departments":
    st.header('Manage Departments')
    new_dept = st.text_input("New Department")
    add_dept = st.button("Add Department")
    remove_dept = st.selectbox("Remove Department", st.session_state.departments)
    remove_button = st.button("Remove Department")

    if add_dept and new_dept:
        if new_dept not in st.session_state.departments:
            st.session_state.departments.append(new_dept)
            st.session_state.inventory[new_dept] = 0  # Add new column to inventory
            st.success(f"Department '{new_dept}' added.")
        else:
            st.warning(f"Department '{new_dept}' already exists.")

    if remove_button:
        if remove_dept in st.session_state.departments:
            st.session_state.departments.remove(remove_dept)
            st.session_state.inventory.drop(columns=[remove_dept], inplace=True)  # Remove column from inventory
            st.success(f"Department '{remove_dept}' removed.")
        else:
            st.warning(f"Department '{remove_dept}' does not exist.")
