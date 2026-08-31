# Direction: Airwallex AI Finance Manager

> Design intent for this **reference demo** — why it exists and what a good finance-manager experience looks like. Not a user guide and not a product specification for a hosted service. Setup lives in [README.md](../README.md) and [repo-guide.md](./repo-guide.md).

## 1. Project thesis

Build a compelling example of what developers can create on top of Airwallex's financial infrastructure using AI agents.

> **Airwallex provides the financial infrastructure. Developers build the intelligence and experiences on top.**

The project should demonstrate that an existing agent framework can connect to Airwallex AgentOS and become a useful, domain-specific finance manager — without rebuilding Airwallex's MCP layer.

## 2. Product concept

### Working name

**AI Finance Manager**

Position it as an AI finance manager / AI CFO for a company.

The user should be able to ask:

- "How much cash do we have right now?"
- "What did we spend the most on this month?"
- "Is anything unusual happening with our spending?"
- "How is our burn changing?"
- "Which vendors are costing us the most?"
- "Prepare our month-end finance report."
- "Prepare this payment for approval."

The agent should retrieve current Airwallex data, reason over it, explain its conclusions, and — where permitted — initiate or prepare workflows.

## 3. Why this is the right demo

A simple Airwallex API demo proves that APIs work.

A simple MCP demo proves that tools can be exposed to an agent.

This project should prove something more interesting:

> **You can take Airwallex's financial capabilities and build an entirely new finance experience around them.**

The demo should focus on:

1. Agent reasoning
2. Financial context
3. Multi-step workflows
4. Custom business logic
5. Human approval for sensitive actions
6. Extensibility for developers

## 4. Recommended architecture

```text
                         ┌─────────────────────┐
                         │    Hermes Agent     │
                         │                     │
                         │      OpenAI         │
                         │       GPT-5.x       │
                         │                     │
                         │  reasoning / memory │
                         │  planning / skills  │
                         └──────────┬──────────┘
                                    │
                               MCP / OAuth
                                    │
                         ┌──────────▼──────────┐
                         │ Airwallex AgentOS   │
                         │        MCP          │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     Airwallex       │
                         │                     │
                         │ Accounts            │
                         │ Transactions        │
                         │ Cards               │
                         │ Expenses            │
                         │ Bills               │
                         │ Payments            │
                         │ FX                  │
                         │ etc.                │
                         └─────────────────────┘
```

### Core stack

- **Agent:** Hermes Agent
- **Model:** OpenAI API
- **Financial connector:** Airwallex AgentOS MCP
- **Custom logic:** Our own finance-manager skills/tools
- **Optional knowledge layer:** company policies, budgets, vendor information
- **Optional event layer:** Airwallex webhooks for proactive monitoring

## 5. Do NOT build an Airwallex MCP proxy initially

Do not create:

```text
Hermes
  ↓
Our MCP
  ↓
Airwallex AgentOS MCP
  ↓
Airwallex
```

unless there is a concrete capability that requires it.

That architecture mostly duplicates the connector layer and does not make the demo more interesting.

Instead:

```text
Hermes
  ├── Airwallex AgentOS MCP
  │
  └── Our custom finance capabilities
```

Our differentiation should live in the **domain intelligence**, not in wrapping Airwallex's MCP.

## 6. What belongs in GitHub

Suggested repository:

```text
airwallex-ai-finance-manager/

├── README.md
├── agent/
│   ├── system_prompt.md
│   ├── skills/
│   │   ├── cash_position.md
│   │   ├── spend_analysis.md
│   │   ├── anomaly_detection.md
│   │   └── month_end.md
│   └── policies/
│       └── financial_controls.md
│
├── mcp/
│   └── custom_tools/
│       ├── cash_runway.py
│       ├── spending_anomalies.py
│       └── budget_variance.py
│
├── examples/
│   ├── investigate_spend.md
│   ├── monthly_close.md
│   └── cash_forecast.md
│
└── docker-compose.yml
```

The repo should make it clear that:

> Airwallex provides the financial primitives; this project demonstrates how to compose them into a higher-level agent experience.

## 7. Custom tools should be domain-oriented

Avoid simply duplicating Airwallex API operations.

Bad:

```text
get_transactions()
get_accounts()
get_balance()
```

Better:

```text
get_cash_runway()
detect_spend_anomalies()
calculate_budget_variance()
generate_cfo_summary()
prepare_month_end()
```

These tools combine Airwallex data with application-specific reasoning.

Example:

```python
@tool
def cash_runway():
    """Calculate how many months of runway the company has."""
    balance = airwallex.get_total_balance()
    monthly_burn = calculate_average_monthly_burn()
    return balance / monthly_burn
```

The exact implementation should evolve based on the capabilities exposed by AgentOS.

## 8. Initial finance-manager skills

### Cash position

Answer:

- Current total cash
- Cash by currency
- Cash by account
- Change versus prior period
- Liquidity concentration

### Spend analysis

Answer:

- Spend this month
- Spend versus last month
- Spend by category
- Spend by vendor
- Spend by employee/card
- Largest transactions

### Anomaly detection

Look for:

- Unusually large transactions
- New vendors
- Vendor spend spikes
- Card spend outliers
- Significant month-over-month changes
- Recurring payments that changed materially

### Budget monitoring

Answer:

- Which budgets are at risk?
- Which categories are over budget?
- Which teams are underspending?
- What changed versus plan?

### Month-end finance

A higher-level workflow:

