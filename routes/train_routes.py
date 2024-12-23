from fastapi import APIRouter, UploadFile, File, HTTPException
from datasets import Dataset
from transformers import T5ForConditionalGeneration, T5Tokenizer, Trainer, TrainingArguments
import pandas as pd
import os

train_router = APIRouter()

# Route to fine-tune the T5 model with a CSV dataset
@train_router.post("/train-model/")
async def train_t5_model(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

    try:
        # Load the CSV dataset
        df = pd.read_csv(file.file)

        # Ensure the CSV has the expected columns: 'answer', 'context', 'question'
        if not {'answer', 'context', 'question'}.issubset(df.columns):
            raise HTTPException(status_code=400, detail="CSV must contain 'answer', 'context', and 'question' columns.")

        # Convert the pandas DataFrame into Hugging Face Dataset format
        dataset = Dataset.from_pandas(df)

        # Preprocess function to combine the 'context' and 'question' columns for the input
        def preprocess_function(examples):
            combined_input = [f"Context: {context}. Question: {question}" for context, question in zip(examples['context'], examples['question'])]
            return {
                'input_text': combined_input,  # Combined 'context' and 'question'
                'target_text': examples['answer']  # SQL answer (query)
            }

        # Apply preprocessing
        tokenized_dataset = dataset.map(preprocess_function, batched=True)

        # Load model and tokenizer
        model = T5ForConditionalGeneration.from_pretrained("t5-small")
        tokenizer = T5Tokenizer.from_pretrained("t5-small")

        # Tokenize the input and target text
        def tokenize_function(examples):
            inputs = tokenizer(examples['input_text'], max_length=512, truncation=True, padding="max_length")
            targets = tokenizer(examples['target_text'], max_length=512, truncation=True, padding="max_length")
            inputs['labels'] = targets['input_ids']
            return inputs

        tokenized_dataset = tokenized_dataset.map(tokenize_function, batched=True)

        # Split dataset into train and validation sets
        tokenized_dataset = tokenized_dataset.train_test_split(test_size=0.1)

        # Define training arguments
        training_args = TrainingArguments(
            output_dir="./MySQL_t5_model",
            evaluation_strategy="epoch",
            learning_rate=2e-5,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            num_train_epochs=3,
            save_strategy="epoch",
            logging_dir='./logs',
            logging_steps=10,
        )

        # Trainer for fine-tuning
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_dataset['train'],
            eval_dataset=tokenized_dataset['validation'],
        )

        # Train and save the model
        trainer.train()
        trainer.save_model("./MySQL_t5_model")
        tokenizer.save_pretrained("./MySQL_t5_model")

        return {"detail": "Model fine-tuned and saved at './MySQL_t5_model'"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during training: {str(e)}")
