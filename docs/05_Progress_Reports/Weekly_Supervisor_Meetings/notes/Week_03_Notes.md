Meeting Date: October 3rd, 2025 

Key Discussion Points: 

Forecasting Horizon and Cadence: 

Forecasting horizon depends on the product lifecycle 

10-12 weeks in fashion vs. continuous replenishment in grocery or CPG. 

Different cadences for different companies 

Monthly allocations, weekly insights, etc. 

Need to distinguish between Horizon (how far ahead to forecast) and Cadence (how often to run the model) in requirements documentation. 

Current notes are mixing the two concepts, which leads to confusion. 

Inventory Allocation and Reallocation: 

Capture both allocation and reallocation as separate use cases. 

External Factors: 

Define rules when external data is usable (short term only). Currently, it assumes external data is always applicable. 

Align factors with data granularity (weather forecasts may not exist 10 months out). 

Data Pipeline: 

Add automated data pipeline setup to the requirements. 

Architecture Discussion: 

Demand forecasting must capture both long-term and short-term needs. 

Original plan focuses on multiple small agents within demand forecasting. 

Agentic AI Architecture must avoid over-complication by creating too many small agents. 

Focus on 3 key agents.  

Define the ML models as tools, not agents. 

ML (time-series forecasting) supports agents, rather than being separate agents. 

Add an orchestrator role where agents communicate through a central orchestrator to share the data and the results. 

Focus on one use case first (allocation forecasting), instead of tackling all at once. 

 

 

 

 

 

 

Next Steps: 

Draft technical architecture for 3 agents (forecasting, inventory, pricing). 

Define data required per agent. 

Define decisions each agent makes. 

Define time horizon and frequency of use. 

Explore spec-driven development tools like Spec Kit (proposed by Fatih) for agent building. 

 

 

--------------- 

Meeting Minutes - Demand Forecasting and Inventory Management System 

Date: October 3rd, 2025 

Key Discussion Points 

1. Forecasting Horizon and Cadence Clarification 

Critical Distinction Identified: The team must differentiate between: 

Horizon: How far ahead to forecast (e.g., 10-12 weeks for fashion, continuous for CPG) 

Cadence: How often to run the model (e.g., monthly, weekly) 

Industry Variations: 

Fashion retail: Fixed lifecycle of 10-12 weeks per product 

Grocery/CPG: Continuous replenishment model 

Current Issue: Requirements documentation is mixing these concepts, causing confusion 

Action: Clearly separate these concepts in all documentation 

2. External Data Integration Constraints 

Key Finding: External data usability is time-bound 

Weather forecasts: Only available for short-term (1-2 weeks) 

Macroeconomic indicators: Cannot predict 10 months ahead 

Competitor data: Time-sensitivity varies 

Requirement: Define rules for when external data is usable (short term only) 

Implementation Need: Align external factors with forecasting granularity and horizon 

3. Architecture Decision: Three-Agent System 

Confirmed Architecture: Focus on 3 key agents: 

Demand Forecasting Agent: Handles all prediction tasks 

Inventory Agent: Manages allocation and reallocation decisions 

Pricing Agent: Develops pricing strategies 

Key Principle: ML models are tools, not agents 

Time-series forecasting models support agents rather than being separate agents 

This avoids over-complication from too many small agents 

Orchestrator Role: Add central orchestrator for agent communication and data sharing 

4. Use Case Prioritization 

Decision: Focus on one use case first - Allocation Forecasting 

Rationale: Avoid tackling all use cases simultaneously 

Three identified use cases: 

Pre-season planning (pricing, promotions) 

Inventory allocation (initial distribution) 

Inventory reallocation (mid-season adjustments) 

5. Tool Selection 

Spec-driven Development: Explore Spec-It tool (proposed by Fatih) 

SDK Research: Investigate Google ADK and OpenAI Agency SDK for agent building 

Additional Pain Points Identified 

6. Data Pipeline Automation 

