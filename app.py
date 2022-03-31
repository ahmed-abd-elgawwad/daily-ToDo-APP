from PyQt5.QtWidgets import QApplication, QMainWindow , QMessageBox , QListWidgetItem
from PyQt5 import uic  
from sys import argv
from sqlite3 import connect 
from ast import literal_eval
from PyQt5.QtCore import Qt
# main class 
class Mainwindow(QMainWindow): 
    def __init__(self):
        super(Mainwindow,self).__init__()
        # initiate the ui file
        uic.loadUi("ui/ui.ui",self)
        # initiate the connections betweeen buttons
        self.buttons() 
    # connecting the buttons 
    def buttons(self):
        self.calendarWidget.clicked.connect(self.show_list)
        self.add_item_button.clicked.connect(self.add_item)
        self.remove_item_button.clicked.connect(self.delete_item)
        self.save_changes.clicked.connect(self.save_to_database)
    
    # adding item to the list of tasks 
    def add_item(self):
        text= self.lineEdit.text()
        item = QListWidgetItem(text)
        item.setCheckState(Qt.Unchecked)
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.listWidget.addItem(item)
        self.lineEdit.setText("")
    
    # delete unwanted item
    def delete_item(self):
        index_of_item = self.listWidget.currentRow()
        # delete the item with the index 
        self.listWidget.takeItem(index_of_item)
    # show the list widged 
    def show_list(self,date):
        try:
            date= int("".join([str(i) for i in self.calendarWidget.selectedDate().getDate()]))
            conn =connect("database/todo.db")
            c= conn.cursor()
            c.execute(""" SELECT list ,checkList FROM todo WHERE dateid =(:id)""",{"id":date})
            row = c.fetchall()
            if row:
            # show the list on the list widget
                text=row[0][0]
                check = row[0][1]
                texts = literal_eval(text)
                checks = literal_eval(check)
                # clear the current items 
                self.listWidget.clear()
                for i in range(len(texts)):
                    item= QListWidgetItem(texts[i])
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                    if checks[i] == 0:
                        item.setCheckState(Qt.Unchecked)
                    elif checks[i] ==2:
                        item.setCheckState(Qt.Checked)
                    self.listWidget.addItem(item) 
            else:
                self.listWidget.clear()
            conn.close()
        except:
            QMessageBox.warning(None,"Error","There is some error.")
        
    def save_to_database(self):
        try:
            #connect to the database
            conn = connect("database/todo.db")
            c = conn.cursor()
            """"
            1- check if the date exist or not if exist then update the list if not then add new row to the databse
            """
            date= int("".join([str(i) for i in self.calendarWidget.selectedDate().getDate()]))
            # gat all the dated from the database 
            c.execute("""SELECT * from todo""")
            rows = c.fetchall()
            dic = {t[0]:t[1] for t in rows}
            # get list widget items
            items = [self.listWidget.item(i).text() for i in range(self.listWidget.count())]
            str_items = str(items)
            # save the chek_state
            check_states = [self.listWidget.item(i).checkState() for i in range(self.listWidget.count())]
            # check if the date exsit 
            if date in dic.keys():
                # update the previous list 
                # 
                c.execute("""UPDATE todo SET list=(:list),checkList=(:cl) WHERE dateid =(:id)""",{"list":str_items,"cl":str(check_states),"id":date})
                conn.commit()
            else:
                # add new row to the database
                
                c.execute("""INSERT INTO todo values (:id,:list,:cl)""",{"id":date,"list":str_items,"cl":str(check_states)})
                conn.commit()
            # print(dic)
            # print(rows)
            conn.close()
            QMessageBox.information(None,"success","task saved to this day")
        except:
            QMessageBox.warning(None,"Error","There is some error.")

# looping  
if __name__ == "__main__":
    app = QApplication(argv)
    window = Mainwindow()
    window.show() 
    app.exec_() 