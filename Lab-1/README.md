# Lab 1 — Requirements Engineering & UML Use-Case Modelling

**Problem Statement #45 — Multi-Cloud Asset Cost Optimization Portal**
**Author:** Akshay Kumar M
**SRN:** PES1UG24CS045

---

## Overview

A FinOps analytics portal that ingests AWS, Azure, and GCP billing CSVs, identifies unattached storage volumes and idle compute instances, generates cost-optimization recommendations, and dispatches budget-breach alerts.

**Actors:** FinOps Analyst, Cloud Administrator

---

## Contents

| Folder | File | Description |
|---|---|---|
| `Requirements/` | `requirements.docx` | Complete requirements table — 5 Functional Requirements (FR-001–FR-005) and 2 Non-Functional Requirements (NFR-001, NFR-002), each with ID, Type, Description, Priority, Acceptance Criteria, and Rationale. |
| `UML/` | `Use_Case_Diagram.pdf` | UML Use-Case Diagram covering both actors, all primary use cases, at least one `<<include>>` relationship, and at least one `<<extend>>` relationship. |
| `Use-Case-Flow/` | `use-case-flow.docx` | One-page Use-Case Flow Specification for the core use case *Detect Idle Compute Instances*, including Preconditions, Postconditions, Main Success Scenario, and one Alternate Flow. |

---

## Summary of Deliverables

1. **Requirements Table** — exactly 5 FRs and 2 NFRs, fully specified.
2. **UML Use-Case Diagram** — FinOps Analyst and Cloud Administrator as actors; *Generate Optimization Recommendations* `<<include>>`s both *Detect Idle Compute Instances* and *Detect Unattached Storage*; *Receive Budget Breach Alert* `<<extend>>`s *Monitor Cloud Spending*.
3. **Use-Case Flow Specification** — detailed flow for *Detect Idle Compute Instances* (FR-002).
