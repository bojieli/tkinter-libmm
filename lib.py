#!/usr/bin/python3
# -*- coding: utf-8 -*-
# requires tkinter (>=8.6) and pymssql (>=2.1) modules

import tkinter
from tkinter import Tk, Menu, Label, Entry, Button, Frame, Toplevel, Radiobutton, IntVar
from tkinter import messagebox
import tkinter.ttk as ttk
import sys
import time
import datetime
import random

import pymssql
dbcon = None
dbcur = None

root = Tk()
root.title("图书馆借阅管理系统")
root.geometry('1024x600')
# default italic font looks so bad for Chinese chars...
root.option_add("*Font", "Simsun 10")

root_frame = Frame(root)

def refresh_root_frame():
    global root
    global root_frame
    if root_frame:
        root_frame.destroy()
    root_frame = Frame(root)

def sql_query(query, args=None):
    global dbcur
    try:
        dbcur.execute(query, args)
    except:
        messagebox.showwarning("错误", "数据库操作失败\n\n" + query + "\n\n" + str(sys.exc_info()))
        return False
    return True

def sql_result(query, args=None):
    global dbcur
    if sql_query(query, args):
        try:
            row = dbcur.fetchone()
            return row[0]
        except:
            messagebox.showwarning("错误", "数据库操作失败\n\n" + query + "\n\n" + str(sys.exc_info()))
    return None

def sql_commit():
    global dbcon
    dbcon.commit()

def check_dbinit():
    for table in ['readers', 'books', 'borrows']:
        if sql_result("SELECT OBJECT_ID ('" + table + "', 'U')") is None:
            return False
    global filemenu
    filemenu.entryconfig("初始化数据库", state="normal")
    return True

def enable_menubars():
    global menubar
    global filemenu
    menubar.entryconfig("图书编目", state="normal")
    menubar.entryconfig("书目检索", state="normal")
    menubar.entryconfig("图书借还", state="normal")
    menubar.entryconfig("读者管理", state="normal")
    filemenu.entryconfig("数据统计", state="normal")

# defined so early because load_sample_data needs them
def unchecked_borrowbook(reader_id, book_id, borrow_time):
    borrow_days_limit = 60
    sql_query("INSERT INTO borrows (reader_id, book_id, borrow_date, expected_return_date, return_date, returned) VALUES (%s, %s, %d, %d, %d, %d)",
        (reader_id, book_id, borrow_time, borrow_time + borrow_days_limit * 86400, 0, 0))
    sql_query("UPDATE readers SET curr_books = curr_books + 1 WHERE id = %s", (reader_id))
    sql_query("UPDATE books SET borrowed = 1 WHERE id = %s", (book_id))
    sql_commit()

def unchecked_returnbook(reader_id, book_id):
    sql_query("UPDATE borrows SET returned = 1, return_date = %d WHERE reader_id = %d AND book_id = %d AND returned = 0",
            (time.time(), reader_id, book_id))
    sql_query("UPDATE readers SET curr_books = curr_books - 1 WHERE id = %s", (reader_id))
    sql_query("UPDATE books SET borrowed = 0 WHERE id = %s", (book_id))
    sql_commit()

