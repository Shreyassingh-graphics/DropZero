from fastapi import FastAPI, BackgroundTasks
from pymysql import Error
import pymysql.cursors
import pandas as pd
from transformers import pipeline
import gc

app = FastAPI()

# Global variable to hold the model. It starts as None.
SENT_PIPE = None

# ------------------ DATABASE CONNECTION ------------------ #
def get_db_connection():
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="DropZero",
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Error as e:
        print(f"❌ DATABASE ERROR: Could not connect to MySQL. Error: {e}")
        return None

# ------------------ SENTIMENT ANALYSIS LOGIC ------------------ #
def run_sentiment_analysis():
    global SENT_PIPE # We need to modify the global variable

    try:
        # LAZY LOADING: Load the model only if it hasn't been loaded yet.
        if SENT_PIPE is None:
            print("Model is not loaded. Loading now (this will only happen once)...")
            model_name = "cardiffnlp/twitter-roberta-base-sentiment"
            SENT_PIPE = pipeline(
                "sentiment-analysis",
                model=model_name,
                tokenizer=model_name,
                device=-1,
                return_all_scores=True
            )
            print("✅ Model has been loaded for the first time and is now in memory.")

        print("🚀 Starting sentiment analysis process...")
        conn = get_db_connection()
        if not conn:
            print("❌ Aborting analysis because database connection failed.")
            return

        cursor = conn.cursor()
        print("Clearing old sentiment results...")
        cursor.execute("DELETE FROM sentiment_score")
        conn.commit()

        print("Fetching comments from the database...")
        cursor.execute("SELECT username, comment, discussion_topic FROM comment")
        comments_data = cursor.fetchall()
        
        if not comments_data:
            print("No comments found to analyze.")
            cursor.close()
            conn.close()
            return
            
        df = pd.DataFrame(comments_data)
        # ... (rest of the analysis code is the same) ...
        df["comment_clean"] = (
            df["comment"].astype(str)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
        )
        df = df[df["comment_clean"].str.len() > 2].copy()
        
        results = []
        for index, row in df.iterrows():
            comment_text = row['comment_clean']
            analysis_result = SENT_PIPE(comment_text[:512])[0]
            scores = {r['label']: r['score'] for r in analysis_result}
            pos = scores.get('LABEL_2', 0.0)
            neg = scores.get('LABEL_0', 0.0)
            sentiment_score = pos - neg
            highest_score_label = max(scores, key=scores.get)
            if highest_score_label == 'LABEL_2':
                label = "SUPPORT"
            elif highest_score_label == 'LABEL_0':
                label = "CRITICIZE"
            else:
                label = "NEUTRAL"
            results.append(tuple([
                row['username'], row['comment'], row['discussion_topic'], comment_text,
                pos, neg, sentiment_score, label
            ]))

        print("Saving results to the database...")
        insert_query = """
            INSERT INTO sentiment_score
            (username, comment, discussion_topic, comment_clean, pos_score, neg_score, sentiment_score, label)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(insert_query, results)
        conn.commit()
        print("✅ Sentiment analysis complete!")
        
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ An unexpected error occurred in the analysis thread: {e}")

# ------------------ API ENDPOINT ------------------ #
@app.post("/analyze")
def trigger_analysis(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_sentiment_analysis)
    return {"message": "Sentiment analysis process has been started."}