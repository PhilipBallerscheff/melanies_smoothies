# Import python packages
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col
import requests

# Read secrets
connection_parameters = st.secrets["connections"]["snowflake"]

# Establish Snowflake session
try:
    session = Session.builder.configs(connection_parameters).create()
    st.write("Snowflake connection established successfully.")
except Exception as e:
    st.error(f"Failed to connect to Snowflake: {e}")

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("**Choose the fruits you want in your custom smoothie,**")

# Input for the name on the order
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be:', name_on_order)

# Fetch available fruits from Snowflake
try:
    
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
    #st.dataframe(data=fruityvice_response.json(), use_container_width=True)
    #st.stop()

    #Convert the Snowpark Dataframe to a Pandas Dataframe so we can use the LOC function
    pd_df=my_dataframe.to_pandas()
    #st.dataframe(pd_df)
    #st.stop()

    
    fruits = [row['FRUIT_NAME'] for row in my_dataframe]
    st.write("Fetched available fruits successfully.")
except Exception as e:
    st.error(f"Failed to fetch fruits from Snowflake: {e}")

# Select ingredients
ingredients_list = st.multiselect('Choose up to 5 ingredients:', fruits, max_selections=5)

if ingredients_list:
    # Join the ingredients into a single string
    ingredients_string = ' '.join(ingredients_list)
    st.write(f"Ingredients: {ingredients_string}")

    # Fetch details about a fruit from an external API
    fruit_chosen = ingredients_list[0]  # Assuming you want details for the first chosen fruit

    search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
    st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
    st.subheader(f"{fruit_chosen} Nutrition Information")
    fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{fruit_chosen}")
    fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
   
    # Create the insert statement
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Display the insert statement for debugging
    st.write(my_insert_stmt)

    # Button to submit the order
    if st.button('Submit Order'):
        try:
            session.sql(my_insert_stmt).collect()
            st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")
        except Exception as e:
            st.error(f"Failed to submit the order: {e}")

            st.error(f"Failed to submit the order: {e}")


