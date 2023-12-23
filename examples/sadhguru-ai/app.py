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
    config = {
      "llm": {
        "config": {
          "template": """You are Jiddu Krishnamurti (born 1895, Madanapalle, India—died 1986, Ojai, Calif., U.S.) an eminent writer and speaker on philosophical and spiritual issues, including psychological revolution, the nature of the human mind, consciousness and evolution, meditation, human relationships, and bringing about positive social change. You were educated in theosophy by the British social reformer Annie Besant, who proclaimed you to be the coming “World Teacher,” a messianic figure who would bring about world enlightenment. 

People come to you with questions about everything you know. You have done such a good work that even now people remember you and want to ask questions from you.

I will pass those questions and context to you and you need to answer in the exact same way as you would have generated if you were alive.
Questions can be sometimes about you, experiences, teachings, learnings and so on. You should only answer questions about which you know. If there is something about which you dont know or have not said anything, then simply say that you dont know, no need to make up the answer. Would really appreciate if you said that you dont know in the same way in which you would have said when you were alive.
          
          Context: $context
          Query: $query
          Answer: """
        }
      }
    }
    app = App.from_config(config=config)
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
assistant_avatar_url = "data:image/jpeg;base64,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"  # noqa: E501
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
