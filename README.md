# DropZero – Sentiment Analysis for MoCA E-Consultation
  It addresses the challenge of analyzing large volumes of stakeholder and public feedback received through the Ministry of Corporate Affairs (MoCA) E-Consultation module.
  The solution automates sentiment classification (Positive, Negative, Neutral), generates summaries and word clouds, and provides real-time insights to support data-driven policymaking.

# Objectives:
  Automate sentiment prediction for public comments.
  Reduce manual effort and improve efficiency in reviewing legislative feedback.
  Generate actionable insights with summaries & word clouds.
  Support transparent and data-driven governance.
  Ensure scalability and responsiveness using asynchronous task handling.

# Scope:
  Applies to MoCA E-Consultation feedback on draft legislations.
  Workflow: CSV Upload → Sentiment Analysis → Word Cloud → Summary Generation.
  Decoupled architecture using frontend, backend API, and cloud-hosted database.
  Future scalability for AI dashboards, trend detection, and identity protection.

# Tech Stack:
  Frontend: HTML, CSS, Flask
  Backend: FastAPI, PHP
  Database: MySQL (cloud-hosted)
  AI/ML: Hugging Face Transformers (DistilBERT, RoBERTa)
  Programming: Python, PHP

# Features:
  Sentiment Classification (Positive, Negative, Neutral)
  Word Clouds for SUPPORT, CRITICIZE, and NEUTRAL categories
  Summaries for individual reviews & overall insights
  Bulk Data Upload & Processing (CSV support)
  Real-time Analysis & Visualization

# Future Scope:
  Scalable AI-powered dashboards
  Anonymity & Identity Protection for commenters
  Voice-enabled submissions
  Fake/Spam comment detection
  Trend detection for evolving public sentiment

# References
  * [MCA Acts & Rules](https://www.mca.gov.in/content/mca/global/en/acts-rules/ebooks.html)
  * [DistilBERT Model](https://huggingface.co/distilbert/distilbert-base-uncased-finetuned-sst-2-english)
  * [MyGov – Mann Ki Baat Ideas](https://www.mygov.in/group-issue/inviting-ideas-mann-ki-baat-prime-minister-narendra-modi-28th-september-2025/)

# Conclusion
  DropZero demonstrates how AI can revolutionize public policy feedback mechanisms. By reducing manual review time, enabling instant insights, and ensuring scalability, this solution aligns      with the **vision of New India** through **innovation, efficiency, and transparency**.

