# CSV Sentiment Analyzer

A simple web app to analyze sentiments from comments in a CSV file.  
It supports:
- Uploading raw comments CSV (`comments.csv`).
- Processing comments using backend logic to assign sentiment labels (Positive/Support, Negative/Criticise, Neutral).
- Downloading the processed CSV (`comments_with_sentiment.csv`).
- Uploading the processed CSV to view a **Dashboard** showing the percentage distribution of sentiments.
- (Optional) Running a **summary generator** (currently available as a Google Colab notebook).

---

## 🚀 How It Works

### 1. Input CSV format
You start with a CSV file `comments.csv` that contains:
- `username`
- `comments`
- `topic`

Example:

| username | comments                          | topic   |
|----------|----------------------------------|---------|
| user1    | I love this idea!                 | Topic A |
| user2    | This is a waste of resources.     | Topic A |
| user3    | Not sure if this will even work.  | Topic B |

---

### 2. Sentiment Analysis
1. Go to the **CSV Sentiment Analyzer** page.
2. Upload `comments.csv`.
3. The backend runs sentiment logic and returns a new file:
   - `comments_with_sentiment.csv`

This file will have an extra column (`label`) marking each comment as **Positive (support)**, **Negative (criticize)**, or **Neutral**.

---

### 3. Dashboard
1. Take the `comments_with_sentiment.csv` file.
2. Upload it in the **Dashboard** section.
3. A chart will show what percentage of comments are **Support (Positive)**, **Criticize (Negative)**, and **Neutral** for each topic.

---

### 4. Summarization (Optional)
We also provide a summarization feature that creates summaries of the comments by topic and sentiment.  
⚠️ This is not integrated into the web app yet.

Instead:
- Open the provided Jupyter notebook (`summarizer.ipynb`) in **Google Colab**.
- Upload your `comments_with_sentiment.csv`.
- Run all cells to generate per-topic summaries.



## Run Summary Generator

You can run the summary generator notebook directly in Google Colab:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1qM76-nJPB38J-UwYtuKRTUFtbvBToivO?usp=sharing)

