from preprocess_data import Preprocessor

# Create Preprocessor instance
pssor = Preprocessor()

# Format SQuAD training and validation dataset and print an example
squadt = pssor.format_data(pssor.squad['train'])
squadv = pssor.format_data(pssor.squad['validation'])
