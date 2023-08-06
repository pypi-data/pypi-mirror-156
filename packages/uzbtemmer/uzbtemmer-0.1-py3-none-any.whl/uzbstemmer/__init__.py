import csv

with open('stem.csv', newline='') as f:
    reader = csv.reader(f)
    data = [tuple(row) for row in reader]

#for x in data:
#    if x[1] == 'vatan':
#        print(x[1])

def Stemmeruz(inputW):
        stem = list()
        str1 = ''
        str2 = '' 
        inputletter = ''
        rootletter = ''
        for x in inputW:
            for y in x['inputT']: 
                inputletter += y
                for r in data:
                    if inputletter == r[1]:
                        rootletter = r[1]
               
            str1 = inputletter
            str2 = rootletter
            suffix = str1.replace(str2, "")
            if len(rootletter) > 0:
                stem.append("Input Word->"+inputletter+'; Root word->'+rootletter+"; suffix->"+suffix)
            else:
                stem.append('Invalid word!')
            inputletter = ''
            rootletter = ''
        return stem 
