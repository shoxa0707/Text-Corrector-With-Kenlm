import kenlm
from lm import check_and_correct, recycle_sentence, prepare_unigram_set

# load language model (til modelini yuklash)
arpa_path = 'airi.arpa'
model = kenlm.LanguageModel(arpa_path)
model.vocab = prepare_unigram_set(arpa_path, model)

if __name__ == '__main__':
    while True:
        sentence = input() # user input (foydalanuvchi kiritgan gapni olish)
        print(recycle_sentence(sentence)) # return result (yakuniy natijani qaytarish)
