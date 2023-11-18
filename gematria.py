#!/usr/bin/env python3

import argparse
import sqlite3
import pandas as pd
import logging
import os

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

def extract_text(file_path):
    """
    Extracts text from a file based on its extension.
    """
    text = ""
    file_ext = os.path.splitext(file_path)[1].lower()

    try:
        if file_ext == '.csv':
            df = pd.read_csv(file_path)
            text = ' '.join(df.astype(str).sum())
        elif file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        else:
            logger.warning(f"[!] Unsupported file format: {file_ext}")
    except Exception as e:
        logger.error(f"[x] Error processing file {file_path}: {e}")

    return text

def calculate_gematria(word):
    """
    Calculates the Simple Gematria value of a word.
    """
    return sum(ord(char) - 96 for char in word.lower() if char.isalpha())

def calculate_hebrew_gematria(word):
    """
    Calculates the Hebrew Gematria value of a word using the values provided by Gematrix.org.
    """
    hebrew_values = {
        'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9,
        'k': 10, 'l': 20, 'm': 30, 'n': 40, 'o': 50, 'p': 60, 'q': 70, 'r': 80,
        's': 90, 't': 100, 'u': 200, 'x': 300, 'y': 400, 'z': 500, 'j': 600,
        'v': 700, 'w': 900
    }
    return sum(hebrew_values[char] for char in word.lower() if char in hebrew_values)

def calculate_english_gematria(word):
    """
    Calculates the English Gematria value of a word using the values provided by Gematrix.org.
    """
    english_values = {
        'a': 6, 'b': 12, 'c': 18, 'd': 24, 'e': 30, 'f': 36, 'g': 42, 'h': 48, 'i': 54,
        'j': 60, 'k': 66, 'l': 72, 'm': 78, 'n': 84, 'o': 90, 'p': 96, 'q': 102, 'r': 108,
        's': 114, 't': 120, 'u': 126, 'v': 132, 'w': 138, 'x': 144, 'y': 150, 'z': 156
    }
    return sum(english_values[char] for char in word.lower() if char in english_values)

def create_database():
    """
    Creates a SQLite database to store the results.
    """
    conn = sqlite3.connect('gematria.db')
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS words (
            word TEXT PRIMARY KEY, 
            simple_gematria INTEGER,
            hebrew_gematria INTEGER,
            english_gematria INTEGER
        )''')
        conn.commit()
    except Exception as e:
        logger.error(f"[x] Error creating database: {e}")
    finally:
        conn.close()

def insert_word(word, simple_value, hebrew_value, english_value):
    """
    Inserts a word and its three types of gematria values into the database.
    """
    try:
        conn = sqlite3.connect('gematria.db')
        conn.execute('''INSERT OR IGNORE INTO words 
            (word, simple_gematria, hebrew_gematria, english_gematria) 
            VALUES (?, ?, ?, ?)''',
            (word, simple_value, hebrew_value, english_value))
        conn.commit()
    except Exception as e:
        logger.error(f"[x] Error inserting into database: {e}")
    finally:
        conn.close()

def process_file(file_path):
    """
    Process a file, calculate Gematria values, and store in the database.
    """
    text = extract_text(file_path)
    words = set(word for word in text.split() if word.isalpha())
    for word in words:
        simple_value = calculate_gematria(word)
        hebrew_value = calculate_hebrew_gematria(word)
        english_value = calculate_english_gematria(word)
        insert_word(word, simple_value, hebrew_value, english_value)
        logger.info(f"[i] Processed word: {word}, Simple: {simple_value}, Hebrew: {hebrew_value}, English: {english_value}")

def main():
    parser = argparse.ArgumentParser(description='Gematria Calculator')
    parser.add_argument('file', type=str, help='Path to the input file')
    args = parser.parse_args()

    create_database()
    process_file(args.file)

if __name__ == '__main__':
    main()
