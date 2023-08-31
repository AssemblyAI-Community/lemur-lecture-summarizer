import os

import streamlit as st
import assemblyai as aai
from dotenv import load_dotenv
load_dotenv()

from utils import get_transcript, ask_question, return_ytdlp_fname

environ_key = os.environ.get("ASSEMBLYAI_API_KEY")
if environ_key is None:
    pass
elif environ_key == "paste-your-key-here":
    environ_key = None
else:
    aai.settings.api_key = environ_key

# Remove existing temp files in case if improper shutdown
temp_files = [f for f in os.listdir() if f.startswith('tmp')]
for f in temp_files:
    os.remove(f)

# constant
YTDLP_FNAME = return_ytdlp_fname()

# Setting defaults for conditional rendering
input_key = None
f = None
entered = None
summary = None
question_submit = None
answer = ''

# Initializing state variables
state_strings = ['summary', 'entered', 'transcript']
for s in state_strings:
    if s not in st.session_state:
        st.session_state[s] = None

def set_aai_key():
    """ Callback to change set AAI API key when the key is input in the text area """
    aai.settings.api_key = st.session_state.input_aai_key

# MAIN APPLICATION CONTENT

"# Lecture Summarizer"
"Use this application to **automatically summarize a virtual lecture** and **ask questions** about the lesson material."
"Learn how to build this app [here](https://www.assemblyai.com/blog/build-an-interactive-lecture-summarization-app/)."

with st.expander("Processing time"):
    "The time to process a file is 15-30% of the file's duration, so an hour-long lecture will take several minutes to process."
    "If a YouTube link is used, additional time will be required to extract the file."

st.divider()

if not environ_key:
    "## API Key"
    """
To get started, paste your AssemblyAI API key in the below box.
If you don't have an API key, you can get one [here](https://www.assemblyai.com/dashboard/signup). You will need to set up billing in order to use this application since it uses [LeMUR](https://www.assemblyai.com/blog/lemur/).

You can copy your API key by pressing the `Copy token` button on the right hand side of your [Dashboard](https://www.assemblyai.com/app).
    """
    input_key = st.text_input(
        "API Key",
        placeholder="Enter your AssemblyAI API key here",
        type="password",
        on_change=set_aai_key,
        key='input_aai_key'
        )

    st.warning("Note: You can avoid this section by setting the `ASSEMBLYAI_API_KEY` environment variable, either through the terminal or the `.env` file.", icon="🗒️")

if input_key or environ_key:
    "## Lecture"
    """
    Enter the lecture you would like to summarize below. You can use a local file on your computer, a remote file that is publicly-available online, or a YouTube video.
    """

    # File type options
    ftype = st.radio("File type", ('Local file', 'Remote file', 'YouTube link'))

    if ftype == 'Local file':
        # Store the uploaded file in a temporary file
        f = st.file_uploader("File")
        if f:
            uploaded_ftype = f.name.split('.')[-1]
            temp_fname = f"tmp.{uploaded_ftype}"
            with open(temp_fname, 'wb') as fl:
                fl.write(f.read())
            f = temp_fname
    elif ftype == 'Remote file':
        f = st.text_input("Link", 
                          value="https://storage.googleapis.com/aai-web-samples/cs50p-unit-tests.mp3",
                          placeholder="Public link to the file"
                          )
    elif ftype == 'YouTube link':
        f = st.text_input("Link",
                          value="https://www.youtube.com/watch?v=tIrcxwLqzjQ",
                          placeholder="YouTube link"
                          )

    value = "" if ftype == "Local file" else "A lesson from Harvard's CS50P course. The lesson is about Unit Testing in Python."
    placeholder = "Contextualizing information about the file (optional)"
    context = st.text_input("Context", value=value, placeholder=placeholder)
     
if f:
    entered = st.button("Submit")
    if entered:
              
        transcript = get_transcript(f, ftype)
        if ftype == "Local file":
            os.remove(f)
        elif ftype == "YouTube link":
            os.remove(YTDLP_FNAME)  # remove file bc youtube DL will not work if there already exists file with that name

        st.session_state['transcript'] = transcript


        params = {
            'answer_format': "**<part of the lesson>**\n<list of important points in that part>",
            'max_output_size': 4000
        }
        if context: params['context'] = context
        
        with st.spinner("Generating summary..."):
            try:
                summary = transcript.lemur.summarize(**params)
                st.session_state['summary'] = summary.response.strip().split('\n')
                st.session_state['entered'] = True
                print('session summary: ', st.session_state['summary'])
            except aai.types.LemurError as e:
               st.write(f'Error: {str(e)}')
               st.session_state['entered'] = False

if st.session_state['entered']:
    "## Results"
    
    if st.session_state['summary']:
        for i in st.session_state['summary']:
            st.markdown(i)


if st.session_state['summary']:
    "# Questions"
    "Ask a question about the lesson below:"
    
    question = st.text_input("Question",
                              placeholder="What is the point of using Pytest?",
                              )
    
    question_asked = st.button("Submit", key='question_asked')
    if question_asked:
        with st.spinner('Asking question...'):
            answer = ask_question(st.session_state['transcript'], question)
    answer
    
