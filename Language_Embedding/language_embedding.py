# -*- coding: utf-8 -*-
"""Language_Embedding.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1yMWsB1iAlJoCUyII8YX3ceX8MitMz5iP
"""

from google.colab import drive
drive.mount('/content/drive')

import pandas as pd

# df = pd.read_csv('metadata.csv', on_bad_lines='skip')

# directory = '/content/drive/MyDrive/LJSpeech-1.1/test'

"""### audio"""

import torch
import torchaudio
from transformers import Wav2Vec2Processor, Wav2Vec2Model
import os
import numpy as np

# Load the pre-trained Wav2Vec 2.0 model and processor
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")

# Load audio file
def load_audio(audio_path):
    waveform, sample_rate = torchaudio.load(audio_path)
    # Resample if necessary (Wav2Vec2.0 expects 16kHz audio)
    if sample_rate != 22050:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=22050)
        waveform = resampler(waveform)
    return waveform

# Preprocess audio and extract embeddings
def extract_audio_embedding(audio_path):
    waveform = load_audio(audio_path)

    # Process the waveform using the Wav2Vec 2.0 processor
    input_values = processor(waveform, return_tensors="pt", sampling_rate=16000).input_values

    # Ensure input_values has the shape [batch_size, sequence_length]
    input_values = input_values.squeeze(1)  # Remove the extra dimension if needed

    # Extract hidden states from the model (last hidden state gives embeddings)
    with torch.no_grad():
        hidden_states = model(input_values).last_hidden_state  # Shape: [batch_size, sequence_length, hidden_size]

    # Optionally, you can take the mean of the hidden states to get a fixed-size embedding
    audio_embedding = torch.mean(hidden_states, dim=1)  # Shape: [batch_size, hidden_size]

    return audio_embedding

features = []
directory = '/content/drive/MyDrive/LJSpeech-1.1/test'
for audio in os.listdir(directory):
    audio_path = directory+audio
    a= (audio_path)
    output = extract_audio_embedding(a)
    features.append(output)

len(features)

# # Example usage
# audio_path = "/content/drive/MyDrive/LJSpeech-1.1/test/LJ047-0001.wav"
# embedding = extract_audio_embedding(audio_path)
# print("Audio Embedding Shape:", embedding.shape)



embedding

from IPython.display import Audio
hifigan_output = "/content/drive/MyDrive/LJSpeech-1.1/test/LJ047-0001.wav"
Audio(hifigan_output)

"Report of the President's Commission on the Assassination of President Kennedy. The Warren Commission Report. By The President's Commission on the Assassination of President Kennedy.|Report of the President's Commission on the Assassination of President Kennedy. The Warren Commission Report. By The President's Commission on the Assassination of President Kennedy."

# embedding

# import os
# import numpy as np

# import torch
# import torchaudio
# from transformers import Wav2Vec2Processor, Wav2Vec2Model

# # Load the pre-trained Wav2Vec 2.0 model and processor
# processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
# model = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base-960h")

# # Load audio file
# def load_audio(audio_path):
#     waveform, sample_rate = torchaudio.load(audio_path)
#     # Resample if necessary (Wav2Vec2.0 expects 16kHz audio)
#     if sample_rate != 22050:
#         resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=22050)
#         waveform = resampler(waveform)
#     return waveform

# # Preprocess audio and extract embeddings
# def extract_audio_embedding(audio_path):
#     waveform = load_audio(audio_path)

#     # Process the waveform using the Wav2Vec 2.0 processor
#     input_values = processor(waveform, return_tensors="pt", sampling_rate=16000).input_values

#     # Ensure input_values has the shape [batch_size, sequence_length]
#     input_values = input_values.squeeze(1)  # Remove the extra dimension if needed

#     # Extract hidden states from the model (last hidden state gives embeddings)
#     with torch.no_grad():
#         hidden_states = model(input_values).last_hidden_state  # Shape: [batch_size, sequence_length, hidden_size]

