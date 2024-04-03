import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplates import css, bot_template, user_template
from langchain.llms import HuggingFaceHub
import os
import subprocess
import json
import asyncio
import aiofiles

openai_key = os.getenv('OPENAI_API_KEY')


def get_text_from_doc(docs):
    text = ""
    for doc in docs:
        print(doc.type)
        if doc.type == "application/pdf":
            pdf_reader = PdfReader(doc)
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
        elif doc.type in ["text/plain", "application/rtf", "text/rtf"]:
            text += doc.read().decode("utf-8")
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def get_vectorstore(text_chunks, model_name="gpt-4-0125-preview"):
    embeddings = OpenAIEmbeddings(model=model_name)
    # embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore


def get_conversation_chain(vectorstore, model_name="gpt-4-0125-preview"):
    llm = ChatOpenAI(temperature=0.2, model_name=model_name,
                     openai_api_key=openai_key)

    # llm = HuggingFaceHub(repo_id="google/flan-t5-xxl", model_kwargs={"temperature":0.5, "max_length":512})

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory
    )
    return conversation_chain


def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)

# takes audio file name and returns in yml of the conversation


async def get_audio_text(audio_path):
    # Define dynamic output file name based on audio file name
    output_file_name = audio_path.rsplit('.', 1)[0] + ".json"

    # Execute insanely-fast-whisper command with dynamic output file name asynchronously
    command = ["insanely-fast-whisper", "--file-name", audio_path, "--device-id",
               "mps", "--language", "fr", "--transcript-path", output_file_name]
    await asyncio.create_subprocess_exec(*command)

    # Asynchronously read the dynamically named output file
    async with aiofiles.open(output_file_name, "r") as f:
        output = json.loads(await f.read())

    # Optionally remove the audio and output files
    # os.remove(audio_path)
    # os.remove(output_file_name)

    return output['chunks']


def main():
    load_dotenv()
    st.set_page_config(page_title="Interroger vos documents")
    st.write(css, unsafe_allow_html=True)

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None

    st.header("Interroger plusieurs documents")

    user_question = st.text_input(
        "Entrez votre question relative aux documents :")
    model_choice = st.selectbox(
        "Modèle à utiliser",
        options=[("GPT 4 - 128k", "gpt-4-0125-preview"),
                 ("GPT 3 - 16k", "gpt-3.5-turbo-0125")],
        format_func=lambda x: x[0],
        index=0,
    )
    selected_model_value = model_choice[1]
    if user_question:
        handle_userinput(user_question)

    with st.sidebar:
        st.subheader("Vos documents")
        doc_files = st.file_uploader(
            "Chargez vos documents ici, puis appuyez sur 'Traiter'", accept_multiple_files=True)
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Traiter"):
                if not doc_files:
                    st.error("Aucun document n'a été sélectionné.")
                    return
                with st.spinner("Traitement en cours"):
                    # Get audio text
                    raw_text = get_text_from_doc(doc_files)
                    if not raw_text:
                        st.error(
                            "Aucun texte n'a été extrait des fichiers.")
                        return
                    # Get the text chunks
                    text_chunks = get_text_chunks(raw_text)

                    # Create vector store
                    vectorstore = get_vectorstore(
                        text_chunks, model_name=selected_model_value)

                    # Create conversation chain
                    st.session_state.conversation = get_conversation_chain(
                        vectorstore, model_name=selected_model_value)


if __name__ == '__main__':
    main()
