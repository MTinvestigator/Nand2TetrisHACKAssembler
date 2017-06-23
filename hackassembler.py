#HACK ASSEMBLER 

import re 

inst_dic={}
var_address = 16
symbol_table = {'R0': '0','R1': '1','R2': '2','R3': '3','R4': '4','R5': '5','R6': '6','R7': '7','R8': '8','R9': '9','R10': '10','R11': '11','R12': '12','R13': '13','R14': '14','R15': '15','SCREEN': '16384', 'KBD':'24576', 'SP':'0', 'LCL':'1','ARG':'2','THIS':'3','THAT':'4' } 
comp_dic = {'0': '0101010', '1': '0111111', '-1': '0111010','D': '0001100', 'A': '0110000', 'M': '1110000', '!D': '0001101', '!A': '0110001', '!M': '1110001','-D': '0001111', '-A': '0110011', '-M': '1110011','D+1': '0011111', 'A+1': '0110111', 'M+1': '1110111', 'D-1':'0001110', 'A-1':'0110010', 'M-1':'1110010', 'D+A':'0000010', 'D+M':'1000010', 'D-A':'0010011', 'D-M':'1010011', 'A-D':'0000111', 'M-D':'1000111', 'D&A':'0000000', 'D&M':'1000000', 'D|A':'0010101', 'D|M':'1010101'}
jmp_dic = {'':'000', 'JGT':'001', 'JEQ':'010', 'JGE':'011', 'JLT':'100', 'JNE':'101', 'JLE':'110', 'JMP':'111'}
dest_dic = {'':'000', 'M':'001', 'D':'010', 'MD':'011', 'A':'100', 'AM':'101', 'AD':'110', 'AMD':'111'}
inst_list_first = []
inst_list_second = []

def find_labels(line, symbol_table, line_number): #finds labels
    label = re.search ("\((.+)\)", line)
    if label: 
        label = label.group(1)
    if label not in symbol_table:
        symbol_table[label] = str(line_number)
    elif label in symbol_table:
        line = ''.join(['@',symbol_table.get(label)])
    return symbol_table

def trans_labels(line,symbol_table):
    label = re.search ("\((.+)\)", line)
    if label: 
        label = label.group(1)
    line = ''.join(['@',symbol_table.get(label)])
    return line
    
def find_symbols(line, symbol_table,var_address, line_number): #finds and replaces symbols
    symbol = re.search ('@(\S+)', line)
    if symbol:
        symbol = symbol.group(1)
    if symbol_table.get(symbol, False)==False :
        symbol_table[symbol] = str(var_address)
        var_address = var_address + 1
    elif symbol in symbol_table:
        line = ''.join(['@',symbol_table.get(symbol)])
    return line, var_address

def trans_a(line, inst_dic, line_number, var_address): #translates a-instructions
    if not re.search ('@([0-9]+)', line): 
        line, var_address = find_symbols(line, symbol_table,var_address, line_number)
    at_pos = line.find('@')
    instruction = line[at_pos+1:]
    instruction = int(instruction)
    instruction = '{0:016b}'.format(instruction)
    inst_dic[line_number] = str(instruction)
    
def trans_c(line,inst_dic,comp_dic, dest_dic, jmp_dic, line_number): #translates c-instructions
    comp = re.search('=(.+);?', line)
    if not comp:
		comp = re.search('=?(.+);', line)
    if comp:
        comp = comp.group(1)
    dest = re.search('(.+)=.+;?', line)
    if dest:
        dest = dest.group(1)
    jmp = re.search('=?.+;(.+)', line)
    if jmp:
        jmp = jmp.group(1)
    bindest = dest_dic.get(dest, '000')
    bincomp = comp_dic.get(comp, '000')
    binjmp = jmp_dic.get(jmp, '000')
    instruction = ''.join(['111', bincomp, bindest , binjmp])
    inst_dic[line_number] = str(instruction)
    return inst_dic
    
def first_parse(symbol_table, var_address): #scans labels 
    has_more_commands = True
    line_number = 0
    while has_more_commands == True: 
        line = f.readline()
        if line in ['\n', '\r\n']:
            continue
        line = line.strip(' ')
        if line.startswith('//'):   #skips if it finds a comment 
            continue
        if line == '':   #checks if there is more commands
            has_more_commands = False
            break 
        if re.search('(.+?)//.+', line):
            line = re.search('(.*?)//.+', line)
            if line:
                line = line.group(1)
        if re.search ("\((.+)\)", line):
            line_number = line_number
        else:
            line_number = line_number + 1
        if re.search ("\((.+)\)", line):  #identifies Labels
            find_labels(line, symbol_table, line_number)
        line = "".join(line.split())
        inst_list_first .append(line)
    return inst_list_first     
    
def second_parse(symbol_table, var_address, inst_list_first): #scans variables
    has_more_commands = True
    line_number = 0
    for line in inst_list_first: 
        if line.startswith('//'):   #skips if it finds a comment 
            continue
        if line == '':   #checks if there is more commands
            has_more_commands = False
            break 
        if re.search('(.+?)//.+', line):
            line = re.search('(.*?)//.+', line)
            if line:
                line = line.group(1)
        if re.search ("\((.+)\)", line):
            line_number = line_number
        else:
            line_number = line_number + 1
        if not re.search('@([0-9]+)', line) and re.search ('@(\S+)', line):  #identifies Labels
            line, var_address = find_symbols(line, symbol_table,var_address, line_number)      
        line = "".join(line.split())
        inst_list_second.append(line)
    return inst_list_second
        
def main_loop(inst_list_second , inst_dic, comp_dic, dest_dic, jmp_dic, var_address):
    has_more_commands = True
    line_number = 0
    for line in inst_list_second: 
        if line.startswith('//'):   #skips if it finds a comment 
            continue
        if line.startswith('@'):    #identifies and translates A-instruction
            line_number = line_number+1
            trans_a(line, inst_dic,line_number, var_address)           
        elif re.search ("\((.+)\)", line):  #identifies Labels
            continue
        elif re.search('=(.+);?', line) or re.search('=?(.+);', line):   #translates C-instructions
            line_number = line_number+1
            trans_c(line,inst_dic, comp_dic, dest_dic, jmp_dic, line_number)
    return inst_dic
                
def outputfile(inst_dic):    #outputs the stored instructions to a file
    outhack = open('Max.hack', "w")
    for key in inst_dic:
        inst = inst_dic[key]
        outhack.write(inst)
        outhack.write("\n")
    print "finished!"

file_address = raw_input('write file address: ')
f = open(file_address, 'r')

first_parse(symbol_table, var_address)
second_parse(symbol_table, var_address, inst_list_first)

main_loop(inst_list_second , inst_dic, comp_dic, dest_dic, jmp_dic, var_address)

outputfile(inst_dic)

f.close()