#     # Optionally, you can take the mean of the hidden states to get a fixed-size embedding
#     audio_embedding = torch.mean(hidden_states, dim=1)  # Shape: [batch_size, hidden_size]

#     return audio_embedding

# # # Example usage
# # audio_path = "/content/drive/MyDrive/LJSpeech-1.1/test"
# # embedding = extract_audio_embedding(audio_path)
# # print("Audio Embedding Shape:", embedding.shape)

features = []
directory = '/content/drive/MyDrive/LJSpeech-1.1/test/'
for audio in os.listdir(directory):
    audio_path = directory+audio
    a= (audio_path)
    output = extract_audio_embedding(a)
    features.append(output)

len(features)

"""### Used text as input"""

import torch
from torch import nn
from transformers import BertModel, BertTokenizer

class LanguageEmbeddingModel(nn.Module):
    def __init__(self, mbert_model_name='bert-base-multilingual-cased', mel_spec_dim=(80, 46), embedding_dim=768):
        super(LanguageEmbeddingModel, self).__init__()

        # Load mBERT model and tokenizer
        self.tokenizer = BertTokenizer.from_pretrained(mbert_model_name)
        self.mbert = BertModel.from_pretrained(mbert_model_name)
        self.mel_spec_dim = mel_spec_dim  # Mel spectrogram size
        self.embedding_dim = embedding_dim  # mBERT embedding size

        # Linear layer to project mBERT embedding to match mel spectrogram time dimension
        self.proj_layer = nn.Linear(self.embedding_dim, mel_spec_dim[1])
    #def forward(self, mel_spectrogram, language_text):
    def forward(self, language_text):
        """
        mel_spectrogram: input mel spectrogram of size (batch_size, 80, 46)
        language_text: list of language-specific texts for embedding extraction
        """

        # Tokenize the language input text for mBERT
        language_tokens = self.tokenizer(language_text, return_tensors='pt', padding=True, truncation=True)

        # Get the language embedding from mBERT (we use the CLS token's representation)
        with torch.no_grad():
            language_embedding = self.mbert(**language_tokens).last_hidden_state[:, 0, :]  # CLS token embedding

        # # Project language embedding to match the mel spectrogram time dimension (46)
        # projected_lang_emb = self.proj_layer(language_embedding)  # Shape: (batch_size, 46)

        # # Expand dimensions to concatenate with mel_spectrogram
        # projected_lang_emb = projected_lang_emb.unsqueeze(1)  # Shape: (batch_size, 1, 46)

        # # Repeat language embedding to match the frequency dimension (80)
        # repeated_lang_emb = projected_lang_emb.repeat(1, self.mel_spec_dim[0], 1)  # Shape: (batch_size, 80, 46)

        # # Concatenate language embedding with mel spectrogram along the feature axis
        # combined_input = torch.cat((mel_spectrogram, repeated_lang_emb), dim=2)  # Shape: (batch_size, 80, 92)

        return language_embedding

# Example usage:
if __name__ == "__main__":
    model = LanguageEmbeddingModel()

    # Dummy mel spectrogram input (batch_size=2, 80x46)
    mel_spectrograms = torch.randn(2, 80, 46)

    # Language text input corresponding to different languages
    language_texts = ["Report of the President's Commission on the Assassination of President Kennedy. The Warren Commission Report. By The President's Commission on the Assassination of President Kennedy.|Report of the President's Commission on the Assassination of President Kennedy. The Warren Commission Report. By The President's Commission on the Assassination of President Kennedy."]

    # Forward pass through the model
    output = model(language_texts)

    print(output.shape)  # Output shape: (2, 80, 92) -> Mel spectrogram with language embedding concatenated

output[0][5]

l=[]
for i in range(768):
  a = (output[0][i] in embedding[0])
  #print(output[0][i])
  if a == False:
    l.append(i)

len(l)

### Concat

import torch

a = torch.randn(1,512)
b = torch.randn(1,768)

a.size()

b.size()

combined_output = torch.cat((a, b), dim=1)

combined_output.size()

combined_output = torch.cat((a, b), dim=0)

combined_output