from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from fastapi import File, UploadFile
import requests
from bs4 import BeautifulSoup
import hashlib
from doc_indexer import Worker
from config import config
from doc_indexer import similarity_search, get_db_retriever
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
from fastapi.middleware.cors import CORSMiddleware
#from langchain.callbacks import get_openai_callback
from langchain.chains import OpenAIModerationChain
from doc_indexer import count_tokens
from stats import update_openapi_cost, update_user_feedback, get_stats, increment_query_count

#creating logger instance etc.
cfg = config()
#Asynchronous handling of api calls for indexing
worker_instance = Worker()
#launch API server
app = FastAPI()
origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
chat_history = []

#dummy uri
@app.get("/")
def index():
    return {
        "message": "Make a post request to /ask to ask questions"
    }

@app.get("/stats")
def getstats():
    return get_stats()

@app.post("/feedback")
def feedback(feedback: str):
    global stats
    if feedback == '1':
        update_user_feedback(True)
    else:
        update_user_feedback(False)
    return {'response':'OK'}

#for chat (POST the query)
@app.post("/clearchathist")
def clear_chat_history():
    global chat_history
    try:
        cfg.logger.info(f"Clear chat history")
        chat_history = []
        return {
            "response": "Chat history cleared"
        }
    except Exception as e:
        return {
            "response": "Exception while clearing chat history - "+str(e)
        }

#for chat (POST the query)
@app.post("/ask")
def ask(query: str):
    global chat_history
    try:
        cfg.logger.info(f"The query is [{query}]")
        increment_query_count()
        
        db_retriever = get_db_retriever()
        if db_retriever is None:
            return {
                "response": f"Query - [{query}]. Cannot respond as db retriever is missing"
            }
        moderation_chain = OpenAIModerationChain()
        resp = moderation_chain.run(query)
        if 'violates' in resp.lower():
            return {"response": "Query content violates our content moderation policy"}
        
        qa = ConversationalRetrievalChain.from_llm(OpenAI(temperature=0.1), db_retriever)
        result = qa({"question": query, "chat_history": chat_history})
        cfg.logger.info(f">>>>>>>>>>>>> {result}")
        if 'market' in query.lower():
            cfg.logger.info(f">>>>>>>>>>>>> 1")
            qa2 = load_qa_chain(OpenAI(temperature=0), chain_type="stuff")
            result2 = qa2.run(input_documents=[], question=query)
            result['answer'] = result2
        #chat_history.append((query, result['answer']))
        if len(chat_history) > 4:
            chat_history.pop(0)
        output_cost = (count_tokens(result['answer'])*0.002/1000) #$0.002 per 1K tokens
        input_cost = (2400*0.0015/1000)#count of tokens is an approximation. Cost is $0.0015 per 1K tokens
        update_openapi_cost(output_cost+input_cost)

        cfg.logger.info(f"Query:[{query}], Response:[{result['answer']}]")

        """
        with get_openai_callback as cb:
            cfg.logger.info(f"The token count is [{str(cb)}]")
        """
        return {            
            "response": result['answer']
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
    return JSONResponse(content="OK", status_code=200)
    #response = Response(content="OK", status_code=200)
    #return response

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
        return JSONResponse(content="ERROR", status_code=500)
        #return {"message": "There was an exception uploading the file {e}}"}
    finally:
        return JSONResponse(content="OK", status_code=200)
        #return {"message": f"Successfully retrieved webpage content"}
