### Mindhive AI Chatbot Engineer Assessment Submission
This repository contains my submission for the Mindhive AI Chatbot Engineer technical assessment. The project is a multi-tool agent capable of holding conversations, performing calculations, and querying custom APIs for information about ZUS Coffee products and outlets.

Hosted Demo URL: https://mindhive-chatbot.vercel.app

### Architecture Overview
This project is built using a Python-based, code-first approach.
* Core Framework: LangChain is used for its robust agent framework, memory modules, and abstractions for tools, chains, and RAG/Text2SQL pipelines.
* Agent & LLM: The chatbot is an "OpenAITools" style agent powered by Google's gemini-1.5-flash-latest model, chosen for its strong reasoning capabilities and generous free tier.
* Custom API: A FastAPI server provides two custom endpoints:
- /outlets: A Text2SQL endpoint connected to a local SQLite database for outlet information. SQLite was chosen for its simplicity and serverless nature, which is ideal for this assessment.
- /products: A RAG endpoint using a FAISS vector store to provide information on ZUS Coffee drinkware. FAISS was chosen for its efficiency and ability to run locally.
* Key Trade-off: For this project, product and outlet data were hardcoded or added via a simple script rather than a live web scraper. This was a deliberate choice to ensure the system's reliability and robustness against frequent changes in the source website's HTML structure, focusing the project on the core AI engineering tasks rather than web scraping maintenance.

### Setup and Run Instructions
1. Clone the repository:
git clone https://github.com/myaghmaei/mindhive-chatbot.git
cd mindhive-chatbot

2. Create and activate the environment:
conda create --name mindhive-chatbot python=3.10
conda activate mindhive-chatbot

3. Install dependencies:
A requirements.txt file is included in the repository.
pip install -r requirements.txt

4. Set up environment variables:
- Create a .env file in the root directory.
- Add your Google API key: GOOGLE_API_KEY="your-key-here"

5. Initialize the database and vector store:
- Run the database creation script once:
  python create_db.py
- Run the product ingestion script once:
  python ingest_products.py
6. Run the system: You will need two terminals.
- In Terminal 1, run the API server:
  uvicorn api_server:app --reload
- In Terminal 2, run the agent:
  python agent_bot.py


### Deliverables & Transcripts
# Part 1: Sequential Conversation
The bot uses LangChain's "ConversationBufferMemory" to retain context across turns. Automated tests were created to validate this functionality for both happy and interrupted paths. The tests directly inspect the memory buffer to confirm that user inputs are stored correctly.

Test Result:

============================= test session starts ==============================
platform win32 -- Python 3.10.13, pytest-8.2.0, pluggy-1.5.0
rootdir: C:\Users\MOHSEN-PC\Desktop\Work Doc\mindhive-chatbot
collected 2 items

test_conversation.py ..                                                  [100%]

============================== 2 passed in 6.61s ===============================

# Part 2: Agentic Planning
Our chatbot uses a LangChain "Tools Agent" to decide its next action. The core logic follows a ReAct (Reason and Act) framework, which serves as the planner/controller loop.
1. Intent Parsing: When a user sends a message (e.g., "what is (100 - 50) / 2?"), the input is passed to the agent. The agent's LLM analyzes the user's intent by comparing it against the descriptions of the available tools.
2. Action Selection: Based on the parsed intent, the agent selects the appropriate tool (e.g., the calculator tool). If no tool is needed, it uses its conversational ability to respond directly.
3. Execution and Observation: The AgentExecutor runs the selected action, receives the result, and feeds this observation back to the agent to generate the final, user-facing response.

# Part 3: Tool Calling (Calculator)
A calculator tool was integrated to handle mathematical queries. The tool uses the numexpr library for safe evaluation and includes robust error handling.

Success Transcript:
You: what is (100 - 50) / 2?

> Entering new AgentExecutor chain...
Invoking: `calculator` with `{'expression': '(100 - 50) / 2'}`

The result of the expression '(100 - 50) / 2' is 25.0.
25.0

> Finished chain.
Agent: 25.0

Graceful Failure Transcript:
> You: what is apple + orange?

> Entering new AgentExecutor chain...
Invoking: `calculator` with `{'expression': 'apple + orange'}`

Sorry, I couldn't calculate that. The expression 'apple + orange' is not a valid mathematical formula. Please provide a standard mathematical expression (e.g., '5 * (2 + 3)').
I'm sorry, but I can't add 'apple' and 'orange' as it's not a valid mathematical calculation.

