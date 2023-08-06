def SecondWord(messagetext):
    quote = messagetext.split(' ')
    quote.pop(0)
    a =' '.join(map(str, quote))
    return a

def NiceList(list):
    nicelist = '\n'.join(list)
    return nicelist

def test():
    print("test")
