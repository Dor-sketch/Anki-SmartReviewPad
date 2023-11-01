from PyDictionary import PyDictionary

def generate_sentence_with_word(word):
    dictionary = PyDictionary()
    meaning = dictionary.meaning(word)
    if meaning:
        # Get the first noun meaning if available, else use the first verb meaning
        first_meaning = meaning.get('Noun', meaning.get('Verb'))[0]
        if first_meaning:
            return f"The word '{word}' means '{first_meaning}'."
    return f"Could not generate a sentence for the word '{word}'."