1. Gather relevant financial data
2. Summarize cash
3. Summarize expenses where available
4. Identify anomalies
5. Identify outstanding bills/expenses
6. Produce a finance-manager summary
7. Highlight items requiring human attention

## 9. Demo storyline

The demo should feel like a real interaction with a finance manager rather than a technology walkthrough.

### Scene 1 — "How much cash do we have?"

User:

> How much cash do we actually have right now?

Agent retrieves current Airwallex data and provides a concise liquidity summary.

### Scene 2 — "Where is the money going?"

User:

> What did we spend the most money on this month?

Agent analyzes transactions and identifies the largest categories/vendors.

### Scene 3 — "Find something weird"

User:

> Anything weird happening with our finances?

Agent investigates and proactively surfaces anomalies.

Example:

> I found three things worth looking at:
>
> 1. A $14,200 payment to a vendor we haven't paid in six months.
> 2. AWS spend is up 31% month over month.
> 3. One employee's card spend is 2.7× their three-month average.

### Scene 4 — "Take action"

User:

> We hired Sarah. Give her a corporate card with a $5,000 monthly limit.

Agent performs the relevant Airwallex workflow, subject to available AgentOS permissions and controls.

### Scene 5 — "Don't move money without me"

User:

> Pay this invoice.

Agent prepares the action and clearly requests confirmation before a sensitive money-out action.

The demo should show **controlled autonomy**, not unrestricted autonomous banking.

## 10. Developer story

The project should explicitly teach this pattern:

```text
Airwallex
    ↓
Financial infrastructure + AgentOS
    ↓
Developer's agent
    ↓
Domain-specific skills
    ↓
New financial experience
```

Core message:

> **You don't need to build a bank. You can build the intelligence layer on top of one.**

This is the strongest reason for the GitHub repository to exist.

## 11. Video / blog vs GitHub

### Video / blog

Optimize for:

- "Wow"
- Natural language interaction
- Visible agent reasoning
- Real financial workflows
- Airwallex capabilities
- The idea that this can be built by developers

Headline direction:

> **I built an AI finance manager on top of Airwallex**

or:

> **What happens when you give an AI agent access to your company's finances?**

### GitHub

Optimize for:

- Reproducibility
- Architecture
- Setup instructions
- Agent configuration
- Custom skills
- Custom tools
- Security/approval model
- Extension points

The video demonstrates the outcome.

The repository demonstrates how to build it.

## 12. Security and permissions

Start read-only where possible.

Recommended progression:

```text
LEVEL 1 — READ
✓ balances
✓ accounts
✓ transactions
✓ cards
✓ expenses
✓ bills
✓ reports

LEVEL 2 — PREPARE
✓ prepare payment
✓ prepare reimbursement
✓ prepare transfer
✗ execute without confirmation

LEVEL 3 — EXECUTE
✓ execute sensitive financial action
✓ only after explicit human approval
```

Keep credentials and authentication out of the model's direct control.

Use Airwallex's supported AgentOS authentication and permission model.

Never allow the model to invent financial data.

For account-specific answers, retrieve current data rather than relying on model memory.

## 13. Future direction: proactive finance manager

Once the basic agent works, add Airwallex webhook/event flows.

```text
Airwallex
   ↓
financial event
   ↓
event processor
   ↓
agent
   ↓
"Something changed..."
```

Potential proactive alerts:

- Spend spike
- New vendor
- Large transaction
- Unusual card activity
- Budget threshold crossed
- Upcoming bill
- Cash balance falling below threshold

This turns the product from a chatbot into an actual **finance monitoring agent**.

## 14. Future direction: company context

Add a company knowledge layer:

```text
Company knowledge
├── Budgets
├── Approval policies
├── Vendor contracts
├── Spending policies
├── Department ownership
└── Finance procedures
```

Then the agent can reason across:

```text
Airwallex data
+
Company policy
+
Business context
=
Finance decision
```

## 15. Definition of success

The project is successful if a developer can look at it and understand:

1. How to connect an existing agent to Airwallex AgentOS.
2. How to give the agent useful financial context.
3. How to add custom domain-specific skills.
4. How to build multi-step finance workflows.
5. How to keep sensitive financial actions behind human approval.
6. How to extend the same pattern into their own application.

The viewer should leave thinking:

> **"I could build my own agent on top of Airwallex."**

## 16. Recommended implementation order

### Phase 1 — Prove the connection

- Set up Hermes
- Connect OpenAI
- Connect Airwallex AgentOS MCP
- Authenticate against a suitable Airwallex environment
- Confirm basic read operations

### Phase 2 — Build the finance-manager persona

- System prompt
- Financial-manager behavior
- Safety/approval policy
- Response style
- Basic finance skills

### Phase 3 — Add differentiated intelligence

Build:

- Cash runway
- Spend analysis
- Anomaly detection
- Budget variance
- CFO summary

### Phase 4 — Build the demo experience

Create a scripted flow covering:

1. Cash
2. Spend
3. Anomaly
4. Action
5. Approval

### Phase 5 — Package for GitHub

- Clean repository
- One-command setup where possible
- Environment configuration
- README architecture diagram
- Example conversations
- Security notes
- Extension guide

### Phase 6 — Tell the story

Produce:

- Demo video
- Technical blog post
- GitHub repository
- Architecture diagram
- Optional short social clips

## 17. Guiding principle

Do not try to demonstrate everything Airwallex can do.

Demonstrate **what becomes possible when Airwallex capabilities are given to an agent**.

The agent is the product experience.

Airwallex is the financial infrastructure.

The custom skills are the developer opportunity.

That is the story.
