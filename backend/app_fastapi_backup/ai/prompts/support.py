SUPPORT_SYSTEM_PROMPT = """You are a helpful customer support AI assistant for {company_name}.
Your tone is {tone} and your personality is {personality}.

Rules:
- Answer ONLY based on the provided context. If the context doesn't contain the answer, say you don't know and offer to connect with a human agent.
- Always cite your sources when referencing specific information.
- Be concise but thorough.
- Never make up information not in the context.
- If asked about billing, refunds, or account issues you cannot resolve, suggest escalating to a human agent.

Context:
{context}
"""

QUERY_REWRITE_PROMPT = """Given the conversation history and the latest user question, rewrite the question to be a standalone search query that captures the full intent.

Conversation:
{history}

Latest question: {question}

Rewritten query:"""

CONFIDENCE_PROMPT = """Rate your confidence (0.0 to 1.0) that your answer is accurate based on the provided context.
Reply with ONLY a number between 0.0 and 1.0.

Question: {question}
Answer: {answer}
Context available: {has_context}"""

TICKET_SUMMARY_PROMPT = """Analyze this customer support conversation and generate a ticket summary.

Conversation:
{conversation}

Respond in JSON format:
{{
  "title": "brief ticket title",
  "summary": "conversation summary",
  "detected_intent": "customer intent",
  "suggested_resolution": "suggested resolution steps",
  "priority": "low|medium|high|critical",
  "category": "technical|billing|refund|feature_request|bug_report"
}}"""
