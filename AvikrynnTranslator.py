import json
import nltk
from PyMultiDictionary import MultiDictionary
import re

nltk.download('averaged_perceptron_tagger')


# Load the English-Avikrynn dictionary from the json file
def _set_en_av_dict():
    with open("en_av_dict.json", "r") as en_av_file:
        return json.load(en_av_file)


# Load the English-English synonyms dictionary from the json file
def _set_en_synonyms():
    with open("en_synonyms.json", "r") as en_synonyms_file:
        return json.load(en_synonyms_file)


# Check if the string contains a whitespace
def contains_whitespace(s):
    return bool(re.search(r'\s', s))


def get_user_confirmation(message):
    proceed = input(f"{message} (y/n)\n").lower()
    return proceed == 'y'


class AvikrynnTranslator:
    def __init__(self):
        self.dictionary = MultiDictionary()
        self.en_av_dict = _set_en_av_dict()
        self.en_synonyms = _set_en_synonyms()
        self.stemmer = nltk.stem.SnowballStemmer('english')

    # Get the synonym for a word, ignore the dictionary check if
    # ignore_dict is True
    def get_synonym(self, choice):
        if choice in self.en_av_dict:
            return choice

        if choice in self.en_synonyms:
            return choice

        synonym_match = choice
        synonyms = self.dictionary.synonym('en', choice)
        synonyms_list = []

        for synonym in synonyms:
            if synonym in self.en_av_dict:
                synonym_match = synonym
            if not contains_whitespace(synonym):
                synonyms_list.append(synonym)

        synonyms.sort()
        self.en_synonyms[choice] = synonyms_list
        self._save_en_synonyms()  # Update synonyms dictionary after new
        # words are added
        self.en_synonyms = _set_en_synonyms()

        return synonym_match

    # Translate a word from English to Avikrynn
    def translate_word(self, word):

        if word in self.en_av_dict:
            return self.en_av_dict[word]

        if self.stemmer.stem(word) in self.en_av_dict:
            return self.en_av_dict[self.stemmer.stem(word)]

        synonym = self.get_synonym(word)
        if synonym in self.en_av_dict:
            return self.en_av_dict[synonym]

        return word

    # 1. Accepts a sentence in English - DONE
    # 2. Identify parts of speech for each word using the NLTK library
    # 3. Remove any words that are not acceptable POS for Avikrynn
    # 4. Translate each word to Avikrynn using the translate_word method
    # TODO: 5. Reconstruct the sentence in Avikrynn using Avikrynn grammar
    #  rules
    # TODO: 6. Return the translated sentence
    def translate_sentence(self, sentence):
        # Tokenize the sentence
        tokens = nltk.word_tokenize(sentence)
        # Get the part of speech for each word
        pos_tags = nltk.pos_tag(tokens)
        print(pos_tags)
        # Remove any words that are not acceptable POS for Avikrynn
        for word, pos in pos_tags:
            if pos in ('EX', 'FW', 'PDT', 'UH'):
                pos_tags.remove((word, pos))
            if word in ('a', 'an', 'the'):
                pos_tags.remove((word, pos))
        print(pos_tags)
        # Translate each word to Avikrynn using the translate_word method
        translated_sentence = []
        for word, pos in pos_tags:
            translated_sentence.append(self.translate_word(word))
        print(translated_sentence)

    # Validate the structure of Avikrynn word
    def validate_avikrynn_word(self, av):
        # Available consonants and vowels
        consonants = ['zh', 'sh', 'th', 'b', 'd', 'g', 'p', 'k', 't', 'v',
                      'z', 'f', 's', 'm', 'n', 'l', 'r', 'w', 'j']
        vowels = ['ah', 'ai', 'au', 'ei', 'ou', 'a', 'e', 'i', 'y', 'o',
                  'u']
        forbidden_combinations = ['ai', 'au', 'ei', 'ou']

        # Create regex pattern
        consonant_pattern = "(" + "|".join(consonants) + ")?"
        vowel_pattern = "(" + "|".join(vowels) + ")"
        avikrynn_pattern = consonant_pattern * 2 + vowel_pattern \
                           + consonant_pattern * 2

        # Find units
        def split_into_units(word):
            # List of individual characters, but treating specific
            # combinations as single units
            special_units = ['zh', 'sh', 'th', 'ah', 'ai', 'au', 'ei', 'ou']
            units = []
            i = 0
            while i < len(word):
                if i <= len(word) - 2 and word[i:i + 2] in special_units:
                    units.append(word[i:i + 2])
                    i += 2
                else:
                    units.append(word[i])
                    i += 1
            return units

        def find_syllables(word):
            units = split_into_units(word)

            # Try to split into multiple syllables
            for i in range(1, len(units) + 1):
                potential_syllable = ''.join(units[:i])
                if re.fullmatch(avikrynn_pattern, potential_syllable) and \
                        potential_syllable in self.en_av_dict.values():
                    result = find_syllables(''.join(units[i:]))
                    if not result and potential_syllable != word:
                        continue
                    return [potential_syllable] + result

            # If no valid combination is found, return None
            return []

        # Initial attempt to find syllables
        if re.fullmatch(avikrynn_pattern, av):
            syllables = [av]
        else:
            syllables = find_syllables(av)

        # If that fails and the word ends with a double consonant
        if not syllables:
            for cons in consonants:
                # If the word ends with a double consonant
                if av.endswith(cons + cons):
                    # Remove the last occurrence of the double consonant
                    av_without_double_consonant = av.rsplit(cons, 1)[0]
                    # Try to find syllables again
                    syllables = find_syllables(av_without_double_consonant)

        # If no valid combination is found return False
        if not syllables:
            print(f"Invalid syllable structure: {av}")
            return False

        # Multi-syllable check
        if len(syllables) > 1:
            # Check if the word ends with a double consonant
            for cons in consonants:
                if av.endswith(
                        cons) and not av.endswith(cons * 2):
                    print(
                        f"Invalid word: {av}. Should end "
                        f"with a double consonant.")
                    return False
        # Single-syllable check
        else:
            # Checks if the word ends with a double consonant
            for cons in consonants:
                if av.endswith(cons * 2):
                    print(
                        f"Invalid word: {av}. Single syllable words should "
                        f"not end with a double consonant.")
                    return False

        # Check for duplicate syllables
        for syllable in syllables:
            if syllables.count(syllable) > 1:
                print(f"Invalid syllable: {syllable}. It appears more than "
                      f"once.")
                return False

        # Check for forbidden combinations
        for syllable in range(len(syllables) - 1):
            if syllables[syllable][-1] + syllables[syllable + 1][0] in \
                    forbidden_combinations:
                print(
                    f"Invalid syllables: {syllables[syllable]} and "
                    f"{syllables[syllable + 1]}. They form a forbidden "
                    f"combination.")
                return False

        return True

    def remove_synonym(self, word, synonym):
        self.en_synonyms[word].remove(synonym)
        if not self.en_synonyms[word]:
            del self.en_synonyms[word]

        if synonym in self.en_synonyms and word in self.en_synonyms[synonym]:
            self.en_synonyms[synonym].remove(word)
            if not self.en_synonyms[synonym]:
                del self.en_synonyms[synonym]

    # Save the updated English-English synonyms dictionary to the json file
    def _save_en_synonyms(self):
        with open("en_synonyms.json", "w") as en_synonyms_file:
            my_keys = list(self.en_synonyms.keys())
            my_keys.sort()
            self.en_synonyms = {k: self.en_synonyms[k] for k in my_keys}
            json.dump(self.en_synonyms, en_synonyms_file, ensure_ascii=False,
                      indent=4)

    # Save the updated English-Avikrynn dictionary to the json file
    def _save_en_av_dict(self):
        with open("en_av_dict.json", "w") as en_av_file:
            my_keys = list(self.en_av_dict.keys())
            my_keys.sort()
            self.en_av_dict = {k: self.en_av_dict[k] for k in my_keys}
            json.dump(self.en_av_dict, en_av_file, ensure_ascii=False,
                      indent=4)

    # Add a new word to the English-Avikrynn dictionary
    def add_word(self, en, av):
        if not en.strip() or contains_whitespace(en):
            print("Your English word contains no text or has whitespace!")
            return False
            # Check for whitespace
        if not av.strip() or contains_whitespace(av):
            print("Your Avikrynn word contains no text or has whitespace!")
            return False
        if not self.validate_avikrynn_word(av):
            return False

        if en in self.en_av_dict:
            print(f"The word '{en}' is already in the dictionary!")
            return False

        # This will speed up the process of finding a word
        av_en_dict = {v: k for k, v in self.en_av_dict.items()}

        if av in av_en_dict:
            print(
                f"The word '{av}' is already in the dictionary as "
                f"{av_en_dict[av]}.\n")
            return False

        self.get_synonym(en)
        synonyms = self.en_synonyms.get(en)
        if synonyms:
            for synonym in synonyms:
                if synonym in self.en_av_dict.keys():
                    print(f"{en} is already in the dictionary as {synonym}.")
                    if not get_user_confirmation(
                            "Would you like to add it anyway?"):
                        return False
                    self.remove_synonym(en, synonym)

        self.en_av_dict[en] = av
        self._save_en_av_dict()
        self._save_en_synonyms()

        return True

    def print_dictionary(self):
        print("English - Avikrynn dictionary:")
        for en, av in self.en_av_dict.items():
            print(f"{en} - {av}")
