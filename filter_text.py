import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def load_sensitive_words(file_paths):
    sensitive_words = set()
    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            words = file.read().split(',')
            for word in words:
                sensitive_words.add(word.strip())
    return list(sensitive_words)

sensitive_words_files = ['sensitive/sensitive_politics.txt', 'sensitive/sensitive_pornographic.txt', 'sensitive/sensitive_illegal.txt']
sensitive_words = load_sensitive_words(sensitive_words_files)

def remove_duplicates(paragraphs):
    """去重"""
    return list(set(paragraphs))

def filter_sensitive_content(paragraphs, sensitive_words):
    """过滤包含敏感词的段落"""
    filtered_paragraphs = []
    for paragraph in paragraphs:
        if not any(word in paragraph for word in sensitive_words):
            filtered_paragraphs.append(paragraph)
    return filtered_paragraphs

def filter_relevant_content(paragraphs, threshold=0.1):
    """使用TF-IDF向量化和余弦相似度进行相关性筛选"""
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(paragraphs)
    similarities = cosine_similarity(tfidf_matrix)

    relevant_paragraphs = []
    for i, similarity_row in enumerate(similarities):
        if similarity_row.mean() > threshold:
            relevant_paragraphs.append(paragraphs[i])
    
    return relevant_paragraphs

def filter_content(paragraphs, threshold=0.1):
    """综合筛选"""
    unique_paragraphs = remove_duplicates(paragraphs)
    non_sensitive_paragraphs = filter_sensitive_content(unique_paragraphs, sensitive_words)
    relevant_paragraphs = filter_relevant_content(non_sensitive_paragraphs, threshold)
    return relevant_paragraphs