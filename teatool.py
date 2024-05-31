"""
Copyleft 2024, Sunit Bhattacharya
Institute of Formal and Applied Linguistics,
Charles University in Prague, Czech Republic.

Translation Error Analysis Tool (TEA-tool)

This script provides a set of functions to analyze translation outputs based on several quality metrics.
It uses the COMET model to check for paraphrasing and includes various utility functions to check for
empty translations, source copying, repeated substrings, and language detection.

Dependencies:
- pandas
- torch
- comet-ml
- langdetect
- argparse
- re
- os
- sys

Functions:
- check_empty(translations): Calculates the percentage of empty translations.
- check_source_copy(source, translation): Calculates the percentage of translations that directly copy the source text.
- is_repeated_substring(s): Checks if a string contains repeated substrings.
- are_same_language(text1, text2): Checks if two texts are in the same language using `langdetect`.
- are_paraphrases(texts1, texts2, model, batch_size=512): Checks if pairs of texts are paraphrases using a given model.
- check_translation(source, translation, reference, l1, l2): Analyzes translations for various quality metrics.
- write_file(file_info, file_path="translation_stats.csv"): Writes or updates the analysis results in a CSV file.
- analyze(input_file, file, l1, l2): Main function to analyze a file and collect statistics.
- process_file(input_file): Processes a single input file for analysis.
- count_lines(file): Counts the number of lines in a file.

Usage:
Run the script from the command line with a specified input file or directory containing multiple files:

    python script.py input_path

The `input_path` can be a file or a directory. If it is a directory, the script processes all files within it.

Output:
The script generates a CSV file named `translation_stats.csv` containing the analysis results.
If the file already exists, it updates the existing entries or appends new ones.
"""

import sys
import pandas as pd
import os
import re
import argparse

# import sacrebleu
from comet import download_model, load_from_checkpoint
import torch

# Initialize COMET model
comet_model_path = download_model("Unbabel/wmt22-comet-da")
comet_model = load_from_checkpoint(comet_model_path)

def check_empty(translations):
    return sum(1 for t in translations if not t) / len(translations) * 100

def check_source_copy(source, translation):
    return sum(1 for s, t in zip(source, translation) if s in t.strip()) / len(source) * 100

def is_repeated_substring(s):
    doubled_s = (s + s)[1:-1]
    return s in doubled_s

def are_same_language(text1, text2):
    from langdetect import detect
    try:
        return detect(text1) == detect(text2)
    except:
        return False

def are_paraphrases(texts1, texts2, model, batch_size=512):
    if len(texts1) != len(texts2):
        raise ValueError("The length of texts1 and texts2 must be the same")

    batch = [{'src': t1, 'mt': t2, 'ref': t1} for t1, t2 in zip(texts1, texts2)]
    
    try:
        use_cuda = torch.cuda.is_available()
        scores = model.predict(batch, batch_size=512, gpus=1 if use_cuda else 0)['scores']
    except ValueError as e:
        print(f"Error during model prediction: {e}")
    
    paraphrase_threshold = 0.8
    
    return [score >= paraphrase_threshold for score in scores]

def check_translation(source, translation, reference, l1, l2):
    count_empty, count_hallucinate, count_src, count_ref = 0, 0, 0, 0
    results = []

    for s, t, r in zip(source, translation, reference):
        t = t.strip()  
        res = t
        if s in t:
            "Remove the prompt from the translation"
            res = re.sub(fr'\b{re.escape(s)}', '', t)
            res = re.sub(fr'\b{re.escape(l1)}\s*:', '', res)
            res = re.sub(fr'\b{re.escape(l2)}\s*:', '', res)
 
        if len(res.split()) <= 1:
            count_empty += 1

        if is_repeated_substring(res):
            count_hallucinate += 1

        if are_same_language(res, s):
            count_src += 1
        
        if are_same_language(res, r):
            count_ref += 1
 
        results.append(res)
   
    paraphrase_src = sum(are_paraphrases(source, results, comet_model))
    paraphrase_tgt = sum(are_paraphrases(translation, results, comet_model))
    
    return {
        "empty_translation": count_empty / len(source) * 100,
        "repeat_hallucination": count_hallucinate / len(source) * 100,
        "generated_is_src_lang": count_src / len(source) * 100,
        "generated_is_ref_lang": count_ref / len(source) * 100,
        "generated_is_source_paraphrase": paraphrase_src / len(source) * 100,
        "generated_is_reference_paraphrase": paraphrase_tgt / len(source) * 100,
    }

def write_file(file_info, file_path="translation_stats.csv"):
    if not os.path.exists(file_path):
        pd.DataFrame([file_info]).to_csv(file_path, index=False)
    else:
        df = pd.read_csv(file_path)
        if file_info["output_location"] in df["output_location"].values:
            index_to_update = df.index[df["output_location"] == file_info["output_location"]].tolist()[0]
            for key, value in file_info.items():
                df.at[index_to_update, key] = value
        else:
            df = df.append(file_info, ignore_index=True)
        df.to_csv(file_path, index=False)

def analyze(input_file, file, l1, l2):
    print(input_file,l1,l2)
    source = file['source'].tolist()
    translation = file['translation'].tolist()
    reference = file['reference'].tolist()

    stats = {
        "output_location": input_file,
        "empty_output": check_empty(translation),
        "source_copy": check_source_copy(source, translation),
    }

    stats.update(check_translation(source, translation, reference, l1, l2))
    
    return stats

def process_file(input_file):
    
    lang_dic = {
        "hien": "English", "hi": "Hindi",
        "csen": "English", "cs": "Czech",
        "fren": "English", "fr": "French",
    }
    
    l1, l2 = (input_file.split("/")[-1]).split("_")[:2]
    
    if not os.path.exists(input_file):
        print(f"Error: file '{input_file}' not found")
        return

    file = pd.read_csv(input_file, sep='\t')
    if len(file.columns) != 3:
        print("Error: input file should have exactly 3 columns (source, translation, reference)")
        return

    file.columns = ['source', 'translation', 'reference']
    file_stats = analyze(input_file, file, lang_dic[l1], lang_dic[l2])
    write_file(file_stats)

def count_lines(file):
    with open(file, 'r') as f:
        return len(f.readlines())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple tool to analyze translation outputs")
    parser.add_argument("input", help="Input file")
    args = parser.parse_args()

    if not args.input:
        print("Error: input file not provided. Please provide path to a folder/file containing translation outputs")
        sys.exit(1)
    
    if os.path.isdir(args.input):
        for root, dirs, files in os.walk(args.input):
            for file in files:
                input_file = os.path.join(root, file)
                if count_lines(input_file) > 1:
                    process_file(input_file)
    else:
        process_file(args.input)
