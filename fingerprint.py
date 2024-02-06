import librosa
import librosa.display
from scipy.spatial.distance import cosine
import numpy as np
import glob
import pandas as pd
from sklearn.metrics import pairwise
import ast
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw

class audioSpectogram():
    def __init__(self, path, mode, id = 0):
        self.path = path
        self.id = id
        self.samples = None
        self.sample_rate = None
        self.mode = mode
        self.readAudio()    
        self.getData()

    def __del__(self):
        self.path = None
        self.samples = None
        self.sample_rate = None

    def readAudio(self):
        self.samples , self.sample_rate = librosa.load(self.path)
    

    def getData(self):
        if self.sample_rate:
            if self.mode == 1:
                stft = librosa.stft(y = self.samples)

                chroma = librosa.feature.chroma_stft(S = stft)
                chroma_mean = np.mean(chroma, axis=1)

                zero_crossings = librosa.feature.zero_crossing_rate(self.samples)

                mfcc = librosa.feature.mfcc(sr = self.sample_rate, S = stft)
                std_mfcc = np.std(mfcc, axis=1)

                energy = np.sum(np.abs(stft), axis=0)

                fingerprint = np.concatenate([
                    np.angle(chroma_mean),
                    np.abs(chroma_mean),
                    std_mfcc,
                    zero_crossings.flatten(),
                    energy
                ])

                fingerprint_flat = fingerprint.flatten().astype(float)
            else:
                mfcc = librosa.feature.mfcc(y = self.samples, sr = self.sample_rate, n_mfcc = 13)
                fingerprint_flat = mfcc.flatten().astype(float).tolist()


            return fingerprint_flat


    
def loopFolder(path:str,extension:str):
    Files = glob.glob(path + "/*" + extension)
    return Files

def cosine_similarity(a, b, mode):
    if mode == 1:
        return 1 - cosine(a, b)
    else:
        # return pairwise.cosine_similarity(np.array(a).reshape(1, -1), np.array(b).reshape(1, -1))[0, 0]
        return compare_audio_files(a, b)
    
def compare_audio_files(file1, file2, use_dtw=False):

    # Reshape MFCC matrices for cosine similarity calculation
    file1, file2 = np.array(file1), np.array(file2)
    mfccs1_flat = np.reshape(file1, (len(file1), -1))
    mfccs2_flat = np.reshape(file2, (len(file2), -1))

    # Normalize MFCC matrices
    mfccs1_normalized = normalize(mfccs1_flat)
    mfccs2_normalized = normalize(mfccs2_flat)

    if use_dtw:
        # Calculate DTW distance
        distance, _ = fastdtw(mfccs1_flat.T, mfccs2_flat.T, dist=euclidean)
        similarity_score = 1 / (1 + distance)  # Convert distance to similarity score
    else:
        # Calculate cosine similarity on normalized matrices
        similarity_score = pairwise.cosine_similarity(mfccs1_normalized.T, mfccs2_normalized.T)

    return similarity_score  # Directly return the float value


def fingerprint_from_string(fp_str):
    return np.fromstring(fp_str[1:-1], sep=' ')

def compare(path, mode):
    df = pd.read_csv('hashing1.csv') if mode == 1 else pd.read_csv('hashing2.csv')

    input_spectrogram = audioSpectogram(path, mode)
    input_fingerprint = input_spectrogram.getData()

    similarity_scores = []
    for fp_str in df['Fingerprint']:
        stored_fingerprint = fingerprint_from_string(fp_str)
        if mode == 1:
            similarity_scores.append(cosine_similarity(input_fingerprint, stored_fingerprint, mode))
        else:
            stored_mfcc = ast.literal_eval(fp_str)
            similarity_scores.append(cosine_similarity(input_fingerprint, stored_mfcc, mode))

    result_df = df[['Person', 'Phrase']].copy()
    result_df['Similarity Score'] = similarity_scores
    result_df.to_csv('result.csv', index=False)

    if mode == 2:
        result_df['Similarity Score'] = result_df['Similarity Score'].apply(lambda x: x[0][0])

    return similarity_scores, result_df, calculate_max_probability_for_each_person(result_df)


def calculate_max_probability_for_each_person(df):
    grouped_df = df.groupby('Person')

    max_probabilities = []
    for person, group in grouped_df:
        similarity_scores = group['Similarity Score'].values
        exp_scores = np.exp(similarity_scores)
        max_person_probability = np.max(exp_scores / np.sum(exp_scores))
        max_probabilities.append({'Person': person, 'Max Probability': max_person_probability})

    return pd.DataFrame(max_probabilities)

# # Example usage
# similarity_scores, df = compare('./AudioFingerprints/fady/Open middle door/record10.wav', 1)

# # Calculate maximum probabilities for each person
# max_person_probabilities_df = calculate_max_probability_for_each_person(df)

# # Display the result DataFrame with maximum probabilities for each person
# print(max_person_probabilities_df)