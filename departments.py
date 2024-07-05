import streamlit as st

def manage_departments():
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
