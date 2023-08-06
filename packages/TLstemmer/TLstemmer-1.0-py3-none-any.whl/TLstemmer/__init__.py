def TFLstemmer(inputW, root):
        stem = list()
        str1 = ''
        str2 = '' 
        inputletter = ''
        rootletter = ''
        for x in inputW:
            for y in x['inputT']: 
                inputletter += y
                for r in root:
                    if inputletter == r['stem']:
                        rootletter = r['stem']
               
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
