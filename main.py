import streamlit as st
from inventory import display_inventory, display_ledger, add_stock, issue_items
from departments import manage_departments
from utils import load_ledger, load_overview

# Initialize session state for data persistence
if 'departments' not in st.session_state:
    st.session_state.departments = ['Sports', 'Boys Hostel', 'Canteen', 'Girls Hostel', 'Personal']
if 'ledger' not in st.session_state:
    st.session_state.ledger = load_ledger()
if 'inventory' not in st.session_state:
    st.session_state.inventory = load_overview()

# Streamlit app
st.title('School Housekeeping Inventory Management')

# Sidebar with headers and subheaders
st.sidebar.header("Main Menu")
# st.sidebar.subheader("Overview")
if st.sidebar.button("Show Inventory Overview"):
    display_inventory()

# st.sidebar.subheader("Ledger")
if st.sidebar.button("Show Transaction Ledger"):
    display_ledger()

# st.sidebar.subheader("Add Stock")
if st.sidebar.button("Add New Stock"):
    add_stock()

# st.sidebar.subheader("Issue Items")
if st.sidebar.button("Issue Items to Departments"):
    issue_items()

# st.sidebar.subheader("Manage Departments")
if st.sidebar.button("Manage Departments"):
    manage_departments()