def load_sample_data():
    readers = [
            ('PB14001', '叶文洁', 2, '少年班学院', 8, 0),
            ('PB14002', '罗辑', 1, '物理学院', 8, 0),
            ('PB14003', '程心', 2, '化学学院', 8, 0),
            ('PB14004', '云天明', 1, '生命科学学院', 8, 0),
            ('PB14005', '艾AA', 1, '地球与空间科学学院', 8, 0),
            ('PB14006', '章北海', 1, '计算机学院', 8, 0),
            ('PB14007', '维德', 1, '人文与社会科学学院', 8, 0),
            ('PB14008', '关一帆', 1, '数学系', 8, 0),
            ('PB14009', '丁仪', 1, '物理学院', 8, 0),
            ('PB14010', '史强', 1, '人文与社会科学学院', 8, 0),
            ('PB14011', '汪淼', 1, '少年班学院', 8, 0),
            ('PB14012', '智子', 2, '计算机学院', 8, 0),
            ('PB14013', '歌者', 0, '教务处', 8, 0)
            ]
    for reader in readers:
        sql_query("INSERT INTO readers VALUES (%s, %s, %d, %s, %d, %d)", reader)

    books = [
("44.566/18/9", "我们是怎样读<<红楼梦>>的", "4", "武汉大学著", "人民教育出版社 1975", "1"),
("O242.23/24", "MATLAB优化算法案例分析与应用", "O", "余胜威编著", "清华大学出版社 2014", "2"),
("73.9631/442", "怎样使用MS-DOS7.0--Winsows 95的DOS环境", "7", "曹国钧", "上海科学普及出版社 1996.7.1", "3"),
("TM571.61/6", "西门子PLC工业通信完全精通教程", "T", "向晓汉主编", "化学工业出版社 2013", "4"),
("J614.8/16", "玩转音乐:Apple Logic Pro9完全精通", "J", "杨旋著", "化学工业出版社 2011", "5"),
("G131.3/5", "字解日本:十二岁时", "G", "茂吕美耶", "广西师范大学出版社 2010", "6"),
("O174.22/18", "基于FPGA的FFT处理系统的研究与应用", "O", "杨军, 丁洪伟著", "科学出版社 2012", "7"),
("27.1039/59", "批判“四人帮”对“唯生产力论”的“批判”", "2", "林子力,有林著", "人民出版社 1978", "8"),
("43.2/198", "文论十笺", "4", "程千帆编著", "黑龙江人民出版社 1983", "9"),
("TP393/460", "基于TCP/IP的PC联网技术", "T", "(美)[C.亨特]Craig Hunt著", "电子工业出版社 1997", "10"),
("I712.45/883", "圣地", "I", "(美)欧文·华莱士(Irving Wallace)著", "光明出版社 1999", "11"),
("47.6352/419", "洛杉矶的女人们", "4", "(美)欧文·华莱士(Irving Wallace)著", "光明出版社 1999", "12"),
("F272.92/146", "孙悟空是个好员工:解读《西游记》的28条职业箴言", "F", "成君忆著", "中信出版社 2004", "13"),
("TP332.3/6", "挑战SOC:基于NIOS的SOPC设计与实践", "T", "彭澄廉主编", "清华大学出版社 2004", "14"),
("TP332/63", "基于PROTEUS的ARM虚拟开发技术", "T", "周润景, 袁伟亭编著", "北京航空航天大学出版社 2007", "15"),
("R954/4", "美国FDA的CGMP现场检查", "R", "蒋婉, 屈毅主编", "中国医药科技出版社 2007", "16"),
("F49/15", "CIO的N条军规:IT部门全面管理手册", "F", "袁磊, 刘远编著", "电子工业出版社 2007", "17"),
("TP311.138OR/48", "基于Linux的Oracle数据库管理", "T", "李爱武编著", "北京邮电学院出版社 2008", "18"),
("B221.4/8", "易经新注", "B", "焦作森译著", "吉林大学出版社 2010", "19"),
("P208/153", "基于Flex的WebGIS开发", "P", "吴信才著", "电子工业出版社 2011", "20"),
("I247.5/2322/5", "千门之心", "I", "方白羽著", "二十一世纪出版社 2009", "21"),
("TP312C-43/91", "基于Visual C++的MFC编程", "T", "仇谷峰主编", "清华大学出版社 2015", "22"),
("73.9621/JA-267(2)", "Java高级编程", "7", "(美) Brett Spell著", "清华大学出版社 2006", "26"),
("TP393.09/208", "网络编程技术及应用", "T", "谭献海等编著", "清华大学出版社 2006", "27"),
("TP311.56/59", "自己动手写Struts:构建基于MVC的Web开发框架", "T", "思志学等编著", "电子工业出版社 2007", "28"),
("TP393.409/14", "智慧地图:Google Earth/Maps/KML核心开发技术揭秘", "T", "马谦编著", "电子工业出版社 2010", "29"),
("TP393/53", "云计算", "T", "刘鹏主编", "电子工业出版社 2010", "30"),
("TP312PH/18", "Zend Framework技术大全", "T", "陈营辉, 赵伟, 赵海波等编著", "化学工业出版社 2010", "31"),
("C934/42", "基于网格的开放式决策支持系统", "C", "迟嘉昱著", "电子科技大学出版社 2010", "32"),
("TP332/173", "基于MDK的LPC1100处理器开发应用", "T", "李宁编著", "北京航空航天大学出版社 2010", "33"),
("B563.1/6-1", "斯宾诺莎书信集", "B", "斯宾诺莎", "商务印书馆 2009", "34"),
("F224.3/4", "评价相对有效性的数据包络分析模型:DEA和网络DEA", "F", "魏权龄著", "中国人民大学出版社 2012", "35"),
("K825.46=72/3", "激荡的中国:北大校长眼中的近代史", "K", "蒋梦麟著", "九州出版社 2015", "36"),
("TP393.4/112", "Linnux?的?Internet 站点建立与维护", "T", "(美)Dee-Ann LeBlanc 著", "清华大学出版社 1997", "37"),
("TP393.4/110", "面向 Windows?的?Internet 网络应用与开发", "T", "孙燕唐主编", "电子工业出版社 1996", "38"),
("K225.04/15", "左传名句选译", "K", "来可泓编著", "中国青年出版社 1994.8", "39"),
("73.9953/284", "Photoshop 锦囊妙计", "7", "(美)Adobe Systems公司著", "清华大学出版社 2000", "40"),
("P208/112", "基于MapX的GIS应用开发", "P", "李连营 ... [等] 编著", "武汉大学出版社 2003", "41"),
("TP312JA/632", "精通Struts:基于MVC的Java Web设计与开发", "T", "孙卫琴编著", "电子工业出版社 2004", "42"),
("TP332.1/40", "基于Quartus Ⅱ的FPGA/CPLD设计", "T", "李洪伟, 袁斯华编著", "电子工业出版社 2006", "43"),
("TP393.092/572", "基于.NET的Web程序设计:ASP.NET标准教程", "T", "刘振岩编著", "电子工业出版社 2006", "44"),
("TP311.56/166", "Struts实用开发指南:基于MVC+MyEclipse的Java Wed应用开发", "T", "高红岩编著", "科学出版社 2007", "45"),
("TP312JA/294", "J2EE开源编程精要15讲:整合Eclipse、Struts、Hibernate和Spring的Java Web开发", "T", "邬继成编著", "电子工业出版社 2008", "46"),
("TP274/62", "虚拟仪器教学实验简明教程:基于LabVIEW的NI ELVIS", "T", "杨智, 袁媛, 贾延江编著", "北京航空航天大学出版社 2008", "47"),
("TP312JA/253", "精通Struts 2:基于MVC的Java Web应用开发实战", "T", "陈云芳编著", "人民邮电出版社 2008", "48"),
("TP368.1/173", "基于Proteus的8051单片机实例教程", "T", "李学礼主编", "电子工业出版社 2008", "49"),
("TP316.89/32", "基于Scilab的ARM-Linux嵌入式计算及应用", "T", "马龙华, 彭哲编著", "科学出版社 2008", "50"),
("D432.7/6", "可爱的80后", "D", "李博实编著", "中国长安出版社 2008", "51"),
("TP393.09/60", "疯狂Ajax讲义:Prototype/jQuery+DWR+Spring+Hibernate整合开发", "T", "李刚编著", "电子工业出版社 2009", "52"),
("TP332.1/29", "基于VHDL的CPLD/FPGA开发与应用", "T", "张丕状, 李兆光编著", "国防工业出版社 2009", "53"),
("TP332.1/8", "基于Verilog HDL的FPGA设计与工程应用", "T", "徐洋 ... [等] 编著", "人民邮电出版社 2009", "54"),
("TP332/143", "基于FPGA的SOPC实践教程", "T", "杨军编著", "科学出版社 2010", "55"),
("TP332.1/87", "基于Quartus II的FPGA/CPLD设计实例精解", "T", "李大社, 王彬, 刘淑娥等编著", "电子工业出版社 2010", "56"),
("TM571.6/89", "基于Automation Studio的PLC系统设计、仿真及应用", "T", "周润景, 张丽娜, 刘梦男编著", "电子工业出版社 2012", "57"),
("TP332.1/71(2)", "基于Quartus Ⅱ的FPGA/CPLD数字系统设计实例.第2版", "T", "周润景, 苏良碧编著", "电子工业出版社 2013", "58"),
("TP312C-43/83", "基于UNIX/Linux的C系统编程", "T", "张杰敏, 王巍编著", "清华大学出版社 2013", "59"),
("TP312C/369", "精通Windows程序设计:基于Visual C++实现", "T", "朱娜敏, 魏宗寿, 李红编著", "人民邮电出版社 2009", "60"),
("TP332.1/110", "基于Quartus Ⅱ的FPGA/CPLD数字系统设计与应用", "T", "黄平, 王伟, 周广涛编著", "电子工业出版社 2014", "61"),
("TP3/192", "计算机原理与设计:Verilog HDL版", "T", "李亚民著", "清华大学出版社 2011", "62"),
("", "高等数学题典", "", "黄光谷 ... [等]编", "机械工业出版社 2004", "63"),
("27.44/101", "“第四代”西方经济学“新体系”:高级经济学", "2", "周天华, 周京著", "天津大学出版社 2009", "64"),
("P208-39/4", "基于Silverlight的WebGIS开发", "P", "吴信才著", "电子工业出版社 2011", "65"),
("B563.1/6", "斯宾诺莎书信集", "B", "洪汉鼎译", "商务印书馆 1993", "66"),
("TN916.4/1", "ITT1240数字交换系统", "T", "美国ITT公司编", "人民邮电出版社 1986", "67"),
("TP360.7/10(-2)", "IBM微型电子计算机系统故障检修300例.2版(修订本)", "T", "张毅忠等编著", "广东科技出版社 1993.12", "68"),
("73.87221/648", "DOS6使用与技术大全", "7", "(美)索 采(Socha,J.)等著", "清华大学出版社 1994.5", "69"),
("73.87221/495", "深入DOS编程", "7", "求伯君主编", "北京大学出版社 1993.1", "70"),
("73.9953/4", "计算机图形核心系统GKS与C联编应用", "7", "陈德人,董金祥编著", "浙江大学出版社 1993.8", "71"),
("29-Nov", "大众哲学", "2", "艾思奇著", "生活. 读书. 新知识三联书店 1979", "72"),
("41.68055/88", "大学英语六级考试分类题解", "4", "张德中主编", "上海科学技术文献出版社 1991.3", "73"),
("I712.45/1098", "安·伊丽莎叛婚记", "I", "(美)欧文·华莱士(Irving Wallace)著", "光明日报出版社 1999", "74"),
("73.87221/869", "MicrosoftC/C++7.0使用指南", "7", "(美)阿特金森(Atkinson,L.)等著", "清华大学出版社 1993.10", "75"),
("43.257/41", "我们是怎样读《红楼梦》的", "4", "武汉大学中文系七二级评《红》组著", "人民教育出版社 1975", "76"),
("C93/9", "东方管理金律", "C", "徐广权著", "青岛出版社 2004", "77"),
("I207.411/88", "红楼夢的破譯", "I", "作者孔祥贤", "江苏文艺出版社 2001", "78"),
("TP312UM/56", "UML基础、案例与应用", "T", "(美) Joseph Schmuller著", "人民邮电出版社 2004", "79"),
("TP312C/138", "Visual C++数据库编程实战", "T", "韩存兵编著", "科学出版社 2003", "80"),
("I521.25/1-1", "杜伊诺哀歌", "I", "里尔克著", "辽宁教育出版社 2005", "81"),
("H31/137", "Jolin的24堂英文日记课", "H", "蔡依林著", "接力出版社 2005", "82"),
("G449.4/22", "逻辑陷阱", "G", "(英)罗伯特·艾伦主编", "希望出版社 2004", "83"),
("44.28/19/:6", "郭沫若全集.第六卷,考古编,金文丛考补录", "4", "郭沫若,", "科学出版社 2002", "84"),
("F279.712.444/4", "点击Google:关于Google的50个故事", "F", "宋宏斌著", "中国书籍出版社 2006", "87"),
("TP332.1/4", "面向CPLD/FPGA的VHDL设计", "T", "王开军, 姜宇柏等编著", "机械工业出版社 2007", "88"),
("TM380.2-39/1", "基于COMSOL Multiphysics的MEMS建模及应用", "T", "张玉宝, 李强主编", "冶金工业出版社 2007", "89"),
("TP393.09/6", "深入理解Ajax:基于JavaScript的RIA开发", "T", "(美) Joshua Eichorn著", "人民邮电出版社 2007", "90"),
("TP332.1/71", "基于Quartus II的FPGA/CPLD数字系统设计实例", "T", "周润景, 图雅, 张丽敏编著", "电子工业出版社 2007", "91"),
("78.122/327", "UG机械设计实用教程", "7", "袁浩主编", "化学工业出版社 2007", "92"),
("TN911.72/151", "TMS320C6000系列DSP的CPU与外设", "T", "(美) Texas Instruments Incorporated著", "清华大学出版社 2007", "93"),
("TP332.1/13", "基于EDK的FPGA嵌入式系统开发", "T", "杨强浩等编著", "机械工业出版社 2008", "94"),
("B979.951.6/4", "马丁·路德时代", "B", "(美) 威尔·杜兰著", "东方出版社 2007", "95"),
("TP316.81/258", "基于Linux的Web程序设计:PHP网站开发", "T", "刘振岩, 王勇, 陈立平编著", "人民邮电出版社 2008", "96"),
("B565.26/12/:2", "卢梭时代", "B", "(美) 威尔·杜兰, 艾丽尔·杜兰著", "东方出版社 2007", "97"),
("B565.26/12/:1", "卢梭时代", "B", "(美) 威尔·杜兰, 艾丽尔·杜兰著", "东方出版社 2007", "98"),
("TP332/71", "开源软核处理器OpenRisc的SOPC设计", "T", "徐敏, 孙恺, 潘峰编著", "北京航空航天大学出版社 2008", "99"),
("K812.4/2", "西方文化的异类:“紫红色十年”的30位名人肖像", "K", "孙宜学主编", "上海人民出版社 2008", "100")
            ]
    for book in books:
        sql_query("INSERT INTO books VALUES (%s, %s, %s, %s, %s, %d, 0)", book)

    for reader in readers:
        reader_id = reader[0]
        curr_books = 0
        for i in range(0, 20):
            index = random.randint(0, len(books) - 1)
            book_id = books[index][0]
            if book_id and 0 == sql_result("SELECT borrowed FROM books WHERE id = %s", (book_id)):
                unchecked_borrowbook(reader_id, book_id, time.time() - random.randint(0, 100) * 86400)
                curr_books += 1
                if random.randint(0, 1) == 0:
                    unchecked_returnbook(reader_id, book_id)
                    curr_books -= 1
                if curr_books == 8:
                    break

    sql_commit()

