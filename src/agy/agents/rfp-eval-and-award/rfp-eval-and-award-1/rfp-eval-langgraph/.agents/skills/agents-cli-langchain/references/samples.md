# Reference examples (LangChain ecosystem)

The examples are LangChain's own template and example repos, plus the LangChain docs. They are not
collected in one monorepo, so each entry below names its own repo.

**Reading this page is not studying an example.** Clone the repo and read its `README.md` (and
`AGENTS.md`, where there is one) before you write code.

**Study and adapt — don't scaffold from one.** Your project already has its scaffold: the example's
graph belongs in `app/agent.py` as `root_agent`, and `app/fast_api_app.py` stays as it is. Copy the
graph, tools and prompts; leave the repo's own serving, config and deploy layers behind.

```bash
git clone --depth 1 https://github.com/langchain-ai/<repo> /tmp/<repo>
cat /tmp/<repo>/README.md
```

| You need | Study | Key files |
|---|---|---|
| The baseline shape: tools, prompt, state and config in a real layout | `react-agent`, the LangGraph project template | `src/react_agent/graph.py`, `tools.py`, `state.py`, `context.py` |
| Planning, sub-agents with isolated context, a virtual filesystem, runtime-loaded skills | `deepagents` (`create_deep_agent()` returns a compiled graph, so it drops into `root_agent`) | `AGENTS.md`, `examples/` (14 agents), `libs/deepagents/` |
| To understand that harness rather than adopt it | `deep-agents-from-scratch`, the same ideas as notebooks | `notebooks/1_todo.ipynb` → `4_full_agent.ipynb` |
| Iterative research with cited sources | `open_deep_research` | `src/open_deep_research/deep_researcher.py`, `configuration.py`, `prompts.py` |
| Web research into a fixed output schema | `data-enrichment`, with a reflection loop that judges the result | `src/enrichment_agent/graph.py`, `tools.py`, `state.py` |
| Memory across conversations | `langmem` (extraction, consolidation, retrieval over a store), or the [long-term memory](https://docs.langchain.com/oss/python/langchain/long-term-memory) docs | `docs/docs/hot_path_quickstart.md`, `background_quickstart.md` |
| Resuming a thread, durable state, time travel | [persistence](https://docs.langchain.com/oss/python/langgraph/persistence) | |
| Approval gate before a risky action | [interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts) | |
| Multi-agent topologies | `langgraph-supervisor-py` (central router) · `langgraph-swarm-py` (peer handoff); both small | `supervisor.py` / `swarm.py`, `handoff.py` |
| An agent with hundreds of tools | `langgraph-bigtool` (retrieve tools instead of listing them) | |
| Retrieval over your own documents | [knowledge base](https://docs.langchain.com/oss/python/langchain/knowledge-base) · `rag-from-scratch` for technique | |
| Running untrusted code, a per-user sandbox | `deepagents` filesystem backends | |
| Moderating what the agent says | [middleware](https://docs.langchain.com/oss/python/langchain/middleware) | |
| Speaking A2A to other agents | `references/langchain.md` — your scaffold already serves A2A | |

Capabilities with no LangChain example: OAuth user consent, per-user credentials the model
must not see, event or schedule triggers, image and video generation. Those are application code
or infrastructure in a LangChain project — design them yourself.

Gemini models: your scaffold already wires up `ChatGoogleGenerativeAI` from `langchain-google-genai`,
which talks to Gemini platform with your ADC when `GOOGLE_GENAI_USE_VERTEXAI=True` is set (`app/agent.py`
sets it). Most of these repos default to Anthropic or OpenAI, so swap the model line and keep the
rest. Watch for embeddings too: memory and RAG examples often hardcode an OpenAI embedding model.
