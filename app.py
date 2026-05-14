import streamlit as st
from agent import process_query

st.set_page_config(
    page_title = 'AI Search Agent',
    page_icon = '🔍',
    layout= 'centered',
)

st.title('🔍 AI Search Agent')

st.markdown(
    """
    Ask a question and the agent will search the web for 
    the latest information to provide you with an accurate answer."""
)

query = st.text_input("What do you want to search today?: ")

if st.button("Search"):
    st.write("Searching the web...")
    
    if query.strip() == "":
        st.warning("Please enter a query to search.")
    else:
        with st.spinner("Fetching search results..."):
            
            try: 
                response = process_query(query)
                st.success("Done!")
                st.markdown(f"**Search Results:**\n\n{response}")
                
            except Exception as e:
                st.error(f"An error occurred: {e}")