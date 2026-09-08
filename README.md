# AI Student Support Assistant

An AI-powered student support chatbot for answering questions about college regulations, syllabus, frequently asked questions, and notices. The assistant uses retrieval-augmented generation (RAG): documents are embedded with Ollama, stored in Pinecone, and retrieved by category before the local Ollama chat model writes an answer.

## Features

- Web chat interface built with Flask, HTML, CSS, and JavaScript
- Interactive command-line chat mode
- Category-aware retrieval for regulations, syllabus, FAQs, and notices
- Conversation history per session, held in memory
- Pinecone vector search with Ollama embeddings
- Quick actions for common student questions
- Document ingestion for `.txt`, `.pdf`, and `.md` files

## Architecture

1. The user sends a question through the web UI or CLI.
2. The LangChain agent selects the appropriate document-search tool.
3. Pinecone searches the matching namespace using `nomic-embed-text` embeddings.
4. Ollama generates a response using the retrieved college information.
5. The conversation is stored in the in-memory session history.

## Requirements

- Python 3.10 or newer
- [Ollama](https://ollama.com/) running locally
- Ollama models:
	- `qwen2.5:1.5b` for chat
	- `nomic-embed-text` for embeddings
- A Pinecone account and API key

Pull the Ollama models before starting the application:

```bash
ollama pull qwen2.5:1.5b
ollama pull nomic-embed-text
```

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```env
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=student-assistant
OLLAMA_MODEL=qwen2.5:1.5b
OLLAMA_BASE_URL=http://localhost:11434
```

The Pinecone index is created automatically when ingestion starts if it does not already exist. It uses cosine similarity, dimension `768`, and the AWS `us-east-1` serverless region.

## Load documents

The repository includes sample documents under `data/`. Ingest each category into its matching Pinecone namespace:

```bash
python ingest.py --source ./data/regulations --namespace regulation
python ingest.py --source ./data/syllabus --namespace syllabus
python ingest.py --source ./data/faqs --namespace faq
python ingest.py --source ./data/notices --namespace notice
```

You can also ingest a single supported file. Chunking defaults to 800 characters with 200 characters of overlap:

```bash
python ingest.py --source ./path/to/document.pdf --namespace notice
```

Use `--chunk-size` and `--chunk-overlap` to change those defaults.

## Run the application

### Web application

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in a browser.

### Command-line application

```bash
python main.py
```

CLI commands:

| Command | Action |
| --- | --- |
| `/clear` | Clear the current conversation history |
| `/history` | Display recent conversation history |
| `/help` | Display available commands |
| `/quit` | Exit the application |

## API

### Send a message

`POST /api/chat`

Request:

```json
{
	"message": "What are the hostel fees?",
	"session_id": "student-123"
}
```

Response:

```json
{
	"response": "..."
}
```

### Get conversation history

`GET /api/history?session_id=student-123`

### Clear conversation history

`POST /api/clear`

```json
{
	"session_id": "student-123"
}
```

## Project structure

```text
agent.py             LangChain agent and system prompt
app.py               Flask web application and REST API
config.py            Environment-based configuration
ingest.py            Document loading, chunking, and Pinecone ingestion
main.py              Command-line chat application
memory.py            In-memory conversation history
tools.py             Category-specific document search tools
vectorstore.py       Ollama embeddings and Pinecone access
data/                Source documents grouped by category
templates/           Flask HTML templates
static/              Frontend CSS and JavaScript
```

## Notes

- Conversation history is stored in process memory and is lost when the application restarts.
- The default Flask server runs with `debug=True`; use a production WSGI server before deploying publicly.
- Keep `.env` out of version control and replace any exposed credentials before sharing or deploying the project.
"# AI-student-support-assistant" 