def initdb_ex():
    sql_query("IF OBJECT_ID('readers', 'U') IS NOT NULL DROP TABLE readers")
    sql_query('''CREATE TABLE readers (
        id NVARCHAR(20) NOT NULL PRIMARY KEY,
        name NVARCHAR(30) NOT NULL,
        gender TINYINT NOT NULL DEFAULT 0,
        address NVARCHAR(100),
        max_books INT NOT NULL,
        curr_books INT NOT NULL DEFAULT 0
    )''')
    sql_query("CREATE INDEX key_reader_name ON readers (name)")
    sql_query("IF OBJECT_ID('books', 'U') IS NOT NULL DROP TABLE books")
    sql_query('''CREATE TABLE books (
        id NVARCHAR(20) NOT NULL PRIMARY KEY,
        name NVARCHAR(100) NOT NULL,
        category NVARCHAR(10) NOT NULL,
        author NVARCHAR(100) NOT NULL,
        publisher NVARCHAR(100) NOT NULL,
        price INT NOT NULL,
        borrowed BIT DEFAULT 0
    )''')
    sql_query("CREATE INDEX key_book_name ON books (name)")
    sql_query("IF OBJECT_ID('borrows', 'U') IS NOT NULL DROP TABLE borrows")
    sql_query('''CREATE TABLE borrows (
        id INT NOT NULL IDENTITY(1,1) PRIMARY KEY,
        reader_id NVARCHAR(20) NOT NULL,
        book_id NVARCHAR(20) NOT NULL,
        borrow_date INT NOT NULL,
        expected_return_date INT NOT NULL,
        return_date INT,
        returned BIT NOT NULL DEFAULT 0
    )''')
    sql_query("CREATE INDEX key_borrow_reader ON borrows (reader_id)")
    sql_query("CREATE INDEX key_borrow_book ON borrows (book_id)")
    sql_commit()

    if check_dbinit():
        load_sample_data()
        messagebox.showinfo("成功", "数据库初始化成功，您可以开始使用了")
        enable_menubars()
    else:
        if messagebox.askyesno("", "数据库初始化失败，是否重试？"):
            initdb_ex()


