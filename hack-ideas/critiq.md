## **Project Title:** CritiQ – AI-Powered Document Analyzer with Configurable Evaluation Criteria

### **Overview**
**CritiQ** is a smart, AI-powered tool that ingests structured and unstructured documents—such as RFPs, RFQs, or internal idea proposals—and automatically highlights gaps, risks, and compliance issues based on **customizable evaluation criteria**. Designed for flexibility, CritiQ empowers teams to accelerate governance, procurement, and innovation workflows with intelligent, domain-specific insights.

### **Problem Statement**
Manual document reviews are slow, inconsistent, and prone to oversight. Organizations need a scalable solution that can adapt to different document types and evaluation standards, while providing fast, reliable feedback to support decision-making.

### **Objectives**
- Ingest and analyze documents of various types (e.g., RFPs, RFQs, idea proposals).
- Identify gaps, risks, and compliance issues using configurable guidelines.
- Provide actionable insights to accelerate governance and procurement workflows.
- Enable flexible rule configuration to support diverse business domains and evaluation needs.

### **Use Case Examples**
- **RFQ/RFP Analyzer**: Reviews procurement documents to flag missing components, risks, or misalignments with business requirements.
- **Idea Analyzer**: Evaluates internal proposals for feasibility, completeness, and alignment with strategic goals.

### **Key Features**
1. **Document Ingestion**
   - Accepts multiple formats (PDF, DOCX, TXT).
   - Uses Azure Cognitive Search to extract and index content.

2. **AI-Powered Analysis**
   - Leverages Azure OpenAI to interpret document context.
   - Highlights gaps, risks, and compliance issues.
   - Maps findings to configurable evaluation criteria.

3. **Customizable Evaluation Engine**
   - Allows users to define and update evaluation rules and scoring logic.
   - Supports templates for different document types and business domains.

4. **Insight Generation**
   - Summarizes findings with risk scores, missing elements, and recommendations.
   - Flags ambiguous or incomplete sections.

5. **Workflow Integration**
   - Connects with Power Automate to trigger review, approval, or escalation workflows.
   - Sends alerts or summaries to relevant stakeholders.

### **Tech Stack**
- **AI & NLP**: Azure OpenAI, LangChain
- **Search & Indexing**: Azure Cognitive Search
- **Automation**: Power Automate
- **Frontend**: Power Apps or Streamlit
- **Storage**: Azure Blob Storage

### **Impact**
- Speeds up document review and governance processes.
- Reduces manual effort and human error.
- Improves consistency and transparency in evaluations.
- Enables scalable, domain-specific document analysis.

### **Team Roles**
- **AI Engineer**: Build and fine-tune document analysis models.
- **Solution Architect**: Design configurable evaluation framework.
- **Automation Specialist**: Integrate with Power Automate and enterprise workflows.
- **Frontend Developer**: Build user interface for document upload, rule configuration, and insights.
