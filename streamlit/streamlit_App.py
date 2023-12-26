import streamlit as st
import oracledb
import cohere
import array
from typing import List

st.set_page_config(page_title="Chat with the Cohere and Oracle vector DB , demo powered by LB", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets["openai_key"]
st.title("Chat with the Cohere and Oracle vector DB , demo powered by LB 💬")
st.info("find all stuff in github repository [blog post](https://github.com/lucbind?tab=repositories)", icon="📃")
         
if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question about CV that are in the vector Oracle Database"}
    ]

@st.cache_resource(show_spinner=False)

###-----------------

co = cohere.Client(cohere_api_key)


# Connect to your Oracle 23.4 database
#print (oracle_user, oracle_password,oracle_hostname,oracle_port,oracle_service_name)
connection = oracledb.connect(
    user=oracle_user,
    password=oracle_password,
    dsn=oracle_hostname+":"+oracle_port+"/"+oracle_service_name
    )
cursor = connection.cursor()


def embed (prompt);
    try :
        embedding  = co.embed(
            texts=[prompt],
             model='embed-english-v3.0',
             input_type='search_query'
            )
    return response

def generate_text(prompt, temp=0):
  response = co.generate(
    model='command',
    prompt=prompt,
    max_tokens=200,
    temperature=temp)
  return response.generations[0].text

###-----------------



if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = embed(prompt);
            #Ricerca all'intenro del database oracle sfruttando l'operatore VECTOR_DISTANCE
            vector_prompt:List[float]=response.embeddings[0]
            cursor = connection.cursor()
            sql = """SELECT CHUNK  from Vector_CV_PDF where (ID_PDF, id_chunk) in 
            (
            select ID_PDF ,substr(ranking,instr(ranking,'-',-1)+1)chunk_id from (
            select ID_PDF , min(ranking) ranking
              from (
                    select ID_PDF,VECTOR_DISTANCE(V,:1)||'--'||id_chunk ranking 
                      from Vector_CV_PDF  
                    order by VECTOR_DISTANCE(V,:2)
                    )
            group by id_pdf order by 2,1 desc FETCH FIRST 3 ROWS ONLY
            )
            )"""

            with connection.cursor() as cursor:
                    array_query1 = array.array("d", vector_prompt)
                    array_query2 = array.array("d", vector_prompt)
                    cursor.execute(sql,[array_query1,array_query1])
                    rows = cursor.fetchall()
            #print(rows)
text_prompt ='Kindly answer the following question  ' + prompt_question  + ' based on  ' ;
for i in range(len(rows)):
    text_prompt += rows[i][0]+' and  '
response = generate_text(text_prompt, temp=0.5)
print(response)
st.write(response)
message = {"role": "assistant", "content": response}
st.session_state.messages.append(message) # Add response to message history