def connectdb_ex(host, user, password, database):
    global dbcon
    global dbcur
    try:
        dbcon = pymssql.connect(host, user, password, database, charset='utf8')
    except:
        messagebox.showwarning("错误", "数据库连接失败\n\n" + str(sys.exc_info()))
        return

    dbcur = dbcon.cursor()
    if check_dbinit():
        messagebox.showinfo("成功", "数据库连接成功，您可以开始使用了")
        enable_menubars()
    else:
        choice = messagebox.askyesno("", "数据库尚未初始化，是否现在初始化？")
        if choice:
            initdb_ex()

def connectdb():
    global root
    window = Toplevel(root)
    window.title("连接数据库")

    Label(window, text="服务器名").grid(row=0,column=0,sticky='EW')
    server_entry = Entry(window)
    server_entry.grid(row=0,column=1,sticky='EW')
    server_entry.insert(0, "localhost")

    Label(window, text="用户名").grid(row=1,column=0,sticky='EW')
    user_entry = Entry(window)
    user_entry.grid(row=1,column=1,sticky='EW')
    user_entry.insert(0, "lib")

    Label(window, text="密码").grid(row=2,column=0,sticky='EW')
    pass_entry = Entry(window, show='*')
    pass_entry.grid(row=2,column=1,sticky='EW')
    pass_entry.insert(0, "123456")

    Label(window, text="数据库名").grid(row=3,column=0,sticky='EW')
    dbname_entry = Entry(window)
    dbname_entry.grid(row=3,column=1,sticky='EW')
    dbname_entry.insert(0, "lib")

    def connectdb_onclick():
        connectdb_ex(server_entry.get(), user_entry.get(), pass_entry.get(), dbname_entry.get())
        window.destroy()

    Button(window, text="连接", command=connectdb_onclick).grid(row=4,column=0,columnspan=2)
    Label(window, text="您需要首先创建一个 SQL server 用户和数据库").grid(row=5,column=0,columnspan=2)

    for child in window.winfo_children():
        child.grid_configure(padx=5, pady=5)
    user_entry.focus()


def initdb():
    if check_dbinit():
        choice = messagebox.askyesno("", "数据库已经初始化，重新初始化将清空数据，是否继续？")
        if choice:
            initdb_ex()
    else:
        initdb_ex()

def stats():
    readers = sql_result("SELECT COUNT(*) FROM readers")
    books = sql_result("SELECT COUNT(*) FROM books")
    borrowed_books = sql_result("SELECT COUNT(*) FROM books WHERE borrowed = 1")
    borrow_history = sql_result("SELECT COUNT(*) FROM borrows")
    messagebox.showinfo("数据统计",
          "读者数：" + str(readers) + "\n"
        + "书籍数：" + str(books) + "\n"
        + "当前借出：" + str(borrowed_books) + " 本\n"
        + "总借阅次数：" + str(borrow_history)
        );

def about():
    messagebox.showinfo("关于", "作者：张静宁 (PB14203209)\njenny42@mail.ustc.edu.cn\n2015年12月\n\n"
        + "------\n"
        + "Program version: 0.1\n"
        + "Python version: " + str(sys.version_info) + "\n"
        + "tkinter version: " + str(tkinter.TkVersion) + "\n"
        + "pymssql version: " + str(pymssql.__version__) + "\n"
        );

