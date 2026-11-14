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
- Gemini (`gemini-3.6-flash`) as the LLM, `gemini-embedding-001` for embeddings
- ChromaDB as the vector store

## Project structure

    agent.py        # tools + agent definition
    index.py        # loads sss.txt into ChromaDB and tests retrieval
    sss.txt         # synthetic FAQ used as the knowledge base
    test_seti.py    # tool-selection evaluation (15 questions)

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

`test_seti.py` runs 15 questions and checks whether the model picks the expected tool(s) on its first step. The set covers single-tool questions, two-tool questions, a customer that does not exist, and an out-of-scope question (no tool expected).

**Result: [X]/15 correct tool selections** (single run, [date]).

What this measures: only tool selection, not answer quality. Failed cases:

- [Question number and a one-line explanation of what went wrong, or "none"]

## Limitations

- Prototype with a very small synthetic FAQ and a 15-question test set; the result is indicative, not statistically meaningful.
- Model outputs can vary between runs, so the score may change slightly.
- Answer correctness and retrieval quality are not evaluated yet.
- No human-approval step for sensitive actions yet.
- Uses the Gemini API. With real customer data, a locally hosted model would be the safer choice.

## Next steps

- Evaluate answer correctness and retrieval quality, not only tool selection.
- Add a human-approval step before sensitive actions (e.g. card cancellation).
- Compare with a locally hosted model.
- Serve the agent behind a simple API and containerize it.
