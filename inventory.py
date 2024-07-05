import streamlit as st
import pandas as pd
from datetime import datetime
from utils import load_ledger, load_overview, save_ledger, save_overview, update_inventory

def display_inventory():
    st.header('Inventory Overview')
    inventory = st.session_state.inventory.copy()
    st.dataframe(inventory)

def display_ledger():
    st.header('Transaction Ledger')
    st.write(st.session_state.ledger)

def add_stock():
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

def issue_items():
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
