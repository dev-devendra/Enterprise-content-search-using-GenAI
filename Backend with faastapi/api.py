from fastapi import FastAPI
from fastapi import File, UploadFile
import requests
from bs4 import BeautifulSoup
import hashlib
from doc_indexer import Worker
from config import config
from langchain.llms import GPT4All
from langchain.callbacks.base import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from doc_indexer import similarity_search
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains.question_answering import load_qa_chain

#loading the model for q&a
gpt4all_path = './models/gpt4all-converted.bin'
# Calback manager for handling the calls with  the model
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
llm = GPT4All(model=gpt4all_path, callback_manager=callback_manager, verbose=True)
#creating logger instance etc.
cfg = config()
#Asynchronous handling of api calls for indexing
worker_instance = Worker()
#launch API server
app = FastAPI()

#dummy uri
@app.get("/")
def index():
    return {
        "message": "Make a post request to /ask to ask questions"
    }

#for chat (POST the query)
@app.post("/ask")
def ask(query: str):
    try:
        cfg.logger.info(f"The query is [{query}]")
        #extract documents similar to the query
        docs = similarity_search(query)
        #handle a null return
        if docs is None:
            return {
                "response": f"Query - [{query}]. Cannot respond as document index is missing"
            }
        else:
            #create the chain and run the query (takes time for the run call to return results)
            #chain = load_qa_with_sources_chain(llm, chain_type="stuff")
            #resp = chain.run({"input_documents": docs, "question": query}, return_only_outputs=True)
            chain = load_qa_chain(llm, chain_type="stuff")
            resp = chain.run(input_documents=docs, question=query).encode()
            cfg.logger.info(f"Query:[{query}], Response:[{resp}]")
            return {
                "response": resp
            }
    except Exception as e:
        return {
            "response": "Exception while processing query: "+str(e)
        }

#API to receive a document for indexing
@app.post("/index_doc")
def index_doc(file:UploadFile=File(...)):
    try:
        fname = "./data/"+file.filename
        with open(fname, 'wb') as f:
            while contents := file.file.read(1024 * 1024):
                f.write(contents)
        #enque for indexing
        worker_instance.enqueue((fname, cfg.logger))
    except Exception as e:
        return {"message": "There was an exception uploading the file {e}}"}
    finally:
        file.file.close()

    return {"message": f"Successfully uploaded {file.filename}"}

#API to receive a URL and extract it's content
@app.post("/index_webpage")
def index_webpage(pageurl: str):
    content=""
    try:
        #fetch the webpage content
        response = requests.get(pageurl)
        if response.status_code != 200:
            return {"message": "URL fetch unsuccessful - {response.status_code}}"}
        soup = BeautifulSoup(response.text,'html.parser')
        content = soup.get_text()
        #use the url hash as the file name
        m = hashlib.sha256()
        m.update(pageurl.encode('utf-8'))
        hd = m.hexdigest()
        fname = "./data/"+hd+".web.txt"
        with open(fname, "wb") as f:
            f.write(content.encode())
        #enque for indexing
        worker_instance.enqueue((fname, cfg.logger))
    except Exception as e:
        return {"message": "There was an exception uploading the file {e}}"}
    finally:
        return {"message": f"Successfully retrieved webpage content"}
