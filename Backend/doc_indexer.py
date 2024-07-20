from queue import Queue
from threading import Thread, Event
from sys import stdout, stderr
from time import sleep
from langchain import document_loaders
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
import os
from langchain.embeddings import OpenAIEmbeddings
from transformers import GPT2TokenizerFast
from stats import update_openapi_cost

os.environ['OPENAI_API_KEY'] = "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"

#initialize a global search index
search_index = None
#local db storage location
local_vdb_name = './db/enterprise_search_vdb'

embeddings = OpenAIEmbeddings()

#load the vector index if it exists
try:
    search_index = FAISS.load_local(local_vdb_name,embeddings)
except:
    pass

tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text))

#create index from document content
def create_index(chunks):
    token_count = 0
    for chunk in chunks:
        token_count += count_tokens(chunk)
    update_openapi_cost(token_count*0.0001/1000)#$0.0001 per 1K tokens
    db = FAISS.from_documents(chunks, embeddings)
    return db

#break document content into chunks
def chunk_content(pages, logger):
    chunks = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=512,chunk_overlap=24)
    chunks = splitter.create_documents([pages])
    return chunks

#extract PDF content
def index_pdf(fname, logger):
    ldr = document_loaders.PyPDFLoader(fname)
    pages = ldr.load()
    content_list = [page.page_content for page in pages]
    content = ' '.join(content_list)
    return chunk_content(content, logger)

#extract text content
def index_text(fname, logger):
    ldr = document_loaders.TextLoader(fname)
    pages = ldr.load()
    content_list = [page.page_content for page in pages]
    content = ' '.join(content_list)
    return chunk_content(content, logger)

#dummy method to index MS WORD docs
#My current langchain version does not have MS WORD content extractor 
def index_msword(fname, logger):
    return None

#index powerpoint content
def index_ppt(fname, logger):
    ldr = document_loaders.UnstructuredPowerPointLoader(fname)
    pages = ldr.load()
    content_list = [page.page_content for page in pages]
    content = ' '.join(content_list)
    return chunk_content(content, logger)

#extract similar documents
def similarity_search(query):
    global search_index
    if search_index is None:
        return None
    return search_index.similarity_search(query)

def get_db_retriever():
    global search_index
    if search_index is None:
        return None
    return search_index.as_retriever()

#index csv content
def index_csv(fname, logger):
    ldr = document_loaders.CSVLoader(fname)
    pages = ldr.load()
    content_list = [page.page_content for page in pages]
    content = ' '.join(content_list)
    return chunk_content(content, logger)

#worker thread
def index_doc(doc_path, logger):
    global search_index
    logger.info("Processing - "+doc_path)
    chunks = None
    try:
        filepath = doc_path.lower()
        if filepath.endswith(".pdf"):
            chunks = index_pdf(doc_path, logger)
        elif filepath.endswith(".txt"):
            chunks = index_text(doc_path, logger)
        elif filepath.endswith(".doc") or filepath.endswith(".docx"):
            chunks = index_msword(doc_path, logger)
        elif filepath.endswith(".ppt") or filepath.endswith(".pptx"):
            chunks = index_ppt(doc_path, logger)
        elif filepath.endswith(".csv"):
            chunks = index_csv(doc_path, logger)
        else:
            logger.info("Unsupported document")
        if chunks != None and len(chunks) > 0:
            index = create_index(chunks)
            if search_index is None:
                search_index = index
            else:
                search_index.merge_from(index)
            search_index.save_local(local_vdb_name)
        else:
            logger.info("No chunks to process")
    except Exception as e:
        logger.info("Exception - "+str(e))

#helper class for workers
class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self):
        Thread.__init__(self)
        self.abort = Event()
        self.queue = Queue()
        self.daemon = True
        self.start()
  
    """Add a task to the queue"""
    def abort(self):
        self.abort.set()

    """Add a task to the queue"""
    def enqueue(self, fname):
        self.queue.put((fname))

    """Thread work loop calling the function with the params"""
    def run(self):
        #keep running until told to abort
        while not self.abort.is_set():
            try:
                #get a task and raise immediately if none available
                fname, logger = self.queue.get()
            except:
                continue

            try:
                #the function may raise
                index_doc(fname, logger)
            except Exception as e:
                logger.info("Exception while calling worker function - "+str(e))
            finally:
                #task complete no matter what happened
                self.queue.task_done()
