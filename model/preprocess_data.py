""" Contains functions to facilitate the connection with the mongo db """

import random

from pymongo import MongoClient
from datasets import load_dataset


class Preprocessor:
    """ Defines a Preprocessor """

    def __init__(self):
        """ Initializes a Preprocessor Instance """
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db     = self.client['laws_db']

        ######## Loading datasets
        self.squad  = load_dataset("rajpurkar/squad")
        print("Squad dataset loaded...")

        self.qa4mre = load_dataset("community-datasets/qa4mre", "2011.main.EN")
        print("qa4mre dataset loaded...")

        # self.trivia = load_dataset("mandarjoshi/trivia_qa", "rc")
        # print("Trivia dataset loaded")

        self.oaulqa = self.load_json_dataset('./data_extraction/qa.jsonl')
        print("Open Australian Legal QA dataset loaded...\n")
        ########

    def load_json_dataset(self, path):
        """ Loads the Open Australian QA Dataset """
        import json

        data = []
        with open(path, 'r') as f:
            for line in f:
                data.append(json.loads(line))
        return data
    
    def paraphrase_one(self, sentence):
        """ Returns 3 paraphrases for a given sentece """
        from transformers import BartForConditionalGeneration, BartTokenizer

        # Load BART model and tokenizer
        model_name = "facebook/bart-large"
        bart_model = BartForConditionalGeneration.from_pretrained(model_name)
        model_tser = BartTokenizer.from_pretrained(model_name)

        # Preprocess input for the model
        input_text = f"paraphrase: {sentence}"

        # Encode input text
        input_ids = model_tser.encode(input_text, return_tensors="pt", truncation=True, padding=True)

        # Generate paraphrase
        output = bart_model.generate(input_ids, max_length=128, num_beams=30, num_return_sequences=4, no_repeat_ngram_size=2)

        # Decode generated paraphrases
        paraphrases = [model_tser.decode(o, skip_special_tokens=True) for o in output]

        # Return the generated paraphrases
        return {paraphrase if paraphrase.endswith('.') else f'{paraphrase}.' for paraphrase in paraphrases}

    def format_data(self, dataset):
        """ Formats the data for the squad dataset """
        qg_examples = []
        qa_examples = []
        for example in dataset:
            # Extract context, question, and expected answers
            context = example['context']
            question = example['question']
            answers = set(example['answers']['text'])

            # QG Task
            qg_examples.append({'task': 'qg', 'context': context, 'question': question})

            # QA Task with all possible answers
            for answer in answers:
                qa_examples.append({'task': 'qa', 'context': context, 'question': question, 'answer': answer})

        return qg_examples + qa_examples

    def generate_answer(self, question, context, answer):
        # List of random phrases to start the answer with
        intro_phrases = [
            "Based on my information",
            "Based on my current information",
            "Based on my current knowledge",
            "It seems that",
            "I think that",
            "According to my understanding",
            "From what I can gather",
        ]

        [print(p) for p in self.paraphrase_one(random.choice(intro_phrases))]