def delbook(selected_book):
    if messagebox.askyesno("删除确认", "确定要删除书籍编号 " + selected_book[0] + " 书名 " + selected_book[1] + " 吗？"):
        if sql_query("DELETE FROM books WHERE id = %s", selected_book[0]):
            sql_commit()
            messagebox.showinfo("成功", "删除成功")
        else:
            messagebox.showinfo("失败", "删除失败")

def addbook_ex(id, name, category, author, publisher, price):
    if sql_result("SELECT COUNT(*) FROM books WHERE id=%s", (id)) > 0:
        if messagebox.askyesorno("书号 " + id + " 已经存在，是否替换？"):
            if sql_query("UPDATE books SET name=%s, category=%s, author=%s, publisher=%s, price=%d WHERE id=%s",
                    (name, category, author, publisher, price, id)):
                sql_commit()
                messagebox.showinfo("成功", "《" + name + "》入库成功")
    else:
        if sql_query("INSERT INTO books (id, name, category, author, publisher, price, borrowed) VALUES (%s, %s, %s, %s, %s, %d, %d)",
                (id, name, category, author, publisher, price, 0)):
            sql_commit()
            messagebox.showinfo("成功", "《" + name + "》入库成功")

def addbook(selected_book=None):
    global root
    window = Toplevel(root)
    window.title("新书入库 / 更新书籍信息")

    Label(window, text="书籍编号").grid(row=0,column=0,sticky='EW')
    id_entry = Entry(window)
    id_entry.grid(row=0,column=1,sticky='EW')

    Label(window, text="书名").grid(row=1,column=0,sticky='EW')
    name_entry = Entry(window)
    name_entry.grid(row=1,column=1,sticky='EW')

    Label(window, text="分类号").grid(row=2,column=0,sticky='EW')
    user_entry = Entry(window)
    user_entry.grid(row=2,column=1,sticky='EW')

    Label(window, text="作者").grid(row=3,column=0,sticky='EW')
    pass_entry = Entry(window)
    pass_entry.grid(row=3,column=1,sticky='EW')

    Label(window, text="出版社").grid(row=4,column=0,sticky='EW')
    dbname_entry = Entry(window)
    dbname_entry.grid(row=4,column=1,sticky='EW')

    Label(window, text="单价").grid(row=5,column=0,sticky='EW')
    price_entry = Entry(window)
    price_entry.grid(row=5,column=1,sticky='EW')

    if selected_book:
        id_entry.insert(0, selected_book[0])
        name_entry.insert(0, selected_book[1])
        user_entry.insert(0, selected_book[2])
        pass_entry.insert(0, selected_book[3])
        dbname_entry.insert(0, selected_book[4])
        price_entry.insert(0, selected_book[5])

    def addbook_onclick():
        try:
            price = int(price_entry.get())
            addbook_ex(id_entry.get(), name_entry.get(), user_entry.get(), pass_entry.get(), dbname_entry.get(), price)
            window.destroy()
        except:
            messagebox.showwarning("", "输入数据不合法")

    Button(window, text="提交", command=addbook_onclick).grid(row=6,column=0,columnspan=2)

    for child in window.winfo_children():
        child.grid_configure(padx=5, pady=5)
    id_entry.focus()


def addreader_ex(id, name, gender, address, max_books):
    if sql_result("SELECT COUNT(*) FROM readers WHERE id=%s", (id)) > 0:
        if messagebox.askyesorno("读者证号 " + id + " 已经存在，是否替换？"):
            if sql_query("UPDATE readers SET name=%s, gender=%d, address=%s, max_books=%d WHERE id=%s",
                    (name, gender, address, max_books, id)):
                sql_commit()
                messagebox.showinfo("成功", "读者证号 " + id + " 入库成功")
    else:
        if sql_query("INSERT INTO readers (id, name, gender, address, max_books, curr_books) VALUES (%s, %s, %d, %s, %d, %d)",
                (id, name, gender, address, max_books, 0)):
            sql_commit()
            messagebox.showinfo("成功", "读者证号 " + id + " 入库成功")

def delreader(selected_reader):
    if messagebox.askyesno("删除确认", "确定要删除读者证号 " + selected_reader[0] + " 姓名 " + selected_reader[1] + " 吗？"):
        if sql_query("DELETE FROM readers WHERE id = %s", selected_reader[0]):
            sql_commit()
            messagebox.showinfo("成功", "删除成功")
        else:
            messagebox.showinfo("失败", "删除失败")

def addreader(selected_reader=None):
    global root
    window = Toplevel(root)
    window.title("添加 / 更新读者信息")

    Label(window, text="读者证号").grid(row=0,column=0,sticky='EW')
    id_entry = Entry(window)
    id_entry.grid(row=0,column=1,columnspan=2,sticky='EW')

    Label(window, text="姓名").grid(row=1,column=0,sticky='EW')
    name_entry = Entry(window)
    name_entry.grid(row=1,column=1,columnspan=2,sticky='EW')

    Label(window, text="性别").grid(row=2,column=0,sticky='EW')
    gender_entry = IntVar()
    Radiobutton(window, text="男", variable=gender_entry, value=1).grid(row=2,column=1,sticky='EW')
    Radiobutton(window, text="女", variable=gender_entry, value=2).grid(row=2,column=2,sticky='EW')

    Label(window, text="地址").grid(row=3,column=0,sticky='EW')
    pass_entry = Entry(window)
    pass_entry.grid(row=3,column=1,columnspan=2,sticky='EW')

    Label(window, text="最大借书数量").grid(row=4,column=0,sticky='EW')
    maxnum_entry = Entry(window)
    maxnum_entry.grid(row=4,column=1,columnspan=2,sticky='EW')

    if selected_reader:
        if sql_query("SELECT * FROM readers WHERE id = %s", (selected_reader[0])):
            global dbcur
            selected_reader = dbcur.fetchone()

            id_entry.insert(0, selected_reader[0])
            name_entry.insert(0, selected_reader[1])
            gender_entry.set(selected_reader[2])
            pass_entry.insert(0, selected_reader[3])
            maxnum_entry.insert(0, selected_reader[4])

    def addreader_onclick():
        try:
            gender = int(gender_entry.get())
            maxnum = int(maxnum_entry.get())
            addreader_ex(id_entry.get(), name_entry.get(), gender, pass_entry.get(), maxnum)
            window.destroy()
        except:
            messagebox.showwarning("", "输入数据不合法")

    Button(window, text="提交", command=addreader_onclick).grid(row=6,column=0,columnspan=3)

    for child in window.winfo_children():
        child.grid_configure(padx=5, pady=5)
    id_entry.focus()

