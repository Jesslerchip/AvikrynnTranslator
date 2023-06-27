from AvikrynnTranslator import AvikrynnTranslator


def prompt_for_word_translation(translator):
    en = input("Which word should I translate?\n").lower()
    print(translator.translate_word(en))


def prompt_for_sentence_translation(translator):
    en = input("Which sentence should I translate?\n").lower()
    print(translator.translate_sentence(en))


def prompt_for_addition(translator):
    en = input("Which word should I add?\n").lower()
    av = input("What should this word be in Avikrynn?\n").lower()
    translator.add_word(en, av)


def main():
    translator = AvikrynnTranslator()

    while True:
        action = input(
            "Would you like to translate a WORD, translate a SENTENCE, "
            "ADD a word, PRINT the dictionary, or QUIT?\n").lower()
        match action:
            case 'word': prompt_for_word_translation(translator)
            case 'sentence': prompt_for_sentence_translation(translator)
            case 'add': prompt_for_addition(translator)
            case 'print': translator.print_dictionary()
            case 'quit': exit("Goodbye!")
            case _:
                print(
                    "Invalid option. Please type 'translate', 'add', 'print', "
                    "or 'quit'.")


if __name__ == "__main__":
    main()
