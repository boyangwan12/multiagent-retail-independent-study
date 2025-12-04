# Component 6: Research Methodology

**Project:** Multi-Agent Retail Demand Forecasting System
**Date Created:** October 2, 2025
**Last Updated:** October 8, 2025
**Purpose:** Document research process, data collection methods, analysis approach, and methodological rigor

---

## Executive Summary

This Evidence Pack is grounded in primary user research conducted through 5 in-depth semi-structured interviews with retail professionals across diverse organizational contexts (furniture, mass retail, fashion, multi-banner operations). The research employed qualitative methods to understand current workflows, pain points, technology stacks, and user needs, with data collected through detailed interview notes and analyzed using thematic analysis, pain point categorization, and cross-interview validation.

The methodology prioritizes **ecological validity** (real-world contexts), **triangulation** (multiple independent sources confirming findings), and **participant diversity** (varied retail segments, company sizes, roles) to ensure findings are robust and generalizable across the retail demand forecasting domain.

---

## Research Objectives

### Primary Objectives

1. **Problem Validation:** Establish that demand forecasting challenges are real, significant, and pervasive across retail segments
2. **User Need Identification:** Understand specific pain points, workflows, and unmet needs in retail demand planning
3. **Requirements Elicitation:** Extract functional, data, and technical requirements from user contexts
4. **Solution Direction Validation:** Confirm that AI/multi-agent approach aligns with user-expressed preferences and needs

### Secondary Objectives

1. **Workflow Documentation:** Map current-state planning, forecasting, and allocation processes
2. **Technology Landscape Mapping:** Identify existing tools, systems, and workarounds
3. **Success Criteria Definition:** Understand how users would measure solution effectiveness
4. **Horizon vs cadence:** Capture "how far ahead we forecast" vs "how often we run" distinctly across participants/processes
4. **Collaboration Opportunities:** Identify stakeholders willing to provide ongoing validation and testing access

---

## Interview Design

### Interview Structure

**Format:** Semi-structured interviews with open-ended questions
**Duration:** 30-60 minutes per interview
**Mode:** Video call (1-on-1) or in-person
**Recording:** Note-taking during/immediately after interviews; no audio/video recording to encourage candor

**Interview Guide Sections:**
1. **Workflow Understanding:** Current planning, forecasting, and optimization processes
2. **Pain Points:** Specific challenges, frequency, time impact, severity
3. **Time Breakdown:** How analysts/planners spend their time (data prep, analysis, meetings, firefighting, reporting)
4. **Technology Stack:** Systems, tools, Excel usage, workarounds
5. **Key Metrics:** Forecast accuracy, planning cycle time, number of SKUs/stores
6. **Magic Wand Question:** "If you could fix ONE thing, what would it be and how?"

**Rationale for Semi-Structured Approach:**
- **Flexibility:** Allows follow-up questions based on participant responses
- **Depth:** Encourages detailed narrative descriptions of workflows and pain points
- **Comparability:** Core questions consistent across interviews enable cross-interview analysis
- **Discovery:** Open-ended format surfaces unexpected insights and nuances

---

### Interview Guide Development

**Source Documents:**
- Initial project pitch (retail demand forecasting focus)
- Academic literature on retail planning and forecasting
- Industry reports (NRF, Gartner, IHL Group)
- Preliminary understanding of retail workflows

**Interview Guide Iterations:**
1. **Version 1 (INT-001):** High-level workflow and pain point discovery; emphasis on cross-border complexity
2. **Version 2 (INT-002, INT-003):** Added time breakdown questions; refined pain point severity/frequency questions
3. **Version 3 (INT-004, INT-005):** Added technology stack deep-dive; refined "magic wand" question for solution direction validation

**Key Interview Questions:**

**Workflow Understanding:**
- "Walk me through your current planning and forecasting process from start to finish."
- "What are the key steps in your pre-season planning? In-season execution? Optimization?"
- "How do you handle allocation and replenishment decisions?"

**Pain Points:**
- "What are the biggest challenges you face in demand forecasting?"
- "How often does this problem occur? How much time does it cost you?"
- "On a scale of 1-5, how severe is this pain point for your operations?"

**Time Breakdown:**
- "How do you spend a typical week? (Data prep, analysis, meetings, firefighting, reporting)"
- "What are your biggest time wasters?"

