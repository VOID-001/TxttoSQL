from datasets import Dataset
from transformers import T5ForConditionalGeneration, T5Tokenizer, Trainer, TrainingArguments
import pandas as pd
import os

def train_t5_model(csv_file_path: str):
    try:
        # Load the CSV dataset
        df = pd.read_csv(csv_file_path)

        # Ensure the CSV has the expected columns: 'english_query' and 'sql_query'
        if not {'english_query', 'sql_query'}.issubset(df.columns):
            raise ValueError("CSV must contain 'english_query' and 'sql_query' columns.")

        # Convert the pandas DataFrame into Hugging Face Dataset format
        dataset = Dataset.from_pandas(df)

        # Preprocess function to use 'english_query' as input and 'sql_query' as target
        def preprocess_function(examples):
            return {
                'input_text': examples['english_query'],  # English question (text input)
                'target_text': examples['sql_query']  # SQL query (output)
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

        # Ensure train/test split was successful
        if 'train' not in tokenized_dataset or 'test' not in tokenized_dataset:
            raise ValueError("Failed to split dataset into training and validation sets.")

        # Define training arguments
        training_args = TrainingArguments(
            output_dir="./MySQL_t5_model",
            eval_strategy="epoch",  # Use eval_strategy instead of deprecated evaluation_strategy
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
            eval_dataset=tokenized_dataset['test'],
        )

        # Train and save the model
        print("Starting model training...")
        trainer.train()

        # Save the model and tokenizer
        trainer.save_model("./MySQL_t5_model")
        tokenizer.save_pretrained("./MySQL_t5_model")

        print("Model fine-tuned and saved at './MySQL_t5_model'")

    except Exception as e:
        print(f"Error during training: {str(e)}")


if __name__ == "__main__":
    # Set the path to your CSV file here
    csv_file_path = "TxttoSQL.csv"  # Replace this with your actual CSV file path
    train_t5_model(csv_file_path)
