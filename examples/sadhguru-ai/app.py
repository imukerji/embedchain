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
    url = "https://gist.githubusercontent.com/imukerji/58bafd0a7d655dbb47d9a158a237fb49/raw/60c1ce00a5c89a462ded2f93d6f993c3e005c12d/gistfile1.csv"  # noqa:E501
    response = requests.get(url)
    csv_file = StringIO(response.text)
    for row in csv.reader(csv_file):
        if row and row[0] != "url":
            app.add(row[0], data_type="web_page")


app = sadhguru_ai()
add_data_to_app()

assistant_avatar_url = "https://kfoundation.org/wp-content/uploads/2022/08/Jiddu_Krishnamurti.jpg"  # noqa: E501


st.title("🙏 J. Krishnamurti AI")

styled_caption = '<p style="font-size: 17px; color: #aaa;">🚀 An <a href="https://github.com/embedchain/embedchain">Embedchain</a> app powered with Sadhguru\'s wisdom!</p>'  # noqa: E501
st.markdown(styled_caption, unsafe_allow_html=True)  # noqa: E501

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """
                Krishnamurti is regarded globally as one of the greatest thinkers and religious teachers of all time. He did not expound any philosophy or religion, but rather talked of the things that concern all of us in our everyday lives, of the problems of living in modern society with its violence and corruption, of the individual's search for security and happiness, and the need for mankind to free itself from inner burdens of fear, anger, hurt, and sorrow. He explained with great precision the subtle workings of the human mind, and pointed to the need for bringing to our daily life a deeply meditative and spiritual quality.

Krishnamurti belonged to no religious organization, sect or country, nor did he subscribe to any school of political or ideological thought. On the contrary, he maintained that these are the very factors that divide human beings and bring about conflict and war. He reminded his listeners again and again that we are all human beings first and not Hindus, Muslims or Christians, that we are like the rest of humanity and are not different from one another. He asked that we tread lightly on this earth without destroying ourselves or the environment. He communicated to his listeners a deep sense of respect for nature. His teachings transcend man-made belief systems, nationalistic sentiment and sectarianism. At the same time, they give new meaning and direction to mankind's search for truth. His teaching, besides being relevant to the modern age, is timeless and universal.

Krishnamurti spoke not as a guru but as a friend, and his talks and discussions are based not on tradition-based knowledge but on his own insights into the human mind and his vision of the sacred, so he always communicates a sense of freshness and directness although the essence of his message remained unchanged over the years. When he addressed large audiences, people felt that Krishnamurti was talking to each of them personally, addressing his or her particular problem. In his private interviews, he was a compassionate teacher, listening attentively to the man or woman who came to him in sorrow, and encouraging them to heal themselves through their own understanding. Religious scholars found that his words threw new light on traditional concepts. Krishnamurti took on the challenge of modern scientists and psychologists and went with them step by step, discussed their theories and sometimes enabled them to discern the limitations of those theories. Krishnamurti left a large body of literature in the form of public talks, writings, discussions with teachers and students, with scientists and religious figures, conversations with individuals, television and radio interviews, and letters. Many of these have been published as books, and audio and video recordings.
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
