def clean_data(text):
    if 'Any text entered here will be displayed in the response input box when a new attempt ' \
       'at the question starts.' in text:
        text = text.replace('Any text entered here will be displayed in the '
                            'response input box when a new attempt at the '
                            'question starts.', '')
        text = text.strip()
        if text == '':
            text = '-'
        return text
