# Banking Support Agent (Prototype)

A small tool-calling agent built with LangChain and Gemini. Given a customer question, the agent decides on its own which tool(s) to call: a knowledge search (RAG), a loan calculator, or a mock account lookup.

This is a learning prototype built to practice agentic workflows on top of an existing RAG skill set. It uses **synthetic data only**.

## What it does

The agent has three tools:

- `bilgi_ara`: RAG search over a small, self-written FAQ (card fees, limits, early repayment, loan terms, EFT/transfer rules), stored in ChromaDB.
- `kredi_taksiti`: calculates the monthly payment of a loan from amount, term and monthly interest rate.
- `hesap_bilgisi`: returns the balance and recent transactions of a mock customer.

A single question can need several tools. For example, "What is the card fee, what is the balance of customer 1001, and what is the monthly payment for a 100,000 TL loan over 24 months at 3% monthly interest?" makes the agent call all three tools and combine the results in one answer.

## Stack

- Python, LangChain (`create_agent`, tool calling)
- Gemini (`gemini-3.5-flash-lite` by default; other Gemini models can be selected with the `MODEL` environment variable) as the LLM, `gemini-embedding-001` for embeddings
- ChromaDB as the vector store

## Project structure

    agent.py        # tools + agent definition
    index.py        # loads sss.txt into ChromaDB and tests retrieval
    sss.txt         # synthetic FAQ used as the knowledge base
    test_seti.py    # basic tool-selection evaluation (15 questions)
    test_zor.py     # harder tool-selection set (12 questions)
    test_v2.py      # 12 further scenarios: tool selection, arguments, final answer

## Setup

    python -m venv .venv
    source .venv/bin/activate
    pip install langchain langchain-google-genai langchain-chroma python-dotenv

Create a `.env` file with your Gemini API key:

    GOOGLE_API_KEY=your_key_here

Then build the vector store and run the agent:

    python index.py
    python agent.py

## Evaluation

Three question sets, all written by the author. "Tool selection" means the model called the expected tool(s) (or none, where none is the right behaviour). `test_v2.py` also checks the arguments sent to the tools and the final answer.

| Set | Model | Prompt | Result |
|---|---|---|---|
| Basic (15 questions) | gemini-3.6-flash | v1 | 15/15 tool selection |
| Basic (15 questions) | gemini-3.5-flash-lite | v2 | 15/15 tool selection |
| Hard (12 questions) | gemini-3.6-flash | v1 | 7/8 completed; the run was stopped by the free-tier daily quota. One unexpected behaviour: it looked up an account when asked to make a transfer it has no tool for |
| Hard (12 questions) | gemini-3.5-flash-lite | v2 | 12/12 tool selection |
| New scenarios (12) | gemini-3.5-flash-lite | v2 | tool selection 12/12, arguments 6/6 (checked where applicable), final answer 11/12 |

Early runs used gemini-3.6-flash. Because of the free-tier daily quota, later runs switched to gemini-3.5-flash-lite, which is now the default model.

Prompt v2 is v1 plus one rule: the assistant cannot perform actions such as transfers or card cancellation and must say so. The rule was added after the first hard-set run. The prompt was not modified after seeing the results of the 12 new scenarios, so they act as a held-out set.

The final-answer check is automatic (keywords and numbers). Its one miss was a gap in my keyword list: the answer was a correct refusal, so after manual review it is 12/12. The keyword list was then extended, and the set was not re-run to turn the result green.

Run a set with the default model, or choose another one:

    python test_v2.py
    MODEL=gemini-3.6-flash python test_v2.py

Caveats: between rows 3 and 4 both the model and the prompt changed, so the effect of the new rule alone is not isolated. Each result is a single run, and model outputs can vary between runs.

## Limitations

- Prototype with a very small synthetic FAQ and three small, self-written test sets (39 questions in total); the result is indicative, not statistically meaningful.
- Model outputs can vary between runs, so the score may change slightly.
- Final answers are only checked with keyword rules on 12 scenarios, and retrieval quality is not evaluated separately.
- No human-approval step for sensitive actions yet.
- Uses the Gemini API. With real customer data, a locally hosted model would be the safer choice.

## Next steps

- Evaluate answer quality with a stronger method than keyword rules (e.g. human or LLM-based review) and evaluate retrieval quality separately.
- Add a human-approval step before sensitive actions (e.g. card cancellation).
- Compare with a locally hosted model.
- Serve the agent behind a simple API and containerize it.