def listreader():
    sql_query("SELECT * FROM readers")
    display_readers()
    global root_frame
    Button(root_frame, text="刷新", command=listreader).pack()

def display_readers():
    refresh_root_frame()
    global root_frame
    tree = ttk.Treeview(root_frame, columns = ('name', 'gender', 'address', 'max_books', 'curr_books'), height=25)
    ysb = ttk.Scrollbar(root_frame, orient='vertical', command=tree.yview)
    ysb.pack(anchor='e', fill='y', side='right')
    tree.configure(yscroll=ysb.set)
    tree.heading('#0', text='读者证号')
    tree.column('name', width=100)
    tree.heading('name', text='姓名')
    tree.column('gender', width=50)
    tree.heading('gender', text='性别')
    tree.heading('address', text='地址')
    tree.column('max_books', width=100)
    tree.heading('max_books', text='最大借阅数')
    tree.column('curr_books', width=100)
    tree.heading('curr_books', text='已借数')

    reader_id_map = []

    global dbcur
    for row in dbcur:
        reader_id_map.append(row)

        id = row[0]
        name = row[1]
        if row[2] == 1:
            gender = '男'
        elif row[2] == 2:
            gender = '女'
        else:
            gender = 'N/A'
        address = row[3]
        max_books = row[4]
        curr_books = row[5]

        tree.insert('', 'end', text=id, values=(name, gender, address, max_books, curr_books))

    def popup(event):
        selected_row_id = tree.identify_row(event.y)
        if selected_row_id:
            tree.selection_set(selected_row_id)
            # row_id format: I001 .. I00A
            int_row_id = int(selected_row_id[1:], 16) - 1
            selected_user = reader_id_map[int_row_id]

            rclick_menu = Menu(root, tearoff=0)
            rclick_menu.add_command(label="更新信息", command=lambda: addreader(selected_user))
            rclick_menu.add_command(label="删除读者", command=lambda: delreader(selected_user))
            rclick_menu.add_separator()
            rclick_menu.add_command(label="查询借阅", command=lambda: checkuser(selected_user))
            rclick_menu.add_command(label="借书", command=lambda: borrowbook(None, selected_user))
            rclick_menu.add_command(label="还书", command=lambda: returnbook(None, selected_user))
            rclick_menu.post(event.x_root, event.y_root)

    tree.bind("<Button-3>", popup)

    tree.pack()
    Label(root_frame, text="Hint: 右键单击读者可进行更新信息、删除读者、查询借阅、借书、还书操作").pack()
    root_frame.pack()



menubar = Menu(root)

def sql_like_escape(search):
    return search.replace("'", "").replace('\\', "").replace("%", "")

def display_search_result(fieldtext, field, query):
    try:
        sql_query("SELECT * FROM books WHERE " + field + " LIKE N'%" + sql_like_escape(query) + "%'")
    except:
        return False
    display_book_by_category()
    global root_frame
    Label(root_frame, text="显示" + fieldtext + "包含 " + query + " 的搜索结果").pack()
    Button(root_frame, text="刷新", command=lambda: display_search_result(fieldtext, field, query)).pack()
    return True

def generic_search(field, fieldtext):
    global root
    window = Toplevel(root)
    window.title("书目检索")

    Label(window, text=fieldtext).grid(row=0,column=0,sticky='EW')
    id_entry = Entry(window)
    id_entry.grid(row=0,column=1,sticky='EW')

    def search_onclick():
        query = id_entry.get()
        if display_search_result(fieldtext, field, query):
            window.destroy()

    Button(window, text="搜索", command=search_onclick).grid(row=6,column=0,columnspan=2)

    for child in window.winfo_children():
        child.grid_configure(padx=5, pady=5)
    id_entry.focus()

def searchtitle():
    generic_search('name', "书名")

def searchauthor():
    generic_search('author', "作者")

def searchpublisher():
    generic_search('publisher', "出版社")

def display_book_by_category():
    books_by_category = {}

    global dbcur
    for row in dbcur:
        id = row[0]
        name = row[1]
        category = row[2]
        author = row[3]
        publisher = row[4]
        price = row[5]
        borrowed = row[6]
        if category in books_by_category:
            books_by_category[category].append(row)
        else:
            books_by_category[category] = [row]

    refresh_root_frame()
    global root_frame
    tree = ttk.Treeview(root_frame, columns = ('name', 'author', 'publisher', 'price', 'borrowed'), height=25)
    ysb = ttk.Scrollbar(root_frame, orient='vertical', command=tree.yview)
    ysb.pack(anchor='e', fill='y', side='right')
    tree.configure(yscroll=ysb.set)
    tree.heading('#0', text='图书编号')
    tree.heading('name', text='书名')
    tree.heading('author', text='作者')
    tree.heading('publisher', text='出版社')
    tree.column('price', width=100)
    tree.heading('price', text='价格')
    tree.column('borrowed', width=100)
    tree.heading('borrowed', text='借阅状态')

    tree_view_row_map = []
    for category in books_by_category:
        books = books_by_category[category]
        cat_obj = tree.insert('', 'end', text=category, open=True)
        tree_view_row_map.append(None)
        for book in books:
            if book[6] == 1:
                status = '已借出'
            else:
                status = '可借'
            tree.insert(cat_obj, 'end', text=book[0], values=(book[1], book[3], book[4], book[5], status))
            tree_view_row_map.append(book)

    def popup(event):
        selected_row_id = tree.identify_row(event.y)
        if selected_row_id:
            # row_id format: I001
            int_row_id = int(selected_row_id[1:], 16) - 1
            if tree_view_row_map[int_row_id]:
                tree.selection_set(selected_row_id)
                selected_book = tree_view_row_map[int_row_id]

                rclick_menu = Menu(root, tearoff=0)
                rclick_menu.add_command(label="更新信息", command=lambda: addbook(selected_book))
                rclick_menu.add_command(label="删除图书", command=lambda: delbook(selected_book))
                rclick_menu.add_separator()
                if selected_book[6] == 1:
                    rclick_menu.add_command(label="还书", command=lambda: returnbook(selected_book))
                else:
                    rclick_menu.add_command(label="借书", command=lambda: borrowbook(selected_book))
                rclick_menu.post(event.x_root, event.y_root)

    tree.bind("<Button-3>", popup)

    tree.pack()
    Label(root_frame, text="Hint: 右键单击书目可进行更新信息、删除图书、借书、还书操作").pack()
    root_frame.pack()

