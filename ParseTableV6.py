from progress.bar import IncrementalBar

#bar = IncrementalBar('Прогресс ', max = lineCount)
#file = open('D:\\ObjTxt\\AllObjTest.txt', 'r', encoding='866')
#file = open('D:\\ObjTxt\\AllObjTest.txt', 'r', encoding='1251')
#file = open('D:\\ObjTxt\\AllTable.txt', 'r', encoding='866')
#file = open('D:\\ObjTxt\\AllObjTestSmall.txt', 'r', encoding='866')
#file = open('D:\\ObjTxt\\c50088.txt', 'r', encoding='866')

file = open('FocusObj.txt', 'r', encoding='866')
fileOut = open('output.txt', 'w', encoding='1251')


lineNo = 0
#parentLineNo = 0;
propLine = []; #id, parentId, lineType, propName, propType, propValue, lineNo, startPos, addInfo
propTable = []
levelBuffer = []  #lineNo, indentPos, proprtyType, propertyName
bSkipObject = False
currSection = ''
propName = ''
propType = ""
propValue = ''
lineType = ''
propLineNo = 0
valIndent = 0

def FSym(s):
  if len(s)==0:
    return '',-1
  s2 = s.lstrip()
  c = s2[0]
  pos = s.find(c)
  return c, pos

def FWord(str):
  s = str.lstrip()
  pos = s.find("=", 0)
  if pos > 0:
    sep = '='
    word = s[:pos]
    tail2 = s[pos+1:]
    return word, tail2, sep  
  pos = s.find(" : ", 0)
  if pos > 0:
    sep = ':'
    word = s[:pos]
    tail2 = s[pos+3:]
    return word, tail2, sep
  pos = s.find(" ", 0)
  if pos > 0:
    sep = ' '
    word = s[:pos]
    tail2 = s[pos+1:]
    return word, tail2, sep
  return s, '', ''
   
def AddProperty(*args):  #StartProperty2
  lineNo = args[0]
  #Позиция, с которой начинается
  startPos = args[1]
  #Свойство propName+propValue (обрезанная строка)
  propString = args[2]  
  propType = ''  
  #retValue
  global levelBuffer
  global propTable  
  global valIndent    
  global lineType
  global propLineNo

  propLineNo += 1
  #levelBuffer = setLevel(levelBuffer, lineNo, startPos)
  if lineType == 'documentation':
    startPos = 4
  levelBuffer = setLevel(levelBuffer, propLineNo, startPos)
  parent = levelBuffer[len(levelBuffer)-2]

  if lineType == 'cal':
    propName = ''
    propValue = propString
    #propLine = [lineNo, parent[0] , lineType, propName, propValue, startPos];
    propLine = [propLineNo, parent[0] , lineType, propName, '', propValue, lineNo, startPos]
    propTable.append(propLine)
    return propLine
  if lineType == 'var':
    word, tail, sep = FWord(propString)
    #propName = word
    p = word.find("@",0) 
    propName = word[:p]
    propValue = tail.lstrip().rstrip(';}')    
    #propLine = [lineNo, parent[0] , lineType, propName, propValue, startPos];
    propType, propValue, addInfo = GetTypeAndValue(propValue)
    propLine = [propLineNo, parent[0] , lineType, propName, propType, propValue, lineNo, startPos, addInfo]
    propTable.append(propLine)
    return propLine
  if lineType == 'documentation':
    propName = ''
    propValue = propString    
    propLine = [propLineNo, parent[0] , 'documentation', propName, '', propValue, lineNo, startPos+2]
    propTable.append(propLine)
    return propLine
  
  word, tail, sep = FWord(propString)
  propName = word
  #VNR261224  propValue = tail.rstrip(';} ')  
  propValue = tail.rstrip('} ')  
  #lineNo, indentPos, proprtyType, propertyName
  
  if propValue=="BEGIN":
    #propLine = [lineNo, parent[0] , 'trigger', propName, '', startPos];
    propLine = [propLineNo, parent[0] , 'trigger', propName, '', '', lineNo, startPos]
    propTable.append(propLine)    
    valIndent = startPos+propString.find("BEGIN", 0)     
    lineType = 'cal'
    return propLine
  if propValue=="VAR":
    #propLine = [lineNo, parent[0] , 'trigger', propName, '', startPos];    
    propLine = [propLineNo, parent[0] , 'trigger', propName, '', '', lineNo, startPos]
    propTable.append(propLine)    
    valIndent = startPos+propString.find("VAR", 0)    
    lineType = 'var'
    return propLine  
  #propLine = [propLineNo, parent[0] , 'property', propName, "", propValue, lineNo, startPos]
  propType, propValue, addInfo = GetTypeAndValue(propValue)
  propLine = [propLineNo, parent[0], 'property', propName, propType, propValue, lineNo, startPos, addInfo]
  valIndent = startPos+propString.find(propValue, 0)
  propTable.append(propLine)

  return propLine

  
