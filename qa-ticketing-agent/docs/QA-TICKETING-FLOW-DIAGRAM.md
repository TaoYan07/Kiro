# QA & Auto-Ticketing Agent - Visual Flow

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER QUERY INPUT                             │
│                    "How do I reset my password?"                     │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  1. INTENT CLASSIFIER  │
                    │      (LLM Node)        │
                    │                        │
                    │  Determines:           │
                    │  • question            │
                    │  • issue               │
                    │  • request             │
                    │  + confidence score    │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │  2. KB SEARCH          │
                    │     (MCP Tool)         │
                    │                        │
                    │  🔌 knowledge-base-    │
                    │     server             │
                    │                        │
                    │  • Vector search       │
                    │  • Top 5 results       │
                    │  • Relevance scores    │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │  3. ANSWER GENERATOR   │
                    │      (LLM Node)        │
                    │                        │
                    │  Synthesizes answer    │
                    │  from KB results       │
                    │  + confidence score    │
                    └───────────┬────────────┘
                                │
                                ▼
                    ┌────────────────────────┐
                    │  4. CONFIDENCE CHECK   │
                    │   (Condition Node)     │
                    │                        │
                    │  confidence < 0.7?     │
                    │  OR no KB results?     │
                    └───────┬────────┬───────┘
                            │        │
                    YES ────┘        └──── NO
                     │                      │
                     ▼                      │
        ┌────────────────────────┐         │
        │  5. TICKET CREATOR     │         │
        │     (MCP Tool)         │         │
        │                        │         │
        │  🔌 ticketing-server   │         │
        │                        │         │
        │  Creates ticket with:  │         │
        │  • Title: user query   │         │
        │  • Description: full   │         │
        │    context             │         │
        │  • Priority: based on  │         │
        │    intent              │         │
        │  • Labels: auto-gen    │         │
        └───────────┬────────────┘         │
                    │                      │
                    └──────────┬───────────┘
                               │
                               ▼
                  ┌────────────────────────┐
                  │  6. RESPONSE FORMATTER │
                  │     (Code Node)        │
                  │                        │
                  │  Combines:             │
                  │  • Answer              │
                  │  • Ticket ID (if any)  │
                  └───────────┬────────────┘
                              │
                              ▼
                  ┌────────────────────────┐
                  │      FINAL OUTPUT      │
                  │                        │
                  │  "Here's the answer... │
                  │   Ticket #123 created" │
                  └────────────────────────┘
```

## MCP Server Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    WORKFLOW ENGINE                            │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Workflow Context                         │   │
│  │  • user_query                                         │   │
│  │  • intent_classifier.intent                           │   │
│  │  • kb_search.results                                  │   │
│  │  • answer_generator.response                          │   │
│  │  • ticket_creator.ticket_id                           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└───────────────────┬──────────────────┬───────────────────────┘
                    │                  │
                    │                  │
        ┌───────────▼─────────┐   ┌───▼──────────────┐
        │  MCP: Knowledge     │   │  MCP: Ticketing  │
        │  Base Server        │   │  Server          │
        │                     │   │                  │
        │  Tools:             │   │  Tools:          │
        │  • search_kb        │   │  • create_ticket │
        │  • add_to_kb        │   │  • update_ticket │
        │                     │   │  • search_ticket │
        │  Backend:           │   │                  │
        │  • Vector DB        │   │  Backend:        │
        │  • Embeddings       │   │  • GitHub Issues │
        │                     │   │  • Jira/Linear   │
        └─────────────────────┘   └──────────────────┘
```

## Decision Logic Flow

```
START
  │
  ├─→ Classify Intent
  │     │
  │     ├─→ "question" → priority: medium
  │     ├─→ "issue"    → priority: high
  │     └─→ "request"  → priority: medium
  │
  ├─→ Search Knowledge Base
  │     │
  │     └─→ Returns: results[] + scores
  │
  ├─→ Generate Answer
  │     │
  │     └─→ Returns: answer + confidence
  │
  ├─→ Check Confidence
  │     │
  │     ├─→ confidence >= 0.7 AND results > 0
  │     │     └─→ Return answer only ✓
  │     │
  │     └─→ confidence < 0.7 OR no results
  │           └─→ Create ticket + return answer
  │
  └─→ Format Response
        │
        └─→ END
```

## Example Scenarios

### Scenario 1: High Confidence Answer (No Ticket)
```
Input: "How do I reset my password?"
  ↓
Intent: "question" (confidence: 0.95)
  ↓
KB Search: 3 results found (top score: 0.92)
  ↓
Answer: "To reset your password, go to Settings..." (confidence: 0.95)
  ↓
Confidence Check: PASS (0.95 >= 0.7)
  ↓
Output: "To reset your password, go to Settings..."
Ticket: None
```

### Scenario 2: Low Confidence Answer (Ticket Created)
```
Input: "Why is the new feature not working?"
  ↓
Intent: "issue" (confidence: 0.88)
  ↓
KB Search: 0 results found
  ↓
Answer: "I don't have information about this..." (confidence: 0.3)
  ↓
Confidence Check: FAIL (0.3 < 0.7)
  ↓
Create Ticket: TICKET-1234 (priority: high, labels: [auto-generated, issue])
  ↓
Output: "I don't have enough information. I've created ticket #1234 to track this."
Ticket: TICKET-1234
```

### Scenario 3: Partial Answer (Ticket Created)
```
Input: "How do I configure the advanced settings?"
  ↓
Intent: "question" (confidence: 0.92)
  ↓
KB Search: 1 result found (score: 0.65)
  ↓
Answer: "Based on limited info..." (confidence: 0.6)
  ↓
Confidence Check: FAIL (0.6 < 0.7)
  ↓
Create Ticket: TICKET-1235 (priority: medium)
  ↓
Output: "Here's what I found... I've created ticket #1235 for further assistance."
Ticket: TICKET-1235
```

## Key Features

### 1. Smart Routing
- Intent classification determines priority
- Confidence scoring triggers ticket creation
- Context preserved throughout flow

### 2. Modular Design
- MCP servers are independent
- Easy to swap backends (Jira → Linear)
- Workflow is declarative JSON

### 3. Auto-Escalation
- Low confidence → automatic ticket
- No KB results → automatic ticket
- User context included in ticket

### 4. Extensibility
- Add new MCP servers
- Customize workflow nodes
- Integrate with any ticketing system
