# ChatGoogleGenerativeAI - Docs by LangChain

Access Google’s Generative AI models, including the Gemini family, via the **Gemini Developer API** or **Vertex AI**. The Gemini Developer API offers quick setup with API keys, ideal for individual developers. Vertex AI provides enterprise features and integrates with Google Cloud Platform. For information on the latest models, model IDs, their features, context windows, etc. head to the [Google AI docs](https://ai.google.dev/gemini-api/docs).

**Vertex AI consolidation & compatibility**As of `langchain-google-genai` 4.0.0, this package uses the consolidated [`google-genai`](https://googleapis.github.io/python-genai/) SDK instead of the legacy [`google-ai-generativelanguage`](https://googleapis.dev/python/generativelanguage/latest/) SDK.This migration brings support for Gemini models both via the Gemini Developer API and Gemini API in Vertex AI, superseding certain classes in `langchain-google-vertexai`, such as `ChatVertexAI`.Read the [full announcement and migration guide](https://github.com/langchain-ai/langchain-google/discussions/1422).

**API Reference**For detailed documentation of all features and configuration options, head to the [`ChatGoogleGenerativeAI`](https://reference.langchain.com/python/integrations/langchain_google_genai/#langchain_google_genai.ChatGoogleGenerativeAI) API reference.

## 

[​

](#overview)

Overview

### 

[​

](#integration-details)

Integration details

Class

Package

Serializable

[JS support](https://js.langchain.com/docs/integrations/chat/google_generative_ai)

Downloads

Version

[`ChatGoogleGenerativeAI`](https://reference.langchain.com/python/integrations/langchain_google_genai/#langchain_google_genai.ChatGoogleGenerativeAI)

[`langchain-google-genai`](https://reference.langchain.com/python/integrations/langchain_google_genai)

beta

✅

![PyPI - Downloads](https://img.shields.io/pypi/dm/langchain-google-genai?style=flat-square&label=%20)

![PyPI - Version](https://img.shields.io/pypi/v/langchain-google-genai?style=flat-square&label=%20)

### 

[​

](#model-features)

Model features

[Tool calling](/oss/python/langchain/tools)

[Structured output](/oss/python/langchain/structured-output)

[Image input](/oss/python/langchain/messages#multimodal)

Audio input

Video input

[Token-level streaming](/oss/python/langchain/streaming)

Native async

[Token usage](/oss/python/langchain/models#token-usage)

[Logprobs](/oss/python/langchain/models#log-probabilities)

✅

✅

✅

✅

✅

✅

✅

✅

⚠️

## 

[​

](#setup)

Setup

To access Google AI models you’ll need to create a Google Account, get a Google AI API key, and install the `langchain-google-genai` integration package.

### 

[​

](#installation)

Installation

Copy

```
pip install -U langchain-google-genai
```

### 

[​

](#credentials)

Credentials

This integration supports two backends: **Gemini Developer API** and **Vertex AI**. The backend is selected automatically based on your configuration.

#### 

[​

](#backend-selection)

Backend selection

The backend is determined as follows:

1.  If `GOOGLE_GENAI_USE_VERTEXAI` env var is set, uses that value
2.  If `credentials` parameter is provided, uses Vertex AI
3.  If `project` parameter is provided, uses Vertex AI
4.  Otherwise, uses Gemini Developer API

You can also explicitly set `vertexai=True` or `vertexai=False` to override auto-detection.

-   Gemini Developer API
    
-   Vertex AI with API key
    
-   Vertex AI with credentials
    

**Quick setup with API key**Recommended for individual developers / new users.Head to [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key) to generate an API key:

Copy

```
import getpass
import os

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")
```

The integration checks for `GOOGLE_API_KEY` first, then `GEMINI_API_KEY` as a fallback.

**Vertex AI using API key authentication**You can use Vertex AI with API key authentication for simpler setup:

Copy

```
export GEMINI_API_KEY='your-api-key'
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT='your-project-id'
```

Or programmatically:

Copy

```
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key="your-api-key", 
    project="your-project-id", 
    vertexai=True, 
)
```

**Vertex AI using service account or ADC**Set up [Application Default Credentials (ADC)](https://cloud.google.com/docs/authentication/application-default-credentials):

Copy

```
gcloud auth application-default login
```

Set your Google Cloud project:

Copy

```
export GOOGLE_CLOUD_PROJECT='your-project-id'
# Optional: set region (defaults to us-central1)
export GOOGLE_CLOUD_LOCATION='us-central1'
```

Or use service account credentials:

Copy

```
from google.oauth2 import service_account
from langchain_google_genai import ChatGoogleGenerativeAI

credentials = service_account.Credentials.from_service_account_file(
    "path/to/service-account.json",
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    credentials=credentials, 
    project="your-project-id", 
)
```

#### 

[​

](#environment-variables)

Environment variables

Variable

Purpose

Backend

`GOOGLE_API_KEY`

API key (primary)

Both (see `GOOGLE_GENAI_USE_VERTEXAI`)

`GEMINI_API_KEY`

API key (fallback)

Both (see `GOOGLE_GENAI_USE_VERTEXAI`)

`GOOGLE_GENAI_USE_VERTEXAI`

Force Vertex AI backend (`true`/`false`)

Vertex AI

`GOOGLE_CLOUD_PROJECT`

GCP project ID

Vertex AI

`GOOGLE_CLOUD_LOCATION`

GCP region (default: `us-central1`)

Vertex AI

To enable automated tracing of your model calls, set your [LangSmith](https://docs.langchain.com/langsmith/home) API key:

Copy

```
os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API key: ")
os.environ["LANGSMITH_TRACING"] = "true"
```

## 

[​

](#instantiation)

Instantiation

Now we can instantiate our model object and generate responses:

-   Gemini Developer API
    
-   Vertex AI
    

Copy

```
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(
    model="gemini-3-pro-preview",
    temperature=1.0,  # Gemini 3.0+ defaults to 1.0
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)
```

Copy

```
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(
    model="gemini-3-pro-preview",
    project="your-project-id", 
    location="us-central1",  # Optional, defaults to us-central1
    temperature=1.0,  # Gemini 3.0+ defaults to 1.0
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)
```

Providing `project` automatically selects the Vertex AI backend unless you explicitly set `vertexai=False`.

**Temperature for Gemini 3.0+ models**If `temperature` is not explicitly set and the model is Gemini 3.0 or later, it will be automatically set to `1.0` instead of the default `0.7` per Google GenAI API best practices. Using `0.7` with Gemini 3.0+ can cause infinite loops, degraded reasoning performance, and failure on complex tasks.

See the [`ChatGoogleGenerativeAI`](https://reference.langchain.com/python/integrations/langchain_google_genai/#langchain_google_genai.ChatGoogleGenerativeAI) API Reference for the full set of available model parameters.

### 

[​

](#proxy-configuration)

Proxy configuration

If you need to use a proxy, set these environment variables before initializing:

Copy

```
export HTTPS_PROXY='http://username:password@proxy_uri:port'
export SSL_CERT_FILE='path/to/cert.pem'  # Optional: custom SSL certificate
```

For SOCKS5 proxies or advanced proxy configuration, use the `client_args` parameter:

Copy

```
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(
    model="gemini-3-pro-preview",
    client_args={"proxy": "socks5://user:pass@host:port"},
)
```

## 

[​

](#invocation)

Invocation

Copy

```
messages = [
    (
        "system",
        "You are a helpful assistant that translates English to French. Translate the user sentence.",
    ),
    ("human", "I love programming."),
]
ai_msg = model.invoke(messages)
ai_msg
```

Gemini 3

Gemini 2.5

Copy

```
AIMessage(content=[{'type': 'text', 'text': "J'adore la programmation.", 'extras': {'signature': 'EpoWCpc...'}}], additional_kwargs={}, response_metadata={'prompt_feedback': {'block_reason': 0, 'safety_ratings': []}, 'finish_reason': 'STOP', 'model_name': 'gemini-3-pro-preview', 'safety_ratings': [], 'model_provider': 'google_genai'}, id='lc_run--fb732b64-1ab4-4a28-b93b-dcfb2a164a3d-0', usage_metadata={'input_tokens': 21, 'output_tokens': 779, 'total_tokens': 800, 'input_token_details': {'cache_read': 0}, 'output_token_details': {'reasoning': 772}})
```

**Message content shape**Gemini 3 series models will always return a list of content blocks to capture [thought signatures](#thought-signatures). Use the `.text` property to recover string content.

Copy

```
response.content  # -> [{"type": "text", "text": "Hello!", "extras": {"signature": "EpQFCp...lKx64r"}}]
response.text     # -> "Hello!"
```

Copy

```
print(ai_msg.content)
```

Gemini 3

Gemini 2.5

Copy

```
[{'type': 'text',
'text': "J'adore la programmation.",
'extras': {'signature': '...'}}]
```

Copy

```
print(ai_msg.text)
```

Copy

```
J'adore la programmation.
```

## 

[​

](#multimodal-usage)

Multimodal usage

Gemini models can accept multimodal inputs (text, images, audio, video) and, for some models, generate multimodal outputs.

### 

[​

](#supported-input-methods)

Supported input methods

Method

[Image](#image-input)

[Video](#video-input)

[Audio](#audio-input)

[PDF](#pdf-input)

[File upload](#file-upload) (Files API)

✅

✅

✅

✅

Base64 inline data

✅

✅

✅

✅

HTTP/HTTPS URLs\*

✅

✅

✅

✅

GCS URIs (`gs://...`)

✅

✅

✅

✅

\*YouTube URLs are supported for video input in preview.

### 

[​

](#file-upload)

File upload

You can upload files to Google’s servers and reference them by URI. This works for PDFs, images, videos, and audio files.

Copy

```
import time
from google import genai
from langchain.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

client = genai.Client()
model = ChatGoogleGenerativeAI(model="gemini-3-pro-preview")

# Upload file to Google's servers
myfile = client.files.upload(file="/path/to/your/file.pdf")
while myfile.state.name == "PROCESSING":
    time.sleep(2)
    myfile = client.files.get(name=myfile.name)

# Reference by file_id in FileContentBlock
message = HumanMessage(
    content=[
        {"type": "text", "text": "What is in the document?"},
        {
            "type": "file",
            "file_id": myfile.uri,  # or myfile.name
            "mime_type": "application/pdf",
        },
    ]
)
response = model.invoke([message])
```

Once uploaded, you can reference the file in any of the media-specific sections below using the `file_id` pattern.

### 

[​

](#image-input)

Image input

Provide image inputs along with text using a [`HumanMessage`](https://reference.langchain.com/python/langchain/messages/#langchain.messages.HumanMessage) with a list content format.

Image URL

Chat Completions image\_url format

Base64 encoded

Uploaded file

Copy

```
from langchain.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(model="gemini-3-pro-preview")

message = HumanMessage(
    content=[
        {"type": "text", "text": "Describe the image at the URL."},
        {
            "type": "image",
            "url": "https://picsum.photos/seed/picsum/200/300",
        },
    ]
)
response = model.invoke([message])
```

Other supported image formats:

-   A Google Cloud Storage URI (`gs://...`). Ensure the service account has access.

### 

[​

](#pdf-input)

PDF input

Provide PDF file inputs along with text.

URL

Base64 encoded

Uploaded file

Copy

```
from langchain.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(model="gemini-3-pro-preview")

message = HumanMessage(
    content=[
        {"type": "text", "text": "Describe the document in a sentence."},
        {
            "type": "image_url",  # (PDFs are treated as images)
            "image_url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
        },
    ]
)
response = model.invoke([message])
```

### 

[​

](#audio-input)

Audio input

Provide audio file inputs along with text.

URL

Base64 encoded

Uploaded file

Copy

```
from langchain.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(model="gemini-3-pro-preview")

message = HumanMessage(
    content=[
        {"type": "text", "text": "Summarize this audio in a sentence."},
        {
            "type": "image_url",
            "image_url": "https://example.com/audio.mp3",
        },
    ]
)
response = model.invoke([message])
```

### 

[​

](#video-input)

Video input

Provide video file inputs along with text.

Base64 encoded

Uploaded file

YouTube URL

Copy

```
import base64
from langchain.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(model="gemini-3-pro-preview")

video_bytes = open("path/to/your/video.mp4", "rb").read()
video_base64 = base64.b64encode(video_bytes).decode("utf-8")
mime_type = "video/mp4"

message = HumanMessage(
    content=[
        {"type": "text", "text": "Describe what's in this video in a sentence."},
        {
            "type": "video",
            "base64": video_base64,
            "mime_type": mime_type,
        },
    ]
)
response = model.invoke([message])
```

**YouTube limitations**

-   Only public videos are supported (not private or unlisted)
-   Free tier: max 8 hours of YouTube video per day
-   Feature is currently in preview

### 

[​

](#image-generation)

Image generation

Certain models can generate text and images inline. See more information on the [Gemini API docs](https://ai.google.dev/gemini-api/docs/image-generation) for details. This example demonstrates how to generate and display an image in a Jupyter notebook:

Copy

```
import base64

from IPython.display import Image, display
from langchain.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-image") 

response = model.invoke("Generate a photorealistic image of a cuddly cat wearing a hat.")

def _get_image_base64(response: AIMessage) -> None:
    image_block = next(
        block
        for block in response.content
        if isinstance(block, dict) and block.get("image_url")
    )
    return image_block["image_url"].get("url").split(",")[-1]

image_base64 = _get_image_base64(response)
display(Image(data=base64.b64decode(image_base64), width=300))
```

Use `image_config` to control resulting image dimensions and quality. See [`genai.types.ImageConfig`](https://googleapis.github.io/python-genai/genai.html#genai.types.ImageConfig) for a list of supported fields and their values. Setting `image_config` during instantiation applies the configuration to all invocations, while setting it during invocation overrides the default for that call only; this allows for flexible control over generation parameters on a per-request basis.

Instantiation

Invocation

Copy

```
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-image", 
    image_config={ 
        "aspect_ratio": "16:9", 
    }, 
)

response = model.invoke("Generate a photorealistic image of a cuddly cat wearing a hat.")
```

Supported parameters vary by model and backend (Gemini Developer API and Vertex AI each support different subsets of parameters and models).

By default, image generation models may return both text and images (e.g. _“Ok! Here’s an image of a…”_). You can request that the model only return images by setting the `response_modalities` parameter:

Instantiation

Invocation

Copy

```
from langchain_google_genai import ChatGoogleGenerativeAI, Modality

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-image",
    response_modalities=[Modality.IMAGE],  
)

# All invocations will return only images
response = model.invoke("Generate a photorealistic image of a cuddly cat wearing a hat.")
```

### 

[​

](#audio-generation)

Audio generation

Certain models can generate audio files. See more information on the [Gemini API docs](https://ai.google.dev/gemini-api/docs/speech-generation) for details.

**Vertex AI Limitation**Audio generation models are currently in limited preview on Vertex AI and may require allowlist access. If you encounter an `INVALID_ARGUMENT` error when using TTS models with `vertexai=True`, your GCP project may need to be allowlisted.For more details, see this [Google AI forum discussion](https://discuss.ai.google.dev/t/request-allowlist-access-for-audio-output-in-gemini-2-5-pro-flash-tts-vertex-ai/108067).

Copy

```
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-tts") 

response = model.invoke("Please say The quick brown fox jumps over the lazy dog")

# Base64 encoded binary data of the audio
wav_data = response.additional_kwargs.get("audio")
with open("output.wav", "wb") as f:
    f.write(wav_data)
```

## 

[​

](#tool-calling)

Tool calling

You can equip the model with tools to call.

Copy

```
from langchain.tools import tool
from langchain.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Define the tool
@tool(description="Get the current weather in a given location")
def get_weather(location: str) -> str:
    return "It's sunny."

# Initialize and bind (potentially multiple) tools to the model
model_with_tools = ChatGoogleGenerativeAI(model="gemini-3-pro-preview").bind_tools([get_weather])

# Step 1: Model generates tool calls
messages = [HumanMessage("What's the weather in Boston?")]
ai_msg = model_with_tools.invoke(messages)
messages.append(ai_msg)

# Check the tool calls in the response
print(ai_msg.tool_calls)

# Step 2: Execute tools and collect results
for tool_call in ai_msg.tool_calls:
    # Execute the tool with the generated arguments
    tool_result = get_weather.invoke(tool_call)
    messages.append(tool_result)

# Step 3: Pass results back to model for final response
final_response = model_with_tools.invoke(messages)
final_response
```

Copy

```
[{'name': 'get_weather', 'args': {'location': 'Boston'}, 'id': '879b4233-901b-4bbb-af56-3771ca8d3a75', 'type': 'tool_call'}]
```

Copy

```
AIMessage(content=[{'type': 'text', 'text': 'The weather in Boston is sunny.'}], additional_kwargs={}, response_metadata={'prompt_feedback': {'block_reason': 0, 'safety_ratings': []}, 'finish_reason': 'STOP', 'model_name': 'gemini-3-pro-preview', 'safety_ratings': [], 'model_provider': 'google_genai'}, id='lc_run--190be543-c974-460b-a708-7257892c3121-0', usage_metadata={'input_tokens': 143, 'output_tokens': 7, 'total_tokens': 150, 'input_token_details': {'cache_read': 0}})
```

## 

[​

](#structured-output)

Structured output

Force the model to respond with a specific structure. See the [Gemini API docs](https://ai.google.dev/gemini-api/docs/structured-output) for more info.

Copy

```
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from typing import Literal

class Feedback(BaseModel):
    sentiment: Literal["positive", "neutral", "negative"]
    summary: str

model = ChatGoogleGenerativeAI(model="gemini-3-pro-preview")
structured_model = model.with_structured_output(
    schema=Feedback.model_json_schema(), method="json_schema"
)

response = structured_model.invoke("The new UI is great!")
response["sentiment"]  # "positive"
response["summary"]  # "The user expresses positive..."
```

For streaming structured output, merge dictionaries instead of using `+=`:

Copy

```
stream = structured_model.stream("The interface is intuitive and beautiful!")
full = next(stream)
for chunk in stream:
    full.update(chunk)  # Merge dictionaries
print(full)  # Complete structured response
# -> {'sentiment': 'positive', 'summary': 'The user praises...'}
```

### 

[​

](#structured-output-methods)

Structured output methods

Two methods are supported for structured output:

-   **`method="json_schema"` (default)**: Uses Gemini’s native structured output. Recommended for better reliability, as it constrains the model’s generation process directly rather than relying on post-processing tool calls.
-   **`method="function_calling"`**: Uses tool calling to extract structured data.

## 

[​

](#token-usage-tracking)

Token usage tracking

Access token usage information from the response metadata.

Copy

```
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(model="gemini-3-pro-preview")

result = model.invoke("Explain the concept of prompt engineering in one sentence.")

print(result.content)
print("\nUsage Metadata:")
print(result.usage_metadata)
```

Copy

```
Prompt engineering is the art and science of crafting effective text prompts to elicit desired and accurate responses from large language models.

Usage Metadata:
{'input_tokens': 10, 'output_tokens': 24, 'total_tokens': 34, 'input_token_details': {'cache_read': 0}}
```

## 

[​

](#thinking-support)

Thinking support

Certain Gemini models support configurable thinking depth. Depending on the model version used, you can control this via either `thinking_level` (Gemini 3+) or `thinking_budget` (Gemini 2.5).

### 

[​

](#thinking-level)

Thinking level

For Gemini 3+ models, use `thinking_level` to control reasoning depth. Some model providers call this “reasoning effort”.

Value

Models

Description

`'minimal'`

Flash

Matches the “no thinking” setting for most queries

`'low'`

Flash, Pro

Minimizes latency and cost

`'medium'`

Flash

Balances latency/cost with reasoning depth

`'high'`

Pro

Maximizes reasoning depth (default)

Note that `minimal` does not guarantee that thinking is off.

Copy

```
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-3-pro-preview",
    thinking_level="low",  
)

response = llm.invoke("How many O's are in Google?")
```

### 

[​

](#gemini-2-5-models:-thinking_budget)

Gemini 2.5 models: `thinking_budget`

For Gemini 2.5 models, use `thinking_budget` (an integer token count) instead:

-   Set to `0` to disable thinking (where supported)
-   Set to `-1` for dynamic thinking (model decides)
-   Set to a positive integer to constrain token usage

Copy

```
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    thinking_budget=1024,  
)
```

Not all models allow disabling thinking. See the [Gemini models documentation](https://ai.google.dev/gemini-api/docs/models) for details.

### 

[​

](#viewing-model-thoughts)

Viewing model thoughts

To see a thinking model’s reasoning, set `include_thoughts=True`:

Copy

```
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-3-pro-preview",
    include_thoughts=True,  
)

response = llm.invoke("How many O's are in Google? How did you verify your answer?")
reasoning_tokens = response.usage_metadata["output_token_details"]["reasoning"]

print("Response:", response.content)
print("Reasoning tokens used:", reasoning_tokens)
```

Copy

```
Response: [{'type': 'thinking', 'thinking': '**Analyzing and Cou...'}, {'type': 'text', 'text': 'There a...', 'extras': {'signature': 'EroR...'}}]
Reasoning tokens used: 672
```

See the [Gemini API docs](https://ai.google.dev/gemini-api/docs/thinking) for more information on thinking.

### 

[​

](#thought-signatures)

Thought signatures

[Thought signatures](https://ai.google.dev/gemini-api/docs/thinking) are encrypted representations of the model’s reasoning processes. They enable Gemini to maintain thought context across multi-turn conversations, since the API is stateless and treats each request independently.

Gemini 3 may raise 4xx errors if thought signatures are not passed back with tool call responses. Upgrade to `langchain-google-genai >= 3.1.0` to ensure this is handled correctly.

Signatures appear in two places in `AIMessage` responses:

-   **Text blocks**: Stored in `extras.signature` within the content block
-   **Tool calls**: Stored in `additional_kwargs["__gemini_function_call_thought_signatures__"]`

Copy

```
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-3-pro-preview",
    include_thoughts=True, 
)

response = llm.invoke("How many O's are in Google? How did you verify your answer?")

response.content_blocks[-1]
```

Copy

```
{'type': 'text',
 'text': 'There are **2** O\'s in the word "Google...',
 'extras': {'signature': 'EsUSCsIS...'}}
```

For multi-turn conversations with tool calls, you must pass the full `AIMessage` back to the model so signatures are preserved. This happens automatically when you append the `AIMessage` to your messages list:

Copy

```
from langchain.tools import tool
from langchain.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

@tool
def get_weather(location: str) -> str:
    """Get current weather for a location."""
    return f"Weather in {location}: sunny, 22°C"

model = ChatGoogleGenerativeAI(model="gemini-3-pro-preview").bind_tools([get_weather])
messages = [HumanMessage("What's the weather in Tokyo?")]

# Step 1: Model returns tool call with thought signature attached
ai_msg = model.invoke(messages)
messages.append(ai_msg)  # Preserves thought signature

# Step 2: Execute tool and add result
for tool_call in ai_msg.tool_calls:
    result = get_weather.invoke(tool_call)
    messages.append(result)

# Step 3: Model receives signature back, continues reasoning coherently
final_response = model.invoke(messages)
```

**Don’t reconstruct messages manually.** If you create a new `AIMessage` instead of passing the original object, the signatures will be lost and the API may reject the request.

## 

[​

](#built-in-tools)

Built-in tools

Google Gemini supports a variety of built-in tools, which can be bound to the model in the usual way.

### 

[​

](#google-search)

Google search

See [Gemini docs](https://ai.google.dev/gemini-api/docs/grounding/search-suggestions) for detail.

Bind to model

Use on invocation

Copy

```
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(model="gemini-3-pro-preview")

model_with_search = model.bind_tools([{"google_search": {}}]) 
response = model_with_search.invoke("When is the next total solar eclipse in US?")

response.content_blocks
```

Copy

```
[{'type': 'text',
  'text': 'The next total solar eclipse visible in the contiguous United States will occur on...',
  'annotations': [{'type': 'citation',
    'id': 'abc123',
    'url': '<url for source 1>',
    'title': '<source 1 title>',
    'start_index': 0,
    'end_index': 99,
    'cited_text': 'The next total solar eclipse...',
    'extras': {'google_ai_metadata': {'web_search_queries': ['next total solar eclipse in US'],
       'grounding_chunk_index': 0,
       'confidence_scores': []}}},
   ...
```

### 

[​

](#google-maps)

Google maps

Certain models support grounding using Google Maps. Maps grounding connects Gemini’s generative capabilities with Google Maps’ current, factual location data. This enables location-aware applications that provide accurate, geographically specific responses. See [Gemini docs](https://ai.google.dev/gemini-api/docs/maps-grounding) for detail.

Bind to model

Use on invocation

Copy

```
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(model="gemini-2.5-pro")

model_with_maps = model.bind_tools([{"google_maps": {}}]) 
response = model_with_maps.invoke(
    "What are some good Italian restaurants near the Eiffel Tower in Paris?"
)
```

The response will include grounding metadata with location information from Google Maps. You can optionally provide a specific location context using `tool_config` with `lat_lng`. This is useful when you want to ground queries relative to a specific geographic point.

Bind to model

Use on invocation

Copy

```
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(model="gemini-2.5-pro")

# Provide location context (latitude and longitude)
model_with_maps = model.bind_tools(
    [{"google_maps": {}}], 
    tool_config={
        "retrieval_config": {  # Eiffel Tower
            "lat_lng": { 
                "latitude": 48.858844, 
                "longitude": 2.294351, 
            } 
        }
    },
)

response = model_with_maps.invoke(
    "What Italian restaurants are within a 5 minute walk from here?"
)
```

### 

[​

](#url-context)

URL context

The URL context tool enables the model to access and analyze content from URLs you provide in your prompt. This is useful for tasks like summarizing web pages, extracting data from multiple sources, or answering questions about online content. See [Gemini docs](https://ai.google.dev/gemini-api/docs/url-context) for detail and limitations.

Bind to model

Use on invocation

Copy

```
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

model_with_url_context = model.bind_tools([{"url_context": {}}]) 
response = model_with_url_context.invoke(
    "Summarize the content at https://docs.langchain.com"
)
```

### 

[​

](#code-execution)

Code execution

See [Gemini docs](https://ai.google.dev/gemini-api/docs/code-execution?lang=python) for detail.

Bind to model

Use on invocation

Copy

```
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(model="gemini-3-pro-preview")

model_with_code_interpreter = model.bind_tools([{"code_execution": {}}]) 
response = model_with_code_interpreter.invoke("Use Python to calculate 3^3.")

response.content_blocks
```

Copy

```
[{'type': 'server_tool_call',
  'name': 'code_interpreter',
  'args': {'code': 'print(3**3)', 'language': <Language.PYTHON: 1>},
  'id': '...'},
 {'type': 'server_tool_result',
  'tool_call_id': '',
  'status': 'success',
  'output': '27\n',
  'extras': {'block_type': 'code_execution_result',
   'outcome': <Outcome.OUTCOME_OK: 1>}},
 {'type': 'text', 'text': 'The calculation of 3 to the power of 3 is 27.'}]
```

### 

[​

](#computer-use)

Computer use

The Gemini 2.5 Computer Use model (`gemini-2.5-computer-use-preview-10-2025`) can interact with browser environments to automate web tasks like clicking, typing, and scrolling.

**Preview model limitations**The Computer Use model is in preview and may produce unexpected behavior. Always supervise automated tasks and avoid use with sensitive data or critical operations. See the [Gemini API docs](https://ai.google.dev/gemini-api/docs/computer-use) for safety best practices.

Bind to model

Use on invocation

Copy

```
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(model="gemini-2.5-computer-use-preview-10-2025") 
model_with_computer = model.bind_tools([{"computer_use": {}}]) 

response = model_with_computer.invoke("Please navigate to example.com")

response.content_blocks
```

Copy

```
[{'type': 'tool_call',
  'id': '08a8b175-16ab-4861-8965-b736d5d4dd7e',
  'name': 'open_web_browser',
  'args': {}}]
```

You can configure the environment and exclude specific UI actions:

Advanced configuration

Copy

```
from langchain_google_genai import ChatGoogleGenerativeAI, Environment

model = ChatGoogleGenerativeAI(model="gemini-2.5-computer-use-preview-10-2025") 

# Specify the environment (browser is default)
model_with_computer = model.bind_tools(
    [{"computer_use": {"environment": Environment.ENVIRONMENT_BROWSER}}] 
)

# Exclude specific UI actions
model_with_computer = model.bind_tools(
    [
        {
            "computer_use": {
                "environment": Environment.ENVIRONMENT_BROWSER,
                "excludedPredefinedFunctions": [ 
                    "drag_and_drop", 
                    "key_combination", 
                ], 
            }
        }
    ]
)

response = model_with_computer.invoke("Search for Python tutorials")
```

The model returns function calls for UI actions (like `click_at`, `type_text_at`, `scroll`) with normalized coordinates. You’ll need to implement the actual execution of these actions in your browser automation framework.

## 

[​

](#safety-settings)

Safety settings

Gemini models have default safety settings that can be overridden. If you are receiving lots of `'Safety Warnings'` from your models, you can try tweaking the `safety_settings` attribute of the model. For example, to turn off safety blocking for dangerous content, you can construct your LLM as follows:

Copy

```
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)

llm = ChatGoogleGenerativeAI(
        model="gemini-3-pro-preview",
        safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    },
)
```

For an enumeration of the categories and thresholds available, see Google’s [safety setting types](https://ai.google.dev/api/python/google/generativeai/types/SafetySettingDict).

## 

[​

](#context-caching)

Context caching

Context caching allows you to store and reuse content (e.g., PDFs, images) for faster processing. The `cached_content` parameter accepts a cache name created via the Google Generative AI API.Single file example

This caches a single file and queries it.

Copy

```
import time
from google import genai
from google.genai import types
from langchain.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

client = genai.Client()

# Upload file
file = client.files.upload(file="path/to/your/file")
while file.state.name == "PROCESSING":
    time.sleep(2)
    file = client.files.get(name=file.name)

# Create cache
model = "gemini-3-pro-preview"
cache = client.caches.create(
    model=model,
    config=types.CreateCachedContentConfig(
        display_name="Cached Content",
        system_instruction=(
            "You are an expert content analyzer, and your job is to answer "
            "the user's query based on the file you have access to."
        ),
        contents=[file],
        ttl="300s",
    ),
)

# Query with LangChain
llm = ChatGoogleGenerativeAI(
    model=model,
    cached_content=cache.name,
)
message = HumanMessage(content="Summarize the main points of the content.")
llm.invoke([message])
```
Multiple files example

This caches two files using `Part` and queries them together.

Copy

```
import time
from google import genai
from google.genai.types import CreateCachedContentConfig, Content, Part
from langchain.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

client = genai.Client()

# Upload files
file_1 = client.files.upload(file="./file1")
while file_1.state.name == "PROCESSING":
    time.sleep(2)
    file_1 = client.files.get(name=file_1.name)

file_2 = client.files.upload(file="./file2")
while file_2.state.name == "PROCESSING":
    time.sleep(2)
    file_2 = client.files.get(name=file_2.name)

# Create cache with multiple files
contents = [
    Content(
        role="user",
        parts=[
            Part.from_uri(file_uri=file_1.uri, mime_type=file_1.mime_type),
            Part.from_uri(file_uri=file_2.uri, mime_type=file_2.mime_type),
        ],
    )
]
model = "gemini-3-pro-preview"
cache = client.caches.create(
    model=model,
    config=CreateCachedContentConfig(
        display_name="Cached Contents",
        system_instruction=(
            "You are an expert content analyzer, and your job is to answer "
            "the user's query based on the files you have access to."
        ),
        contents=contents,
        ttl="300s",
    ),
)

# Query with LangChain
llm = ChatGoogleGenerativeAI(
    model=model,
    cached_content=cache.name,
)
message = HumanMessage(
    content="Provide a summary of the key information across both files."
)
llm.invoke([message])
```
See the Gemini API docs on [context caching](https://ai.google.dev/gemini-api/docs/caching?lang=python) for more information.

## 

[​

](#response-metadata)

Response metadata

Access response metadata from the model response.

Copy

```
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-3-pro-preview")

response = llm.invoke("Hello!")
response.response_metadata
```

Copy

```
{'prompt_feedback': {'block_reason': 0, 'safety_ratings': []},
 'finish_reason': 'STOP',
 'model_name': 'gemini-3-pro-preview',
 'safety_ratings': [],
 'model_provider': 'google_genai'}
```

---

## 

[​

](#api-reference)

API reference

For detailed documentation of all features and configuration options, head to the [`ChatGoogleGenerativeAI`](https://reference.langchain.com/python/integrations/langchain_google_genai/#langchain_google_genai.ChatGoogleGenerativeAI) API reference.

---

[Edit this page on GitHub](https://github.com/langchain-ai/docs/edit/main/src/oss/python/integrations/chat/google_generative_ai.mdx) or [file an issue](https://github.com/langchain-ai/docs/issues/new/choose).

[Connect these docs](/use-these-docs) to Claude, VSCode, and more via MCP for real-time answers.