Critical Issue: Data cleaning consumes 50% of total project time 

Current State: Most companies perform manual data cleaning 

Requirement: Add automated data pipeline setup to requirements 

Impact: Significant efficiency gain potential 

7. Continuous Learning and Feedback Loops 

Current Capability: Companies have only simple feedback loops 

Desired State: Reinforcement learning-based continuous improvement 

Gap: Technical teams understand RL concepts but lack implementation capability 

Business Need: Systems that improve automatically based on actual sales data 

8. Multi-source Data Integration 

Universal Pain Point: Nearly all interviewed companies struggle with data fragmentation 

Current State: Multiple teams duplicate efforts with separate data sources 

Desired Solution: Unified data platform with centralized data aggregation layer 

Historical sales and inventory levels identified as most critical data sources 

9. Real-time Processing Requirements 

Business-IT Gap Example: 

Current: Monthly model runs predicting next month 

Business wants: Weekly forecasts with weekly runs 

Challenge: Operational constraints may not support desired frequency 

Need: Balance business desires with operational feasibility 

10. Model Interpretability 

Stakeholder Concern: Data teams don't understand how models work 

Requirement: High transparency and interpretability 

Impact: Critical for adoption and trust 

11. Inventory Reallocation Considerations 

Mixed Approaches: 

Some companies avoid reallocation due to high transfer costs 

Others want reallocation capability for mid-season adjustments 

Key Factors: 

Transfer costs between stores 

Timing of reallocation decisions 

Confidence in demand shifts 

Action: Document company-specific reallocation strategies and constraints 

12. Omni-channel Coordination 

Emerging Requirement: Integration between online and physical store channels 

Current Gap: Most planning focuses only on physical stores 

Consideration: Not full omni-channel model, but channel coordination needed 

Domain Knowledge Insights Shared 

Product Lifecycle Management 

CPG Model: Continuous replenishment, no fixed endpoint 

Fashion Model: Fixed selling period, clearance at end 

Impact on Forecasting: Determines aggregation periods and horizon 

Demand Forecasting Types by Use Case 

Pre-season: Long-term, considers price elasticity 

Allocation: Medium-term, matches ordering/manufacturing cadence 

Reallocation: Short-term, based on actual performance data 

Data Availability Constraints 

Cannot use future predictions of external factors for long-term forecasting 

Historical external data must be incorporated carefully 

API availability determines real-time factor inclusion 

Next Steps 

Immediate Actions (Week 1) 

Draft technical architecture document for 3 agents (forecasting, inventory, pricing) 

Define per agent: 

Required data inputs 

Decision types and outputs 

Time horizons and run frequencies 

Communication protocols with other agents 

Complete Evidence Pack consolidating all interview findings 

Finalize PRD with corrected horizon/cadence distinctions 

Technical Research (Week 1-2) 

Explore Spec-It tool for spec-driven development 

Research SDKs: 

Google ADK capabilities 

OpenAI Agency SDK features 

Evaluate orchestrator patterns for agent communication 

Follow-up Activities (Week 2+) 

Conduct targeted follow-up interviews focusing on: 

Specific use case details 

Operational constraints 

Data availability and quality 

Create proof-of-concept for highest priority use case (allocation) 

Document learnings from domain expert guidance 

Key Decisions Made 

Pivot from multiple small agents to three main agents 

Treat ML models as tools, not agents 

Implement central orchestrator for coordination 

Start with allocation forecasting as primary use case 

Use Spec-driven development methodology 

Risk Mitigation 

Original approach would have taken years to implement 

New architecture focuses on reusability and maintainability 

Single codebase approach avoids microservice complexity 

Progressive implementation allows for learning and adjustment 

Meeting Outcome 

Successfully redirected technical approach from overly complex multi-agent system to practical three-agent architecture with clear separation between agents (reasoning) and tools (execution). Team has clear understanding of domain requirements and next steps for implementation. 

 

 