import json
import asyncio
import threading
import gradio as gr

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

# Global container to hold our agent and related objects.
agent_container = {}

# Create a dedicated asyncio event loop that will run in a separate thread.
global_loop = asyncio.new_event_loop()

with open("config.json","r") as file:
    config_data = json.load(file)

def start_loop(loop):
    """Starts the passed event loop in this thread."""
    asyncio.set_event_loop(loop)
    loop.run_forever()

# Start the global event loop in a background thread.
loop_thread = threading.Thread(target=start_loop, args=(global_loop,), daemon=True)
loop_thread.start()

async def setup_agent():
    """
    Sets up the MCP session, loads MCP tools, creates an agent
    using ChatOllama with a conversation memory, and stores the objects.
    """
    # Define your MCP tools subprocess parameters.
    server_params = StdioServerParameters(
        command="python",
        args=[config_data["server_path"]]  # adjust this path as needed
    )
    # Start the MCP tool process and enter its async context.
    stdio = stdio_client(server_params)
    read, write = await stdio.__aenter__()
    # Create a ClientSession for the MCP tools.
    session = await ClientSession(read, write).__aenter__()
    await session.initialize()
    # Load tools available from your MCP setup.
    tools = await load_mcp_tools(session)
    
    # Setup conversation memory – here using LangChain's ConversationBufferMemory.
    memory = ConversationBufferMemory(return_messages=True)
    
    # Setup the language model via Ollama (adjust model name as needed).
    model = ChatOllama(model=config_data["ai_model"])
    
    # Create a React-style LangGraph agent with the above components.
    agent = create_react_agent(model, tools)
    
    # Save them into our global container for later use.
    agent_container["agent"] = agent
    agent_container["session"] = session
    agent_container["stdio"] = stdio
    agent_container["memory"] = memory
    agent_container["conversation_history"] = []

# Schedule the agent setup in the background event loop and wait for it to complete.
setup_future = asyncio.run_coroutine_threadsafe(setup_agent(), global_loop)
setup_future.result()  # blocks until the agent is ready

async def cleanup_agent():
    """Clean up MCP session and resources."""
    if "session" in agent_container:
        await agent_container["session"].__aexit__(None, None, None)
    if "stdio" in agent_container:
        await agent_container["stdio"].__aexit__(None, None, None)
    
    # Clear the agent container to reset memory
    agent_container.clear()

async def invoke_agent(user_message: str) -> str:
    """
    Invokes the LangGraph agent asynchronously with the provided message.
    Returns the agent's final response text.
    """
    agent = agent_container.get("agent")
    if not agent:
        return "Agent is not ready yet."
    
    # Get conversation history
    conversation_history = agent_container.get("conversation_history", [])
    
    # Create message dictionary with history included
    messages = conversation_history.copy()
    messages.append(HumanMessage(content=user_message))
    
    # Invoke agent with conversation history
    msg = {"messages": messages}
    response = await agent.ainvoke(msg)
    
    # Get the last message (agent's response)
    agent_response = response["messages"][-1].content
    
    # Update conversation history
    conversation_history.append(HumanMessage(content=user_message))
    conversation_history.append(AIMessage(content=agent_response))
    agent_container["conversation_history"] = conversation_history
    
    return agent_response

def sync_invoke(user_message: str) -> str:
    """
    A synchronous wrapper for invoking the async agent.
    It uses the global event loop to run the coroutine and waits for the result.
    """
    future = asyncio.run_coroutine_threadsafe(invoke_agent(user_message), global_loop)
    return future.result()

def user_send(user_input, chat_history):
    response = sync_invoke(user_input)
    chat_history = chat_history or []
    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "assistant", "content": response})
    return "", chat_history

def reset_session():
    """Reset the conversation history and memory."""
    if "conversation_history" in agent_container:
        agent_container["conversation_history"] = []
    return "", []

# Build the Gradio interface.
with gr.Blocks() as demo:
    # Use the "messages" type so that Gradio uses a dict structure for messages.
    chatbot = gr.Chatbot(type="messages")
    msg = gr.Textbox(placeholder="Ask me anything...", label="Your Message")
    
    # Add a reset button to clear the conversation
    reset_btn = gr.Button("Reset Conversation")
    reset_btn.click(reset_session, outputs=[msg, chatbot])
    
    # Connect the textbox submission to our user_send function.
    msg.submit(user_send, [msg, chatbot], [msg, chatbot])
    
    # Handle cleanup when the session closes
    demo.close(lambda: asyncio.run_coroutine_threadsafe(cleanup_agent(), global_loop))

if __name__ == "__main__":
    try:
        demo.launch()
    finally:
        # Make sure to run cleanup when the application is shut down
        cleanup_future = asyncio.run_coroutine_threadsafe(cleanup_agent(), global_loop)
        try:
            cleanup_future.result(timeout=5)
        except:
            pass
        # Stop the event loop
        global_loop.call_soon_threadsafe(global_loop.stop)
        loop_thread.join(timeout=5)  # Wait for the loop thread to finish