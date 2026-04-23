# PRD — AarogyaAid AI-Powered Insurance Recommendation Platform

## User Profile

The primary user is an Indian adult aged 25–60, with low-to-moderate insurance literacy, who is often disclosing a health condition for the first time in a digital context. Their biggest fear is choosing a policy that either rejects their claim or leaves them with a bill they cannot afford.

## Problem Statement

Choosing health insurance in India is confusing because:
1. Policy documents are dense, jargon-heavy, and difficult to compare without expert help.
2. Most comparison platforms rank by price or brand popularity — not by suitability to the user's actual medical and financial profile.
3. Critical details like waiting periods, co-pay requirements, and pre-existing condition exclusions are buried in fine print that patients rarely read.

AarogyaAid solves this by putting an empathetic AI agent between the user and the policy documents. The agent reads the actual uploaded policy PDFs, matches them to the user's health profile, and explains the recommendation in plain language.

## Feature Priority

| Priority | Feature | Rationale |
|---|---|---|
| P0 | Grounded RAG recommendation engine | Drives the two highest-weighted scoring criteria (65%) |
| P0 | Exactly 6-field profile form | Required input contract; spec violation if not exact |
| P0 | Three-part recommendation output | Peer comparison table, coverage detail, Why This Policy |
| P1 | Persistent chat explainer | Session context, term definitions, worked examples |
| P1 | Admin knowledge base panel | Upload, list, edit metadata, delete with vector store removal |
| P2 | Admin authentication | Username/password from env variables |
| P3 | Unit test for recommendation logic | Code quality signal |
| Out of scope | Payment/purchase flow, insurer API integration, OCR for scanned PDFs |

## Recommendation Logic

The recommendation engine matches a user's profile to uploaded policy documents using the following logic:

**Step 1 — Profile ingestion:** All 6 fields are captured and injected into the agent context:
- **Full Name** → personalizes tone and policy summary
- **Age** → determines premium bracket, waiting period sensitivity, and peer group
- **Lifestyle** → adjusts risk weighting; active users prioritized for OPD cover
- **Pre-existing Conditions** → primary filter for exclusion matching and waiting period flagging
- **Income Band** → sets affordability threshold and target cover amount
- **City/Tier** → adjusts preference for network hospital breadth and claim settlement estimates

**Step 2 — Retrieval:** The agent queries the Chroma vector store using a hybrid query combining the user's conditions, income band, and city tier to retrieve the most relevant policy chunks.

**Step 3 — Ranking:** Retrieved policy chunks are ranked by suitability. Policies that exclude the user's pre-existing conditions or exceed their affordability threshold are flagged, not hidden.

**Step 4 — Output generation:** The agent produces all three required sections — peer comparison table, coverage detail table, and a warm personalised explanation connecting the recommendation to the user's specific profile.

**Key principle:** If no policy is a perfect fit, the agent explains the trade-offs and never presents a dead end.

## Assumptions

- Uploaded policy PDFs contain enough text-layer content to extract premiums, waiting periods, exclusions, claim types, and major benefits.
- Users are willing to share personal health conditions if the interface explains why the information is needed and treats it with respect.
- The 54-hour prototype prioritises grounded reasoning over actuarially accurate premium computation.
- Some PDFs may be inconsistently formatted; the admin panel's metadata editing compensates for parsing edge cases.
- Session context is maintained in-memory per request cycle; page refreshes reset the session (documented as known limitation).

## Out of Scope

- Insurer-grade premium calculation or live insurer API integration
- Real payment or policy purchase flow
- OCR pipeline for fully scanned/image-based PDFs
- Multi-admin roles and enterprise IAM
- Cross-device persistent chat history
