# test_conversation.py

from conversation_bot import conversation_chain
from langchain.memory import ConversationBufferMemory

def test_happy_path_memory():
    """
    Tests if the memory correctly stores the happy path conversation.
    We check the memory buffer directly, which is more reliable than
    checking the LLM's non-deterministic final output.
    """
    # Use the conversation_chain's own memory for a clean test
    test_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_chain.memory = test_memory

    # Turn 1
    q1 = "Is there an outlet in Petaling Jaya?"
    conversation_chain.predict(question=q1)

    # Turn 2
    q2 = "SS 2, whats the opening time?"
    conversation_chain.predict(question=q2)

    # Assert that the key information from the user was stored in memory
    # The memory stores a list of messages. [0] is the first user message,
    # [2] is the second user message.
    assert "petaling jaya" in test_memory.chat_memory.messages[0].content.lower()
    assert "ss 2" in test_memory.chat_memory.messages[2].content.lower()


def test_interrupted_path_memory():
    """
    Tests if the memory correctly stores the conversation despite an interruption.
    """
    # Use the conversation_chain's own memory for a clean test
    test_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_chain.memory = test_memory

    # Run the full conversation
    conversation_chain.predict(question="Is there an outlet in Petaling Jaya?")
    conversation_chain.predict(question="By the way, what is the capital of Malaysia?")
    conversation_chain.predict(question="Ok, back to the SS 2 outlet, what time does it open?")

    # Assert that the final, critical question was stored in memory correctly.
    # The last user message is at index 4 in the list of messages.
    final_question = test_memory.chat_memory.messages[4].content
    assert "ss 2" in final_question.lower()
    assert "open" in final_question.lower()