def StartProcedure(*args):
  lineNo = args[0]
  #Позиция, с которой начинается
  startPos = args[1]
  #Свойство propName+propValue (обрезанная строка)
  propString = args[2]  
  propType = ''  
  #global procMode
  global lineType
  global propLineNo
  global levelBuffer
  global propTable
  propString = propString.lstrip()
  pos = propString.find(" ", 0)
  if pos == 0:
    return      
  word = propString[:pos]
  if not word in ["LOCAL","PROCEDURE"]:
    return
  #procMode = True
  lineType = 'procedure'
  #propName = 'Procedure' 
  i0 = propString.find('PROCEDURE')+10
  i1 = propString.find('@')
  #propValue = propString[i0:i1]
  propName = propString[i0:i1]
  propValue = ""

  propLineNo += 1
  #levelBuffer = setLevel(levelBuffer, lineNo, startPos)
  levelBuffer = setLevel(levelBuffer, propLineNo, startPos)
  parent = levelBuffer[len(levelBuffer)-2]
  #propLine = [lineNo, parent[0] , lineType, propName, propValue, startPos];
  propLine = [propLineNo, parent[0] , lineType, propName, "", propValue, lineNo, startPos]
  propTable.append(propLine) 

  i0 = propString.find('(')+1
  #i1 = propString.find(')')
  i1 = propString.rindex(")")
  procParams =  propString[i0:i1]
  if procParams != '':
    #levelBuffer = setLevel(levelBuffer, lineNo, startPos)
    #propLineNo += 1
    #levelBuffer = setLevel(levelBuffer, propLineNo, startPos)
    parent = levelBuffer[len(levelBuffer)-1]
    procParams = procParams.split(';')
    for param in procParams:
      addInfo = ""
      param = param.split(':')
      propName = param[0].split('@')[0]
      propValue = param[1].lstrip()
      #propLine = [lineNo, parent[0] , 'param', propName, propValue, startPos]
      propType, propValue, addInfo = GetTypeAndValue(propValue)
      if propName[:3]=="VAR":
         addInfo = "var"
         propName = propName[4:]
      propLineNo += 1
      propLine = [propLineNo, parent[0] , 'param', propName, propType, propValue, lineNo, startPos, addInfo]
      propTable.append(propLine) 
  
def AddValue(line):
  global propTable
  propTable[len(propTable)-1][5] += line.rstrip(';}')  
  return;

def setLevel(*args):
    global valIndent
    buffer = args[0]
    lineNo = args[1]
    posNo = args[2]
    '''
    lastPosNo = 0
    if len(buffer)>=1:
      lastPosNo = buffer[len(buffer)-1][1]
    if posNo < lastPosNo:
      valIndent = 0
    '''  
    pType = ''
    if len(args)>3:
      pType = args[3]
    pName = ''
    if len(args)>4:
      pName = args[4]
    newBuffer = []
    for item in buffer:
        #line, indent, level
        if item[1] < posNo:
          newBuffer.append(item)        
        elif item[1] >= posNo:
            newBuffer.append([lineNo, posNo, pType, pName])            
            return newBuffer    
    newBuffer.append([lineNo, posNo, pType, pName])
    return newBuffer

def GetTypeAndValue(line):
  propType = ""  
  propValue = line
  addInfo = ""
  if propValue[:8] == "Codeunit":
    propType = propValue[:8]
    propValue = propValue[8:].lstrip(" [")
  elif propValue[:4] in ["Text","Code","Form"]:
    propType = propValue[:4]
    propValue = propValue[4:].lstrip(" [").rstrip("] ")
  elif propValue[:6]=="Record" and propValue[:9]!="RecordRef":
    propType = "Record"
    propValue = propValue[7:]
  elif propValue.find("TEMPORARY Record",0)==0:
    propType = "Record"
    propValue = propValue[17:]
    addInfo = "tmp"    
  elif propValue.find("Automation",0)==0:
    propType = "Automation"
    propValue = propValue[propValue.find("}:")+2:].rstrip('"')
  return propType, propValue, addInfo





bHasError = False
str1 = ""
for ln in file:
  lineNo += 1
  if ln.find('\t')>=0:
    print('Строка '+str(lineNo)+': Знак табуляции')
    bHasError = True
  try:  
    str1 = ln.encode("866")  #1251 - any, ascii - all, 866- no
  except Exception:
    print('Строка '+str(lineNo)+': Косяк: '+ln)
    bHasError = True

