from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import torch
from transformers import pipeline
import tempfile
import os
from tqdm import tqdm

app = FastAPI()

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Hugging Face model once at startup
device = 0 if torch.cuda.is_available() else -1
sent_pipe = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    device=device,
    return_all_scores=True
)

@app.post("/process_csv")
async def process_csv(file: UploadFile = File(...)):
    try:
        # Save uploaded CSV temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        df = pd.read_csv(tmp_path)
        os.remove(tmp_path)

        # Ensure Comments column exists
        if "Comments" not in df.columns:
            return JSONResponse(
                {"error": "CSV must contain a 'Comments' column"},
                status_code=400
            )

        # Clean Comments column
        df = df[df["Comments"].notna()].copy()
        df["comment_clean"] = (
            df["Comments"].astype(str).str.strip().str.replace(r"\s+", " ", regex=True)
        )
        df = df[df["comment_clean"].str.len() > 2]

        # Sentiment scoring
        pos_scores, neg_scores, sentiment_scores, labels = [], [], [], []
        for comment in tqdm(df["comment_clean"].tolist(), desc="Scoring"):
            try:
                result = sent_pipe(comment[:512])[0]
                scores = {r["label"].upper(): r["score"] for r in result}
                pos = scores.get("POSITIVE", 0.0)
                neg = scores.get("NEGATIVE", 0.0)
                sentiment = pos - neg

                if abs(pos - neg) < 0.15:
                    label = "NEUTRAL"
                elif pos > neg:
                    label = "SUPPORT"
                else:
                    label = "CRITICIZE"

                pos_scores.append(pos)
                neg_scores.append(neg)
                sentiment_scores.append(sentiment)
                labels.append(label)

            except Exception:
                pos_scores.append(None)
                neg_scores.append(None)
                sentiment_scores.append(None)
                labels.append("ERROR")

        # Add results
        df["pos_score"] = pos_scores
        df["neg_score"] = neg_scores
        df["sentiment_score"] = sentiment_scores
        df["label"] = labels

        # Save output CSV
        out_path = tempfile.mktemp(suffix="_with_sentiment.csv")
        df.to_csv(out_path, index=False)

        return FileResponse(
            out_path,
            filename="comments_with_sentiment.csv",
            media_type="text/csv"
        )

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
