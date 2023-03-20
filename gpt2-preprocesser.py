import pandas as pd
import re
import nltk
from nltk.corpus import stopwords
from transformers import GPT2Tokenizer, GPT2LMHeadModel

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')

max_length = 1024
chunk_size = 512
stop_words = set(stopwords.words('english'))

# Load the Reddit data from the CSV file
reddit_data = pd.read_csv('chatgptt.csv', usecols=['title', 'top_comments'])

# Combine the post titles and top comments into a single text column
reddit_data['text'] = reddit_data['title'] + ' ' + reddit_data['top_comments'].apply(lambda x: ' '.join(x))

# Remove URLs and special characters from the text column
reddit_data['text'] = reddit_data['text'].apply(lambda x: re.sub(r'http\S+', '', x))
reddit_data['text'] = reddit_data['text'].apply(lambda x: re.sub(r'[^a-zA-Z0-9\s]', '', x))

# Split the text column into smaller chunks to avoid the "Token indices sequence length is longer than the specified maximum sequence length" error
reddit_data['text_chunks'] = reddit_data['text'].apply(lambda x: [x[i:i+chunk_size] for i in range(0, len(x), chunk_size)])

# Tokenize and preprocess each text chunk
reddit_data['tokens'] = reddit_data['text_chunks'].apply(lambda x: [tokenizer.encode(chunk, add_special_tokens=True) for chunk in x])
reddit_data['tokens'] = reddit_data['tokens'].apply(lambda x: [chunk for chunks in x for chunk in chunks])
reddit_data['tokens'] = reddit_data['tokens'].apply(lambda x: [token for token in x if token not in stop_words])

# Save the preprocessed data to a new CSV file
reddit_data.to_csv('reddit_data_preprocessed.csv', index=False)