if bHasError:
  quit()

print("Обработка файла "+file.name);

totalLines = lineNo
lineNo = 0
file.seek(0)
line = file.readline()

bar = IncrementalBar('Обработка ', max = totalLines)

while line:
  #bSkipObject = True
  lineNo += 1  
  bar.next();  
  
  line = line.rstrip()  
  #print(line)
  if len(line.lstrip().rstrip()) == 0:
    line = file.readline()
    continue  
  lineShort = line.lstrip().rstrip()
  if lineShort in ['{','}']:
    if lineType != "cal":
      line = file.readline()
      continue 
  if lineShort.find('{ PROPERTIES')>=0:  
      line = line.replace('{',' ')
      lineShort = lineShort.replace('{',' ')
      lineShort = line.lstrip()

  #OBJECT
  sym, pos = FSym(line); 
  if pos==0:  #Object       
    s = line.lstrip().split(' ')
    objType = s[1]
    objNo = s[2]
    objName = " ".join(s[3:])
  #if (objType == 'Table') and (int(objNo) in range(1,23)):
  #if objType in ['Table','Form','Report','Codeunit'] and int(objNo)==69:  # in range(1,4)):
  #  bSkipObject = False    
  if bSkipObject:  #or (currSection in ['KEYS','FIELDGROUPS']):
    line = file.readline()
    continue
  if pos==0:  #Object
    #levelBuffer = setLevel(levelBuffer, lineNo, 0, 'object', objNo)
    propLineNo += 1
    levelBuffer = setLevel(levelBuffer, propLineNo, 0, 'object', objNo)
    propLine = [propLineNo, 0, 'object', objName, objType, objNo, lineNo, 0]
    propTable.append(propLine)
    line = file.readline()
    continue

  #SECTION
  if lineShort == lineShort.upper():
    sectionLine = False
    if pos in [2,4]:
      if lineShort not in ['VAR','BEGIN','END;','END.']:
        sectionLine = True
    if pos in [6,8,10,12,14]:
      if lineShort in ['PROPERTIES','CONTROLS','SECTIONS']:
        sectionLine = True
    if sectionLine:
      currSection = lineShort
      #levelBuffer = setLevel(levelBuffer, lineNo, pos, 'section', currSection)
      propLineNo += 1
      levelBuffer = setLevel(levelBuffer, propLineNo, pos, 'section', currSection)
      parent = levelBuffer[len(levelBuffer)-2][0]
      #propLine = [lineNo, parent , 'section', currSection, '', pos]
      propLine = [propLineNo, parent , 'section', currSection, '', '', lineNo, pos]
      propTable.append(propLine)
      '''
      propIndent = pos+2         #Property
      prop2Indent = 0
      if currSection == 'FIELDS':        
        prop2Indent = 51      #Property2
      '''
      valIndent = 0
      lineType = ''
      line = file.readline()
      continue

    
  #PROPERTY      
  #if lineNo == 17: #6653:
  #  print("stop")
  #if lineNo == 923: #6653:
  #  print("break")
  #  break
      
  if pos>=4:
    #starting CAL block after VAR block (procedure/trigger)
    if pos==valIndent and lineType=='var' and lineShort == "BEGIN":      
      lineType='cal'
      line = file.readline()
      continue
    #ending VAR block (procedure/trigger), ending CAL block (procedure), ending procedure body
    if pos==valIndent and lineType!='' and lineShort == "END;":
      valIndent = 0
      lineType=''
      line = file.readline()
      continue
    #!!!! documentation !!!!
    if pos==valIndent+2 and lineType=='':
      #AddValue()
      propTable[len(propTable)-1][4]+=lineShort
      line = file.readline()
      continue
    #property: variable block (in code/procedure/trigger)
    if pos==valIndent+2 and lineType=='var':
      AddProperty(lineNo, valIndent+2, line[pos:])
      line = file.readline()
      continue
    #continues CAL code in procedure
    if pos>=valIndent+2 and lineType=='cal':
      AddProperty(lineNo, valIndent+2, line[valIndent+2:])   
      line = file.readline()
      continue
    #reset value indentation
    if pos<valIndent:
      valIndent = 0
    #adding of multiline property  
    if valIndent>0 and pos>=valIndent and lineType=='':  #+ end of documentation 170,303      
      AddValue(line[pos-1:])
      line = file.readline()
      continue
        
  #if pos>=4:
    if sym=='{' and currSection == 'FIELDS':       
      valIndent = 0
      s = lineShort.split(';')
      propNumber =  int(s[0].lstrip("{ ").rstrip())
      propName = s[2].rstrip()
      propValue = s[3].rstrip(' }')  #Text20
      if propValue[:4] in ["Text","Code"]:
        propType = propValue[:4]
        propValue = propValue[4:]
      else:
        propType = propValue
        propValue = ""
      #levelBuffer = setLevel(levelBuffer, lineNo, pos, 'field', propName)
      propLineNo += 1
      levelBuffer = setLevel(levelBuffer, propLineNo, pos, 'field', propName)
      parent = levelBuffer[len(levelBuffer)-2]
      #propLine = [lineNo, parent[0] , 'field', propName, propValue, pos];
      propLine = [propLineNo, parent[0] , 'field', propName, propType, propValue, lineNo, pos]  #, propNumber]
      propTable.append(propLine)
      if len(s)>=5:
        if len(s[4])>0:          
          #StartProperty(s[4])
          AddProperty(lineNo, line.find(s[4]), s[4])
      line = file.readline()
      continue
    
    if sym=='{' and currSection == 'CONTROLS':
      valIndent = 0      
      s = lineShort.split(';')
      propName = 'Control'+s[0][2:].rstrip()
      propValue = s[1].rstrip('} ')
      #levelBuffer = setLevel(levelBuffer, lineNo, pos, 'control', propName)
      propLineNo += 1
      levelBuffer = setLevel(levelBuffer, propLineNo, pos, 'control', propName)
      parent = levelBuffer[len(levelBuffer)-2]
      #propLine = [lineNo, parent[0] , 'control', propName, propValue, pos];
      propLine = [propLineNo, parent[0] , 'control', propName, "", propValue, lineNo, pos]
      propTable.append(propLine)
      if len(s)>=7:
        if len(s[6])>0:
          AddProperty(lineNo, line.find(s[6]), s[6])
      line = file.readline()
      continue
        
    if sym=='{' and currSection == 'KEYS':
      valIndent = 0
      s = lineShort.split(';')
      propName = 'Key';
      propValue = s[1].rstrip(' ;}')
      propLineNo += 1
      levelBuffer = setLevel(levelBuffer, propLineNo, pos, 'key', propName)
      parent = levelBuffer[len(levelBuffer)-2]
      propLine = [propLineNo, parent[0] , 'key', propName, "", propValue, lineNo, pos]
      propTable.append(propLine)
      if len(s)>=3:
        if len(s[2])>0:
          AddProperty(lineNo, line.find(s[2]), s[2])
      line = file.readline()
      continue    
        
  #if pos>=4:
    if currSection == "CODE":
      #starts VAR block in code section
      if lineShort == "VAR" and lineType=='':   
        lineType = 'var'
        valIndent = pos
        line = file.readline()
        continue
      #starts VAR block in procedure body
      if lineShort == "VAR" and lineType=='procedure':
        lineType = 'var'    
        valIndent = pos
        line = file.readline()
        continue
      #starts CAL block in procedure body
      if lineShort == "BEGIN" and lineType in ['procedure','var']:
        lineType = 'cal'    
        valIndent = pos
        line = file.readline()
        continue
      #usage is undetected
      if lineShort == "END;" and lineType in ['var','cal']:   
        lineType = ''
        line = file.readline()
        continue
      #starting procedure header  
      if pos==4 and sym in ['L','P']: # and lineType=='':
        word = ""   
        pos2 = lineShort.find(" ", 0)
        if pos2 > 0:
          word = lineShort[:pos2]
        if word in ["LOCAL","PROCEDURE"]:
          StartProcedure(lineNo, pos, lineShort)  
          line = file.readline()
          continue
      #starting documentation block 
      if pos==4 and lineType=='' and lineShort == "BEGIN":
        lineType = 'documentation'
        #propLineNo += 1
        #levelBuffer = setLevel(levelBuffer, propLineNo, pos, 'documentation', currSection)
        line = file.readline()
        continue      
      #ending documentation block 
      if pos==4 and lineType=='documentation' and lineShort == "END.":
        lineType = ''
        line = file.readline()
        continue

      '''  
      if lineShort == "VAR":
        if procMode:
          StartProperty('Procedure=VAR')
        else:  
          StartProperty('Object=VAR')
      if lineShort == "BEGIN":
        StartProperty('Procedure=BEGIN')
      if lineShort == "END;":
        EndValue()
        procMode = False
      '''
      AddProperty(lineNo, pos, lineShort)
      line = file.readline()
      continue
    #end of CODE

    #ordinary property: name=value/name:value
    AddProperty(lineNo, pos, lineShort)
    line = file.readline()
    continue

  #if pos>=4:

  line = file.readline()

