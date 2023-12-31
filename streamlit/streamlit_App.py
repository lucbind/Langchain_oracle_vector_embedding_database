import streamlit as st
import oracledb
import cohere
import array
from typing import List
import os




###-----------------
cohere_api_key =st.secrets["COHERE_API_KEY"] #keep your cohere api key  port  in the .env file and retrieve it
oracle_service_name =st.secrets["SERVICE_NAME"] #keep your oracle listner port  in the .env file and retrieve it
oracle_user = st.secrets ["USERNAME"] #keep your oracle username in the .env file and retrieve it
oracle_password =st.secrets["PASSWORD"] #keep your oracle usernamepassword in the .env file and retrieve it
oracle_hostname =st.secrets["HOST"] #keep your oracle server hostname in the .env file and retrieve it
oracle_port =st.secrets["PORT"] #keep your oracle listner port  in the .env file and retrieve it

co = cohere.Client(cohere_api_key)


# Connect to your Oracle 23.4 database
#print (oracle_user, oracle_password,oracle_hostname,oracle_port,oracle_service_name)
connection = oracledb.connect(
    user=oracle_user,
    password=oracle_password,
    dsn=oracle_hostname+":"+oracle_port+"/"+oracle_service_name
    )
cursor = connection.cursor()


def embed (prompt):
    embedding  = co.embed(
        texts=[prompt],
         model='embed-english-v3.0',
         input_type='search_query'
        )
    return embedding

def generate_text(prompt, temp=0):
  response = co.generate(
    model='command',
    prompt=prompt,
    max_tokens=200,
    temperature=temp)
  return response.generations[0].text

import array
from typing import List

#funzione Ricerca all'intenro del database oracle sfruttando l'operatore VECTOR_DISTANCE

def find_oracle_chunk (vector_prompt:List[float],question_input ):
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

    text_prompt ='Kindly answer the following question'+question_input+' based on '  
    for i in range(len(rows)):
        text_prompt += rows[i][0]+' and  '
    return text_prompt

# Applicare uno stile wide mode
st.set_page_config(layout="wide")
# Applicare uno stile con sfondo nero e testo bianco
st.markdown(
    """
    <style>
        body {
            color: white;
            background-color: black;
        }
    </style>
    """,
    unsafe_allow_html=True
)




     
st.title("Chat with Cohere and Oracle Vector Database  💬🅾️")
st.info("Check out the full tutorial to build this app in our [blog post](https://blog.streamlit.io/build-a-chatbot-with-custom-data-sources-powered-by-llamaindex/)", icon="📃")

with st.chat_message("assistant"):
     st.write("hello human 👋")



question_input = st.chat_input("Your question", key = "question_input")
if question_input:
    with st.chat_message("user"):
       st.write(f"{question_input}")
       with st.spinner("Thinking..."):
          response  = embed(question_input)
          text_prompt=find_oracle_chunk(response.embeddings[0],question_input)
          response = generate_text(text_prompt, temp=0.5)
    with st.chat_message("assistant"):
       st.write(response)




