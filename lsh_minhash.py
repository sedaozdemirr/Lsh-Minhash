import os
import glob
from datetime import datetime
import redis
from PyPDF2 import PdfReader
import random
from datasketch import MinHash

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
def create_shingles(text, k):
    shingles = set()
    for i in range(len(text) - k + 1):
        shingle = text[i:i + k]
        shingles.add(shingle)
    return shingles
def read_pdf(file_path):
    with open(file_path, 'rb') as f:
        pdf_reader = PdfReader(f)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text

def generate_minhash(shingles, num_hashes):
    max_shingle = 2 ** 32 - 1
    next_prime = 4294967311

    def hash_func(x):
        return (a * x + b) % next_prime

    hash_funcs = []
    for _ in range(num_hashes):
        a = random.randint(1, max_shingle)
        b = random.randint(0, max_shingle)
        hash_funcs.append(hash_func)

    minhash_values = [float('inf')] * num_hashes

    for shingle in shingles:
        shingle_hash = hash(shingle)
        for i, hash_func in enumerate(hash_funcs):
            hash_value = hash_func(shingle_hash)
            if hash_value < minhash_values[i]:
                minhash_values[i] = hash_value

    return minhash_values
def compute_minhash(shingles):
    minhash = MinHash(num_perm=128)
    for word in shingles:
        minhash.update(word.encode('utf-8'))
    return minhash
def jaccard_similarity(set1, set2):
    intersection = len(list(set(set1).intersection(set2)))
    union = (len(set1) + len(set2)) - intersection
    return float(intersection) / union

def main():
    t1=datetime.now()
    directory = 'C:/path'  # PDF dosyalarının bulunduğu klasör
    k = 5  # Shingling boyutu
    pdf_files = glob.glob(os.path.join(directory, '*.pdf'))
    num_files = len(pdf_files)
    result_list=[]
    shingle_sets = []
    minhash_values = []
    # Shingle'ları ve MinHash değerlerini oluşturma
    for file_path in pdf_files:
        text = read_pdf(file_path)
        shingles = create_shingles(text, k)
        shingle_sets.append(shingles)
        # minhash = generate_minhash(shingles, num_hashes)
        minhash = compute_minhash(shingles)
        minhash_values.append(minhash.hashvalues)
    print(minhash_values)

    # Jaccard benzerliği hesaplama
    for i in range(num_files):
        for j in range(num_files):

            similarity = jaccard_similarity(shingle_sets[i], shingle_sets[j])*100
            # print(f"Similarity between file {pdf_files[i]} and file {pdf_files[j]}: {similarity}")

        # MinHash benzerliği hesaplama
        for j in range(num_files):
            minhash_similarity = jaccard_similarity(minhash_values[i], minhash_values[j])*100
            # r.set(j, m.packb(minhash_values[j]))
            # print(f"MinHash similarity between file {pdf_files[i]} and file {pdf_files[j]}: {minhash_similarity}")
            result_list.append(minhash_similarity)
    t2=datetime.now()
    print("Total time: ", t2-t1)
    return result_list
if __name__ == '__main__':
    main()
