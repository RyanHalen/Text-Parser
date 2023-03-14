def ident(text):
    return text

def extractDigits(text):
    valid_chars = [str(num) for num in range(10)]
    valid_chars.append('.')
    valid_text = [char for char in text if char in valid_chars]
    string = ''.join(valid_text)
    if string.count('.') == 2:
        return string[::-1].replace('.','',1)[::-1]
    else:
        return ''.join(valid_text)

def extractDate(text):
    valid_chars = [str(num) for num in range(10)]
    valid_chars.append('/')
    valid_text = [char for char in text if char in valid_chars]
    return ''.join(valid_text)

def extractJudgementCode(text):
    valid_files = ['JUDDFAT',
               'JDGHD',
               'JWTP',
               'JDGSTPP',
               'JDGACTP',
               'JDGACT',
               'JDSTAP',
               'JWT',
               'JDGSTP',
               'JRV',
               'JDGDACT',
               'JDGSTA',
               'JDGSTAP'
               ]
    
    for file in valid_files:
        if file in text:
            return file