def view_by_category():
    sql_query("SELECT * FROM books")
    display_book_by_category()
    global root_frame
    Button(root_frame, text="刷新", command=view_by_category).pack()

def ts2date(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

def display_borrows(user_id=None):
    returned_borrows = []
    nonreturned_borrows = []
    expired_borrows = []

    global dbcur
    for row in dbcur:
        id = row[0]
        name = row[1]
        price = row[2]
        borrow_date = row[3]
        expected_return_date = row[4]
        returned = row[5]
        return_date = row[6]

        book = (id, name, price, ts2date(borrow_date), ts2date(expected_return_date), returned, ts2date(return_date))

        if returned == 1:
            returned_borrows.append(book)
        elif int(expected_return_date / 86400) >= int(time.time() / 86400):
            nonreturned_borrows.append(book)
        else:
            expired_borrows.append(book)

    refresh_root_frame()
    global root_frame
    tree = ttk.Treeview(root_frame, columns = ('name', 'price', 'borrow_date', 'expected_return_date', 'return_date'), height=25)
    ysb = ttk.Scrollbar(root_frame, orient='vertical', command=tree.yview)
    ysb.pack(anchor='e', fill='y', side='right')
    tree.configure(yscroll=ysb.set)
    tree.heading('#0', text='图书编号')
    tree.heading('name', text='书名')
    tree.column('price', width=100)
    tree.heading('price', text='价格')
    tree.column('borrow_date', width=100)
    tree.heading('borrow_date', text='借阅日期')
    tree.column('expected_return_date', width=100)
    tree.heading('expected_return_date', text='应还日期')
    tree.column('return_date', width=100)
    tree.heading('return_date', text='实还日期')

    tree_view_row_map = []
    cat_obj = tree.insert('', 'end', text='逾期未还图书', open=True)
    tree_view_row_map.append(None)
    for book in expired_borrows:
        tree.insert(cat_obj, 'end', text=book[0], values=(book[1], book[2], book[3], book[4], 'N/A'))
        tree_view_row_map.append(book)

    cat_obj = tree.insert('', 'end', text='已借图书', open=True)
    tree_view_row_map.append(None)
    for book in nonreturned_borrows:
        tree.insert(cat_obj, 'end', text=book[0], values=(book[1], book[2], book[3], book[4], 'N/A'))
        tree_view_row_map.append(book)

    cat_obj = tree.insert('', 'end', text='已还图书', open=True)
    tree_view_row_map.append(None)
    for book in returned_borrows:
        tree.insert(cat_obj, 'end', text=book[0], values=(book[1], book[2], book[3], book[4], book[6]))
        tree_view_row_map.append(None)

    def popup(event):
        selected_row_id = tree.identify_row(event.y)
        if selected_row_id:
            # row_id format: I001
            int_row_id = int(selected_row_id[1:], 16) - 1
            if tree_view_row_map[int_row_id]:
                tree.selection_set(selected_row_id)
                selected_book = tree_view_row_map[int_row_id]
                if user_id:
                    selected_user = [user_id]
                else:
                    selected_user = None

                rclick_menu = Menu(root, tearoff=0)
                rclick_menu.add_command(label="还书", command=lambda: returnbook(selected_book, selected_user))
                rclick_menu.post(event.x_root, event.y_root)

    tree.bind("<Button-3>", popup)

    tree.pack()
    Label(root_frame, text="Hint: 右键单击未还书目可进行还书操作").pack()
    root_frame.pack()



def checkuser(selected_user=None):
    def query_borrows(query):
        if sql_result("SELECT COUNT(*) FROM readers WHERE id = %s", (query)) == 0:
            messagebox.showwarning("", "读者证号 " + query + " 不存在")
            return False
        sql_query("SELECT books.id, books.name, books.price, borrows.borrow_date, borrows.expected_return_date, borrows.returned, borrows.return_date FROM borrows JOIN books ON borrows.book_id = books.id WHERE borrows.reader_id = %s", (query))
        display_borrows(query)
        global root_frame
        Label(root_frame, text="显示读者证号 " + query + " 的借阅记录").pack()
        Button(root_frame, text="刷新", command=lambda: query_borrows(query)).pack()
        return True

    if selected_user:
        query_borrows(selected_user[0])
        return

    global root
    window = Toplevel(root)
    window.title("读者借阅查询")

    Label(window, text="读者证号").grid(row=0,column=0,sticky='EW')
    id_entry = Entry(window)
    id_entry.grid(row=0,column=1,sticky='EW')

    def checkuser_onclick():
        query = id_entry.get()
        if query_borrows(query):
            window.destroy()

    Button(window, text="查询", command=checkuser_onclick).grid(row=6,column=0,columnspan=2)

    for child in window.winfo_children():
        child.grid_configure(padx=5, pady=5)
    id_entry.focus()

def borrowbook_ex(reader_id, book_id):
    try:
        global dbcur
        sql_query("SELECT id, name, max_books, curr_books FROM readers WHERE id = %s", (reader_id))
        reader = dbcur.fetchone()
        if not reader:
            messagebox.showwarning("失败", "读者证号 " + reader_id + " 不存在")
            return
        reader_name = reader[1]
        reader_max_books = reader[2]
        reader_curr_books = reader[3]

        is_borrowing = sql_result("SELECT COUNT(*) FROM borrows WHERE reader_id = %s AND book_id = %s AND returned = 0", (reader_id, book_id))
        if is_borrowing == 1:
            messagebox.showwarning("失败", "读者 " + reader_id + " 已经借阅了 " + book_id + " 这本书")
            return

        if reader_curr_books >= reader_max_books:
            messagebox.showwarning("失败", "读者 " + reader_id + " 借阅图书数量超限 (" + str(reader_max_books) + ")")
            return

        book_exists = sql_result("SELECT COUNT(*) FROM books WHERE id = %s", (book_id))
        if book_exists == 0:
            messagebox.showwarning("失败", "图书 " + book_id + " 不存在")
            return

        book_is_borrowed = sql_result("SELECT borrowed FROM books WHERE id = %s", (book_id))
        if book_is_borrowed == 1:
            messagebox.showwarning("失败", "图书 " + book_id + " 已被借出")
            return

        unchecked_borrowbook(reader_id, book_id, time.time())
    except:
        return
    messagebox.showinfo("成功", "读者 " + reader_id + " 借阅图书 " + book_id + " 成功")
    

def borrowbook(selected_book=None, selected_user=None):
    global root
    window = Toplevel(root)
    window.title("借阅图书")

    Label(window, text="读者证号").grid(row=0,column=0,sticky='EW')
    reader_entry = Entry(window)
    reader_entry.grid(row=0,column=1,sticky='EW')
    if selected_user:
        reader_entry.insert(0, selected_user[0])

    Label(window, text="图书编号").grid(row=1,column=0,sticky='EW')
    book_entry = Entry(window)
    book_entry.grid(row=1,column=1,sticky='EW')
    if selected_book:
        book_entry.insert(0, selected_book[0])

    def borrow_onclick():
        reader_id = reader_entry.get()
        book_id = book_entry.get()
        borrowbook_ex(reader_id, book_id)

    Button(window, text="借书", command=borrow_onclick).grid(row=2,column=0,columnspan=2)

    for child in window.winfo_children():
        child.grid_configure(padx=5, pady=5)
    reader_entry.focus()

def returnbook_ex(reader_id, book_id):
    try:
        is_borrowing = sql_result("SELECT COUNT(*) FROM borrows WHERE reader_id = %d AND book_id = %d AND returned = 0", (reader_id, book_id))
        if is_borrowing != 1:
            messagebox.showwarning("失败", "读者 " + reader_id + " 未借图书 " + book_id + " 或已归还")
            return

        unchecked_returnbook(reader_id, book_id)
    except:
        return
    messagebox.showinfo("成功", "读者 " + reader_id + " 归还图书 " + book_id + " 成功")


def returnbook(selected_book=None, selected_user=None):
    global root
    window = Toplevel(root)
    window.title("归还图书")

    Label(window, text="读者证号").grid(row=0,column=0,sticky='EW')
    reader_entry = Entry(window)
    reader_entry.grid(row=0,column=1,sticky='EW')
    if selected_user:
        reader_entry.insert(0, selected_user[0])

    Label(window, text="图书编号").grid(row=1,column=0,sticky='EW')
    book_entry = Entry(window)
    book_entry.grid(row=1,column=1,sticky='EW')
    if selected_book:
        book_entry.insert(0, selected_book[0])

    def return_onclick():
        reader_id = reader_entry.get()
        book_id = book_entry.get()
        returnbook_ex(reader_id, book_id)

    Button(window, text="还书", command=return_onclick).grid(row=2,column=0,columnspan=2)

    for child in window.winfo_children():
        child.grid_configure(padx=5, pady=5)
    reader_entry.focus()



menubar = Menu(root)

# create a pulldown menu, and add it to the menu bar
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="连接数据库", command=connectdb)
filemenu.add_command(label="初始化数据库", command=initdb)
filemenu.entryconfig("初始化数据库", state="disabled")
filemenu.add_separator()
filemenu.add_command(label="数据统计", command=stats)
filemenu.entryconfig("数据统计", state="disabled")
filemenu.add_separator()
filemenu.add_command(label="退出", command=root.quit)
menubar.add_cascade(label="系统", menu=filemenu)

