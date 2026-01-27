# langchain-qwq · PyPI

# langchain-qwq 0.3.4

pip install langchain-qwq Copy PIP instructions

[Latest version](/project/langchain-qwq/)

Released: Jan 9, 2026

An integration package connecting Qwen 3, QwQ and LangChain

### Navigation

### Verified details

_These details have been [verified by PyPI](https://docs.pypi.org/project_metadata/#verified-details)_

###### Maintainers

 [![Avatar for yigit353 from gravatar.com](https://pypi-camo.freetls.fastly.net/d3d9ce762cd82c0cb95051c7ac0cf468427f73cc/68747470733a2f2f7365637572652e67726176617461722e636f6d2f6176617461722f34306133356430313331333163343063343833326230336330613336616430613f73697a653d3530 "Avatar for yigit353 from gravatar.com")yigit353](/user/yigit353/)

###### Meta

-   **Author:** [Yiğit Bekir Kaya, PhD](mailto:yigit353@gmail.com)

### Unverified details

_These details have **not** been verified by PyPI_

###### Project links

-   [Homepage](https://github.com/yigit353/langchain-qwq)
-   [Release Notes](https://github.com/langchain-ai/langchain/releases?q=tag%3A%22qwq%3D%3D0%22&expanded=true)
-   [Repository](https://github.com/yigit353/langchain-qwq)
-   [Source Code](https://github.com/yigit353/langchain-qwq/tree/main/langchain_qwq)

###### Meta

-   **License:** MIT License (MIT)
-   **Author:** Yiğit Bekir Kaya, PhD
-   **Requires:** Python <4.0, >=3.10

###### Classifiers

-   **License**
    -   [OSI Approved :: MIT License](/search/?c=License+%3A%3A+OSI+Approved+%3A%3A+MIT+License)
-   **Programming Language**
    -   [Python :: 3](/search/?c=Programming+Language+%3A%3A+Python+%3A%3A+3)
    -   [Python :: 3.10](/search/?c=Programming+Language+%3A%3A+Python+%3A%3A+3.10)
    -   [Python :: 3.11](/search/?c=Programming+Language+%3A%3A+Python+%3A%3A+3.11)
    -   [Python :: 3.12](/search/?c=Programming+Language+%3A%3A+Python+%3A%3A+3.12)
    -   [Python :: 3.13](/search/?c=Programming+Language+%3A%3A+Python+%3A%3A+3.13)

[Report project as malware](https://pypi.org/project/langchain-qwq/submit-malware-report/)

## Project description

# langchain-qwq

This package provides seamless integration between LangChain and QwQ models as well as other Qwen series models from Alibaba Cloud BaiLian (via OpenAI-compatible API).

## Features

-   **QwQ Model Integration**: Full support for QwQ models with advanced reasoning capabilities
-   **Qwen3 Model Integration**: Comprehensive support for Qwen3 series models with hybrid reasoning modes
-   **Other Qwen Models**: Compatibility with Qwen-Max, Qwen2.5, and other Qwen series models
-   **Vision Models**: Native support for Qwen-VL series vision models
-   **Streaming Support**: Synchronous and asynchronous streaming capabilities
-   **Tool Calling**: Function calling with support for parallel execution
-   **Structured Output**: JSON mode and function calling for structured response generation
-   **Reasoning Access**: Direct access to internal model reasoning and thinking content

## Installation

To install the package:

pip install \-U langchain-qwq

If you want to install additional dependencies for development:

pip install \-U langchain-qwq\[test\]
pip install \-U langchain-qwq\[codespell\]
pip install \-U langchain-qwq\[lint\]
pip install \-U langchain-qwq\[typing\]

**Note**: The documentation notebooks in `docs/` can be viewed directly on GitHub or in VS Code without additional dependencies. To run them interactively, install Jupyter separately: `pip install jupyterlab`

## Environment Variables

Authentication and configuration are managed through the following environment variables:

-   `DASHSCOPE_API_KEY`: Your DashScope API key (required)
-   `DASHSCOPE_API_BASE`: Optional API base URL (defaults to `"https://dashscope-intl.aliyuncs.com/compatible-mode/v1"`)

> **Note**: Domestic Chinese users should configure `DASHSCOPE_API_BASE` to the domestic endpoint, as `langchain-qwq` defaults to the international Alibaba Cloud endpoint.

## ChatQwQ

The ChatQwQ class provides access to QwQ chat models with built-in reasoning capabilities.

### Basic Usage

from langchain\_qwq import ChatQwQ

model \= ChatQwQ(model\="qwq-plus")
response \= model.invoke("Hello, how are you?")
print(response.content)

### Accessing Reasoning Content

You can access the internal reasoning content of QwQ models via `additional_kwargs`:

response \= model.invoke("Hello")
content \= response.content
reasoning \= response.additional\_kwargs.get("reasoning\_content", "")
print(f"Response: {content}")
print(f"Reasoning: {reasoning}")

### Streaming

#### Sync Streaming

model \= ChatQwQ(model\="qwq-plus")

is\_first \= True
is\_end \= True

for msg in model.stream("Hello"):
    if hasattr(msg, 'additional\_kwargs') and "reasoning\_content" in msg.additional\_kwargs:
        if is\_first:
            print("Starting to think...")
            is\_first \= False
        print(msg.additional\_kwargs\["reasoning\_content"\], end\="", flush\=True)
    elif hasattr(msg, 'content') and msg.content:
        if is\_end:
            print("\\nThinking ended")
            is\_end \= False
        print(msg.content, end\="", flush\=True)

#### Async Streaming

is\_first \= True
is\_end \= True

async for msg in model.astream("Hello"):
    if hasattr(msg, 'additional\_kwargs') and "reasoning\_content" in msg.additional\_kwargs:
        if is\_first:
            print("Starting to think...")
            is\_first \= False
        print(msg.additional\_kwargs\["reasoning\_content"\], end\="", flush\=True)
    elif hasattr(msg, 'content') and msg.content:
        if is\_end:
            print("\\nThinking ended")
            is\_end \= False
        print(msg.content, end\="", flush\=True)

### Using Content Blocks

ChatQwQ also supports v1 version content\_blocks, for example

from langchain\_qwq import ChatQwen, ChatQwQ
model \= ChatQwQ(model\="qwq-plus")
print(model.invoke("Hello").content\_blocks)

### Tool Calling

from langchain\_core.tools import tool

@tool
def get\_weather(city: str) \-> str:
    """Get the weather for a city"""
    return f"The weather in {city} is sunny."

bound\_model \= model.bind\_tools(\[get\_weather\])
response \= bound\_model.invoke("What's the weather in New York?")
print(response.tool\_calls)

### Structured Output

#### JSON Mode

from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

struct\_model \= model.with\_structured\_output(User, method\="json\_mode")
response \= struct\_model.invoke("Hello, I'm John and I'm 25 years old")
print(response)  \# User(name='John', age=25)

#### Function Calling Mode

struct\_model \= model.with\_structured\_output(User, method\="function\_calling")
response \= struct\_model.invoke("My name is Alice and I'm 30")
print(response)  \# User(name='Alice', age=30)

### Integration with LangChain Agents

from langchain.agents import create\_agent
from langchain\_core.messages import HumanMessage
from langchain\_core.tools import tool
from langchain\_qwq import ChatQwen, ChatQwQ

@tool
def get\_weather(city: str) \-> str:
    """Get the weather in a city."""
    return f"The weather in {city} is sunny."

model \= ChatQwQ(model\="qwq-plus")
agent \= create\_agent(model, tools\=\[get\_weather\])
print(agent.invoke({"messages": \[HumanMessage("What is the weather like in New York?")\]}))

### QvQ Model Example

from langchain\_core.messages import HumanMessage

messages \= \[
    HumanMessage(
        content\_blocks\=\[
            {
                "type": "image",
                "url": "https://www.example.com/image.jpg",
            },
            {"type": "text", "text": "describe the image"},
        \]
    )
\]

\# model = ChatQwen(model="qwen-plus-latest")
model \= ChatQwQ(model\="qvq-plus")
print(model.invoke(messages))

## ChatQwen

The ChatQwen class offers enhanced support for Qwen3 and other Qwen series models, including specialized parameters for Qwen3's thinking mode.

### Basic Usage

from langchain\_qwq import ChatQwen

\# Qwen3 model
model \= ChatQwen(model\="qwen3-235b-a22b-instruct-2507")
response \= model.invoke("Hello")
print(response.content)

model\=ChatQwen(model\="qwen3-235b-a22b-thinking-2507")
response\=model.invoke("Hello")
\# Access reasoning content (Qwen3 only)
reasoning \= response.additional\_kwargs.get("reasoning\_content", "")
print(f"Reasoning: {reasoning}")

### Thinking Control

> **Note**: This feature is only applicable to Qwen3 models. It applies to all Qwen3 models except the latest ones, including but not limited to `Qwen3-235b-a22b-thinking-2507`, `Qwen3-235b-a22b-instruct-2507`, `Qwen3-Coder-480B-a35b-instruct`, and `Qwen3-Coder-plus`.

#### Disable Thinking Mode

\# Disable thinking for open-source Qwen3 models
model \= ChatQwen(model\="qwen3-32b", enable\_thinking\=False)
response \= model.invoke("Hello")
print(response.content)  \# No reasoning content

#### Enable Thinking for Proprietary Models

\# Enable thinking for proprietary models
model \= ChatQwen(model\="qwen-plus-latest", enable\_thinking\=True)
response \= model.invoke("Hello")
reasoning \= response.additional\_kwargs.get("reasoning\_content", "")
print(f"Reasoning: {reasoning}")

#### Control Thinking Length

\# Set thinking budget (max thinking tokens)
model \= ChatQwen(model\="qwen3-32b", thinking\_budget\=20)
response \= model.invoke("Hello")
reasoning \= response.additional\_kwargs.get("reasoning\_content", "")
print(f"Limited reasoning: {reasoning}")

### Other Qwen Models

#### Qwen-Max

model \= ChatQwen(model\="qwen-max-latest")
print(model.invoke("Hello").content)

\# Tool calling
bound\_model \= model.bind\_tools(\[get\_weather\])
response \= bound\_model.invoke("Weather in Shanghai and Beijing?", parallel\_tool\_calls\=True)
print(response.tool\_calls)

\# Structured output
struct\_model \= model.with\_structured\_output(User, method\="json\_mode")
result \= struct\_model.invoke("I'm Bob, 28 years old")
print(result)

#### Qwen2.5-72B

model \= ChatQwen(model\="qwen2.5-72b-instruct")
print(model.invoke("Hello").content)

\# All features work the same as other models
bound\_model \= model.bind\_tools(\[get\_weather\])
struct\_model \= model.with\_structured\_output(User, method\="json\_mode")

### Using Content Blocks

ChatQwen supports content blocks, for example

from langchain\_qwq import ChatQwen

model \= ChatQwen(model\="qwen-plus-latest",enable\_thinking\=True)
print(model.invoke("Hello").content\_blocks)

### Integration with LangChain Agents

from langchain.agents import create\_agent
from langchain\_core.messages import HumanMessage
from langchain\_core.tools import tool
from langchain\_qwq import ChatQwen

@tool
def get\_weather(city: str) \-> str:
    """Get the weather in a city."""
    return f"The weather in {city} is sunny."

model \= ChatQwen(model\="qwen-plus-latest")
agent \= create\_agent(model, tools\=\[get\_weather\])
print(agent.invoke({"messages": \[HumanMessage("查询New York的天气")\]}))

### Vision Models

from langchain\_core.messages import HumanMessage
from langchain\_qwq import ChatQwen

messages \= \[
    HumanMessage(
        content\_blocks\=\[
            {
                "type": "image",
                "url": "https://www.example.com/image.jpg",
            },
            {"type": "text", "text": "描述图片内容"},
        \]
    )
\]

model \= ChatQwen(model\="qwen3-vl-plus")
print(model.invoke(messages))

## Middleware

This library provides a middleware `DashScopeContextCacheMiddleware` that can be used to create display caching.

Example usage

from langchain.agents import create\_agent
from langchain.tools import tool

from langchain\_qwq import ChatQwen
from langchain\_qwq.middleware import DashScopeContextCacheMiddleware

@tool
def get\_weather(city: str) \-> str:
    """Get the current weather in a given city."""
    return f"The weather in {city} is 20 degrees Celsius."

model \= ChatQwen(model\="qwen3-max")

agent \= create\_agent(
    model, tools\=\[get\_weather\], middleware\=\[DashScopeContextCacheMiddleware()\]
)

## Model Comparison

Feature

ChatQwQ

ChatQwen

QwQ Models

✅ Primary

❌

QvQ Models

✅ Primary

❌

Qwen3 Models

✅ Basic

✅ Enhanced

Other Qwen Models

❌

✅ Full Support

Vision Models

❌

✅ Supported

Thinking Control

❌

✅ (Qwen3 only)

Thinking Budget

❌

✅ (Qwen3 only)

### Usage Guidance

-   Use ChatQwQ for QwQ and QvQ models.
-   For Qwen3 series models (available only on Alibaba Cloud BAILIAN platform) with deep thinking mode enabled, all invocations will automatically use streaming.
-   For other Qwen series models (including self-deployed or third-party deployed Qwen3 models), use ChatQwen, and streaming will not be automatically enabled.

## Project details

### Verified details

_These details have been [verified by PyPI](https://docs.pypi.org/project_metadata/#verified-details)_

###### Maintainers

 [![Avatar for yigit353 from gravatar.com](https://pypi-camo.freetls.fastly.net/d3d9ce762cd82c0cb95051c7ac0cf468427f73cc/68747470733a2f2f7365637572652e67726176617461722e636f6d2f6176617461722f34306133356430313331333163343063343833326230336330613336616430613f73697a653d3530 "Avatar for yigit353 from gravatar.com")yigit353](/user/yigit353/)

###### Meta

-   **Author:** [Yiğit Bekir Kaya, PhD](mailto:yigit353@gmail.com)

### Unverified details

_These details have **not** been verified by PyPI_

###### Project links

-   [Homepage](https://github.com/yigit353/langchain-qwq)
-   [Release Notes](https://github.com/langchain-ai/langchain/releases?q=tag%3A%22qwq%3D%3D0%22&expanded=true)
-   [Repository](https://github.com/yigit353/langchain-qwq)
-   [Source Code](https://github.com/yigit353/langchain-qwq/tree/main/langchain_qwq)

###### Meta

-   **License:** MIT License (MIT)
-   **Author:** Yiğit Bekir Kaya, PhD
-   **Requires:** Python <4.0, >=3.10

###### Classifiers

-   **License**
    -   [OSI Approved :: MIT License](/search/?c=License+%3A%3A+OSI+Approved+%3A%3A+MIT+License)
-   **Programming Language**
    -   [Python :: 3](/search/?c=Programming+Language+%3A%3A+Python+%3A%3A+3)
    -   [Python :: 3.10](/search/?c=Programming+Language+%3A%3A+Python+%3A%3A+3.10)
    -   [Python :: 3.11](/search/?c=Programming+Language+%3A%3A+Python+%3A%3A+3.11)
    -   [Python :: 3.12](/search/?c=Programming+Language+%3A%3A+Python+%3A%3A+3.12)
    -   [Python :: 3.13](/search/?c=Programming+Language+%3A%3A+Python+%3A%3A+3.13)

  

## Release history [Release notifications](/help/#project-release-notifications) | [RSS feed](/rss/project/langchain-qwq/releases.xml)

This version

![](https://pypi.org/static/images/blue-cube.572a5bfb.svg)

[

0.3.4

Jan 9, 2026

](/project/langchain-qwq/0.3.4/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[

0.3.1

Nov 29, 2025

](/project/langchain-qwq/0.3.1/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[

0.3.0

Nov 16, 2025

](/project/langchain-qwq/0.3.0/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[

0.2.1

Aug 10, 2025

](/project/langchain-qwq/0.2.1/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[

0.2.0

Jun 21, 2025

](/project/langchain-qwq/0.2.0/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[

0.1.6

Jun 16, 2025

](/project/langchain-qwq/0.1.6/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[

0.1.5

Jun 10, 2025

](/project/langchain-qwq/0.1.5/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[

0.1.4

Jun 8, 2025

](/project/langchain-qwq/0.1.4/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[

0.1.3

May 23, 2025

](/project/langchain-qwq/0.1.3/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[

0.1.2

May 23, 2025

](/project/langchain-qwq/0.1.2/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[

0.1.1

May 23, 2025

](/project/langchain-qwq/0.1.1/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[

0.1.0

May 22, 2025

](/project/langchain-qwq/0.1.0/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[

0.0.10

May 21, 2025

](/project/langchain-qwq/0.0.10/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[

0.0.9

May 21, 2025

](/project/langchain-qwq/0.0.9/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[

0.0.8

May 20, 2025

](/project/langchain-qwq/0.0.8/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[

0.0.7

Apr 2, 2025

](/project/langchain-qwq/0.0.7/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[

0.0.6

Apr 2, 2025

](/project/langchain-qwq/0.0.6/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[

0.0.5

Apr 2, 2025

](/project/langchain-qwq/0.0.5/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[

0.0.4

Apr 2, 2025

](/project/langchain-qwq/0.0.4/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[

0.0.3

Apr 2, 2025

](/project/langchain-qwq/0.0.3/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[

0.0.2

Apr 1, 2025

](/project/langchain-qwq/0.0.2/)

![](https://pypi.org/static/images/white-cube.2351a86c.svg)

[

0.0.1

Apr 1, 2025

](/project/langchain-qwq/0.0.1/)

## Download files

Download the file for your platform. If you're not sure which to choose, learn more about [installing packages](https://packaging.python.org/tutorials/installing-packages/ "External link").

### Source Distribution

[langchain\_qwq-0.3.4.tar.gz](https://files.pythonhosted.org/packages/a0/89/12444f63b4b9a1b4df3a2338c09c3b0650bc99b377a621815353142553b0/langchain_qwq-0.3.4.tar.gz) (18.0 kB [view details](#langchain_qwq-0.3.4.tar.gz))

Uploaded Jan 9, 2026 `Source`

### Built Distribution

Filter files by name, interpreter, ABI, and platform.

If you're not sure about the file name format, learn more about [wheel file names](https://packaging.python.org/en/latest/specifications/binary-distribution-format/ "External link").

The dropdown lists show the available interpreters, ABIs, and platforms.

Enable javascript to be able to filter the list of wheel files.

Copy a direct link to the current filters [https://pypi.org/project/langchain-qwq/#files](https://pypi.org/project/langchain-qwq/#files) Copy

Showing 1 of 1 file.

File name 

Interpreter Interpreter py3

ABI ABI none

Platform Platform any

[langchain\_qwq-0.3.4-py3-none-any.whl](https://files.pythonhosted.org/packages/d6/88/c7b1b2ee8cfd3f11eec50a1a8130b9a01ba2b41cce428e9ed9cb02e26b10/langchain_qwq-0.3.4-py3-none-any.whl) (17.8 kB [view details](#langchain_qwq-0.3.4-py3-none-any.whl))

Uploaded Jan 9, 2026 `Python 3`

## File details

Details for the file `langchain_qwq-0.3.4.tar.gz`.

### File metadata

-   Download URL: [langchain\_qwq-0.3.4.tar.gz](https://files.pythonhosted.org/packages/a0/89/12444f63b4b9a1b4df3a2338c09c3b0650bc99b377a621815353142553b0/langchain_qwq-0.3.4.tar.gz)
-   Upload date: Jan 9, 2026
-   Size: 18.0 kB
-   Tags: Source
-   Uploaded using Trusted Publishing? No
-   Uploaded via: poetry/2.0.1 CPython/3.13.0rc3 Darwin/25.2.0

### File hashes

Hashes for langchain\_qwq-0.3.4.tar.gz

Algorithm

Hash digest

SHA256

`5156c1f6c5082d1cb8e509b912e4184182baf15f0e3cab66ff9ad62ce144bf77`

Copy

MD5

`29a75f6b7ba16e60a432d63767859844`

Copy

BLAKE2b-256

`a08912444f63b4b9a1b4df3a2338c09c3b0650bc99b377a621815353142553b0`

Copy

[See more details on using hashes here.](https://pip.pypa.io/en/stable/topics/secure-installs/#hash-checking-mode "External link")

## File details

Details for the file `langchain_qwq-0.3.4-py3-none-any.whl`.

### File metadata

-   Download URL: [langchain\_qwq-0.3.4-py3-none-any.whl](https://files.pythonhosted.org/packages/d6/88/c7b1b2ee8cfd3f11eec50a1a8130b9a01ba2b41cce428e9ed9cb02e26b10/langchain_qwq-0.3.4-py3-none-any.whl)
-   Upload date: Jan 9, 2026
-   Size: 17.8 kB
-   Tags: Python 3
-   Uploaded using Trusted Publishing? No
-   Uploaded via: poetry/2.0.1 CPython/3.13.0rc3 Darwin/25.2.0

### File hashes

Hashes for langchain\_qwq-0.3.4-py3-none-any.whl

Algorithm

Hash digest

SHA256

`d04d5e1803fb694d1bb513dcbf83d7d6b04069f934786e05a706d32d9324251c`

Copy

MD5

`13f58607cfbf603a7e48445f6046bb2f`

Copy

BLAKE2b-256

`d688c7b1b2ee8cfd3f11eec50a1a8130b9a01ba2b41cce428e9ed9cb02e26b10`

Copy

[See more details on using hashes here.](https://pip.pypa.io/en/stable/topics/secure-installs/#hash-checking-mode "External link")