# from spellchecker import SpellChecker
#
# spellchecker = SpellChecker(language='en')
#
# # Path to the coding_words.txt file
# coding_words_file = 'assets/coding_words.txt'
#
#
# def perform_spell_correction(text):
#     # Open the coding_words.txt file
#     with open(coding_words_file, 'r') as file:
#         # Read the file line by line
#         for line in file:
#             # Remove leading/trailing whitespaces and newline characters
#             word = line.strip()
#
#             # Add the word to the spellchecker's internal dictionary
#             spellchecker.word_frequency.load_words([word])
#     corrected_text = []
#     words = text.split()
#     for word in words:
#         corrected_word = spellchecker.correction(word)
#         corrected_text.append(corrected_word)
#     spell_corr = list(filter(None, corrected_text))
#     return ' '.join(spell_corr)
# def clean_data(file_name):
#     if '/' in file_name:
#         folder_names = file_name.split('/', 1)[0]
#         folder_names = folder_names.replace('.', '').replace(' ', '')
#         if folder_names.startswith('Q'):
#             student_id = file_name.split('/')[1].split()[0]
#             name_parts = file_name.split("-")
#             if len(name_parts) >= 3:
#                 student_name = name_parts[2].strip()
#             if student_id != 'Question' and 'Attempt1_textresponse' in file_name:
#                 text_response = zip_file.read(file_name).decode('utf-8')
#                 text_response = text_response.lower()
#                 if 'any text entered here will be displayed in the response input box when a new attempt ' \
#                    'at the question starts.' in text_response:
#                     text_response = text_response.replace('any text entered here will be displayed in the '
#                                                           'response input box when a new attempt at the '
#                                                           'question starts.', '')
#                     text_response = text_response.strip()
#                     if text_response == '':
#                         text_response = 'null'
#                 if "'s" in text_response:
#                     text_response = text_response.replace("'s", '')
#                 if "don't" in text_response:
#                     text_response = text_response.replace("don't", 'do not')
#                 text_response = re.sub(r'[^a-zA-Z0-9 ]', ' ', text_response)
#                 text_response = perform_spell_correction(text_response)
#                 question = Question(course_id=3, question=folder_names, student_name=student_name,
#                                     student_id=student_id, answer=text_response)
#                 question_dict = question.to_dict()
#                 db.Question.insert_one(question_dict)
#         else:
#             return 'This file is not in the right format'
#     return 'Successfully upload the files'