# create more pulldown menus
editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(label="新书入库", command=addbook)
editmenu.add_command(label="更新书籍信息", command=addbook)
editmenu.add_separator()
editmenu.add_command(label="分类浏览", command=view_by_category)
menubar.add_cascade(label="图书编目", menu=editmenu)
menubar.entryconfig("图书编目", state="disabled")

searchmenu = Menu(menubar, tearoff=0)
searchmenu.add_command(label="按书名查询", command=searchtitle)
searchmenu.add_command(label="按作者查询", command=searchauthor)
searchmenu.add_command(label="按出版社查询", command=searchpublisher)
menubar.add_cascade(label="书目检索", menu=searchmenu)
menubar.entryconfig("书目检索", state="disabled")

readermenu = Menu(menubar, tearoff=0)
readermenu.add_command(label="新增读者", command=addreader)
readermenu.add_command(label="更新读者信息", command=addreader)
readermenu.add_separator()
readermenu.add_command(label="借阅查询", command=checkuser)
readermenu.add_separator()
readermenu.add_command(label="读者列表", command=listreader)
menubar.add_cascade(label="读者管理", menu=readermenu)
menubar.entryconfig("读者管理", state="disabled")

borrowmenu = Menu(menubar, tearoff=0)
borrowmenu.add_command(label="图书借阅", command=borrowbook)
borrowmenu.add_command(label="图书归还", command=returnbook)
menubar.add_cascade(label="图书借还", menu=borrowmenu)
menubar.entryconfig("图书借还", state="disabled")

menubar.add_command(label="关于", command=about)

# display the menu
root.config(menu=menubar)

# display welcome screen
l = Label(root_frame, text="欢迎使用图书借阅管理系统", font=("微软雅黑", 18))
l.pack()
l = Label(root_frame, text="请首先连接 SQL Server 数据库: 系统 => 连接数据库")
l.pack()
root_frame.pack()

root.mainloop()

