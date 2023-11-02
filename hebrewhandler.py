"""
This module contains a class that handles Hebrew text.
"""

import re

# Range for Hebrew letters excluding punctuation
HEBREW_CHAR_RANGE = r'[\u05D0-\u05EA]'
HIRIK = "\u05B4"  # Hirik unicode
HOLAM = "\u05B9"  # Holam unicode
NIKKUD_RANGE = r'[\u0591-\u05C7]'  # Range for other Niqqud characters


class HebrewHandler:
    """
    A class that handles Hebrew text.
    """
    
    @staticmethod
    def replace_hirik_with_yud(text):
        """
        Replaces the Hirik (dot under word) with its equivalent "י", but only if "י" doesn't immediately follow it.
        """
        return re.sub(f"{HIRIK}(?!י)", "י", text)

    @staticmethod
    def replace_holam_with_vav(text):
        """
        Replaces the Holam (dot above word) with its equivalent "ו", but only if "ו" doesn't immediately follow or precede it.
        """
        return re.sub(f"(?<!ו){HOLAM}(?!ו)", "ו", text)

    @staticmethod
    def remove_nikkud(text):
        """
        Removes all Niqqud from the given text and replaces Hirik and Holam with their equivalent 'י' and 'ו'
        :param text: Text to modify
        :return: Modified text
        """
        # Replace Hirik with its equivalent "י"
        text = HebrewHandler.replace_hirik_with_yud(text)

        # Replace Holam with its equivalent "ו"
        text = HebrewHandler.replace_holam_with_vav(text)

        # Remove other Niqqud
        nikkud = re.compile(NIKKUD_RANGE)
        return nikkud.sub('', text)

    @staticmethod
    def extract_content_words(fields):
        """
        Extracts all content words after removing Niqqud.
        :param fields: List of fields containing Hebrew text
        :return: Set of Hebrew words without Niqqud
        """
        all_content = [HebrewHandler.remove_nikkud(field) for field in fields]
        all_content_words = set(word for field in all_content for word in re.findall(
            f'{HEBREW_CHAR_RANGE}+', field))
        return all_content_words