**Technology Stack:**
- "What systems and tools do you use for planning, forecasting, inventory management, reporting?"
- "How much do you rely on Excel or manual workarounds?"

**Magic Wand:**
- "If you could fix ONE thing about your demand forecasting process, what would it be?"
- "What would need to happen for that solution to work in your organization?"

---

## Participant Selection and Recruitment

### Selection Criteria

**Diversity Dimensions:**
1. **Retail Segment:** Furniture, mass retail, fashion retail, multi-banner retail
2. **Company Size:** Mid-market (200-400 stores) to enterprise (10,000+ stores)
3. **Role:** Business analyst, planning manager, market analyst, data scientist, BI developer
4. **Geographic Scope:** North America (US/Canada operations)
5. **Experience Level:** Current practitioners with hands-on demand forecasting responsibilities

**Inclusion Criteria:**
- Currently works in or recently worked in retail demand planning/forecasting
- Has direct experience with planning workflows, forecasting tools, and pain points
- Willing to share detailed workflow and technology information
- Available for 30-60 minute interview

**Exclusion Criteria:**
- No current or recent retail demand forecasting experience
- Purely executive role without operational involvement
- Unable to discuss workflows due to confidentiality constraints

---

### Recruitment Process

**Recruitment Channels:**
1. **Professional Networks:** McGill alumni network, LinkedIn connections
2. **Direct Outreach:** Cold outreach to retail professionals via LinkedIn
3. **Referrals:** Snowball sampling from initial participants

**Recruitment Timeline:**
- **Sept 20-23, 2024:** Initial outreach and recruitment
- **Sept 24-29, 2024:** Interview scheduling and execution
- **Sept 30 - Oct 2, 2024:** Follow-up interviews and clarifications

**Response Rate:**
- Outreach to ~15 potential participants
- 5 completed interviews (33% conversion rate)
- 2 additional participants expressed interest but scheduling conflicts prevented interviews

**Ethical Considerations:**
- Voluntary participation (no coercion or incentives offered)
- Informed consent (participants aware of project purpose and how data would be used)
- Anonymity option (2 participants requested company anonymity due to competitive sensitivity)
- Confidentiality (no audio/video recording; notes not shared outside research team)

---

### Participant Demographics

| ID | Role | Company/Industry | Company Size | Geographic Scope | Years Experience |
|---|---|---|---|---|---|
| **INT-001** | Business Analyst | Furniture Manufacturing & Retail (Anonymous) | ~1,000 employees | Global (US/Canada) | Mid-level (inferred) |
| **INT-002** | Planning Manager | Walmart (Mass Retail) | ~10,000 stores globally | Global (US/Canada focus) | Senior (inferred) |
| **INT-003** | Market Analyst | La Vie En Rose (Fashion Retail) | 400+ stores, 20 countries | International (Canada/US expansion) | Mid-level (inferred) |
| **INT-004** | Data Scientist (Marketing/DS) | Canadian Tire (Multi-Banner Retail) | ~1,700 stores, ~250K SKUs | Canada | Mid-Senior (inferred from technical depth) |
| **INT-005** | BI Developer (prev.), Policy & Governance (current) | Groupe Dynamite (prev.), Walmart (current) | Mid-market → Enterprise | International (SE Asia CPG project, Canada retail) | Mid-Senior (cross-industry experience) |

**Diversity Achieved:**
- **Retail Segments:** 4 distinct segments represented
- **Company Sizes:** 200 stores to 10,000+ stores
- **Roles:** Analyst, manager, data scientist, BI developer (operational to technical spectrum)
- **Geographic Experience:** North America (all), Southeast Asia (INT-005)
- **Industry Breadth:** Fashion, furniture, mass retail, multi-banner, CPG

---

## Data Collection Methods

### Interview Notes

**Process:**
1. **During Interview:** Live note-taking on key points, quotes, workflow details
2. **Immediately After:** Detailed note expansion while memory is fresh (within 1-2 hours)
3. **Structured Format:** Template applied to ensure consistency across interviews
   - Section 1: Workflow Understanding
   - Section 2: Pain Points (table format with frequency, time lost, severity)
   - Section 3: Time Breakdown
   - Section 4: Tech Stack & Tools
   - Section 5: Key Metrics
   - Section 6: Quotes to Remember
   - Section 7: Magic Wand Question

