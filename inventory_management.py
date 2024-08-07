import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Add custom CSS for wide mode
st.markdown(
    """
    <style>
    .main .block-container {
        max-width: 80%;
        padding-left: 10%;
        padding-right: 10%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Define filename and sheet names
FILE_NAME = 'Inventory.xlsx'
LEDGER_SHEET = 'Ledger'
OVERVIEW_SHEET = 'Overview'
DEFAULT_DEPARTMENTS = [
    'Junior block', 'Middle block', 'Senior block', 'Sports', 
    'Arts', 'Boys hostel', 'Girls hostel', 'Owner'
]
ASSET_TYPES = [
    'Housekeeping assets', 'Housekeeping consumables', 'Electrical equipment', 
    'Hardware', 'Gardening equipment', 'Stationary', 
    'Furnitures and fixtures', 'Sports equipment'
]

# Initialize session state for data persistence
if 'ledger' not in st.session_state:
    st.session_state.ledger = pd.DataFrame(columns=[
        'Date', 'Type', 'Item Name', 'Department', 'Quantity Issued', 'Current Stock', 
        'Vendor Name', 'Invoice Number', 'Total Price'
    ])
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=['Item Name', 'Type', 'Total', 'Admin'] + DEFAULT_DEPARTMENTS)
if 'departments' not in st.session_state:
    st.session_state.departments = DEFAULT_DEPARTMENTS
if 'page' not in st.session_state:
    st.session_state.page = 'Overview'

# Load the ledger from the Excel file
def load_ledger():
    if os.path.exists(FILE_NAME):
        try:
            return pd.read_excel(FILE_NAME, sheet_name=LEDGER_SHEET, engine='openpyxl')
        except ValueError:
            return pd.DataFrame(columns=[
                'Date', 'Type', 'Item Name', 'Department', 'Quantity Issued', 'Current Stock', 
                'Vendor Name', 'Invoice Number', 'Total Price'
            ])
    else:
        return pd.DataFrame(columns=[
            'Date', 'Type', 'Item Name', 'Department', 'Quantity Issued', 'Current Stock', 
            'Vendor Name', 'Invoice Number', 'Total Price'
        ])

# Load the overview (inventory) from the Excel file
def load_overview():
    if os.path.exists(FILE_NAME):
        try:
            df = pd.read_excel(FILE_NAME, sheet_name=OVERVIEW_SHEET, engine='openpyxl')
            # Extract departments from the columns, excluding non-department columns
            department_cols = [col for col in df.columns if col not in ['Item Name', 'Type', 'Total', 'Admin']]
            st.session_state.departments = department_cols if department_cols else DEFAULT_DEPARTMENTS
            return df
        except ValueError:
            st.session_state.departments = DEFAULT_DEPARTMENTS
            return pd.DataFrame(columns=['Item Name', 'Type', 'Total', 'Admin'] + st.session_state.departments)
    else:
        st.session_state.departments = DEFAULT_DEPARTMENTS
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

def add_transaction(date, item_type, item_name, department, quantity, vendor_name, invoice_number, total_price):
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
        'Invoice Number': str(invoice_number),
        'Total Price': round(total_price,2)
    }
    st.session_state.ledger = pd.concat([st.session_state.ledger, pd.DataFrame([new_entry])], ignore_index=True)
    st.session_state.inventory = update_inventory(st.session_state.ledger)
    save_ledger(st.session_state.ledger)
    save_overview(st.session_state.inventory)

def delete_inventory_file():
    if os.path.exists(FILE_NAME):
        os.remove(FILE_NAME)
        st.success(f"Deleted {FILE_NAME}")
        # Clear session state and reinitialize
        st.session_state.ledger = pd.DataFrame(columns=[
            'Date', 'Type', 'Item Name', 'Department', 'Quantity Issued', 'Current Stock', 
            'Vendor Name', 'Invoice Number', 'Total Price'
        ])
        st.session_state.inventory = pd.DataFrame(columns=['Item Name', 'Type', 'Total', 'Admin'] + DEFAULT_DEPARTMENTS)
        st.session_state.departments = DEFAULT_DEPARTMENTS
    else:
        st.error(f"{FILE_NAME} does not exist")

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
if st.sidebar.button("Delete Inventory File"):
    st.session_state.page = "Delete Inventory File"
if st.sidebar.button("Download Inventory File"):
    st.session_state.page = "Download Inventory File"

# Streamlit app
st.title('School Inventory Management')

if st.session_state.page == "Overview":
    st.header('Inventory Overview')
    inventory = st.session_state.inventory.copy()
    st.dataframe(inventory.style.set_properties(**{'width': 'auto'}))
    
elif st.session_state.page == "Ledger":
    st.header('Transaction Ledger')
    st.dataframe(st.session_state.ledger.style.set_properties(**{'width': 'auto'}))


elif st.session_state.page == "Add Stock":
    st.header('Add New Stock')
    with st.form("add_stock_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date")
            item_type = st.selectbox("Item Type", ASSET_TYPES)
            item_name = st.text_input("Item Name")
            quantity = st.number_input("Quantity", min_value=1, step=1)
        with col2:
            vendor_name = st.text_input("Vendor Name")
            invoice_number = st.text_input("Invoice Number")
            total_price = st.number_input("Total Price", min_value=0.0, step=0.01)
        
        submitted = st.form_submit_button("Add Stock")
        
        if submitted:
            if not date or not item_type or not item_name or quantity <= 0:
                st.error("Please fill in all mandatory fields: Date, Item Type, Item Name, and Quantity.")
            else:
                add_transaction(
                    date.strftime("%Y-%m-%d"), item_type, item_name, 'Admin', quantity, 
                    vendor_name, invoice_number, total_price
                )
                st.success(f"Added {quantity} units of {item_name} to Admin inventory")

elif st.session_state.page == "Issue Items":
    st.header('Issue Items to Departments')
    
    item_type = st.selectbox("Item Type", ASSET_TYPES)
    item_names = st.session_state.inventory[st.session_state.inventory['Type'] == item_type]['Item Name'].unique()
    
    with st.form("issue_items_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date")
            item_name = st.selectbox("Item Name", item_names)
        with col2:
            department = st.selectbox("Department", st.session_state.departments)
            quantity = st.number_input("Quantity", min_value=1, step=1)
        
        submitted = st.form_submit_button("Issue Items")
        
        if submitted:
            current_stock = st.session_state.inventory.loc[st.session_state.inventory['Item Name'] == item_name, 'Admin'].values[0]
            if quantity <= current_stock:
                add_transaction(date.strftime("%Y-%m-%d"), item_type, item_name, department, quantity, "", "", total_price=None)
                st.success(f"Issued {quantity} units of {item_name} to {department}")
            else:
                st.error(f"Not enough {item_name} in inventory to issue. Available: {current_stock}")

elif st.session_state.page == "Manage Departments":
    st.header('Manage Departments')
    with st.container():
        new_dept = st.text_input("New Department")
        add_dept = st.button("Add Department")
        if add_dept and new_dept:
            if new_dept not in st.session_state.departments:
                st.session_state.departments.append(new_dept)
                st.session_state.inventory[new_dept] = 0  # Add new column to inventory
                st.success(f"Department '{new_dept}' added.")
            else:
                st.warning(f"Department '{new_dept}' already exists.")

    with st.container():
        remove_dept = st.selectbox("Remove Department", st.session_state.departments)
        remove_button = st.button("Remove Department")

        if remove_button:
            if remove_dept in st.session_state.departments:
                st.session_state.departments.remove(remove_dept)
                st.session_state.inventory.drop(columns=[remove_dept], inplace=True)  # Remove column from inventory
                st.success(f"Department '{remove_dept}' removed.")
            else:
                st.warning(f"Department '{remove_dept}' does not exist.")

elif st.session_state.page == "Delete Inventory File":
    st.header('Delete Inventory File')
    st.warning("This action will delete the Inventory.xlsx file permanently.")
    if st.button("Delete File"):
        delete_inventory_file()

elif st.session_state.page == "Download Inventory File":
    st.header('Download Inventory File')
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "rb") as file:
            st.download_button(
                label="Download Inventory.xlsx",
                data=file,
                file_name="Inventory.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.error(f"{FILE_NAME} does not exist")
