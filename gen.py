s = "getEKInfoSD2"
def getConstName(name):
    out = []
    upper = 0
    for i in name:
        if i.upper() == i:
            if upper == 0:
                #camel
                out.append("_")
                out.append(i)
            else:
                out.append(i)
            upper = 1
        else:
            if upper == 1:
                print "out[-2]",i,out[-2]
                if out[-2] != '_':
                    out.insert(-1,'_')
            upper = 0
            out.append(i)
    sOut = ""
    for i in out:
        sOut += i
    return sOut.upper()

print getConstName(s)