file.close()
bar.finish()

bar = IncrementalBar('Выгрузка', max = len(propTable))
for line in propTable:
  #print(line)
  fileOut.write(str(line)+"\n")  
  bar.next()
fileOut.close()  
bar.finish()

#quit()

bar = IncrementalBar('Экспорт XML', max = len(propTable))
import xml.etree.ElementTree as xml
root = xml.Element("root")
el = []
el.append(0)
lastId = -1
lineId = -1
finalId = len(propTable)-1
for line in propTable:
  bar.next()
  lineId += 1
  el.append(line)
  lastId += 1  
  
  if line[1] == 0:
    parent = root
  else:
    parent = el[line[1]]
  #если еcть подчиненный элемент то делаешь простой с аттрибутами
  #appt = xml.Element("appointment")
  #appt.attrib = {"attrib":"value"}
  #root.append(appt)   
  if lineId < finalId and propTable[lineId+1][1] == line[0]:  
    el[line[0]] = xml.Element(line[2])
    attr = {}
    #[propLineNo, parent[0] , 'field', propName, propType, propValue, lineNo, pos, propNumber]
    if line[3]!='':
      attr.update({"name":line[3]})
    if line[4]!='':
      attr.update({"type":line[4]})
    if line[5]!='':
      attr.update({"value":line[5]})
    #if len(line) >= 9:
    #  attr.update({"no":line[8]})
    el[line[0]].attrib = attr
    parent.append(el[line[0]]) 
  else:
    el[line[0]] = xml.SubElement(parent, line[2])
    #el[line[0]].text = "value"  
    #el[line[0]].text = "Name="+line[3]+" Type="+line[4]+" Value="+line[5]
    #if len(line) >= 9:
    #  line[3] += " ("+str(line[8])+")"
    if line[3]=="":
      el[line[0]].text = line[5]
    elif line[4]!="":
      el[line[0]].text = line[3]+"="+line[4]+"("+line[5]+")"
    else:  
      el[line[0]].text = line[3]+"="+line[5]