**Note Quality:**
- INT-001: Good (high-level, limited quantitative detail)
- INT-002: Excellent (detailed workflow, quantitative time breakdowns)
- INT-003: Excellent (detailed pain points, specific $500K markdown impact)
- INT-004: Excellent (technical depth, narrowed scope (e.g. demand forecasting), infrastructure details)
- INT-005: Excellent (methodology detail, recommendations for project)

**Limitations:**
- No verbatim transcripts (note-taking may miss nuances or exact phrasing)
- Reliance on interviewer interpretation and memory
- Potential bias in what was deemed important to record

---

### Supplementary Data Sources

1. **Public Company Information:**
   - Company websites for store counts, geographic presence
   - Industry reports for company size and market position
   - LinkedIn profiles for participant role validation

2. **Follow-Up Communications:**
   - Email clarifications on specific technical details (e.g., infrastructure, tools)
   - LinkedIn messages for additional context or quote verification

3. **Observational Data:**
   - Participant emphasis and tone (noted in interviews)
   - Workflow diagrams sketched during interviews (captured in notes)
   - Examples and anecdotes shared (documented in quote library)

---

## Data Analysis Approach

### Thematic Analysis

**Process:**
1. **Initial Coding:** Read through all interview notes and identify recurring themes
2. **Code Development:** Create initial code list (e.g., "forecast accuracy," "data preparation burden," "stakeholder friction")
3. **Code Application:** Apply codes to all interview notes systematically
4. **Theme Synthesis:** Group codes into higher-level themes
5. **Cross-Interview Validation:** Verify that themes appear across multiple independent interviews

**Themes Identified:**
1. **Traditional ML Inadequacy:** All 5 interviews mentioned forecast accuracy challenges; 3 explicitly expressed interest in AI/LLM approaches
2. **Data Preparation Burden:** 4 of 5 interviews quantified 50% time spent on data prep (INT-002, INT-003, INT-004, INT-005)
3. **External Factor Blindness:** 5 of 5 interviews mentioned external factors models fail to capture (weather, social trends, economic, competitor)
4. **Forecast Accuracy Plateau:** 2 interviews quantified 60-70% accuracy (INT-002, INT-003); others implied inadequate accuracy
5. **System Fragmentation:** 3 interviews described fragmented tools creating reconciliation burden (INT-002, INT-003, INT-004)
6. **Stakeholder Trust Deficit:** 3 interviews mentioned forecasts overridden or treated as "suggestions" (INT-002, INT-003, INT-004)
7. **Reactive Firefighting Culture:** 3 interviews quantified 6-18 hrs/week on firefighting (INT-002, INT-003, INT-004)

---

### Pain Point Categorization

**Methodology:**
1. **Pain Point Extraction:** Identify discrete pain points from each interview
2. **Severity Rating:** Use participant-provided 1-5 severity ratings (or infer from descriptions)
3. **Frequency Classification:** Categorize as daily/weekly, monthly/seasonal, or irregular
4. **Time Impact Quantification:** Document time lost per week where available
5. **Root Cause Tracing:** Map pain points to root causes (e.g., traditional ML inadequacy, data fragmentation)

**Pain Point Inventory:**
- **Total:** 33 unique pain points extracted from 5 interviews
- **Severity 5 (Critical):** 5 pain points (15%)
- **Severity 4 (High):** 11 pain points (33%)
- **Severity 3 (Medium):** 17 pain points (52%)

**Pain Point Mapping:**
- Created Pain_Point_Inventory.md with full categorization
- Mapped pain points to functional requirements (Requirements_Extract.md)
- Visualized pain cascades (how one pain point triggers downstream issues)

---

### Cross-Interview Validation

**Purpose:** Ensure findings are not idiosyncratic to one participant or company; establish generalizability

**Validation Criteria:**
- **Strong Validation:** Theme or pain point appears in 4-5 interviews
- **Moderate Validation:** Theme or pain point appears in 2-3 interviews
- **Weak Validation:** Theme or pain point appears in 1 interview (documented but flagged as potentially unique)

**Strongly Validated Findings:**
1. **Data Preparation Burden (50% time):** INT-002, INT-003, INT-004, INT-005
2. **External Factor Blindness:** All 5 interviews (INT-001 through INT-005)
3. **Forecast Accuracy Challenges:** All 5 interviews (INT-001 through INT-005)
4. **Interest in AI/LLM Solutions:** INT-001 (explicit), INT-002 (implied in magic wand), INT-004 (Robson AI partnership), INT-005 (methodology guidance for AI approach)

