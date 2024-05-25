# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
    """
    **Choose the fruits you want in your custom smoothie,**
    """
)

# Input for the name on the order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be:', name_on_order)

# Get active Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch available fruits from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME')).collect()
fruits = [row['FRUIT_NAME'] for row in my_dataframe]

# Select ingredients
ingredients_list = st.multiselect('Choose up to 5 ingredients:'
, my_dataframe
, max_selections=5
)

if ingredients_list:
    # Join the ingredients into a single string
    ingredients_string = ' '.join(ingredients_list)

    # Display the ingredients string
    st.write(f"Ingredients: {ingredients_string}")

    # Create the insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Display the insert statement for debugging
    st.write(my_insert_stmt)

    # Button to submit the order
    if st.button('Submit Order'):
        # Execute the insert statement
        session.sql(my_insert_stmt).collect()
        
        # Display success message
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