#xml.dump(root)
tree = xml.ElementTree(root)
tree.write("output.xml", encoding="UTF-8")
bar.finish()

print('Выполнено')

'''
bar = IncrementalBar('Выгрузка в БД', max = len(propTable))
import pyodbc
from pyodbc import ProgrammingError, DataError
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=VM10-ROGOZA\SQLEXPRESS;DATABASE=Test;Trusted_Connection=yes;')
cur = conn.cursor()
#requestString = "select top 10 * from dbo.[ObjectTable] "
#cur.execute(requestString)
for ln in propTable:
    bar.next()
    try:
      if len(ln)==9:
          requestString = ("INSERT dbo.[ObjectTableSource]  "
"([LineNo], [ParentNo], [LineType], [PropName], [PropType], [PropValue], [FobLineNo], [StartPos], [AddInfo]) "
"VALUES({}, {}, {}, {}, {}, {}, {}, {}, {}) " ).format(ln[0],ln[1],repr(ln[2]),repr(ln[3]),repr(ln[4]),repr(ln[5][:132].replace("'",'"')),ln[6],ln[7],repr(ln[8]))
      if len(ln)==8:
          requestString = ("INSERT dbo.[ObjectTableSource]  "
"([LineNo], [ParentNo], [LineType], [PropName], [PropType], [PropValue], [FobLineNo], [StartPos]) "
"VALUES({}, {}, {}, {}, {}, {}, {}, {}) " ).format(ln[0],ln[1],repr(ln[2]),repr(ln[3]),repr(ln[4]),repr(ln[5][:132].replace("'",'"')),ln[6],ln[7])
      #print(requestString)
      cur.execute(requestString)
    except (ProgrammingError, DataError) as err:
      print("\n"+str(err))
      print(requestString)
      break
conn.commit()
conn.close()

'''

#Тип объекта не сохраняем )
#+ Многострочные свойства
#+ Секция KEYS доработать
#+ section CODE параметры процеуры перепочинить её а не секции
#+ Двойные свойства разбить 'Form50508' 'Code10' Customer@1000000000', 'Record 18'
#                                                                          IF NOT CONFIRM('Устанавливается Работа по Схеме ПДЗ. Необходимо проверить кредитные условия ╩ отсрочку и КЛ.\Продолжить?')
#<section>FIELDGROUPS=</section>
# var параметров в xml
# отображение return value процедур как параметра процедуры
# свойства полей CaptionML=[ENU=Attempts Till Error RUS=Кол-во попыток (до ошибки)] - через точка с запятой