**Moderately Validated Findings:**
1. **Stakeholder Friction:** INT-002, INT-003, INT-004
2. **System Fragmentation:** INT-002, INT-003, INT-004
3. **Firefighting Culture:** INT-002, INT-003, INT-004
4. **Weather Sensitivity:** INT-003, INT-004, INT-005

**Weakly Validated (Segment-Specific) Findings:**
1. **Cross-Border Complexity:** INT-001 (furniture retail, US/Canada operations)
2. **Dealer vs. Company-Operated Complexity:** INT-004 (Canadian Tire multi-banner)
3. **Fashion Trend Volatility:** INT-003, INT-005 (fashion retail specific)

---

### Quote Library Development

**Purpose:** Preserve participant voice and provide evidentiary support for findings

**Process:**
1. **Quote Extraction:** Identify memorable, illustrative quotes during note review
2. **Thematic Organization:** Group quotes by theme (forecast accuracy, data quality, stakeholder friction, magic wand)
3. **Attribution:** Link each quote to participant ID and role
4. **Context Preservation:** Include minimal context to ensure quote meaning is clear

**Quote Library Highlights:**

**Traditional ML Inadequacy:**
> "Traditional numerical ML models don't provide enough accuracy and agility to predict demand" (INT-001)

**Data Preparation Burden:**
> "50% of the time was data cleaning - removing anomalies, making the data clean." (INT-005)

**Stakeholder Friction:**
> "The merchandising team treats our forecasts like 'suggestions' until the numbers prove them wrong - but by then it's too late to course-correct." (INT-003)

**Magic Wand (Solution Direction):**
> "Make forecasting and allocation truly real-time and integrated into a single source that automatically localizes the assortments and rebalances inventory with less (or no) manual handoffs." (INT-002)

**Scope Guidance:**
> "It's good to focus on one [domain]. It would be too much to cover all aspects across different areas like inventory, revenue, or finance." (INT-005)

---

### Requirements Traceability

**Purpose:** Ensure every functional requirement can be traced back to user-expressed needs

**Methodology:**
1. **Pain Point to Requirement Mapping:** Each functional requirement cites source pain points (e.g., FR-01 addresses PP-023, PP-033, PP-005)
2. **Interview Source Attribution:** Each requirement cites source interviews (e.g., FR-01: INT-002, INT-004, INT-005)
3. **Priority Assignment:** High-priority requirements address high-severity, high-frequency pain points

**Traceability Matrix (Sample):**

| Requirement | Pain Points Addressed | Interview Sources | Priority |
|---|---|---|---|
| FR-01: Multi-Source Data Integration | PP-023, PP-033, PP-005 | INT-002, INT-004, INT-005 | High |
| FR-02: Store-Level Forecasting | PP-002, PP-009, PP-015 | INT-001, INT-002, INT-003 | High |
| FR-04: Event-Based Seasonality | PP-021, PP-014 | INT-004, INT-005 | High |
| FR-09: Automated Data Pipeline | PP-027, PP-023, PP-013, PP-010 | All interviews | High |

**Result:** 100% of functional requirements trace to documented pain points from user interviews

---

## Analytical Rigor and Quality Assurance

### Triangulation

**Definition:** Using multiple independent sources to confirm findings

**Application:**
1. **Data Triangulation:** Multiple participants (5 interviews) providing convergent evidence
2. **Methodological Triangulation:** Interview data + supplementary data (company websites, industry reports)
3. **Investigator Triangulation:** Interview notes reviewed by multiple team members for interpretation consistency

**Example:**
- **Finding:** 50% of analyst time spent on data preparation
- **Sources:** INT-002 (10-20 hrs/week), INT-003 (15 hrs/week), INT-004 (~20 hrs/week, 50% of time), INT-005 (50%+ of project time)
- **Validation:** 4 independent sources converge on ~50% figure across different retail segments and roles

---

### Member Checking

**Definition:** Validating findings with participants to ensure accurate interpretation