> Finished chain.
Agent: I'm sorry, but I can't add 'apple' and 'orange' as it's not a valid mathematical calculation.


# Part 4: Custom API & RAG Integration
A FastAPI server was built with two custom endpoints.
API Specification:
- GET /outlets?query=<nl_query>: Answers questions about ZUS Coffee outlet locations by converting natural language to SQL.
- GET /products?query=<user_question>: Answers questions about ZUS Coffee drinkware products using a RAG pipeline.

Integration Transcripts:
Outlets API Success:

You: Are there any outlets in kuala lumpur?

> Entering new AgentExecutor chain...
Invoking: `query_outlets_api` with `{'query': 'Are there any outlets in Kuala Lumpur?'}`

[('ZUS Coffee - Bangsar Shopping Centre', 'Lot F-1, 1st Floor, Bangsar Shopping Centre, 285, Jalan Maarof, 59000 Kuala Lumpur', '9:00 AM - 9:00 PM'), ('ZUS Coffee - Pavilion KL', 'P1.11.00, Level 1, Pavilion KL, 168, Jalan Bukit Bintang, 55100 Kuala Lumpur', '10:00 AM - 10:00 PM'), ('ZUS Coffee - Mid Valley Megamall', 'LG-076, Lower Ground Floor, Mid Valley Megamall, Lingkaran Syed Putra, 59200 Kuala Lumpur', '10:00 AM - 10:00 PM')]
Yes, there are several ZUS Coffee outlets in Kuala Lumpur, including locations at Bangsar Shopping Centre, Pavilion KL, and Mid Valley Megamall.

> Finished chain.
Agent: Yes, there are several ZUS Coffee outlets in Kuala Lumpur, including locations at Bangsar Shopping Centre, Pavilion KL, and Mid Valley Megamall.

Products API Success:
> You: Tell me about the ZUS button tumbler

> Entering new AgentExecutor chain...
Invoking: `query_products_api` with `{'query': 'ZUS button tumbler'}`

Based on the provided context, the ZUS Button Tumbler has a price of RM79.90.
The ZUS Button Tumbler costs RM79.90.

> Finished chain.
Agent: The ZUS Button Tumbler costs RM79.90.

# Part 5: Unhappy Flows & Security
Error-Handling and Security Strategy
The chatbot is designed to be robust against common failures and malicious inputs through a multi-layered strategy:
- Missing Parameters: The core agent logic inherently handles ambiguous requests. When a user's query lacks the necessary information to use a tool, the agent is prompted to ask clarifying follow-up questions instead of calling the tool with invalid arguments.
- API Downtime: All tools that interact with external APIs are wrapped in try...except blocks. These blocks specifically catch network-related exceptions. If an API is down, the tool returns a clean error message to the agent, which then informs the user without crashing the system.
- Security (SQL Injection): The system has two layers of defense. The primary defense is the agent's base LLM, which is intelligent enough to recognize malicious patterns and refuse to call the tool. As a secondary defense, the Text2SQL API endpoint validates that any generated query is a read-only SELECT statement before execution, blocking any potentially destructive commands.

Unhappy Flow Transcripts

- Scenario 1: Missing Parameters

You: Calculate something for me

> Entering new AgentExecutor chain...
What would you like me to calculate? Please provide me with the expression.

> Finished chain.
Agent: What would you like me to calculate? Please provide me with the expression.

- Scenario 2: API Downtime

You: Tell me about the ZUS button tumbler

> Entering new AgentExecutor chain...
Invoking: `query_products_api` with `{'query': 'Tell me about the ZUS button tumbler'}`

Error connecting to the products API: HTTPConnectionPool(host='127.0.0.1', port=8000): ... No connection could be made because the target machine actively refused it...
I'm sorry, I cannot find any information about the ZUS button tumbler at this time. The system I'm using to access product information is currently unavailable.

> Finished chain.
Agent: I'm sorry, I cannot find any information about the ZUS button tumbler at this time. The system I'm using to access product information is currently unavailable.

- Scenario 3: Malicious Payload

You: Which outlet is named '; DROP TABLE outlets; --

> Entering new AgentExecutor chain...
That's not a valid outlet name. It looks like an attempt at an SQL injection attack. There are no outlets with that name.

> Finished chain.
Agent: That's not a valid outlet name. It looks like an attempt at an SQL injection attack. There are no outlets with that name.
