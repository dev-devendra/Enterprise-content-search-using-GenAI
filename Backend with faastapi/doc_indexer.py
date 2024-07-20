from queue import Queue
from threading import Thread, Event
from sys import stdout, stderr
from time import sleep
from langchain import document_loaders
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores.faiss import FAISS

#load the model to create embeddings (for CPU only)
model_name = "sentence-transformers/all-mpnet-base-v2"
model_kwargs = {'device': 'cpu'}
hf = HuggingFaceEmbeddings(cache_folder='./models/',model_name=model_name,model_kwargs=model_kwargs)

#initialize a global search index
search_index = None
#local db storage location
local_vdb_name = './db/enterprise_search_vdb'
#load the vector index if it exists
try:
    search_index = FAISS.load_local(local_vdb_name,hf)
except:
    pass

#create index from document content
def create_index(chunks):
    texts = [doc.page_content for doc in chunks]
    metadatas = [doc.metadata for doc in chunks]
    return FAISS.from_texts(texts, hf, metadatas=metadatas)

#break document content into chunks
def chunk_content(pages):
    chunks = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=256,chunk_overlap=32)
    for chunk in splitter.split_documents(pages):
        chunks.append(chunk)
    return chunks

#extract PDF content
def index_pdf(fname):
    ldr = document_loaders.PyPDFLoader(fname)
    pages = ldr.load()
    return chunk_content(pages)

#extract text content
def index_text(fname):
    ldr = document_loaders.TextLoader(fname)
    pages = ldr.load()
    return chunk_content(pages)

#dummy method to index MS WORD docs
#My current langchain version does not have MS WORD content extractor 
def index_msword(fname):
    return None

#index powerpoint content
def index_ppt(fname):
    ldr = document_loaders.UnstructuredPowerPointLoader(fname)
    pages = ldr.load()
    return chunk_content(pages)

#extract similar documents
def similarity_search(query):
    global search_index
    if search_index is None:
        return None
    return search_index.similarity_search(query)

#worker thread
def index_doc(doc_path, logger):
    global search_index
    logger.info("Processing - "+doc_path)
    try:
        filepath = doc_path.lower()
        if filepath.endswith(".pdf"):
            chunks = index_pdf(doc_path)
        elif filepath.endswith(".txt"):
            chunks = index_text(doc_path)
        elif filepath.endswith(".doc") or filepath.endswith(".docx"):
            chunks = index_msword(doc_path)
        elif filepath.endswith(".ppt") or filepath.endswith(".pptx"):
            chunks = index_ppt(doc_path)
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
