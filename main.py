import datepicker
import datetime
import fileops

FILE = fileops.EventsStorage('./events.txt')
grammarFiles = ['date.cfg']
interestedNonterminalFile = 'date_interest.tag'

picker = datepicker.AmbiguousDatePicker(grammarFiles,interestedNonterminalFile)

def slotFilling(roottag, tag, word, prob):
    d = {
        'Prep': 'on',
        'Pronoun': 'this',
        'Date-offset': None,
        'Base-date': datetime.date.today()
    }
    '''
    dict = {
        Prep: before, after, on, in, etc.;
        Pronoun: next, this;
        Date-offset: weekdays, today, tomorrow.;
        Base-date: today(by default), any absolute date
    }
    '''
    if roottag == 'Pp_Rel_Date':
        d['Prep'] = word[0]
        d['Pronoun'] = word[1]
        d['Date-offset'] = word[2]
    elif roottag == 'Pp_Abs_Date':
        d['Prep'] = word[0]
        if tag[1] == 'MD':
            md = word[1].split('/-')
            dt = datetime.date(datetime.date.today().year, int(md[0]),int(md[1]))
            d['Base-date'] = dt
        elif tag[1] == 'YMD':
            md = word[1].split('/-')
            dt = datetime.date(int(md[0]),int(md[1]),int(md[2]))
            d['Base-date'] = dt
    elif roottag == 'RelWeekday':
        d['Pronoun'] = word[0]
        d['Date-offset'] = word[1]
    elif roottag == 'Pp_Weekdays':
        d['Prep'] = word[0]
        d['Date-offset'] = word[1]
    return d

def calcActualDate(slot):
    word2digit = {'monday':0,'tuesday':1,'wednesday':2,'thursday':3,'friday':4,'saturday':5,'sunday':6}
    base = slot['Base-date']
    prep = slot['Prep']
    pron = slot['Pronoun']
    offset = slot['Date-offset']
    base_weekday = base.weekday()
    if offset in word2digit:
        target_weekday = word2digit[offset]
    else:
        if offset == 'today':
            target_weekday = base_weekday
        elif offset == 'tomorrow':
            target_weekday = (base_weekday + 1) % 7
    offsetDay = 0
    if pron == 'this':
        offsetDay = target_weekday - base_weekday
    elif pron == 'next':
        offsetDay = 7 - base_weekday + target_weekday
    target_date = base + datetime.timedelta(days=offsetDay)
    print("Today is:", base)
    print("Reminder date is:",target_date)
    return (base,target_date)

while True:
    ipt = input("Todo: ")
    if ipt == 'exit':
        break
    elif ipt == 'ls':
        e = FILE.readFromFile()
        print(e)
        continue
    res = picker.ParseSentence(ipt.split())
    max_len = 0
    max_ind = -1
    for i in range(len(res)):
        if len(res[i][1]) > max_len:
            max_len = len(res[i][1])
            max_ind = i
    actualDate = None
    if max_ind != -1:
        slots = slotFilling(res[max_ind][0],res[max_ind][1],res[max_ind][2],res[max_ind][3])
        actualDate = calcActualDate(slots)
    FILE.saveToFile(ipt,actualDate)
print("Bye!")