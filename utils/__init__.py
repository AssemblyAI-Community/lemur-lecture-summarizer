import streamlit as st
import assemblyai as aai
from yt_dlp import YoutubeDL

YTDLP_FNAME = 'tmp.webm'

# For some reason directly importing the constant did not work
def return_ytdlp_fname():
    return YTDLP_FNAME

def get_transcript(f, ftype):
    transcriber = aai.Transcriber()

    print("entered")
    print(ftype)
    if ftype == 'YouTube link':
        with st.spinner('Downloading video...'):
            ydl_opts = {'outtmpl': YTDLP_FNAME}
            print("downloading")
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([f])
                f = YTDLP_FNAME
    print("returning", f)
    with st.spinner('Transcribing file...'):
        transcript = transcriber.transcribe(f)
    if transcript.error:
        raise TranscriptionException(transcript.error)
    return transcript

def ask_question(transcript, question):
    questions = [
        aai.LemurQuestion(question=question,)
    ]

    result = transcript.lemur.question(questions)

    if transcript.error:
        raise QuestionException(result.error)

    return result.response[0].answer


class TranscriptionException(Exception):
    pass

class QuestionException(Exception):
    pass