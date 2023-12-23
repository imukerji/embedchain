import csv
import queue
import threading
from io import StringIO

import requests
import streamlit as st

from embedchain import Pipeline as App
from embedchain.config import BaseLlmConfig
from embedchain.helpers.callbacks import (StreamingStdOutCallbackHandlerYield,
                                          generate)


@st.cache_resource
def sadhguru_ai():
    app = App()
 

    return app


# Function to read the CSV file row by row
def read_csv_row_by_row(file_path):
    with open(file_path, mode="r", newline="", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            yield row


@st.cache_resource
def add_data_to_app():
    app = sadhguru_ai()
    url = "https://gist.githubusercontent.com/imukerji/58bafd0a7d655dbb47d9a158a237fb49/raw/4d02aa09fd00ea291389c4dac2fa90c68c7603a5/gistfile1.csv"  # noqa:E501
    response = requests.get(url)
    csv_file = StringIO(response.text)
    for row in csv.reader(csv_file):
        if row and row[0] != "url":
            try:
                app.add(row[0], data_type="web_page")
            except Exception as e:
                print(f"Failed to add {row[0]} error {e}")




app = sadhguru_ai()
add_data_to_app()
assistant_avatar_url = "https://kfoundation.org/wp-content/uploads/2022/07/black-and-white-photograph-of-a-smiling-j-krishnamurti-looking-at-the-camera.jpg"  # noqa: E501
st.title("🙏 J. Krishnamurti AI")
styled_caption = '<p style="font-size: 17px; color: #aaa;">🚀 An <a href="https://github.com/embedchain/embedchain">Embedchain</a> app powered with J. Krishnamurti\'s wisdom!</p>'  # noqa: E501
st.markdown(styled_caption, unsafe_allow_html=True)  # noqa: E501
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """
                I am Jiddu Krishnamurti, an eminent writer and speaker on philosophical and spiritual issues, including psychological revolution, the nature of the human mind, consciousness and evolution, meditation, human relationships, and bringing about positive social change.
            """,  # noqa: E501
        }
    ]
for message in st.session_state.messages:
    role = message["role"]
    with st.chat_message(role, avatar=assistant_avatar_url if role == "assistant" else None):
        st.markdown(message["content"])
if prompt := st.chat_input("Ask me anything!"):
    with st.chat_message("user"):
        st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant", avatar=assistant_avatar_url):
        msg_placeholder = st.empty()
        msg_placeholder.markdown("Thinking...")
        full_response = ""
        q = queue.Queue()
        def app_response(result):
            config = BaseLlmConfig(stream=True, callbacks=[StreamingStdOutCallbackHandlerYield(q)])
            answer, citations = app.chat(prompt, config=config, citations=True)
            result["answer"] = answer
            result["citations"] = citations
        results = {}
        thread = threading.Thread(target=app_response, args=(results,))
        thread.start()
        for answer_chunk in generate(q):
            full_response += answer_chunk
            msg_placeholder.markdown(full_response)
        thread.join()
        answer, citations = results["answer"], results["citations"]
        if citations:
            full_response += "\n\n**Sources**:\n"
            for i, citations in enumerate(citations):
                full_response += f"{i+1}. {citations[1]}\n"
        msg_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
