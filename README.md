# Instructions

## How to Run

Not mandatory but I ran all of these in virtual environments to handle the wave of packages. All you need to do to create a virtual environment is

1. 
    ```bash
    python -m venv <path_to_environment> 
    ```

2.
    ```bash
    <venv_path>\Scripts\activate
    ```

My folder was called .venv, so calling it while in the same directory was just

```bash
.\.venv\Scripts\activate
```

### Task 1 - Required Core: The Robot Driver

To run the main automation script:

**Prerequisites:**

1. Install required dependencies from within the corresponding folder:

    ```bash
    pip install -r requirements.txt
    ```

2. Install Playwright browsers if you haven't already:
    ```bash
    playwright install
    ```

Run the actual file

```bash
cd "task 1"
python task_1.py
```

**What it does:**

As stated by the prompt, the program completes a fixed, single task on Amazon.com. In this case, we are looking to find any shirt under $5 and add it to the cart. The browser will be run in headed mode but that can be changed to run headless, and screenshots will be taken regardless as proof of the steps/end goal being achieved by the program.

### Task 2 - Optional Challenge 1: The AI Brain with MCP

To run the AI agent:

```bash
cd "task 2"
python agent2.py
```

To run the MCP server:

```bash
npx @playwright/mcp@latest --port <Your_Port_Number> 
```


**What it does:**

As stated by the prompt, we are now giving the AI agent access to the MCP context and tools so that the agent can decide what the next step should be in order to achieve the goal. We start the MCP server using the given command and give the agent the tools it can execute while trying to reach the goal. I noticed that the model would often respond with the tool call that was made, as well as the contents of the page it read after that tool call was made, so I decided that while the message history is important because the agent is stateless, we can just edit the long returns to just be placeholder messages so that not too many tokens were being used. Obviously if the agent needed to, as specified by the edited message, it could just read the page again if it needed context of what it needed to do next.

I was not sure originally of what the question had implied and had two approaches, one where I let the agent execute the commands automatically and one where I prompted the agent to return the command it would have ran so that I can run it in my program. The latter proved to be a bit less successful because I was using a rather large command map and to make sure it had full functionality, and also was having trouble with keeping the tokens down on more complicated tasks and providing it the MCP webpage context without letting it execute the tasks itself. The first was much more successful at this.

You will have to create your own .env file and provide your own google api key with the name 'GOOGLE_API_KEY'

### Task 3 - Optional Challenge 2: Making It Shareable

To run the script:

**Prerequisites:**

1. Install required dependencies from within the corresponding folder:

    ```bash
    pip install -r requirements.txt
    ```

2. Install Playwright browsers if you haven't already:
    ```bash
    playwright install
    ```

Run the actual file

```bash
uvicorn playwright_mcp:app --reload --port <Your_Port_Number>
```

The default port is 8000 if you don't specify

**What it does:**

The program runs similarly to task 1, the only difference now is that when you connect to the /playwright endpoint, the same playwright code and task that took place in task 1 will take place here. The only difference here is that the screenshots were
served as static files you could visit by heading to the /screenshots/<screenshot_name>.png. This is useful if not just running this locally and was instead hosted on an EC2 instance or made public with tunneling services or a reverse proxy. The server will by default run on http://127.0.0.1:8000/.