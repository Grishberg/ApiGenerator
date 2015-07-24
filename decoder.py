import codecs
class Decoder:
    def __init__(self,cwd):
        self.cwd = cwd
        self.varArray = []
        self.openVars(cwd+"vars.txt")
        self.openStructs(cwd+"structs.txt")
        
    def getType(self, var):
        for i in self.varArray:
            if i[0] == var:
                return [self.getJavaType(i[1]),i[2]]
        return [var,""]

    def openStructs(self, path):
        f = codecs.open(path, "r", "utf-8")
        varsBuf = f.read()
        f.close()
        varArray = []
        lstVars = varsBuf.split("\n")
        index = 0
        for row in lstVars:
            cols = row.split("\t")
            varName = cols[0]
            varType = ""
            varDesc = ""
            if len(cols) == 1:
                varType = cols[0].strip()
                self.varArray[-1][1] += varType
            else:
                varName = cols[0].strip()
                if len(cols) > 1:
                    varType = cols[1].strip()
                self.varArray.append([varName, varName, varType])
                
    def openVars(self, path):
        f = codecs.open(path, "r", "utf-8")
        varsBuf = f.read()
        f.close()
        lstVars = varsBuf.split("\n")
        index = 0
        for row in lstVars:
            cols = row.split("\t")
            varName = cols[0]
            varType = ""
            varDesc = ""
            if len(cols) == 1:
                varDesc = cols[0].strip()
                self.varArray[-1][2] += varDesc
            else:
                varName = cols[0].strip()
                if len(cols) > 1:
                    varType = self.getJavaType(cols[1].strip())
                if len(cols) > 2:
                    varDesc = cols[2].strip()
                self.varArray.append([varName, varType, varDesc])

    def getJavaType(self, t):
        typesApi  = ["string","integer" ,"bool", "float"]
        typesJava = [u"String",u"int"   ,u"boolean", u"float"]
        lowerType = t.lower().strip()
        for i in range(len(typesApi)):
            if lowerType == typesApi[i]:
                return typesJava[i]
        return t
    
    def generateConstNameFromFunc(self, name):
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
                    if out[-2] != '_':
                        out.insert(-1,'_')
                upper = 0
                out.append(i)
        sOut = ""
        for i in out:
            sOut += i
        return sOut.upper()
    
    def generateVarName(self, oldName):
        newName = ""
        lst = oldName.lower().split("_")
        firstSymbol = 1
        for i in lst:
            if firstSymbol:
                newName += i[0].lower()
                firstSymbol = 0
            else:
                newName += i[0].upper()
            if len(i) > 1:
                newName += i[1:]
        return newName

    def isSpace(self, c):
        spaces = " \t\r\n"
        for i in spaces:
            if c == i:
                return True
        return False
    
    def isList(self, word, pos):
        if len(word) - pos > 6:
            if word[pos:pos+5] == "List<":
                return True
        return False
    
    def getParams(self, params, pos):
        word = ""
        words = []
        isBracket = 0
        i = pos
        while i < len(params):
            c = params[i]
            if self.isSpace(c):
                if len(word) > 0:
                    words.append(word)
                    word = ""                
            elif c == ",":
                if len(word) > 0:
                    words.append(word)
                    word = ""
            elif self.isList(params, i):
                i += 5
                lp = self.getParams(params, i)
                words.append(lp[0])
                word = ""
                i = lp[1]
            elif c == ">":
                if len(word) > 0:
                    words.append(word)
                    word = ""
                return [words,i]
            elif c == "(":
                isBracket = 1
            elif isBracket == 0:
                word += c
            elif c==")":
                isBracket = 0
            i += 1
        if len(word) > 0:
            words.append(word)
            word = ""
        return words

    def getFlatConst(self, arr):
        out = ""
        for i in arr:
            if type(i) == type([]):
                out += "//++ array\n"
                s = self.getFlatConst(i)
                out += s
                out += "//-- array\n"
            else:
                out += "public static final String "+ i.upper() + \
                       " = " + '"' + i+ '"'+";\n"
        return out

    def getFlatModel(self, arr):
        out = ""
        for i in arr:
            if type(i) == type([]):
                out += "//++ array\n"
                s = self.getFlatModel(i)
                out += s
                out += "//-- array\n"
            else:
                tp = self.getType(i)
                out += "@SerializedName (RestConst.responseField."+ i.upper() +")\n"
                out += "private "+ tp[0]+" " +\
                       self.generateVarName(i)+";\n\n"
        return out
        
    def generateConst(self, params):
        p = self.getParams(params, 0)
        return self.getFlatConst(p)

    def generateModel(self, params):
        p = self.getParams(params, 0)
        return self.getFlatModel(p)

    def generateConstFunc(self, name):
        return "public static final String "+ self.generateConstNameFromFunc(name) +\
               ' = "/'+name+'";'
    def generateServiceName(self, name):
        return name+"Service"
    def generateInterface(self, name):
        out = "public interface "+self.generateServiceName(name)+" {\n"
        out += "\t@FormUrlEncoded\n"
        out += "\t@POST(RestConst.api."+self.generateConstNameFromFunc(name)+")\n"
        out += "\tvoid "+name+"(@Field(RestConst.field.ACCESS_TOKEN) String accessToken,\n"
        out += "\t\t/*TODO: generate parameters*/,\n"
        out += "\t\tCallback<Response> callback);\n"
        out += "}\n"
        return out
    
    def getWorcerNameFromFuncName(self, name):
        out = name[0].upper() + name[1:] + "Worker"
        return out
    
    def generateService(self, name):
        className = self.getWorcerNameFromFuncName(name)
        serviceName = self.generateServiceName(name)
        out ="public class " + className +" extends BaseWorker{\n"
        out += "public static final String TAG = "+ className + ".class.getSimpleName();\n"
        out += "private static "+className+" sInstance;\n"
        out += "private "+serviceName+" mService;\n"
        out += "private "+className+"() {\n"
        out += "\tmService = buildRestAdapter().create("+serviceName+"+.class);\n"
        out += "}\n\n"
        out += "public static "+className+" getInstance() {\n"
        out += "\tif (sInstance == null) {\n"
        out += "\t\tsInstance = new "+className+"();\n"
        out += "\t}\n"
        out += "\treturn sInstance;\n"
        out += "}\n\n"
        out += "public void "+name+"(/*TODO: add some params*/) {\n"
        out += "\tmService."+name+"(getAccessToken()\n"
        out += "\t\t/*SOME PARAMS*/\n"
        out += "\t\t, new Callback<Request>() {\n"
        out += "\t\t\t@Override\n"
        out += "\t\t\tpublic void success(/*SOME PARAM*/, Response response) {\n"
        out += '\t\t\t\t\tLog.d(TAG, "on success");\n'
        out += '\t/*\n'
        out += '\t\t\t\tRealm realm = Realm.getDefaultInstance();\n'
        out += '\t\t\t\trealm.beginTransaction();\n'
        out += '\t\t\t\trealm.copyToRealmOrUpdate(contentEntry);\n'
        out += '\t\t\t\trealm.commitTransaction();\n'
        out += '\t\t\t\trealm.close();\n'
        out += '\t\t\t\t//App.getBus().post(new '+className+'Event(true));\n'
        out += '\t\t\t*/\n}\n'
        out += '\t\t\t@Override\n'
        out += '\t\t\tpublic void failure(RetrofitError error) {\n'
        out += '\t\t\t\t//App.getBus().post(new GetSimilarEvent(false));\n'
        out += '\t\t\t\tLog.d(TAG, "on fail");\n'
        out += '\t\t\t}\n'
        out += '\t\t});\n'
        out += '\t}\n}\n'
        return out

    
