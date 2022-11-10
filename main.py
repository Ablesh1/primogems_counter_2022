import select
import sys
import addEventTab
import editEventTab
import errorTab

import datetime
import calendar

from GUI import Ui_Dialog
from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUi
from PyQt5.uic.properties import QtGui, QtCore
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QApplication, QDialog, QMainWindow, QMessageBox
)

import pickle

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

mainWindow = None
selectedEvent = ['Paimon', 'GENSHIN', '1.01.2001', '00:00:00']
ogModel = None
hidden = []


# To coś jest do tworzenia label-ów dynamicznie
class ExampleLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setText("Example")
        self.setGeometry(100, 100, 100, 100)
        self.show()


# Listy / Kategorie
class Category:
    def __init__(self, name):
        self.heldEvents = []
        self.name = name

    def eventToCat(self, toAdd):
        self.heldEvents.append(toAdd)

    def eventToEdit(self, toAdd, index):
        if index == 0:
            self.heldEvents.append(toAdd)
            print("Index = " + str(index))
        if index != 0:
            split = self.heldEvents[index - 1:]
            self.heldEvents = self.heldEvents[0:index - 1]
            self.heldEvents.append(toAdd)

            for x in split:
                self.heldEvents.append(x)


class Event:
    def __init__(self, day, month, year, alert=0, text="", category="General", primogems=0):
        self.day = day
        self.month = month
        self.text = text
        self.category = category
        self.alert = alert
        self.year = year
        self.primogems = primogems

        if self.alert != 0:
            self.alert = alert

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


