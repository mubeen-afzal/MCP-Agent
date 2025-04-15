# 🤖 MCP Agent: AI-Powered System Assistan

Welcome to the **MCP Agent**. Nn AI assistant built using LangChain and LangGraph, designed to interact with your system through MCP tools. This agent can provide system information, read file contents, fetch weather updates, and more.

---

## 🚀 Features

- \*_🗓️ System Date & Time_: Retrieve the current system date and time.
- \*_📄 File Reader_: Read contents of `.txt` files by providing the full file path.
- \*_☁️ Weather Updates_: Get real-time weather information for any city.
- **🧠 Session Memory**: Maintains chat history within a session, with the ability to reset.

---

## 🛠️ Installation Guide

Follow these steps to set up the MCP Agent:

### 1. Install Olama

Download and install Ollama from the official website


```bash
https://ollama.com
```


### 2. Pull the Desired Mdel

Use Ollama to pull the model you wish to use. For example:


```bash
ollama pull llama3.2
```


### 3. Clone the Reposiory

Clone the MCP Agent repository from GitHub:

```bash
git clone https://github.com/mubeen-afzal/MCP-Agent
cd MCP-Agent
```


### 4. Install Dependenies

Install the required Python package:

```bash
pip install -r requirements.tx
```


### 5. Configure the Aent

Update the configuration file with the following deails:

- **MCP Server Path**: Provide the full path to your `mcp_server.py` file.
- **Ollama Model Name**: Specify the name of the model you pulled (e.g., `llama3.2`).

### 6. Set Up Weather APIKey

Obtain an API key from [WeatherAPI](https://www.weatherapi.com/) and add it to the `mcp_server.py` file:


````python
WEATHER_API = "your_api_key_here"
``

Alternatively, create a `.env` file in the project root an add:


```bash
WEATHER_API=your_api_key_here
````


### 7. Run the Aent

Start the MCP Agent by typing:


````bash
python mcp_client.py
``

Open your browser and navigae to:

```bash
http://127.0.0.1:786
``

Begin interacting with your AI-powered system assitant!

---

## 💡 Usage Exaples

You can ask the MCP Agnt to:

- "What's the current system-time?"
- "What's today's date?"
- "What's the weather like in Islamabad?"
- "Read the contents of `C:\Users\YourName\Documents\notestxt`."

---

## ⚠️ ImportantNote

Currently, virtual environments are not supported. If you choose to use one, ensure you add the activation commands inside the `mcp_client.py` file at line 38 within the `StdioServerParamters`.

---

Feel free to explore and enhance the MCP Agent to suit your needs. Happy coding!
````
