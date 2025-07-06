\\\\\\\\\\\\\ Deliverables & Transcripts \\\\\\\\\\\\\\

########### Part 1: Sequential Conversation
The bot uses LangChain's ConversationBufferMemory to retain context across turns. Automated tests were created to validate this functionality for both happy and interrupted paths. The tests directly inspect the memory buffer to confirm that user inputs are stored correctly.

Test Result:

============================= test session starts ==============================
platform win32 -- Python 3.10.13, pytest-8.2.0, pluggy-1.5.0
rootdir: C:\Users\MOHSEN-PC\Desktop\Work Doc\mindhive-chatbot
collected 2 items

test_conversation.py ..                                                  [100%]

============================== 2 passed in 6.61s ===============================
 
########### Part 2: Agentic Planning ########### 

Our chatbot uses a LangChain "Tools Agent" to decide its next action. The core logic follows a ReAct (Reason and Act) framework, which serves as the planner/controller loop.

Intent Parsing: When a user sends a message (e.g., "what is (100 - 50) / 2?"), the input is passed to the agent. The agent's LLM analyzes the user's intent by comparing it against the descriptions of the available tools.

Action Selection: Based on the parsed intent, the agent selects the appropriate tool (e.g., the calculator tool). If no tool is needed, it uses its conversational ability to respond directly.

Execution and Observation: The AgentExecutor runs the selected action, receives the result, and feeds this observation back to the agent to generate the final, user-facing response.

########### Part 3: Tool Calling (Calculator) ########### 

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

You: what is apple + orange?

> Entering new AgentExecutor chain...
Invoking: `calculator` with `{'expression': 'apple + orange'}`

Sorry, I couldn't calculate that. The expression 'apple + orange' is not a valid mathematical formula. Please provide a standard mathematical expression (e.g., '5 * (2 + 3)').
I'm sorry, but I can't add 'apple' and 'orange' as it's not a valid mathematical calculation.

> Finished chain.
Agent: I'm sorry, but I can't add 'apple' and 'orange' as it's not a valid mathematical calculation.

########### Part 4: Custom API & RAG Integration ########### 

A FastAPI server was built with two custom endpoints.

API Specification:

GET /outlets?query=<nl_query>: Answers questions about ZUS Coffee outlet locations by converting natural language to SQL.

GET /products?query=<user_question>: Answers questions about ZUS Coffee drinkware products using a RAG pipeline.

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

You: Tell me about the ZUS button tumbler

> Entering new AgentExecutor chain...
Invoking: `query_products_api` with `{'query': 'ZUS button tumbler'}`

Based on the provided context, the ZUS Button Tumbler has a price of RM79.90.
The ZUS Button Tumbler costs RM79.90.

> Finished chain.
Agent: The ZUS Button Tumbler costs RM79.90.

########### Part 5: Unhappy Flows & Security ########### 

Error-Handling and Security Strategy
The chatbot is designed to be robust against common failures and malicious inputs through a multi-layered strategy:

Missing Parameters: The core agent logic inherently handles ambiguous requests. When a user's query lacks the necessary information to use a tool, the agent is prompted to ask clarifying follow-up questions instead of calling the tool with invalid arguments.

API Downtime: All tools that interact with external APIs are wrapped in try...except blocks. These blocks specifically catch network-related exceptions. If an API is down, the tool returns a clean error message to the agent, which then informs the user without crashing the system.

Security (SQL Injection): The system has two layers of defense. The primary defense is the agent's base LLM, which is intelligent enough to recognize malicious patterns and refuse to call the tool. As a secondary defense, the Text2SQL API endpoint validates that any generated query is a read-only SELECT statement before execution, blocking any potentially destructive commands.

Unhappy Flow Transcripts
Scenario 1: Missing Parameters

You: Calculate something for me

> Entering new AgentExecutor chain...
What would you like me to calculate? Please provide me with the expression.

> Finished chain.
Agent: What would you like me to calculate? Please provide me with the expression.

Scenario 2: API Downtime

You: Tell me about the ZUS button tumbler

> Entering new AgentExecutor chain...
Invoking: `query_products_api` with `{'query': 'Tell me about the ZUS button tumbler'}`

Error connecting to the products API: HTTPConnectionPool(host='127.0.0.1', port=8000): ... No connection could be made because the target machine actively refused it...
I'm sorry, I cannot find any information about the ZUS button tumbler at this time. The system I'm using to access product information is currently unavailable.

> Finished chain.
Agent: I'm sorry, I cannot find any information about the ZUS button tumbler at this time. The system I'm using to access product information is currently unavailable.

Scenario 3: Malicious Payload

You: Which outlet is named '; DROP TABLE outlets; --

> Entering new AgentExecutor chain...
That's not a valid outlet name. It looks like an attempt at an SQL injection attack. There are no outlets with that name.

> Finished chain.
Agent: That's not a valid outlet name. It looks like an attempt at an SQL injection attack. There are no outlets with that name.
