import Levenshtein
import logging


logger = logging.getLogger(__name__)
def load_unigram_set_from_arpa(arpa_path):
    """Read unigrams from arpa file."""
    unigrams = set()
    with open(arpa_path) as f:
        start_1_gram = False
        for line in f:
            line = line.strip()
            if line == "\\1-grams:":
                start_1_gram = True
            elif line == "\\2-grams:":
                break
            if start_1_gram and len(line) > 0:
                parts = line.split("\t")
                if len(parts) == 3:
                    unigrams.add(parts[1])
    if len(unigrams) == 0:
        raise ValueError("No unigrams found in arpa file. Something is wrong with the file.")
    return unigrams


def prepare_unigram_set(arpa_path, kenlm_model):
    unigrams = load_unigram_set_from_arpa(arpa_path)
    """Filter unigrams down to vocabulary that exists in kenlm_model."""
    if len(unigrams) < 1000:
        logger.warning(
            "Only %s unigrams passed as vocabulary. Is this small or artificial data?",
            len(unigrams),
        )
    unigram_set = set(unigrams)
    unigram_set = set([t for t in unigram_set if t in kenlm_model])
    retained_fraction = 1.0 if len(unigrams) == 0 else len(unigram_set) / len(unigrams)
    if retained_fraction < 0.1:
        logger.warning(
            "Only %s%% of unigrams in vocabulary found in kenlm model-- this might mean that your "
            "vocabulary and language model are incompatible. Is this intentional?",
            round(retained_fraction * 100, 1),
        )
    return unigram_set


def find_equivalent(word, model):
    max_distance = 2
    # Generate candidate words using the Levenshtein library
    candidates = [candidate for candidate in model.vocab if Levenshtein.distance(word, candidate) <= max_distance]
    if len(candidates) == 0:
        return [word]
    return candidates

# main function for correct mistakes (xatolarni to'g'irlash uchun asosiy funksiya)
def check_and_correct(qism, model, gap_boshi=False, gap_oxiri=False):
    global qiymatlar
    qiymatlar = []
    if gap_boshi:
        if len(qism) == 3:
            # detect candidates
            first = find_equivalent(qism[0], model)
            second = find_equivalent(qism[1], model)
            third = find_equivalent(qism[2], model)
            # find the best first and second word
            bir_ikki = [(model.score('<s> '+i+' '+j),i+' '+j) for j in second for i in first]
            bir_ikki.sort(key=lambda x: x[0], reverse=True)

            bir = bir_ikki[0][1].split()[0]
            qiymatlar.append(bir_ikki[0])
            ikki = bir_ikki[0][1].split()[1]
            # find the best third word
            ikki_uch = [(model.score(ikki+' '+i),ikki+' '+i) for i in third]
            ikki_uch.sort(key=lambda x: x[0], reverse=True)
            uchlist = [(model.score(bir_ikki[0][1]+' '+i)+model.score(ikki+' '+i),i) for i in third]
            uchlist.sort(key=lambda x: x[0], reverse=True)
            uch = uchlist[0][1]
            qiymatlar.append(uchlist[0])

            return bir, ikki, uch
        
        elif len(qism) == 2:
            # detect candidates
            first = find_equivalent(qism[0], model)
            second = find_equivalent(qism[1], model)
            # find the best first and second word
            bir_ikki = [(model.score('<s> '+i+' '+j),i+' '+j) for j in second for i in first]
            bir_ikki.sort(key=lambda x: x[0], reverse=True)

            bir = bir_ikki[0][1].split()[0]
            ikki = bir_ikki[0][1].split()[1]
            qiymatlar.append(bir_ikki[0])
            
            return bir, ikki
        
        elif len(qism) == 1:
            # detect candidates
            first = find_equivalent(qism[0], model)
            # find the best word
            bir = [(model.score('<s> '+i),i) for i in first]
            bir.sort(key=lambda x: x[0], reverse=True)
            
            bir = bir[0][1]
            qiymatlar.append(bir[0])

            return [bir]
        else:
            return ""
        
    elif gap_oxiri:
        third = find_equivalent(qism[2], model)
        uchlist = [(model.score(qism[0]+' '+qism[1]+' '+i+' </s>')+model.score(qism[1]+' '+i+' </s>'),i) for i in third]
        uchlist.sort(key=lambda x: x[0], reverse=True)
        uch = uchlist[0][1]
        qiymatlar.append(uchlist[0])

        return qism[0], qism[1], uch
    
    else:
        third = find_equivalent(qism[2], model)
        uchlist = [(model.score(qism[0]+' '+qism[1]+' '+i)+model.score(qism[1]+' '+i),i) for i in third]
        uchlist.sort(key=lambda x: x[0], reverse=True)
        uch = uchlist[0][1]
        qiymatlar.append(uchlist[0])

        return qism[0], qism[1], uch
    
# the process of correct a sentence (gapni to'g'irlash jarayoni)
def recycle_sentence(model, gap):
    gap = gap.split()
    if len(gap) >= 3:
        for i in range(len(gap)-2):
            if i == 0:
                gap[0], gap[1], gap[2] = check_and_correct(gap[:3], model, gap_boshi=True)
            elif i == len(gap)-3:
                gap[-3], gap[-2], gap[-1] = check_and_correct(gap[i:], model, gap_oxiri=True)
            else:
                gap[i], gap[i+1], gap[i+2] = check_and_correct(gap[i:i+3], model)
    else:
        gap = check_and_correct(gap, model, gap_boshi=True)
        
    return ' '.join(gap)