# Główne okno
class Window(QMainWindow, Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.firstAddCats()
        self.loadEvents()
        self.showMaximized()

    # To ma coś robić, zmieniać i wyświetlać eventy na przykład
    # Na razie wyświetla istniejące kategorie
    # Nie używane
    '''
    def onChanged(self):
        print(CatDatabase)
        print(self.selectBoxCat.itemText(self.selectBoxCat.currentIndex()))
    '''

    # Kody błędu przydadzą się do ustalenia reguł działania projektu
    errorCode = 0

    # Funkcja Search
    def onChanged2(self):
        global hidden
        listModel = self.listViewEvent.model()
        countRow = listModel.rowCount()
        for index in range(countRow + 1):
            try:
                expression = (listModel.data(listModel.index(index, 0)).split()[0])
            except:
                continue

            if not expression.startswith(self.lineEditSearch.text()):
                hidden.append(listModel.data(listModel.index(index, 0)).split())

        index = 0
        while True:
            if index == listModel.rowCount():
                break
            if listModel.data(listModel.index(index, 0)).split() in hidden:
                listModel.removeRow(index)
            else:
                index += 1
                self.displayEvent()

        hidden = []
        self.saveEvents()

    def on_clicked(self, index):
        self.listViewEvent.setCurrentIndex(index)
        item = self.listViewEvent.currentIndex()
        itemData = item.data()
        splitted = itemData.split("\t")
        for x in splitted:
            if x == "":
                splitted.remove(x)

        # ToDo --- usuwanie znaków specjalnych z selectedEvents
        # split 3 spacji z początku opisu wydarzenia w listViewEvent
        splitted[0] = splitted[0][3:]
        # split enter-a i 3 spacji z początku daty wydarzenia w listViewEvent
        splitted[2] = splitted[2][4:]

        selectedEvent.clear()
        for x in splitted:
            selectedEvent.append(x)

        # print(selectedEvent)

        dialog = EditEvents(self)
        dialog.exec()

    # Dodawanie kategorii z CatDatabase do selectBoxCat-a na przy otwarciu okna
    def firstAddCats(self):
        for x in CatDatabase:
            self.selectBoxCat.addItem(x.name)

    # Element z selectBoxCat jest usuwany z selectBoxCat-a i z CatDatabase
    def removeCats(self):
        try:
            toRem = self.selectBoxCat.itemText(self.selectBoxCat.currentIndex())

            # Jeszcze sobie wybierzemy nazwę/nazwy kategorii, których nie usuwamy.
            # General na pewno.
            if toRem == general.name:
                print("Nie można usunąć kategorii " + toRem)
                Window.errorCode = 203
                error = ErrorTab(self)
                error.exec()
            else:
                self.selectBoxCat.removeItem(self.selectBoxCat.currentIndex())

            for x in CatDatabase:
                if x.name == toRem:
                    if x.name == general.name:
                        break
                        # print ("Nie można usunąć kategorii " + x.name)
                    else:
                        CatDatabase.remove(x)
                        print("Usunięto kategorię " + x.name)
                        break

        except:
            print("Nie ma czego usuwać")
            Window.errorCode = 204
            error = ErrorTab(self)
            error.exec()
            self.setWindowIcon(QIcon('resources/Troll-faceProblem.jpg'))
            self.listViewEvent.setStyleSheet("background-image : url(resources/Troll-faceProblem.jpg);")

        # Ważne, żeby po usunięciu kategorii zniknęły jej Eventy z ViewList-y.
        self.displayEvent()

    # Dodawanie kategorii
    def execAdd(self):
        # Trzeba zdekodować.
        text = self.lineEditCat.text()

        # Sprawdza, czy taka kategoria już istnieje.
        isCat = False
        for x in CatDatabase:
            if text == x.name:
                isCat = True

        try:
            if text is None or text == "":
                raise TypeError
            elif not isCat:
                self.selectBoxCat.addItem(text)
                CatDatabase.append(Category(text))
                self.lineEditCat.clear()
                print("Dodano kategorię o nazwie " + text)
            else:
                self.lineEditCat.clear()
                print("Istnieje już kategoria o nazwie " + text)
                Window.errorCode = 201
                error = ErrorTab(self)
                error.exec()

        except TypeError:
            print("Proszę wpisać nazwę kategorii")
            Window.errorCode = 202
            error = ErrorTab(self)
            error.exec()

        # Jak na nowo dodamy poprzednio usuniętą kategorię, to odświeży i przywróci jej nazwę jej eventom
        # Jednak nie będą one przypisane do pierwotnej kategorii
        self.displayEvent()

    # Usuwanie kategorii
    def execRem(self):
        self.removeCats()

    # ToDo --- coś z tym trzeba zrobić
    # Zapisywanie kategorii (i ich eventów)
    @staticmethod
    def saveEvents():
        with open('config.dictionary', 'wb') as configfile:
            toSave = []
            for x in CatDatabase:
                toSave.append(x)

            pickle.dump(toSave, configfile)

    @staticmethod
    def loadEvents():
        try:
            pass
        except:
            pass

    # Otwiera okienko z dodawaniem eventów
    def open(self):
        # Tak można łatwo sprawdzić, czy lista jest pusta
        if not CatDatabase:
            print("Brak kategorii")
            Window.errorCode = 205
            error = ErrorTab(self)
            error.exec()
        else:
            dialog = AddEvent(self)
            dialog.exec()

        # IDEA:
        # Przyjmujemy string z selectBoxCat-a z nazwą aktualnie wybranej kategorii
        # Szukamy tej kategorii w CatDataBase po nazwie i do specjalnie nowo stworzonej tablicy wrzucamy jej eventy
        # Wypisujemy eventy do ListView.

    # Zwraca nazwę aktualnej kategorii
    def actCat(self):
        actCat = self.selectBoxCat.itemText(self.selectBoxCat.currentIndex())
        for x in CatDatabase:
            if x.name == self.selectBoxCat.itemText(self.selectBoxCat.currentIndex()):
                actCat = self.selectBoxCat.itemText(self.selectBoxCat.currentIndex())
        return actCat

    # Wyświetla wydarzenia z wybranej kategorii.
    def displayEvent(self, toLoad=None):
        # Zalążek ładowania
        """
        if toLoad is None:
            toLoad = []
        if len(toLoad) == 0:
            toLoad = CatDatabase
        """

        # Ustawianie viewList z poziomu okna Window
        # To ma tu być, bo wtedy dynamicznie zmieniają się wydarzenia w zależności od kategorii
        model = QtGui.QStandardItemModel()
        self.listViewEvent.setModel(model)

        # Nagłówek i uzupełnianie viewList
        row = self.listViewEvent.model()
        label = QtGui.QStandardItem("")
        row.appendRow(label)

        # Tworzy listę eventów, z obecnie wybranej kategorii, do wyświetlenia
        actCat = self.actCat()
        dispEvents = []
        for x in CatDatabase:
            if x.name == actCat:
                dispEvents = x.heldEvents

        # Wyświetla tablice aktualnych kategorii
        actCatTab = []
        for x in CatDatabase:
            actCatTab.append(x.name)

        # Przywracanie eventów do ich dawnych nowo utworzonych kategorii
        for g in general.heldEvents:
            for a in actCatTab:
                for cat in CatDatabase:
                    if cat.name == a:
                        # Event już posiada nazwę kategorii, ale nie znajduje się w niej -> dodajemy go do kategorii
                        if QtGui.QStandardItem(g.category).text() == a and g not in cat.heldEvents:
                            cat.eventToCat(g)

        # ToDo --- wyświetlanie primo

        for e in dispEvents:
            # Warunek, który sprawdza, czy można przypisana zaraz nazwa kategorii należy do istniejącej kategorii
            if QtGui.QStandardItem(e.category).text() in actCatTab:
                if e.text.startswith(self.lineEditSearch.text()):
                    '''
                    item = QtGui.QStandardItem("   " + e.text + "\t" + e.category + "\t\t"
                                               + str(e.day).zfill(2) + "." + str(e.month).zfill(2) + "."
                                               + str(e.year).zfill(2) + "\t" + "Primogems\t" + str(e.primogems))
                    '''
                    # Kolejne elementy selectedEvent !!! pierwsza linia ma tak zostać !!!
                    item = QtGui.QStandardItem("   " + e.text + "\t" + e.category + "\t\n"
                                               + "   " + str(e.day).zfill(2) + "." + str(e.month).zfill(2) + "."
                                               + str(e.year).zfill(2) + "\t" + str(e.primogems))
                    row.appendRow(item)
            else:
                if e.text.startswith(self.lineEditSearch.text()):
                    # Kolejne elementy selectedEvent !!! pierwsza linia ma tak zostać !!!
                    item = QtGui.QStandardItem("   " + e.text + "\t" + "GENERAL" + "\t\n"
                                               + "   " + str(e.day).zfill(2) + "." + str(e.month).zfill(2) + "."
                                               + str(e.year).zfill(2) + "\t" + str(e.primogems))
                    row.appendRow(item)
                    # Od teraz te kategorie zostają w GENERAL z możliwością przywrócenia ich do dawnych kategorii

        # self.listViewEvent.setCurrentIndex(self.entry.indexFromItem(item))


# Loading i ładowanie głównego okna programu
class GUI(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("GUI.ui", self)


# Loading i ładowanie okna błędów
class ErrorTab(QDialog, errorTab.Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        match Window.errorCode:
            case 101:
                self.errorLabel.setText("Such an event already exists")
            case 102:
                self.errorLabel.setText("Please enter the name of the event")
            case 201:
                self.errorLabel.setText("Such a category already exists")
            case 202:
                self.errorLabel.setText("Please enter the name of the category")
            case 203:
                self.errorLabel.setText("The general category cannot be deleted")
            case 204:
                self.errorLabel.setText("There is nothing to delete")
            case 205:
                self.errorLabel.setText("No categories")


# Loading i otwieranie widget-ów
class AddEvent(QDialog, addEventTab.Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        '''
        self.label_4.hide()
        self.remindComb.hide()
        '''

        # Dodaje kategorie do combobox-a w oknie dodawania wydarzeń
        for x in CatDatabase:
            self.comboBoxCat.addItem(x.name)

        self.setup()

    def setup(self):
        # Wyszukiwanie obecnej kategorii okna głównego i ustawienie jej w combobox-ie
        i = 0
        for x in CatDatabase:
            if x.name == Window.actCat(win):
                self.comboBoxCat.setCurrentIndex(i)
            i += 1

    # Funkcja otwiera funkcje do przypomnień po zaznaczeniu przycisku
    '''
    def execRemBox(self):
        if self.label_4.isHidden():
            self.label_4.show()
            self.remindComb.show()
        else:
            self.label_4.hide()
            self.remindComb.hide()
    '''

    def accept(self):
        # Aktualnie wybrana kategoria z combobox-a w oknie edycji
        category = self.comboBoxCat.itemText(self.comboBoxCat.currentIndex())

        for cat in CatDatabase:
            if category == cat.name:
                if self.lineEditName.text() is None or self.lineEditName.text() == "":
                    print("To pole nie może być puste")
                    Window.errorCode = 102
                    error = ErrorTab(self)
                    error.exec()
                else:
                    # Używamy funkcji mainPrimo do wprowadzenia liczby primo
                    newEvent = Event(self.calendarWidget.selectedDate().day(),
                                     self.calendarWidget.selectedDate().month(),
                                     self.calendarWidget.selectedDate().year(),
                                     0, self.lineEditName.text(), cat.name,
                                     mainPrimo(self))
                    try:
                        # Nie można stworzyć wydarzenia, które jest już w bazie general
                        # Dzięki temu przywrócone eventy nie pokryją się z tymi istniejącymi
                        if newEvent in general.heldEvents:
                            print("Takie wydarzenie już istnieje")
                            Window.errorCode = 101
                            error = ErrorTab(self)
                            error.exec()
                            break

                        # Zawsze dodajemy do generala i/albo innej kategorii
                        # General ma mieć wszystkie wydarzenia
                        if cat.name != general.name:
                            cat.eventToCat(newEvent)
                            general.eventToCat(newEvent)
                            print("Dodano wydarzenie " + self.lineEditName.text() + " do kategorii " + cat.name)
                            print("Dodano wydarzenie " + self.lineEditName.text() + " do kategorii " + general.name)
                            self.lineEditName.clear()
                        else:
                            general.eventToCat(newEvent)
                            print("Dodano wydarzenie " + self.lineEditName.text() + " do kategorii " + cat.name)
                            self.lineEditName.clear()

                    # Jeśli kategoria jest pusta:
                    except:
                        if not cat.heldEvents:
                            if cat.name != general.name:
                                cat.eventToCat(newEvent)
                                general.eventToCat(newEvent)
                                print("Dodano wydarzenie " + self.lineEditName.text() + " do kategorii " + cat.name)
                                print("Dodano wydarzenie " + self.lineEditName.text() + " do kategorii " + general.name)
                                self.lineEditName.clear()
                            else:
                                general.eventToCat(newEvent)
                                print("Dodano wydarzenie " + self.lineEditName.text() + " do kategorii " + cat.name)
                                self.lineEditName.clear()
                        else:
                            raise TypeError

        # Wyświetlanie wydarzeń po zamknięciu okna przyciskiem OK
        mainWindow.displayEvent()


class EditEvents(QDialog, editEventTab.Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        '''
        self.label_4.hide()
        self.remindComb.hide()
        '''

        # Dodaje kategorie do combobox-a w oknie dodawania wydarzeń
        for x in CatDatabase:
            self.comboBoxCat.addItem(x.name)

        self.setup()

    def setup(self):
        # Ustawienie obecnego opisu eventu w edit line
        self.lineEditName.setText(selectedEvent[0])
        # Ustawienie obecnej daty eventu w calendar widget
        split = selectedEvent[2].split(".")
        self.calendarWidget.setSelectedDate(QDate(int(split[2]), int(split[1]), int(split[0])))

        # Wyszukiwanie obecnej kategorii eventu i ustawienie jej w combobox-ie
        i = 0
        for x in CatDatabase:
            if x.name == selectedEvent[1]:
                self.comboBoxCat.setCurrentIndex(i)
            i += 1

            # Funkcja otwiera funkcje do przypomnień po zaznaczeniu przycisku
            '''
            def execRemBox(self):
                if self.label_4.isHidden():
                    self.label_4.show()
                    self.remindComb.show()
                else:
                    self.label_4.hide()
                    self.remindComb.hide()
            '''

    # ToDo --- zwiększyć liczbę warunków jak eventy zwiększą liczbę pól
    # Łatwo porównuje, czy eventy są identyczne
    @staticmethod
    def checkIfEqual(selected, y):
        isEqual = False
        if selected[0] == y.text:
            if selected[1] == y.category:
                split = selected[2].split(".")
                if int(split[0]) == y.day and int(split[1]) == y.month and int(split[2]) == y.year:
                    if int(selected[3]) == y.primogems:
                        isEqual = True

        return isEqual

    def accept(self):
        # Aktualnie wybrana kategoria z combobox-a w oknie edycji
        category = self.comboBoxCat.itemText(self.comboBoxCat.currentIndex())

        # Aktualny tekst eventu, zanim zostanie nadpisany zmianą
        previousText = selectedEvent[0]

        # Zwraca numer linii, w której jest edytowany event:
        i = 0
        j = 0
        genIndex = 0
        catIndex = 0
        keptEvent = []
        for x in CatDatabase:
            # W kategorii general
            if x.name == general.name:
                for y in x.heldEvents:
                    i += 1
                    if EditEvents.checkIfEqual(selectedEvent, y):
                        print(selectedEvent)
                        genIndex += i
            # W kategorii innej niż general
            else:
                for y in x.heldEvents:
                    # Jeśli zmieniamy nazwę kategorii na general albo jej nie zmieniamy
                    if category == general.name or category == selectedEvent[1]:
                        if selectedEvent[1] == QtGui.QStandardItem(y.category).text():
                            j += 1
                            if EditEvents.checkIfEqual(selectedEvent, y):
                                catIndex += j
                    # Jeśli zmieniamy nazwę kategorii na inną niż general
                    else:
                        catIndex = 0

        for x in CatDatabase:
            if x.name == general.name:
                # W kategorii general
                for y in x.heldEvents:
                    if EditEvents.checkIfEqual(selectedEvent, y):
                        # Zapamiętaj usuwany event
                        keptEvent = y
                        x.heldEvents.remove(y)
            else:
                # W kategorii innej niż general
                for y in x.heldEvents:
                    if QtGui.QStandardItem(y.category).text() == x.name:
                        if EditEvents.checkIfEqual(selectedEvent, y):
                            # Zapamiętaj usuwany event
                            keptEvent = y
                            x.heldEvents.remove(y)

        # Edycja eventów
        for cat in CatDatabase:
            if category == cat.name:
                if self.lineEditName.text() is None or self.lineEditName.text() == "":
                    print("To pole nie może być puste")
                    Window.errorCode = 102
                    error = ErrorTab(self)
                    error.exec()
                else:
                    # Używamy funkcji mainPrimo do wprowadzenia liczby primo
                    newEvent = Event(self.calendarWidget.selectedDate().day(),
                                     self.calendarWidget.selectedDate().month(),
                                     self.calendarWidget.selectedDate().year(),
                                     0, self.lineEditName.text(), cat.name,
                                     mainPrimo(self))
                    try:
                        # Nie można stworzyć wydarzenia, które jest już w bazie general
                        # Dzięki temu przywrócone eventy nie pokryją się z tymi istniejącymi
                        if newEvent in general.heldEvents:
                            print("Takie wydarzenie już istnieje")
                            Window.errorCode = 101
                            error = ErrorTab(self)
                            error.exec()

                            # Ustaw na poprzedni domyślny tekst (powrót do stanu przed zmianami)
                            self.lineEditName.setText(previousText)
                            # Przywróć event do stanu przed zmianami
                            newEvent = keptEvent

                        # Zawsze dodajemy do generala i/albo innej kategorii
                        # General ma mieć wszystkie wydarzenia
                        if cat.name != general.name:
                            cat.eventToEdit(newEvent, catIndex)
                            general.eventToEdit(newEvent, genIndex)
                            print("Edytowano wydarzenie " + self.lineEditName.text() + " w kategorii " + cat.name)
                            print("Edytowano wydarzenie " + self.lineEditName.text() + " w kategorii " + general.name)
                            self.lineEditName.clear()
                        else:
                            general.eventToEdit(newEvent, genIndex)
                            print("Edytowano wydarzenie " + self.lineEditName.text() + " w kategorii " + general.name)
                            self.lineEditName.clear()

                    # Jeśli kategoria jest pusta:
                    except:
                        if not cat.heldEvents:
                            if cat.name != general.name:
                                cat.eventToEdit(newEvent, catIndex)
                                general.eventToEdit(newEvent, genIndex)
                                print("Edytowano wydarzenie " + self.lineEditName.text() + " w kategorii " + cat.name)
                                print("Edytowano wydarzenie " + self.lineEditName.text() + " w kategorii "
                                      + general.name)
                                self.lineEditName.clear()
                            else:
                                general.eventToEdit(newEvent, genIndex)
                                print("Edytowano wydarzenie " + self.lineEditName.text() + " w kategorii "
                                      + general.name)
                                self.lineEditName.clear()
                        else:
                            raise TypeError

                    mainWindow.displayEvent()
                    # Ładne zamykanie okienka
                    self.reject()


class Primogems:
    def __init__(self, actualAmount, dailyTasks, welkin, spiralAbyss, bargains, starGlitter, events, quests, others):
        self.actualAmount = actualAmount
        self.dailyTasks = dailyTasks
        self.welkin = welkin
        self.spiralAbyss = spiralAbyss
        self.bargains = bargains
        self.starGlitter = starGlitter
        self.events = events
        self.quests = quests
        self.others = others

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)


def countDays(y1, m1, d1):
    today = datetime.date.today()
    someday = datetime.date(y1, m1, d1)
    diff = someday - today
    daysLeft = diff.days

    return daysLeft


def countMonths(y2, m2):
    actMonth = datetime.datetime.now().month
    actYear = datetime.datetime.now().year

    if actYear == y2:
        months = m2 - actMonth
    else:
        months = 12 - actMonth + m2 + 12 * (y2 - actYear - 1)

    return months


def countYears(y3):
    actYear = datetime.datetime.now().year
    years = y3 - actYear

    return years


def countAbyss(period, monthsLeft):
    now = datetime.datetime.now()
    abyss = 0
    add = -1

    daysOfMonth = calendar.monthrange(now.year, now.month)[1]
    daysOfMonthsLeft = daysOfMonth - now.day

    '''
    print("\nDays of month: " + str(daysOfMonth))
    print("Days of month left: " + str(daysOfMonthsLeft))
    print("\nPeriod: " + str(period))
    print("Abyss: " + str(abyss))
    '''

    # New abyss starts in the 1st and the 16th day of each month
    # We consider that ongoing abyss is done for current month
    # Current month
    if daysOfMonthsLeft >= 16 and (now.day + period) >= 16:
        abyss += 1
        period -= daysOfMonthsLeft
    elif daysOfMonthsLeft < 16 and (now.day + period) >= 16:
        period -= daysOfMonthsLeft
    else:
        period = 0

    # All months after current one starting from 1st day
    for i in range(0, monthsLeft):

        diffMonths = calendar.monthrange(now.year, 1 + (now.month + 1 + add) % 12)[1]

        if period >= diffMonths:
            abyss += 2
            period -= diffMonths
        elif 16 <= period < diffMonths:
            abyss += 2
            period -= period
        elif 1 <= period < 16:
            abyss += 1
            period -= period

        add += 1

        '''
        print("\nDays of month: " + str(diffMonths))
        print("Months analyzed: " + str(add))
        print("Period: " + str(period))
        print("Abyss: " + str(abyss))
        '''

    return abyss


def countEvents(event):
    events = 0
    for i in range(0, len(event)):
        events += event[i]
    return events


def countStarGlitter(primo, glitter):
    pull = primo // 160
    golden = pull // 90
    silver = (pull - golden * 10) // 10

    starGlitter = golden * 10 + silver * 2 + glitter

    return starGlitter


def count(amount, days, months, years, abyss, star, event, quest, other):
    pulls = amount[1]
    amount = amount[0]
    daily = days * 60
    welkin = days * 90
    spiral = abyss * 500
    paimonBargains = months * 5 * 160

    total = amount + daily + welkin + spiral + paimonBargains + event + quest + other
    star = countStarGlitter(total, star)

    p = Primogems(amount, daily, welkin, spiral, paimonBargains, star // 5 * 160, event, quest, other)

    total = amount + daily + welkin + spiral + paimonBargains + star // 5 * 160 + event + quest + other
    earned = total - amount

    print("\nDays left:\t\t\t" + str(days))
    print("Months left:\t\t" + str(months))
    print("Years left:\t\t\t" + str(years))

    print("\nGlitter used: \t\t" + str(star - star % 5))
    print("Glitter unused: \t" + str(star % 5))

    print("\nPulls done:\t\t\t" + str(pulls))
    print("Pulls left:\t\t\t" + str(amount // 160))

    print("\n" + str(p))
    print("Total accumulated:\t" + str(other + (star // 5 * 160)) +
          "\tPrimogems\t-->\t" + str((other + (star // 5 * 160)) // 160) + "\tPulls")
    print("Total earned:\t\t" + str(earned) + " \tPrimogems\t-->\t" + str(earned // 160) + "\tPulls")
    print("Total amount:\t\t" + str(total) + "\tPrimogems\t-->\t" + str(total // 160) + "\tPulls\t\n")

    return total


def start(a, y, m, d, s, e, q, o):
    d0 = countDays(y, m, d)
    m0 = countMonths(y, m)
    y0 = countYears(y)
    a0 = countAbyss(d0, m0)
    e0 = countEvents(e)
    q0 = countEvents(q)
    o0 = countEvents(o)

    total = count(a, d0, m0, y0, a0, s, e0, q0, o0)

    return total


def mainPrimo(self):
    chooseDay = int(self.calendarWidget.selectedDate().day())
    chooseMonth = int(self.calendarWidget.selectedDate().month())
    chooseYear = int(self.calendarWidget.selectedDate().year())

    amountOfStarGlitter = 92
    amountOfPrimogems = [10308, 0]  # enter the amount of primogems and done pulls

    eventsTab = [1020, 420, 420, 40, 40, 40]
    questsTab = []
    othersTab = [1800, 300, 600, 300, 2 * 160]

    primogems = start(amountOfPrimogems, chooseYear, chooseMonth, chooseDay, amountOfStarGlitter,
                      eventsTab, questsTab, othersTab)
    return primogems


if __name__ == "__main__":
    general = Category("GENERAL")
    paimon = Category("PAIMON")
    genshin = Category("GENSHIN")

    CatDatabase = [general, paimon, genshin]
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    mainWindow = win
    sys.exit(app.exec())
