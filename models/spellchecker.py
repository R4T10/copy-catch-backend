from spellchecker import SpellChecker


class SpellChecker:
    def __init__(self):
        self.word_frequency = None
        self.spellchecker = SpellChecker(language='en')
        self.coding_words_file = 'assets/coding_words.txt'

    def load_custom_words(self):
        with open(self.coding_words_file, 'r') as file:
            for line in file:
                word = line.strip()
                self.spellchecker.word_frequency.load_words([word])

    def perform_spell_correction(self, text):
        corrected_text = []
        words = text.split()
        for word in words:
            corrected_word = self.spellchecker.correction(word)
            corrected_text.append(corrected_word)
        spell_corr = list(filter(None, corrected_text))
        return ' '.join(spell_corr)

    def correction(self, word):
        pass