**Application:**
1. **Follow-Up Questions:** Email/LinkedIn clarifications on specific details (e.g., technology stack, time breakdowns)
2. **Validation Checkpoint Offers:** INT-001 offered planning team access for MVP validation; INT-005 offered project review before submission
3. **Quote Verification (when ambiguous):** Clarified exact phrasing or context when notes were unclear

**Limitations:**
- Full member checking (sharing complete interview notes for participant review) not conducted due to time constraints
- Future improvement: Share synthesized findings with participants for validation

---

### Reflexivity and Bias Mitigation

**Researcher Bias Awareness:**
1. **Confirmation Bias Risk:** Tendency to seek evidence supporting pre-existing belief in AI/multi-agent value
   - **Mitigation:** Explicitly asked "magic wand" question to surface user-driven solution preferences (not leading questions)
   - **Mitigation:** Documented all pain points, including those not directly addressed by multi-agent approach

2. **Interview Bias:** Participants may have exaggerated pain points to be helpful or polite
   - **Mitigation:** Asked for quantitative time/cost estimates to ground qualitative claims
   - **Mitigation:** Cross-interview validation to confirm patterns are genuine, not exaggerated

3. **Selection Bias:** Participants who agreed to interview may be those most frustrated with current systems
   - **Mitigation:** Recruited across diverse roles (analyst to data scientist) and segments (furniture to mass retail)
   - **Limitation:** Acknowledged in research limitations section

---

## Research Limitations and Considerations

### Limitation 1: Sample Size

**Issue:** 5 interviews is a small sample size for quantitative generalization

**Mitigation:**
- Qualitative research prioritizes depth over breadth; 5 in-depth interviews appropriate for exploratory research
- Cross-interview validation ensures themes are not idiosyncratic
- Participant diversity (4 retail segments, varied company sizes) enhances representativeness

**Implication:**
- Findings are indicative, not statistically generalizable
- Future work should expand sample size for quantitative validation (e.g., survey of 50+ retail professionals)

---

### Limitation 2: Geographic Focus

**Issue:** All participants operate primarily in North America (US/Canada); findings may not generalize to Europe, Asia, other markets

**Mitigation:**
- INT-005 brings Southeast Asia CPG experience, providing some geographic breadth
- North American retail is a large, mature market; findings likely relevant to other developed markets

**Implication:**
- Solution should be tested in other geographic contexts before claiming universal applicability
- Cultural and regulatory differences may create unique pain points or requirements

---

### Limitation 3: Company Anonymity Constraints

**Issue:** 2 participants (INT-001, INT-003 partially) requested anonymity, limiting ability to validate company-specific details

**Mitigation:**
- Anonymity respected to encourage candor and detailed sharing
- Industry segment, company size, and role disclosed to provide context

**Implication:**
- Some details (specific technology platforms, exact financial impacts) may be obscured
- Findings remain credible based on role and segment context

---

### Limitation 4: No Audio/Video Recording

**Issue:** Reliance on note-taking may miss nuances, exact quotes, or details

**Mitigation:**
- Notes expanded immediately after interviews while memory fresh
- Follow-up questions sent via email when clarification needed
- Structured interview guide ensures core questions consistently covered

**Implication:**
- Some participant phrasing may be paraphrased rather than verbatim
- Future work should use audio recording (with consent) for higher fidelity data capture

---

### Limitation 5: Potential Selection Bias

**Issue:** Participants who agreed to interview may be those most dissatisfied with current systems, creating negativity bias

**Mitigation:**
- Explicitly asked "magic wand" question to surface positive aspects (what works well) and negative aspects (what doesn't)
- INT-004 (Canadian Tire) described sophisticated existing systems (Robson AI, hybrid cloud) indicating not all participants are purely negative

**Implication:**
- Findings may overemphasize pain points and underemphasize current solutions that work
- Acknowledged as limitation; future work should include "control group" of satisfied users

---

### Limitation 6: Temporal Validity

**Issue:** Interviews conducted Sept 24-29, 2024; retail environment and technology landscape evolve rapidly

**Mitigation:**
- Focused on structural challenges (forecast accuracy, data prep, external factors) that are likely persistent
- Documented specific technology stacks and constraints as of interview date

**Implication:**
- Findings are time-bound; should be refreshed periodically (e.g., annually) to ensure continued relevance

---

### Limitation 7: Researcher Expertise

**Issue:** Interviewer may lack deep retail domain expertise, potentially missing important nuances or follow-up questions

**Mitigation:**
- Preliminary research on retail workflows, terminology, and challenges before interviews
- Open-ended interview format allows participants to guide conversation based on their expertise
- INT-005 provided methodological guidance and validation checkpoint offer

**Implication:**
- Some domain-specific insights may have been missed
- Validation checkpoints (INT-001 planning team, INT-005 expert review) will surface gaps

---

## Ethical Considerations

### Informed Consent

**Process:**
- Participants verbally informed of project purpose (independent study on retail demand forecasting)
- Explained how data would be used (requirements gathering, evidence pack, academic report)
- Confirmed willingness to participate and share information
- Clarified anonymity options (company name, personal name, role details)

**Consent Obtained:** All 5 participants provided verbal consent

---

### Confidentiality and Anonymity

**Commitment:**
- Company anonymity granted to INT-001 (furniture retail) and partially to INT-003 (specific financial details)
- No audio/video recording to reduce participant concern about data sharing
- Notes stored securely and not shared outside research team
- Aggregated findings presented without identifying individual participant details (unless public figures or roles)

**Data Security:**
- Interview notes stored in secure project directory
- No personally identifiable information (PII) beyond role and company (where disclosed)

---

### Participant Burden

**Consideration:**
- Interview duration: 30-60 minutes (within professional norms for informational interviews)
- No follow-up burden required (validation checkpoints are optional)
- No compensation offered (avoided creating coercive incentive)

**Mitigation:**
- Interviews scheduled at participant convenience
- Flexible format (video call or in-person based on preference)
- Option to decline specific questions if too sensitive

---

## Validity and Reliability

### Internal Validity

**Question:** Do findings accurately reflect participant experiences and retail demand forecasting challenges?

**Strengthened By:**
- Semi-structured interviews allowing detailed narrative descriptions
- Quantitative grounding (time estimates, severity ratings, cost impacts)
- Cross-interview validation (themes confirmed across multiple sources)
- Participant quotes preserving original voice

**Threatened By:**
- Interviewer bias in question framing or interpretation
- Participant recall errors (time estimates may be approximate)
- Social desirability bias (participants may exaggerate challenges to be helpful)

**Overall Assessment:** Strong internal validity due to triangulation and detailed data collection

---

### External Validity (Generalizability)

**Question:** Do findings generalize beyond the 5 interviewed companies to broader retail demand forecasting context?

**Strengthened By:**
- Participant diversity (4 retail segments, varied company sizes, multiple roles)
- Cross-industry validation (furniture, mass retail, fashion, multi-banner, CPG)
- Alignment with academic literature and industry reports on retail forecasting challenges

**Threatened By:**
- Small sample size (5 interviews)
- Geographic focus (North America)
- Selection bias (volunteers may be more dissatisfied than average)

**Overall Assessment:** Moderate external validity; findings likely representative of North American retail, but should be validated in other contexts

---

### Reliability (Replicability)

**Question:** Would another researcher conducting similar interviews reach similar conclusions?

**Strengthened By:**
- Structured interview guide ensures consistency
- Transparent thematic analysis process
- Requirements traceability matrix links findings to evidence
- Detailed documentation of methodology

**Threatened By:**
- Semi-structured format allows interviewer discretion in follow-up questions
- Note-taking (vs. recording) introduces interpretation variation
- Thematic analysis involves subjective judgment

**Overall Assessment:** Moderate reliability; structured process and documentation support replicability, but qualitative methods inherently involve interpretation

---

## Documentation and Transparency

### Research Artifacts

**Created Documents:**
1. **Interview Notes:** INT-001_Notes.md through INT-005_Notes.md (5 files)
2. **Pain Point Inventory:** Pain_Point_Inventory.md (33 pain points categorized)
3. **Quote Library:** Quote_Library.md (organized by theme)
4. **Requirements Extract:** Requirements_Extract.md (12 functional requirements, 10 data requirements, 7 technical constraints, 7 success criteria)
5. **Evidence Pack Components:** 6 comprehensive synthesis documents

**Audit Trail:**
- All interview notes stored in project directory with timestamps
- Evidence Pack documents cite source interviews for all claims
- Traceability matrix links requirements to pain points to interviews

---

### Transparent Limitations

**Acknowledged Throughout:**
- Sample size limitations
- Geographic focus (North America)
- Company anonymity constraints
- No audio recording (note-taking limitations)
- Potential selection and confirmation biases

**Mitigation Strategies Documented:**
- Cross-interview validation
- Quantitative grounding where possible
- Triangulation with industry reports and academic literature
- Validation checkpoints with participants (INT-001 planning team, INT-005 expert review)

---

## Contribution to Evidence Pack

### How Methodology Supports Evidence-Based Claims

1. **Problem Validation (Component 1):**
   - 33 documented pain points from 5 independent sources
   - Severity ratings and frequency classifications provide impact quantification
   - Cross-interview validation ensures problem is pervasive, not isolated

2. **User Research Synthesis (Component 2):**
   - Detailed personas grounded in interview data
   - Workflow documentation from participant descriptions
   - Quote library preserves participant voice

3. **Requirements & Constraints (Component 3):**
   - Requirements traceability matrix ensures 100% of requirements derive from user needs
   - Pain point mapping links requirements to documented problems

4. **Approach Validation (Component 4):**
   - "Magic wand" responses validate AI/multi-agent direction
   - Technology stack analysis validates multi-source integration need
   - Interpretability emphasis validates need for transparent AI

5. **Success Metrics (Component 5):**
   - Current baselines derived from quantitative interview data
   - Target improvements grounded in user expectations
   - Measurement methodology informed by participant workflows

6. **Research Methodology (Component 6 - This Document):**
   - Transparent documentation of process
   - Acknowledgment of limitations
   - Validation of rigor and quality

---

## Future Research Directions

### Recommended Extensions

1. **Quantitative Survey:**
   - Expand sample to 50+ retail professionals
   - Validate pain point prevalence and severity quantitatively
   - Test hypotheses about forecast accuracy, data prep time, cost impacts
   

2. **Protocol upgrades for Phase 2 (qual):**
   - Bound scope to the first use case (allocation forecasting) and a three-agent + orchestrator architecture
   - Distinguish allocation vs reallocation flows explicitly
   - Define time-bounded rules for using external signals (e.g., weather short-term only) aligned with horizon/granularity 

3. **Longitudinal Study:**
   - Track same participants over 12-24 months to observe changes in workflows, pain points, technology adoption
   - Monitor evolution of AI/LLM adoption in retail forecasting

4. **Cross-Geographic Validation:**
   - Conduct interviews with European, Asian, Latin American retail professionals
   - Identify regional variations in pain points and requirements

5. **System Deployment Study:**
   - Implement multi-agent forecasting system in real retail context (e.g., INT-001 planning team)
   - Measure actual improvements in forecast accuracy, data prep time, markdown savings
   - Conduct pre/post case study

6. **Comparative Analysis:**
   - Interview retail professionals using advanced AI/ML solutions (e.g., Blue Yonder, o9 Solutions)
   - Compare pain points and workflows to identify what advanced solutions solve vs. what remains unsolved

---

## Summary

This research methodology prioritized **depth over breadth**, employing 5 in-depth semi-structured interviews to understand retail demand forecasting workflows, pain points, and user needs. The approach emphasized:

1. **Ecological Validity:** Real-world practitioners in operational roles
2. **Triangulation:** Multiple independent sources confirming findings
3. **Participant Diversity:** 4 retail segments, varied company sizes, multiple roles
4. **Transparent Limitations:** Acknowledged sample size, geographic focus, potential biases
5. **Rigorous Analysis:** Thematic analysis, pain point categorization, cross-interview validation, requirements traceability
6. **Ethical Practice:** Informed consent, confidentiality, anonymity options, minimal burden

**Methodological Strengths:**
- Strong internal validity (triangulation, detailed data collection)
- Transparent documentation and audit trail
- Requirements 100% traceable to user-expressed needs
- Validation checkpoints with participants (INT-001, INT-005)

**Acknowledged Limitations:**
- Small sample size (5 interviews)
- North American geographic focus
- Note-taking vs. audio recording
- Potential selection bias

**Overall Assessment:** Methodology is appropriate for exploratory, qualitative research aimed at problem validation, requirements elicitation, and solution direction validation. Findings are credible and well-supported, with clear documentation of limitations and future validation opportunities.

---

**Document Status:** Complete
**Last Updated:** October 8, 2025
**Source Material:** Interview Notes INT-001 through INT-005, Interview Process Documentation, Thematic Analysis Outputs
