from typing import Union

from django.db.models.query import RawQuerySet
from django.urls import reverse
from django.shortcuts import render
from django.shortcuts import redirect
from .models import Person
from .models import Hospital
from .models import HN
from .models import Department
from .models import Patient
from django.db.models import Count, F, Value
from .models import Staff
from .models import Officer
from .models import schedule
from .models import hospitaltime
from .models import bookingperson
from .models import tagdepartment
from django.db.models.functions import Length, Upper
from django.db import connection
from pprint import pprint
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.http import HttpResponseRedirect
import json
from django.db import connection
import MySQLdb
import mysql.connector
from datetime import date, datetime, timedelta
from django.core.mail import send_mail
import smtplib, ssl
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.utils import timezone
from datetimerange import DateTimeRange


def login(request):
    return render(request, 'login.html')


def loginan(request):
    return render(request, 'loginan.html')


def register(request):
    return render(request, 'register.html')


def registeran(request):
    return render(request, 'registeran.html')


def addhuman(request):
    HMid = request.POST['userid']
    HMname = request.POST['usename']
    HMpassword = request.POST['password']
    passwordcomfrim = request.POST['comfirm']
    HMemail = request.POST['mail']
    dataperson = Person.objects.filter(Pid=HMid)
    if dataperson:
        error = 2
        return render(request, 'register.html', {'data': error})
    else:
        inserthuman = Person(Pid=HMid, Pname=HMname, Ppassword=HMpassword, Pemail=HMemail)
        inserthuman.save()
        error = 1
        if request.POST['check'] != '2':
            Patients = Patient(Pid=HMid)
            Patients.save()
            error = 1
            dataPerson = Person.objects.get(Pid=HMid)
            if dataPerson.Pid == HMid and dataPerson.Ppassword == HMpassword:
                dataStaff = Staff.objects.all()
            for dataStaffs in dataStaff:
                if dataStaffs.Pid == HMid:
                    x = 1
                    break
                else:
                    x = 2
            request.session['permission'] = x
            request.session['user_id'] = HMid
            request.session['name'] = HMname
            user_id = request.session['user_id']
            name = request.session['name']
            request.session['hospital'] = ''
            request.session['hn'] = ''
            request.session['Hid'] = ''
            request.session['error'] = ''
            request.session['error2'] = ''
            response = redirect('calendar')
            return response
        else:
            Staffs = Staff(Pid=HMid, status=0)
            Staffs.save()
            error = 1
            dataPerson = Person.objects.get(Pid=HMid)
            if dataPerson.Pid == HMid and dataPerson.Ppassword == HMpassword:
                dataStaff = Staff.objects.all()
            for dataStaffs in dataStaff:
                if dataStaffs.Pid == HMid:
                    x = 1
                    break
                else:
                    x = 2
            request.session['hospital'] = ''
            request.session['hn'] = ''
            request.session['Hid'] = ''
            request.session['error'] = ''
            request.session['error2'] = ''
            request.session['permission'] = x
            request.session['user_id'] = HMid
            request.session['name'] = HMname
            user_id = request.session['user_id']
            name = request.session['name']
            response = redirect('staffmoniter')
            return response


def person(request):
    if request.session._session:
        dataHN = HN.objects.filter(HNpid=request.session['user_id'])
        datahospital = Hospital.objects.all()
        hospitalcheck = []
        hncheck = []
        hospitaledit = []
        hospitalshow = []
        hnlist = []
        for dataHNs in dataHN:
            hnlist.append(dataHN)
        for d in datahospital:
            hospitalcheck.append(int(d.Hid))
        for dataHNs in dataHN:
            hncheck.append(int(dataHNs.HNhid))
        for hncheck in hncheck:
            hospitalcheck.remove(int(hncheck))
            dtHos = Hospital.objects.filter(Hid=int(hncheck))
            for dtHoses in dtHos:
                dataHNcheck = HN.objects.filter(HNpid=request.session['user_id'], HNhid=dtHoses.Hid)
                for dataHNs in dataHNcheck:
                    listex = []
                    listex.append(int(dtHoses.Hid))
                    listex.append(str(dtHoses.Hname))
                    listex.append(str(dataHNs.HN))
                    listex.append(str(dataHNs.id))
                    hospitalshow.append(listex)
        for datahospitals in datahospital:
            for hospitalcheckes in hospitalcheck:
                if datahospitals.Hid == hospitalcheckes:
                    listshow = []
                    listshow.append(int(datahospitals.Hid))
                    listshow.append(str(datahospitals.Hname))
                    hospitaledit.append(listshow)
        return render(request, 'person.html',
                      {'hospital': datahospital, 'hnlist': hnlist, 'HN': dataHN, 'datahospital': datahospital,
                       'hospitaledit': hospitaledit,
                       'hospitalshow': hospitalshow})
    else:
        return redirect('login')


def addhn(request):
    if request.session._session:
        hospitals = Hospital.objects.all()
        for hospitals in hospitals:
            idcheck = hospitals.Hid
            ids = str(idcheck)
            check = str('HN' + ids)
            idsss = str('HNid' + ids)
            check2 = str('HNnew' + ids)
            if check in request.POST:
                chek = request.POST[check]
                idck = request.POST[idsss]
                if chek != "":
                    HN.objects.filter(pk=idck).update(HN=chek)
            if check2 in request.POST:
                che = request.POST[check2]
                if che != "":
                    HNpid = request.session['user_id']
                    inserthn = HN(HNpid=HNpid, HNhid=hospitals.Hid, HN=che)
                    inserthn.save()
        response = redirect('person')
        return response
    else:
        return redirect('login')


def deletehn(request):
    if request.session._session:
        selected_tests = request.POST['test_list_ids']
        selected_tests = json.loads(selected_tests)
        for test in selected_tests:
            if test != '':
                HN.objects.filter(id__in=selected_tests).delete()
        response = redirect('person')
        return response
    else:
        return redirect('login')


def edithn(request):
    if request.session._session:
        HNid = request.POST['id']
        x = HN.objects.get(id=HNid)
        datahospital = Hospital.objects.all()
        return render(request, 'edithn.html', {'x': x, 'datahospital': datahospital})
    else:
        return redirect('login')


def updatehn(request):
    if request.session._session:
        HNdes = request.POST['HN']
        hospitalid = request.POST['hospitalid']
        HNID = request.POST['id']
        Hnupdate = HN.objects.get(pk=HNID)
        Hnupdate.HN = HNdes
        Hnupdate.HNhid = hospitalid
        Hnupdate.save()
        response = redirect('person')
        return response
    else:
        return redirect('login')


def clogin(request):
    Pid = request.POST['Pid']
    Ppassword = request.POST['Ppassword']
    dataPerson = Person.objects.filter(Pid=Pid).first()
    if dataPerson:
        if dataPerson.Pid == Pid and dataPerson.Ppassword == Ppassword:
            dataStaff = Staff.objects.all()
            for dataStaffs in dataStaff:
                if dataStaffs.Pid == Pid:
                    x = 1
                    break
                else:
                    x = 2
        else:
            data = 1
            return render(request, 'login.html',
                          {'data': data, })
        dataHNs = HN.objects.filter(HNpid=dataPerson.Pid, hncheck=1)
        datahos = Hospital.objects.all()
        if dataHNs:
            for dataHNs in dataHNs:
                if dataHNs.hncheck == 1:
                    for datahos in datahos:
                        if datahos.Hid == dataHNs.HNhid:
                            request.session['hospital'] = datahos.Hname
                            request.session['hn'] = dataHNs.HN
                            request.session['Hid'] = datahos.Hid
        else:
            request.session['hospital'] = ''
            request.session['hn'] = ''
            request.session['Hid'] = ''
        request.session['error'] = ''
        request.session['error2'] = ''
        request.session['permission'] = x
        request.session['user_id'] = dataPerson.Pid
        request.session['name'] = dataPerson.Pname
        user_id = request.session['user_id']
        name = request.session['name']
        permission = request.session['permission']
        if x == 1:
            request.session['hospital'] = ''
            request.session['hn'] = ''
            request.session['Hid'] = ''
            response = redirect('dashboard')
            return response
        else:
            response = redirect('calendar')
            return response
    else:
        data = 1
        return render(request, 'login.html',
                      {'data': data, })


def booking(request):
    return render(request, 'booking.html')


def bookingv2(request):
    datahospital = Hospital.objects.all()
    dataHN = HN.objects.filter(HNpid=request.session['user_id'])
    return render(request, 'bookingV2.html',
                  {'datahospital': datahospital, 'dataHN': dataHN, })


def bookingv2ck(request):
    Hid = request.POST['HN']
    x = 9
    y = int(Hid)
    datatime = hospitaltime.objects.filter(Hid=Hid).order_by('timestart')
    datahospital = Hospital.objects.all()
    dataDPM = Department.objects.filter(Hid=Hid)
    dataHN = HN.objects.filter(HNpid=request.session['user_id'])
    dataSTaff = Staff.objects.filter(Hid=Hid)
    dataPerson = Person.objects.all()
    return render(request, 'bookingV2.html',
                  {'datatime': datatime, 'datahospital': datahospital, 'x': x, 'dataHN': dataHN,
                   'Hid': Hid,
                   'dataDPM': dataDPM,
                   'y': y,
                   'dataSTaff': dataSTaff,
                   'dataPerson': dataPerson})


def bookingv2ck2(request):
    Hid = request.POST['HN']
    DD = request.POST['DD']
    Pid = request.POST['Pid']
    x = 10
    y = int(Hid)
    datahospital = Hospital.objects.all()
    dataDPM = Department.objects.filter(Hid=Hid)
    dataHN = HN.objects.filter(HNpid=request.session['user_id'])
    dataSTaff = Staff.objects.filter(Hid=Hid)
    dataOFFFI = Officer.objects.filter(Did=DD)
    dataPerson = Person.objects.all()
    return render(request, 'bookingV2.html',
                  {'datahospital': datahospital, 'x': x, 'dataHN': dataHN,
                   'Hid': Hid,
                   'dataDPM': dataDPM,
                   'y': y,
                   'Pid': Pid,
                   'DD': DD,
                   'dataOFFFI': dataOFFFI,
                   'dataSTaff': dataSTaff,
                   'dataPerson': dataPerson})


def doctor(request):
    if request.session._session:
        checkstaff = Staff.objects.filter(Pid=request.session['user_id']).first()
        if checkstaff.status == 1:
            today = date.today()
            Dids = ''
            OFid = ''
            dataOFF = Officer.objects.filter(Pid=request.session['user_id'])
            if dataOFF:
                for dataOFFs in dataOFF:
                    listdays = []
                    bookingshow = []
                    datatime = hospitaltime.objects.filter(Did=dataOFFs.Did, start=today)
                    dataOFFall = Officer.objects.filter(Did=dataOFFs.Did)
                    Dids = dataOFFs.Did
                    OFid = dataOFFs.OFid
                mydbdashboardesy = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="doqs"
                )
                dashboardsesy = mydbdashboardesy.cursor()
                dashboardsesy.execute(
                    "SELECT START FROM `doqs_schedule` WHERE OFid = %s  GROUP BY start ",
                    [OFid])
                dashboardsesst = dashboardsesy.fetchall()
                for dashboardsesst in dashboardsesst:
                    listday = []
                    listday.append(str(dashboardsesst[0]))
                    listdays.append(listday)
                scheduleshow = schedule.objects.filter(OFid=OFid, status=0).order_by('start')
                for scheduleshow in scheduleshow:
                    count = 0
                    bookinglist = []
                    countbooking = bookingperson.objects.filter(schedule_id=scheduleshow.id)
                    for countbookings in countbooking:
                        count = count + 1
                    sum = (count / scheduleshow.number) * 100
                    if sum > 80:
                        color = '#f22b16'
                    elif sum > 50:
                        color = '#ff9a03'
                    elif sum >= 0:
                        color = 'mediumseagreen'
                    bookinglist.append(str(scheduleshow.start))
                    bookinglist.append(int(scheduleshow.number))
                    bookinglist.append(int(count))
                    bookinglist.append(str(color))
                    bookingshow.append(bookinglist)
                dataST = Staff.objects.get(Pid=request.session['user_id'])
                dataDPM = Department.objects.filter(Hid=dataST.Hid)
                datahospital = Hospital.objects.all()
                dataPerson = Person.objects.all()
                dataOFFall = Officer.objects.filter(Did=Dids)
                count = schedule.objects.filter(OFid=OFid)
                today = date.today()
                d1 = today.strftime("%Y-%m-%d")
                M = today.strftime("%m")
                Y = int(today.strftime("%Y"))
                D = today.strftime("%d")
                Year = Y + 543
                if M == '01':
                    M = "มกราคม"
                elif M == '02':
                    M = "กุมภาพันธ์"
                elif M == '03':
                    M = "มีนาคม"
                elif M == '04':
                    M = "เมษายน"
                elif M == '05':
                    M = "พฤษภาคม"
                elif M == '06':
                    M = "มิถุนายน"
                elif M == '07':
                    M = "กรกฎาคม"
                elif M == '08':
                    M = "สิงหาคม"
                elif M == '09':
                    M = "กันยายน"
                elif M == '10':
                    M = "ตุลาคม"
                elif M == '11':
                    M = "พฤศจิกายน"
                elif M == '12':
                    M = "ธันวาคม"
                schedules = schedule.objects.filter(start=today, OFid=OFid)
                d = {'key': 'value'}
                for da in datatime:
                    x = str(da.timestart)
                    y = str(da.timeend)
                    z = x + '-' + y
                    d[z] = 0
                for scheduless in schedules:
                    x = str(scheduless.timestart)
                    y = str(scheduless.timeend)
                    z = x + '-' + y
                    for a, b in d.items():
                        if a == z:
                            number = scheduless.number
                            if number == 0:
                                d.update({a: 1})
                            else:
                                d.update({a: number})
                persoonall = Person.objects.filter(Pid=request.session['user_id'])
                for persoonalls in persoonall:
                    personname = persoonalls.Pname
                    personid = persoonalls.Pid
                counttoday = schedule.objects.filter(start=today, OFid=OFid)
                dataOFFDPM = Officer.objects.filter(Did=Dids)
                number = 0
                numbertoday = 0
                numberDPM = 0
                numberDPMtoday = 0
                x = 1
                text = ''
                for dataOFFDPMs in dataOFFDPM:
                    countDPM = schedule.objects.filter(OFid=dataOFFDPMs.OFid)
                    for countDPMs in countDPM:
                        numberDPM = countDPMs.number + numberDPM
                for dataOFFDPMs in dataOFFDPM:
                    countDPM = schedule.objects.filter(OFid=dataOFFDPMs.OFid)
                    for countDPMsa in countDPM:
                        if countDPMsa.start == today:
                            numberDPMtoday = countDPMsa.number + numberDPMtoday
                for counttodays in counttoday:
                    if counttodays.OFid == OFid:
                        numbertoday = counttodays.number + numbertoday
                for counts in count:
                    number = counts.number + number
                numbere = 0
                counte = 0
                colore = ''
                dayll = []
                daylls = ''
                for li in listdays:
                    numbere = 0
                    counte = 0
                    colore = ''
                    for bookingshows in bookingshow:
                        if li[0] == bookingshows[0]:
                            numbere = bookingshows[1] + numbere
                            counte = bookingshows[2] + counte
                            colore = bookingshows[3]
                    dayllw = []
                    dayllw.append(li[0])
                    dayllw.append(numbere)
                    dayllw.append(counte)
                    dayllw.append(colore)
                    dayll.append(dayllw)
                mydbdashboardesy = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="doqs"
                )
                dashboardsesy = mydbdashboardesy.cursor()
                dashboardsesy.execute(
                    "SELECT START FROM `doqs_hospitaltime` WHERE Did = %s GROUP BY start",
                    [Dids])
                hospitimess = dashboardsesy.fetchall()
                return render(request, 'doctor.html',
                              {'datatime': datatime, 'dataOFFall': dataOFFall, 'dataOFF': dataOFF, 'dataDPM': dataDPM,
                               'datahospital': datahospital, 'dataPerson': dataPerson, 'dataST': dataST, 'Dids': Dids,
                               'OFid': OFid,
                               'x': x,
                               'd': d,
                               'dayll': dayll,
                               'bookingshow': bookingshow,
                               'listdays': listdays,
                               'schedules': schedules,
                               'number': number,
                               'personname': personname,
                               'personid': personid,
                               'hospitimess': hospitimess,
                               'today': today,
                               'd1': d1,
                               'M': M,
                               'Year': Year,
                               'D': D,
                               'text': text,
                               'numbertoday': numbertoday,
                               'numberDPMtoday': numberDPMtoday,
                               'numberDPM': numberDPM})
            else:
                return redirect('staffinfo')
        else:
            return redirect('staffcheck')
    else:
        return redirect('login')


def testsubmit(request):
    if request.session._session:
        testday = request.POST['datecalendar']
        personid = request.POST['personid']
        dataOFF = Officer.objects.filter(Pid=personid)
        for dataOFFs in dataOFF:
            datatime = hospitaltime.objects.filter(Did=dataOFFs.Did, start=testday)
            dataOFFall = Officer.objects.filter(Did=dataOFFs.Did)
            Dids = dataOFFs.Did
            OFid = dataOFFs.OFid
        today = testday
        text = str(testday)
        d1 = testday
        Y = text[0:4]
        M = text[5:7]
        D = text[8:10]
        Z = int(Y)
        Year = Z + 543
        if M == '01':
            M = "มกราคม"
        elif M == '02':
            M = "กุมภาพันธ์"
        elif M == '03':
            M = "มีนาคม"
        elif M == '04':
            M = "เมษายน"
        elif M == '05':
            M = "พฤษภาคม"
        elif M == '06':
            M = "มิถุนายน"
        elif M == '07':
            M = "กรกฎาคม"
        elif M == '08':
            M = "สิงหาคม"
        elif M == '09':
            M = "กันยายน"
        elif M == '10':
            M = "ตุลาคม"
        elif M == '11':
            M = "พฤศจิกายน"
        elif M == '12':
            M = "ธันวาคม"
        dataST = Staff.objects.get(Pid=request.session['user_id'])
        dataDPM = Department.objects.filter(Hid=dataST.Hid)
        schedules = schedule.objects.filter(start=today, OFid=OFid)
        d = {'key': 'value'}
        for da in datatime:
            x = str(da.timestart)
            y = str(da.timeend)
            z = x + '-' + y
            d[z] = 0
        for scheduless in schedules:
            x = str(scheduless.timestart)
            y = str(scheduless.timeend)
            z = x + '-' + y
            for a, b in d.items():
                if a == z:
                    number = scheduless.number
                    if number == 0:
                        d.update({a: 1})
                    else:
                        d.update({a: number})
        datahospital = Hospital.objects.all()
        dataPerson = Person.objects.all()
        dataOFFall = Officer.objects.filter(Did=Dids)
        count = schedule.objects.filter(OFid=OFid)
        persoonall = Person.objects.filter(Pid=request.session['user_id'])
        for persoonalls in persoonall:
            personname = persoonalls.Pname
        counttoday = schedule.objects.filter(start=testday)
        dataOFFDPM = Officer.objects.filter(Did=Dids)
        number = 0
        numbertoday = 0
        numberDPM = 0
        numberDPMtoday = 0
        x = 1
        text = ''
        for dataOFFDPMs in dataOFFDPM:
            countDPM = schedule.objects.filter(OFid=dataOFFDPMs.OFid)
            for countDPMs in countDPM:
                numberDPM = countDPMs.number + numberDPM
        for dataOFFDPMs in dataOFFDPM:
            countDPM = schedule.objects.filter(OFid=dataOFFDPMs.OFid)
            for countDPMsa in countDPM:
                if countDPMsa.start == today:
                    numberDPMtoday = countDPMsa.number + numberDPMtoday
        for counttodays in counttoday:
            if counttodays.OFid == OFid:
                numbertoday = counttodays.number + numbertoday
        for counts in count:
            number = counts.number + number
        return render(request, 'doctor.html',
                      {'datatime': datatime, 'dataOFFall': dataOFFall, 'dataOFF': dataOFF, 'dataDPM': dataDPM,
                       'datahospital': datahospital, 'dataPerson': dataPerson, 'dataST': dataST, 'Dids': Dids,
                       'OFid': OFid,
                       'x': x,
                       'd1': d1,
                       'd': d,
                       'M': M,
                       'personid': personid,
                       'D': D,
                       'Year': Year,
                       'number': number,
                       'schedules': schedules,
                       'today': today,
                       'personname': personname,
                       'text': text,
                       'numbertoday': numbertoday,
                       'numberDPMtoday': numberDPMtoday,
                       'numberDPM': numberDPM})
    else:
        return redirect('login')


def doctorshow(request):
    if request.session._session:
        Did = request.POST['doctorcheck']
        dataOFF = Officer.objects.filter(Pid=request.session['user_id'])
        dataST = Staff.objects.get(Pid=request.session['user_id'])
        datatime = hospitaltime.objects.filter(Did=Did).order_by('timestart')
        dataDPM = Department.objects.filter(Hid=dataST.Hid)
        datahospital = Hospital.objects.all()
        dataPerson = Person.objects.all()
        x = 8
        return render(request, 'doctor.html',
                      {'datatime': datatime, 'Did': Did, 'dataOFF': dataOFF, 'x': x, 'dataDPM': dataDPM,
                       'datahospital': datahospital})
    else:
        return redirect('login')


def deletehnone(request):
    if request.session._session:
        id = request.POST['id']
        Hn_delete = HN.objects.get(pk=id)
        Hn_delete.delete()
        response = redirect('person')
        return response
    else:
        return redirect('login')


def personinfo(request):
    if request.session._session:
        dataPerson = Person.objects.get(Pid=request.session['user_id'])
        return render(request, 'personinfo.html', {'dataPerson': dataPerson})
    else:
        return redirect('login')


def staff(request):
    if request.session._session:
        checkstaff = Staff.objects.filter(Pid=request.session['user_id']).first()
        if checkstaff.status == 1:
            dataST = Staff.objects.filter(Pid=request.session['user_id']).first()
            dataSTa = Staff.objects.filter(Hid=dataST.Hid)
            dataPs = Person.objects.all()
            dataDPM = Department.objects.filter(Hid=dataST.Hid)
            datahospitales = Hospital.objects.all()
            dataOFFx = Officer.objects.filter(Pid=request.session['user_id']).first()
            Dids = 0
            DPM = 0
            if dataOFFx:
                Dids = dataOFFx.Did
            for datahospitals in datahospitales:
                if dataST.Hid == datahospitals.Hid:
                    hospitalname = datahospitals.Hname
            for dataDPMs in dataDPM:
                if dataDPMs.Did == Dids:
                    DPM = dataDPMs.Dname
            return render(request, 'staff.html',
                          {'dataDPM': dataDPM, 'dataST': dataST, 'datahospitales': datahospitales, 'dataPs': dataPs,
                           'dataSTa': dataSTa,
                           'hospitalname': hospitalname,
                           'DPM': DPM})
        else:
            return redirect('staffcheck')
    else:
        return redirect('login')


def addDPM(request):
    if request.session._session:
        DPM = request.POST['DPM']
        Did = request.POST['Did']
        Hid = request.POST['Hid']
        insertDPM = Department(Did=Did, Dname=DPM, Hid=Hid)
        insertDPM.save()
        response = redirect('staff')
        return response
    else:
        return redirect('login')


def getsession(request):
    if request.session._session:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="doqs"
        )

        mycursor = mydb.cursor()
        mycursor.execute(
            'SELECT a.start,a.end,a.number,c.Dname FROM doqs_schedule as a INNER JOIN  doqs_officer AS b on  a.OFid=b.OFid INNER JOIN  doqs_department AS c on  c.Did=b.Did')
        myresult = mycursor.fetchall()
        return render(request, 'layouts/footbooking.html', {'myresult': myresult})
    else:
        return redirect('login')


def dessession(request):
    del request.session['user_id']
    del request.session['name']
    del request.session['permission']
    del request.session['hn']
    del request.session['hospital']
    del request.session['Hid']
    response = redirect('login')
    return response


def settingHn(request):
    if request.session._session:
        Hid = request.POST['Hid']
        Stupdate = Staff.objects.get(Pid=request.session['user_id'])
        Stupdate.Hid = Hid
        Stupdate.save()
        response = redirect('staff')
        return response
    else:
        return redirect('login')


def addstaff(request):
    if request.session._session:
        Hid = request.POST['Hid']
        Did = request.POST['Did']
        Pname = request.POST['Pname']
        Email = request.POST['Email']
        HMpassword = 'Nopassword'
        checkperson = Person.objects.filter(Pid=Email)
        if checkperson:
            error = 4
            datahospital = Hospital.objects.all()
            dataST = Staff.objects.filter(Pid=request.session['user_id'])
            dataoffSUM = Officer.objects.all()
            dataOFF = Officer.objects.filter(Pid=request.session['user_id'])
            dataDPM = Department.objects.all()
            dataPerson = Person.objects.all()
            if dataOFF:
                x = 3
            else:
                x = 4
            return render(request, 'staffhospital.html',
                          {'datahospital': datahospital, 'dataDPM': dataDPM, 'dataoffSUM': dataoffSUM,
                           'dataPerson': dataPerson,
                           'x': x, 'error': error, 'dataST': dataST,
                           'dataOFF': dataOFF})
        else:
            inserthuman = Person(Pid=Email, Pname=Pname, Ppassword=HMpassword, Pemail=Email)
            inserthuman.save()
            insertstaff = Staff(Pid=Email, Hid=Hid)
            insertstaff.save()
            insertOff = Officer(Pid=Email, Did=Did)
            insertOff.save()
            error = 5
            datahospital = Hospital.objects.all()
            dataST = Staff.objects.filter(Pid=request.session['user_id'])
            dataoffSUM = Officer.objects.all()
            dataOFF = Officer.objects.filter(Pid=request.session['user_id'])
            dataDPM = Department.objects.all()
            dataPerson = Person.objects.all()
            if dataOFF:
                x = 3
            else:
                x = 4
            return render(request, 'staffhospital.html',
                          {'datahospital': datahospital, 'dataDPM': dataDPM, 'dataoffSUM': dataoffSUM,
                           'dataPerson': dataPerson,
                           'x': x, 'error': error, 'dataST': dataST,
                           'dataOFF': dataOFF})
    else:
        return redirect('login')


def mnbook(request):
    if request.session._session:
        today = date.today()
        d1 = today.strftime("%Y-%m-%d")
        M = today.strftime("%m")
        Y = int(today.strftime("%Y"))
        D = today.strftime("%d")
        Year = Y + 543
        if M == '01':
            M = "มกราคม"
        elif M == '02':
            M = "กุมภาพันธ์"
        elif M == '03':
            M = "มีนาคม"
        elif M == '04':
            M = "เมษายน"
        elif M == '05':
            M = "พฤษภาคม"
        elif M == '06':
            M = "มิถุนายน"
        elif M == '07':
            M = "กรกฎาคม"
        elif M == '08':
            M = "สิงหาคม"
        elif M == '09':
            M = "กันยายน"
        elif M == '10':
            M = "ตุลาคม"
        elif M == '11':
            M = "พฤศจิกายน"
        elif M == '12':
            M = "ธันวาคม"
        checkstaff = Staff.objects.filter(Pid=request.session['user_id']).first()
        if checkstaff.status == 1:
            request.session['error2'] = ''
            if request.session['error']:
                request.session['error2'] = request.session['error']
            if request.session['error2']:
                request.session['error'] = ''
            listdays = []
            listday = []
            lisday2 = ''
            lisday3 = ''
            listday4 = []
            dataST = Staff.objects.get(Pid=request.session['user_id'])
            dataDPM = Department.objects.filter(Hid=dataST.Hid)
            datahospital = Hospital.objects.all()
            dataOFF = Officer.objects.filter(Pid=request.session['user_id']).first()
            if dataOFF:
                Dids = dataOFF.Did
                datatime = hospitaltime.objects.filter(Did=Dids).order_by('timestart')
                dataOFFs = Officer.objects.filter(Did=Dids)
                httimes = hospitaltime.objects.filter(Did=Dids)
                for httimes in httimes:
                    listday4.append(str(httimes.start))
                for dataOFFs in dataOFFs:
                    OFid = dataOFFs.OFid
                    mydbdashboardesy = mysql.connector.connect(
                        host="localhost",
                        user="root",
                        password="",
                        database="doqs"
                    )
                    dashboardsesy = mydbdashboardesy.cursor()
                    dashboardsesy.execute(
                        "SELECT START FROM `doqs_schedule` WHERE OFid = %s GROUP BY start ",
                        [OFid])
                    dashboardsesst = dashboardsesy.fetchall()
                    for dashboardsesst in dashboardsesst:
                        listday.append(str(dashboardsesst[0]))
                lisday2 = set(listday)
                lisday3 = set(listday4)
                d1 = today.strftime("%Y-%m-%d")
                return render(request, 'managebooking.html',
                              {'dataDPM': dataDPM, 'today': today, 'Dids': Dids, 'dataST': dataST,
                               'datahospital': datahospital,
                               'listday': lisday2,
                               'lisday3': lisday3,
                               'd1': d1,
                               'D': D,
                               'M': M,
                               'Year': Year,
                               'datatime': datatime})
            else:
                return redirect('staffinfo')
        else:
            return redirect('staffcheck')
    else:
        return redirect('login')


def sthos(request):
    if request.session._session:
        checkstaff = Staff.objects.filter(Pid=request.session['user_id']).first()
        if checkstaff.status == 1:
            dataoffSUM = Officer.objects.all()
            dataOFF = Officer.objects.filter(Pid=request.session['user_id'])
            dataDPM = Department.objects.all()
            dataPerson = Person.objects.all()
            dataST = Staff.objects.filter(Pid=request.session['user_id'])
            datahospital = Hospital.objects.all()
            dataOFFx = Officer.objects.filter(Pid=request.session['user_id']).first()
            if dataOFFx:
                Dids = dataOFFx.Did
                for dataSTs in dataST:
                    Hids = int(dataSTs.Hid)
                for datahospitals in datahospital:
                    if Hids == datahospitals.Hid:
                        hospitalname = datahospitals.Hname
                for dataDPMs in dataDPM:
                    if dataDPMs.Did == Dids:
                        DPM = dataDPMs.Dname
                if dataOFF:
                    x = 3
                else:
                    x = 4
                return render(request, 'staffhospital.html',
                              {'datahospital': datahospital, 'dataDPM': dataDPM, 'dataoffSUM': dataoffSUM,
                               'dataPerson': dataPerson,
                               'x': x, 'dataST': dataST,
                               'dataOFF': dataOFF,
                               'Hids': Hids,
                               'DPM': DPM,
                               'hospitalname': hospitalname, })
            else:
                return redirect('staffinfo')
        else:
            return redirect('staffcheck')
    else:
        return redirect('login')


def sthoscheck(request):
    if request.session._session:
        Didcheck = request.POST['Didcheck']
        dataST = Staff.objects.filter(Pid=request.session['user_id'])
        dataoffSUM = Officer.objects.all()
        dataOFF = Officer.objects.filter(Pid=request.session['user_id'])
        dataDPM = Department.objects.all()
        dataPerson = Person.objects.all()
        datahospital = Hospital.objects.all()
        if Didcheck:
            x = 5
        return render(request, 'staffhospital.html',
                      {'dataDPM': dataDPM, 'dataoffSUM': dataoffSUM, 'dataPerson': dataPerson, 'x': x, 'dataST': dataST,
                       'dataOFF': dataOFF,
                       'Didcheck': Didcheck, 'datahospital': datahospital})
    else:
        return redirect('login')


def addtime(request):
    if request.session._session:
        datetest = request.POST['datetest']
        Hid = request.POST['Hid']
        Did = request.POST['Did']
        dateInputList = datetest.split(',')
        dateList = []
        hpttime = hospitaltime.objects.filter(Did=Did)
        if datetest:
            for i in dateInputList:
                if i not in dateList:
                    dateList.append(i)
            for date in dateList:
                checkdpm = Department.objects.filter(Did=Did)
                for checkdpms in checkdpm:
                    checkOFF = Officer.objects.filter(Did=checkdpms.Did)
                    for checkOFFs in checkOFF:
                        check = schedule.objects.filter(start=date, OFid=checkOFFs.OFid)
                        for checks in check:
                            if checks.number > 0:
                                dateList.remove(date)
            for test in dateList:
                timestart = request.POST['timestart']
                timeend = request.POST['timeend']
                print(timestart)
                print(timeend)
                if timestart != "" and timeend != "":
                    inserttime = hospitaltime(timestart=timestart, timeend=timeend, Hid=Hid, Did=Did, start=test)
                    inserttime.save()
                for x in range(99):
                    name = str(x)
                    timestart = str('timestart' + name)
                    timeend = str('timeend' + name)
                    if timestart in request.POST:
                        timestart = request.POST[timestart]
                        timeend = request.POST[timeend]
                        if timestart != "" and timeend != " ":
                            inserttime = hospitaltime(timestart=timestart, timeend=timeend, Hid=Hid, Did=Did,
                                                      start=test)
                            inserttime.save()
                        else:
                            request.session['error'] = 2
                            return redirect('mnbook')
            for hpttime in hpttime:
                id = str(hpttime.id)
                timestart = str('timestartx' + id)
                timeend = str('timeendx' + id)
                if timestart in request.POST:
                    timestart = request.POST[timestart]
                    timeend = request.POST[timeend]
                    if timestart != "" and timeend != "":
                        hospitaltimest = hospitaltime.objects.filter(pk=id)
                        for hospitaltimest in hospitaltimest:
                            for test in dateList:
                                hospitaltime.objects.filter(start=test, Did=hospitaltimest.Did,
                                                            timestart=hospitaltimest.timestart,
                                                            timeend=hospitaltimest.timeend).update(timestart=timestart,
                                                                                                   timeend=timeend)

            response = redirect('mnbook')
            return response
        else:
            request.session['error'] = 1
            return redirect('mnbook')
    else:
        return redirect('login')


def staffmoniter(request):
    if request.session._session:
        checkstaff = Staff.objects.filter(Pid=request.session['user_id']).first()
        if checkstaff.status == 1:
            dataOFFax = Officer.objects.filter(Pid=request.session['user_id'])
            modalbk = bookingperson.objects.all()
            if dataOFFax:
                dataST = Staff.objects.get(Pid=request.session['user_id'])
                for dataOFFs in dataOFFax:
                    OFid = dataOFFs.OFid
                    datatime = hospitaltime.objects.filter(Did=dataOFFs.Did).order_by('timestart')
                dataDPM = Department.objects.filter(Hid=dataST.Hid)
                datahospital = Hospital.objects.all()
                dataPerson = Person.objects.all()
                dataST = Staff.objects.get(Pid=request.session['user_id'])
                dataOFF = Officer.objects.filter(Pid=request.session['user_id']).first()
                Dids = dataOFF.Did
                dataOFFall = Officer.objects.filter(Did=Dids)
                dataOFF = Officer.objects.filter(Pid=request.session['user_id']).first()
                schedules = schedule.objects.filter(OFid=dataOFF.OFid)
                error = ''
                count = 0
                color = ''
                sum = ''
                bookingshow = []
                for scheduleses in schedules:
                    count = 0
                    personbooking = bookingperson.objects.filter(schedule_id=scheduleses.id)
                    for personbookings in personbooking:
                        count = count + 1

                    bookinglist = []
                    bookinglist.append(str(scheduleses.id))
                    bookinglist.append(str(scheduleses.start))
                    bookinglist.append(str(scheduleses.timestart))
                    bookinglist.append(str(scheduleses.timeend))
                    bookinglist.append(str(scheduleses.number))
                    bookinglist.append(count)
                    bookinglist.append(color)
                    bookingshow.append(bookinglist)
                return render(request, 'staffmoniter.html',
                              {'dataST': dataST, 'datahospital': datahospital,
                               'Dids': Dids,
                               'OFid': OFid,
                               'dataOFFax': dataOFFax,
                               'bookingshow': bookingshow,
                               'dataDPM': dataDPM,
                               'modalbk': modalbk,
                               'error': error,
                               'dataPerson': dataPerson,
                               'schedules': schedules,
                               'dataOFFall': dataOFFall})
            else:
                return redirect('staffinfo')
        else:
            return redirect('staffcheck')
    else:
        return redirect('login')


def staffshow(request):
    if request.session._session:
        dataOFFax = Officer.objects.filter(Pid=request.session['user_id'])
        dataST = Staff.objects.get(Pid=request.session['user_id'])
        for dataOFFs in dataOFFax:
            datatime = hospitaltime.objects.filter(Did=dataOFFs.Did).order_by('timestart')
        dataDPM = Department.objects.filter(Hid=dataST.Hid)
        dataOFFall = Officer.objects.all()
        dataPerson = Person.objects.all()
        datahospital = Hospital.objects.all()
        dataST = Staff.objects.get(Pid=request.session['user_id'])
        Dids = request.POST['Did']
        timehosmin = hospitaltime.objects.filter(Did=Dids).order_by('timestart').first()
        timehosmax = hospitaltime.objects.filter(Did=Dids).order_by('timeend')
        timemin = timehosmin.timestart
        for timehosmaxs in timehosmax:
            maxtime = timehosmaxs.timeend
            showtime = timehosmaxs.timeend
            if maxtime >= timehosmaxs.timeend:
                timemax = showtime

        x = 8
        return render(request, 'staffmoniter.html',
                      {'dataST': dataST, 'datahospital': datahospital, 'timemax': timemax, 'timemin': timemin,
                       'Dids': Dids,
                       'dataOFFax': dataOFFax,
                       'dataDPM': dataDPM,
                       'dataOFFall': dataOFFall,
                       'dataPerson': dataPerson,
                       'x': x})
    else:
        return redirect('login')


def editperson(request):
    if request.session._session:
        HMid = request.POST['userid']
        HMname = request.POST['usename']
        HMpassword = request.POST['password']
        HMemail = request.POST['mail']
        user_edit = Person.objects.get(pk=HMid)
        user_edit.Pname = HMname
        user_edit.Pemail = HMemail
        user_edit.Ppassword = HMpassword
        user_edit.save()
        response = redirect('personinfo')
        return response
    else:
        return redirect('login')


def staffinfo(request):
    if request.session._session:
        checkstaff = Staff.objects.filter(Pid=request.session['user_id']).first()
        dataST = Staff.objects.filter(Pid=request.session['user_id']).first()
        if checkstaff.status == 1:
            dataPerson = Person.objects.get(Pid=request.session['user_id'])
            datahospital = Hospital.objects.all()
            datahospitales = Hospital.objects.all()
            dataST = Staff.objects.get(Pid=request.session['user_id'])
            dataOFF = Officer.objects.filter(Pid=request.session['user_id'])
            if dataST.Hid != '':
                dataDPM = Department.objects.filter(Hid=dataST.Hid)
            else:
                dataDPM = Department.objects.all()
            Dids = ''
            dataOFFx = Officer.objects.filter(Pid=request.session['user_id']).first()
            if dataOFFx:
                Dids = dataOFFx.Did
            if dataOFF:
                x = 1
            else:
                x = 2
            return render(request, 'staffinfo.html',
                          {'dataST': dataST, 'datahospitales': datahospitales, 'datahospital': datahospital,
                           'dataPerson': dataPerson, 'dataOFF': dataOFF,
                           'Dids': Dids,
                           'dataST': dataST,
                           'dataDPM': dataDPM, 'x': x})
        else:
            return redirect('staffcheck')
    else:
        return redirect('login')


def editstaff(request):
    if request.session._session:
        HMid = request.POST['userid']
        HMname = request.POST['usename']
        HMpassword = request.POST['password']
        mail = request.POST['mail']
        Hid = request.POST['Hid']
        Did = request.POST['Did']
        CheckOFf = Officer.objects.filter(Pid=HMid)
        if CheckOFf:
            offupdate = Officer.objects.get(Pid=HMid)
            offupdate.Did = request.POST['Did']
            offupdate.save()
        else:
            officer = Officer(Did=Did, Pid=HMid)
            officer.save()
        user_edit = Person.objects.get(pk=HMid)
        user_edit.Pname = HMname
        user_edit.Ppassword = HMpassword
        user_edit.Pemail = mail
        user_edit.save()
        staff_edit = Staff.objects.get(Pid=HMid)
        staff_edit.Hid = Hid
        staff_edit.save()
        response = redirect('staffinfo')
        return response
    else:
        return redirect('login')


def gettimestart(request):
    if request.session._session:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="doqs"
        )
        dataST = Staff.objects.filter(Pid=request.session['user_id'])
        mycursor = mydb.cursor()
        sql = "SELECT * FROM doqs_hospitaltime"
        mycursor.execute(sql)
        myresult1 = mycursor.fetchall()
        timehosmin = hospitaltime.objects.filter(Hid=dataST.Hid).order_by('timestart').first()
        timehosmax = hospitaltime.objects.filter(Hid=dataST.Hid).order_by('timeend')
        timemin = timehosmin.timestart
        dataOFF = Officer.objects.filter(Pid=request.session['user_id']).first()
        schedules = schedule.objects.filter(OFid=dataOFF.OFid)
        show = '<span class="label label-success m-l-5 t-minus-1">NEW</span>'
        for timehosmaxs in timehosmax:
            maxtime = timehosmaxs.timeend
            showtime = timehosmaxs.timeend
            if maxtime >= timehosmaxs.timeend:
                timemax = showtime
        return render(request, 'layouts/footbooking.html',
                      {'myresult1': myresult1, 'timemin': timemin, 'timemax': timemax, 'schedules': schedules,
                       'show': show})
    else:
        return redirect('login')


def deletetimehos(request):
    if request.session._session:
        selected_tests = request.POST['test_list_ids']
        dateListes = request.POST['dateList']
        dateInputList = dateListes.split(',')
        dateList = []
        for i in dateInputList:
            if i not in dateList:
                dateList.append(i)
        selected_tests = json.loads(selected_tests)
        for dateLists in dateList:
            for test in selected_tests:
                if test != '':
                    hospitaltime.objects.filter(id__in=selected_tests, start=dateLists).delete()
        response = redirect('mnbook')
        return response
    else:
        return redirect('login')


def managecount(request):
    if request.session._session:
        datahospital = Hospital.objects.all()
        dataST = Staff.objects.get(Pid=request.session['user_id'])
        dataOFF = Officer.objects.get(Pid=request.session['user_id'])
        dataTime = hospitaltime.objects.filter(Did=dataOFF.Did)
        return render(request, 'managecount.html',
                      {'datahospital': datahospital, 'dataST': dataST, 'dataOFF': dataOFF, 'dataTime': dataTime})
    else:
        return redirect('login')


def addcount(request):
    if request.session._session:
        datecalendar = request.POST['datetest']
        dateInputList = datecalendar.split(',')
        dateList = []
        for i in dateInputList:
            if i not in dateList:
                dateList.append(i)
        OFids = request.POST['OFid']
        dataOFF = Officer.objects.filter(Pid=OFids)
        for dataOFFs in dataOFF:
            datatime = hospitaltime.objects.filter(Did=dataOFFs.Did)
            dataOFFall = Officer.objects.filter(Did=dataOFFs.Did)
            Dids = dataOFFs.Did
            OFid = dataOFFs.OFid

        for dat in dateList:
            time = hospitaltime.objects.filter(start=dat)
            for x in time:
                tstart = str(x.timestart)
                tend = str(x.timeend)
                ti = str('time' + tstart + '-' + tend)
                cu = str('count' + tstart + '-' + tend)
                ch = str('check' + tstart + '-' + tend)
                if ti in request.POST:
                    tis = request.POST[ti]
                    if ch in request.POST:
                        chs = request.POST[ch]
                    else:
                        chs = 0
                    if cu in request.POST:
                        cus = request.POST[cu]
                        checkes = request.POST[cu]
                        if cus == "":
                            cus = 0

                    timstarts = tis[0:8]
                    timeends = tis[9:17]
                    scheduless = schedule.objects.filter(start=dat, timestart=timstarts, timeend=timeends, OFid=OFids)
                    if scheduless:
                        for scheduless in scheduless:
                            check = int(cus)
                            count = 0
                            bookingpers = bookingperson.objects.filter(schedule_id=scheduless.id)
                            for bookingpers in bookingpers:
                                count = count + 1
                            if check > count:
                                schedule.objects.filter(id=scheduless.id).update(number=cus)
                    else:
                        if cus != 0 or chs != 0:
                            insertcalendar = schedule(number=cus, start=dat, timestart=timstarts, timeend=timeends,
                                                      OFid=OFids,
                                                      status=chs)
                            insertcalendar.save()
        response = redirect('doctor')
        return response
    else:
        return redirect('login')


def testcalendar(request):
    if request.session._session:
        dataOFF = Officer.objects.get(Pid=request.session['user_id'])
        show = '<span class="label label-success m-l-5 t-minus-1">NEW</span>'
        testtime = hospitaltime.objects.filter(Did=dataOFF.Did)
        return render(request, 'testcalendar.html', {'testtime': testtime, 'show': show})
    else:
        return redirect('login')


def doctorcheck(request):
    if request.session._session:
        OFides = request.POST['OFid']
        today = date.today()
        Dids = ''
        OFid = ''
        check = 1
        dataOFF = Officer.objects.filter(Pid=OFides)
        bookingshow = []
        listdays = []
        if dataOFF:
            for dataOFFs in dataOFF:
                datatime = hospitaltime.objects.filter(Did=dataOFFs.Did, start=today)
                dataOFFall = Officer.objects.filter(Did=dataOFFs.Did)
                Dids = dataOFFs.Did
                OFid = dataOFFs.OFid
            mydbdashboardesy = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="doqs"
            )
            dashboardsesy = mydbdashboardesy.cursor()
            dashboardsesy.execute(
                "SELECT START FROM `doqs_schedule` WHERE OFid = %s AND status = '0' GROUP BY start ",
                [OFid])
            dashboardsesst = dashboardsesy.fetchall()
            for dashboardsesst in dashboardsesst:
                listday = []
                listday.append(str(dashboardsesst[0]))
                listdays.append(listday)
            scheduleshow = schedule.objects.filter(OFid=OFid, status=0).order_by('start')
            for scheduleshow in scheduleshow:
                count = 0
                bookinglist = []
                countbooking = bookingperson.objects.filter(schedule_id=scheduleshow.id)
                for countbookings in countbooking:
                    count = count + 1
                sum = (count / scheduleshow.number) * 100
                if sum > 80:
                    color = '#f22b16'
                elif sum > 50:
                    color = '#ff9a03'
                elif sum >= 0:
                    color = 'mediumseagreen'
                bookinglist.append(str(scheduleshow.start))
                bookinglist.append(int(scheduleshow.number))
                bookinglist.append(int(count))
                bookinglist.append(str(color))
                bookingshow.append(bookinglist)
            dataST = Staff.objects.get(Pid=OFides)
            dataDPM = Department.objects.filter(Hid=dataST.Hid)
            datahospital = Hospital.objects.all()
            dataPerson = Person.objects.all()
            dataOFFall = Officer.objects.filter(Did=Dids)
            count = schedule.objects.filter(OFid=OFid)
            today = date.today()
            d1 = today.strftime("%Y-%m-%d")
            M = today.strftime("%m")
            Y = int(today.strftime("%Y"))
            D = today.strftime("%d")
            Year = Y + 543
            if M == '01':
                M = "มกราคม"
            elif M == '02':
                M = "กุมภาพันธ์"
            elif M == '03':
                M = "มีนาคม"
            elif M == '04':
                M = "เมษายน"
            elif M == '05':
                M = "พฤษภาคม"
            elif M == '06':
                M = "มิถุนายน"
            elif M == '07':
                M = "กรกฎาคม"
            elif M == '08':
                M = "สิงหาคม"
            elif M == '09':
                M = "กันยายน"
            elif M == '10':
                M = "ตุลาคม"
            elif M == '11':
                M = "พฤศจิกายน"
            elif M == '12':
                M = "ธันวาคม"
            schedules = schedule.objects.filter(start=today, OFid=OFid)
            d = {'key': 'value'}
            for da in datatime:
                x = str(da.timestart)
                y = str(da.timeend)
                z = x + '-' + y
                d[z] = 0
            for scheduless in schedules:
                x = str(scheduless.timestart)
                y = str(scheduless.timeend)
                z = x + '-' + y
                for a, b in d.items():
                    if a == z:
                        number = scheduless.number
                        if number == 0:
                            d.update({a: 1})
                        else:
                            d.update({a: number})
            persoonall = Person.objects.filter(Pid=OFides)
            for persoonalls in persoonall:
                personname = persoonalls.Pname
                personid = persoonalls.Pid
                Pid = persoonalls.Pid
            counttoday = schedule.objects.filter(start=today, OFid=OFid)
            dataOFFDPM = Officer.objects.filter(Did=Dids)
            number = 0
            numbertoday = 0
            numberDPM = 0
            numberDPMtoday = 0
            x = 1
            text = ''
            for dataOFFDPMs in dataOFFDPM:
                countDPM = schedule.objects.filter(OFid=dataOFFDPMs.OFid)
                for countDPMs in countDPM:
                    numberDPM = countDPMs.number + numberDPM
            for dataOFFDPMs in dataOFFDPM:
                countDPM = schedule.objects.filter(OFid=dataOFFDPMs.OFid)
                for countDPMsa in countDPM:
                    if countDPMsa.start == today:
                        numberDPMtoday = countDPMsa.number + numberDPMtoday
            for counttodays in counttoday:
                if counttodays.OFid == OFid:
                    numbertoday = counttodays.number + numbertoday
            for counts in count:
                number = counts.number + number
            numbere = 0
            counte = 0
            colore = ''
            dayll = []
            daylls = ''
            for li in listdays:
                numbere = 0
                counte = 0
                colore = ''
                for bookingshows in bookingshow:
                    if li[0] == bookingshows[0]:
                        numbere = bookingshows[1] + numbere
                        counte = bookingshows[2] + counte
                        colore = bookingshows[3]
                dayllw = []
                dayllw.append(li[0])
                dayllw.append(numbere)
                dayllw.append(counte)
                dayllw.append(colore)
                dayll.append(dayllw)
            mydbdashboardesy = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="doqs"
            )
            dashboardsesy = mydbdashboardesy.cursor()
            dashboardsesy.execute(
                "SELECT START FROM `doqs_hospitaltime` WHERE Did = %s GROUP BY start",
                [Dids])
            hospitimess = dashboardsesy.fetchall()
            return render(request, 'doctor.html',
                          {'datatime': datatime, 'dataOFFall': dataOFFall, 'dataOFF': dataOFF, 'dataDPM': dataDPM,
                           'datahospital': datahospital, 'dataPerson': dataPerson, 'dataST': dataST, 'Dids': Dids,
                           'OFid': OFid,
                           'x': x,
                           'd': d,
                           'dayll': dayll,
                           'schedules': schedules,
                           'number': number,
                           'personname': personname,
                           'personid': personid,
                           'hospitimess': hospitimess,
                           'Pid': Pid,
                           'today': today,
                           'd1': d1,
                           'M': M,
                           'Year': Year,
                           'check': check,
                           'D': D,
                           'text': text,
                           'numbertoday': numbertoday,
                           'numberDPMtoday': numberDPMtoday,
                           'numberDPM': numberDPM})
        else:
            return redirect('staffinfo')
    else:
        return redirect('login')


def getdatevalue(request):
    if request.session._session:
        dateList = request.POST['dateList']
        dataST = Staff.objects.get(Pid=request.session['user_id'])
        dataDPM = Department.objects.filter(Hid=dataST.Hid)
        datahospital = Hospital.objects.all()
        dataOFF = Officer.objects.filter(Pid=request.session['user_id']).first()
        Dids = dataOFF.Did
        datehos = hospitaltime.objects.filter(start=dateList, Did=Dids)
        dataOFFALL = Officer.objects.filter(Did=Dids)
        daytimelist = []
        listime = ''
        listime2 = []
        for dataOFFALL in dataOFFALL:
            datascd = schedule.objects.filter(OFid=dataOFFALL.OFid)
            for datascd in datascd:
                daytimelist.append(str(datascd.start))

        timelist = []
        for datehoss in datehos:
            time = []
            time.append(str(datehoss.id))
            time.append(str(datehoss.timestart))
            time.append(str(datehoss.timeend))
            time.append(str(datehoss.start))
            timelist.append(time)
        listime = set(daytimelist)
        for listime in listime:
            listime2.append(listime)
        data = json.dumps({
            'timelist': timelist,
            'listime2': listime2,
        })
        return HttpResponse(data, content_type="application/json")
    else:
        return redirect('login')


def testses(request):
    if request.session._session:
        print("xxxx")
        dateList = request.POST['dateList']
        Pid = request.POST['OFid']
        dataOFFCheck = Officer.objects.filter(OFid=Pid).first()
        dataST = Staff.objects.get(Pid=dataOFFCheck.Pid)
        dataDPM = Department.objects.filter(Hid=dataST.Hid)
        datahospital = Hospital.objects.all()
        dataOFF = Officer.objects.filter(Pid=dataOFFCheck.Pid).first()
        Dids = dataOFF.Did
        OFids = dataOFF.OFid
        print(Dids)
        datehos = hospitaltime.objects.filter(start=dateList)
        timelist = []
        timelistes = []
        for datehoss in datehos:
            if datehoss.Did == Dids:
                time = []
                time.append(str(datehoss.id))
                time.append(str(datehoss.timestart))
                time.append(str(datehoss.timeend))
                time.append(str(datehoss.start))
                timelist.append(time)
        for timelists in timelist:
            datatimehos = hospitaltime.objects.filter(Did=Dids)
            for datatimehoss in datatimehos:
                if datatimehoss.Did == Dids:
                    if str(datatimehoss.timestart) == timelists[1] and str(datatimehoss.timeend) == timelists[2]:
                        times = []
                        times.append(str(datatimehoss.id))
                        times.append(str(datatimehoss.timestart))
                        times.append(str(datatimehoss.timeend))
                        times.append(str(datatimehoss.start))
                        timelistes.append(times)
        print(timelist)
        print(timelistes)
        schedules = schedule.objects.filter(start=dateList, OFid=OFids)
        datatime = hospitaltime.objects.filter(start=dateList, Did=Dids)
        timedata = []
        for datetimes in datatime:
            datatimeest = []
            datatimeest.append(str(datetimes.id))
            datatimeest.append(str(datetimes.timestart))
            datatimeest.append(str(datetimes.timeend))
            timedata.append(datatimeest)
        d = {'key': 'value'}
        for da in datatime:
            x = str(da.timestart)
            y = str(da.timeend)
            z = x + '-' + y
            d[z] = 0
        for scheduless in schedules:
            x = str(scheduless.timestart)
            y = str(scheduless.timeend)
            z = x + '-' + y
            for a, b in d.items():
                if a == z:
                    number = scheduless.number
                    if number == 0:
                        d.update({a: 1})
                    else:
                        d.update({a: number})
        print(d)
        counttoday = schedule.objects.filter(start=dateList, OFid=OFids)
        dataOFFDPM = Officer.objects.filter(Did=Dids)
        number = 0
        numbertoday = 0
        numberDPM = 0
        numberDPMtoday = 0
        x = 1
        text = ''
        for dataOFFDPMs in dataOFFDPM:
            countDPM = schedule.objects.filter(OFid=dataOFFDPMs.OFid, start=dateList)
            for countDPMsa in countDPM:
                numberDPMtoday = countDPMsa.number + numberDPMtoday
        for counttodays in counttoday:
            if counttodays.OFid == counttodays.OFid:
                numbertoday = counttodays.number + numbertoday
        data = json.dumps({
            'actions': timelists,
            'numbertoday': numbertoday,
            'numberDPMtoday': numberDPMtoday,
            'holds': timelistes,
            'd': d,
            'timedata': timedata,
        })
        return HttpResponse(data, content_type="application/json")
    else:
        return redirect('login')


def resetcount(request):
    if request.session._session:
        datecalendar = request.POST['datetest']
        dateInputList = datecalendar.split(',')
        dateList = []
        for i in dateInputList:
            if i not in dateList:
                dateList.append(i)
        OFids = request.POST['OFid']
        dataOFF = Officer.objects.filter(Pid=OFids)
        for dataOFFs in dataOFF:
            datatime = hospitaltime.objects.filter(Did=dataOFFs.Did)
            dataOFFall = Officer.objects.filter(Did=dataOFFs.Did)
            Dids = dataOFFs.Did
            OFid = dataOFFs.OFid
        for dat in dateList:
            schedule_delete = schedule.objects.filter(start=dat, OFid=OFids)
            for schedule_delete in schedule_delete:
                schedule.objects.filter(pk=schedule_delete.id).delete()
        response = redirect('doctor')
        return response
    else:
        return redirect('login')


def select(request):
    if request.session._session:
        f1 = request.POST['function']

        if f1 == 'hospital':
            id = request.POST['id']
            datads = Department.objects.filter(Hid=id)
            select = []
            one = []
            one.append("<option value='' selected>แผนก</option>")
            select.append(one)
            for datad in datads:
                test = []
                test.append("<option value='" + datad.Did + "' >" + datad.Dname + "</option>")
                select.append(test)
            return HttpResponse(select)
        if f1 == 'department':
            id = request.POST['id']
            dataofs = Officer.objects.filter(Did=id)
            select = []
            datapers = Person.objects.all()
            one = []
            one.append("<option value='' selected>แพทย์</option>")
            select.append(one)
            for dataof in dataofs:
                for dataper in datapers:
                    if dataper.Pid == dataof.Pid:
                        test = []
                        test.append(
                            "<option value='" + str(dataof.OFid) + "' >" + dataper.Pname + "</option>")
                        select.append(test)
            return HttpResponse(select)
    else:
        return redirect('login')


def getdatebooking(request):
    if request.session._session:
        today = date.today()
        re_dep = request.POST['re_dep']
        re_sta = request.POST['re_sta']
        re_hos = request.POST['re_hos']
        re_hoss = int(re_hos)
        OFid = int(re_sta)
        re_stas = int(re_sta)
        bookingdetail = []
        dataschedule = schedule.objects.filter(OFid=OFid)
        datads = Department.objects.filter(Hid=re_hoss)
        dataofs = Officer.objects.filter(Did=re_dep)
        datapers = Person.objects.all()
        datahospital = Hospital.objects.all()
        dataHN = HN.objects.filter(HNpid=request.session['user_id'])
        for dataschedules in dataschedule:
            bookinglist = []
            bookinglist.append(str(dataschedules.start))
            bookinglist.append(str(dataschedules.number))
            bookingdetail.append(bookinglist)
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="doqs"
        )
        sum = 0
        color = ''
        mycursor = mydb.cursor()
        mycursor.execute(
            "SELECT s.start, SUM(s.number), COUNT(tt.schedule_id) FROM doqs_schedule AS s LEFT JOIN doqs_bookingperson AS tt ON tt.schedule_id = s.id WHERE s.OFid =  %s AND s.status = 0 GROUP BY s.start",
            [OFid])
        myresult = mycursor.fetchall()
        bookingdetail = []
        for myresults in myresult:
            number = 0
            schedulex = schedule.objects.filter(start=myresults[0], OFid=OFid)
            for schedulex in schedulex:
                number = schedulex.number + number
            bookinglist = []
            sum = (myresults[2] / number) * 100
            if sum > 80:
                color = 'red'
            elif sum > 50:
                color = 'orange'
            elif sum >= 0:
                color = 'green'
            bookinglist.append(myresults[0])
            bookinglist.append(number)
            bookinglist.append(myresults[2])
            bookinglist.append(color)
            bookingdetail.append(bookinglist)
        mydbhistory = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="doqs"
        )
        mydbhistory = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="doqs"
        )
        history = mydbhistory.cursor()
        history.execute(
            "SELECT a.event,b.start,b.timestart,b.timeend,d.Dname,e.Pname,a.status FROM doqs_bookingperson AS a INNER JOIN doqs_schedule AS b ON a.schedule_id = b.id INNER JOIN doqs_officer AS c ON b.OFid = c.OFid INNER JOIN doqs_department AS d ON d.Did = c.Did INNER JOIN doqs_person AS e ON e.Pid = c.Pid WHERE a.Pid = %s",
            [request.session['user_id']])
        historys = history.fetchall()
        mydbhistoryes = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="doqs"
        )
        historyes = mydbhistoryes.cursor()
        historyes.execute(
            "SELECT a.event,a.verify,a.status,b.start,b.timestart,b.timeend,d.Pname,f.Dname,g.Hname,a.id,a.reed FROM doqs_bookingperson AS a INNER JOIN doqs_schedule AS b ON a.schedule_id = b.id INNER JOIN doqs_officer AS c ON b.OFid = c.OFid INNER JOIN doqs_person AS d ON c.Pid = d.Pid INNER JOIN doqs_department AS f ON c.Did = f.Did INNER JOIN doqs_hospital AS g ON f.Hid = g.Hid  WHERE a.Pid = %s  ORDER BY b.start DESC",
            [request.session['user_id']])
        historyses = historyes.fetchall()
        dateshowlist = []
        for historyseses in historyses:
            dateshow = historyseses[1]
            dateshowlist.append(dateshow)
        dbqueue = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="doqs"
        )
        queue = dbqueue.cursor()
        queue.execute(
            "SELECT a.event,a.verify,a.status,b.start,b.timestart,b.timeend,d.Pname,f.Dname,g.Hname,a.id,a.reed,b.number,a.callqueue,a.Pid FROM doqs_bookingperson AS a INNER JOIN doqs_schedule AS b ON a.schedule_id = b.id INNER JOIN doqs_officer AS c ON b.OFid = c.OFid INNER JOIN doqs_person AS d ON c.Pid = d.Pid INNER JOIN doqs_department AS f ON c.Did = f.Did INNER JOIN doqs_hospital AS g ON f.Hid = g.Hid WHERE b.start = %s ORDER BY a.id ASC",
            [today])
        queues = queue.fetchall()
        queueslist = []
        countes = 0
        sumq = 0
        for queuesest in queues:
            listqu = []
            countes = countes + 1
            sumq = sumq + 1
            if queuesest[13] == request.session['user_id']:
                if queuesest[12] == None:
                    sumq = sumq - 1
                    listqu.append(countes)
                    listqu.append(str(queuesest[0]))
                    listqu.append(str(queuesest[1]))
                    listqu.append(int(queuesest[2]))
                    listqu.append(str(queuesest[3]))
                    listqu.append(str(queuesest[4]))
                    listqu.append(str(queuesest[5]))
                    listqu.append(str(queuesest[6]))
                    listqu.append(str(queuesest[7]))
                    listqu.append(str(queuesest[8]))
                    listqu.append(str(queuesest[9]))
                    listqu.append(str(queuesest[10]))
                    listqu.append(str(queuesest[11]))
                    listqu.append(str(queuesest[12]))
                    listqu.append(str(queuesest[13]))
                    listqu.append(int(sumq))
                    queueslist.append(listqu)
                    break
                else:
                    sumq = 0
                    listqu.append(countes)
                    listqu.append(str(queuesest[0]))
                    listqu.append(str(queuesest[1]))
                    listqu.append(int(queuesest[2]))
                    listqu.append(str(queuesest[3]))
                    listqu.append(str(queuesest[4]))
                    listqu.append(str(queuesest[5]))
                    listqu.append(str(queuesest[6]))
                    listqu.append(str(queuesest[7]))
                    listqu.append(str(queuesest[8]))
                    listqu.append(str(queuesest[9]))
                    listqu.append(str(queuesest[10]))
                    listqu.append(str(queuesest[11]))
                    listqu.append(str(queuesest[12]))
                    listqu.append(str(queuesest[13]))
                    listqu.append(int(sumq))
                    queueslist.append(listqu)
                    break
        y = 0
        checkactive = ''
        checkactivequeue = ''
        for queueslist in queueslist:
            if queueslist[2] == 'None':
                print("xxx")
            else:
                print("xxx")
                y = 1
                checkactivequeue = int(queueslist[10])
        if historyses:
            x = 0
        else:
            x = 1
        for historyseses in historyses:
            checkactive = historyseses[9]
            break
        return render(request, 'calendar.html',
                      {'bookingdetail': bookingdetail, 're_dep': re_dep, 'datads': datads, 'dataofs': dataofs,
                       'datapers': datapers, 're_sta': re_stas, 're_hos': re_hoss, 'datahospital': datahospital,
                       'dataHN': dataHN,
                       'checkactivequeue': checkactivequeue,
                       'x': x,
                       'y': y,
                       'today': today,
                       'checkactive': checkactive,
                       'historys': historys,
                       'dateshowlist': dateshowlist,
                       'historyses': historyses,
                       'myresult': myresult})
    else:
        return redirect('login')


def getdatebooking2(request, re_dep, re_sta, re_hos):
    if request.session._session:
        today = date.today()
        re_hoss = int(re_hos)
        re_stas = int(re_sta)
        OFid = int(re_sta)
        bookingdetail = []
        dataschedule = schedule.objects.filter(OFid=OFid)
        datads = Department.objects.filter(Hid=re_hoss)
        dataofs = Officer.objects.filter(Did=re_dep)
        datapers = Person.objects.all()
        datahospital = Hospital.objects.all()
        dataHN = HN.objects.filter(HNpid=request.session['user_id'])
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="doqs"
        )
        sum = 0
        color = ''
        mycursor = mydb.cursor()
        mycursor.execute(
            "SELECT s.start, SUM(s.number), COUNT(tt.schedule_id) FROM doqs_schedule AS s LEFT JOIN doqs_bookingperson AS tt ON tt.schedule_id = s.id WHERE s.OFid =  %s AND s.status = 0 GROUP BY s.start",
            [OFid])
        myresult = mycursor.fetchall()
        bookingdetail = []
        for myresults in myresult:
            number = 0
            schedulex = schedule.objects.filter(start=myresults[0], OFid=OFid)
            for schedulex in schedulex:
                number = schedulex.number + number
            bookinglist = []
            sum = (myresults[2] / number) * 100
            if sum > 80:
                color = 'red'
            elif sum > 50:
                color = 'orange'
            elif sum >= 0:
                color = 'green'
            bookinglist.append(myresults[0])
            bookinglist.append(number)
            bookinglist.append(myresults[2])
            bookinglist.append(color)
            bookingdetail.append(bookinglist)
        mydbhistory = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="doqs"
        )
        history = mydbhistory.cursor()
        history.execute(
            "SELECT a.event,b.start,b.timestart,b.timeend,d.Dname,e.Pname,a.status FROM doqs_bookingperson AS a INNER JOIN doqs_schedule AS b ON a.schedule_id = b.id INNER JOIN doqs_officer AS c ON b.OFid = c.OFid INNER JOIN doqs_department AS d ON d.Did = c.Did INNER JOIN doqs_person AS e ON e.Pid = c.Pid WHERE a.Pid = %s",
            [request.session['user_id']])
        historys = history.fetchall()
        mydbhistoryes = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="doqs"
        )
        historyes = mydbhistoryes.cursor()
        historyes.execute(
            "SELECT a.event,a.verify,a.status,b.start,b.timestart,b.timeend,d.Pname,f.Dname,g.Hname,a.id,a.reed FROM doqs_bookingperson AS a INNER JOIN doqs_schedule AS b ON a.schedule_id = b.id INNER JOIN doqs_officer AS c ON b.OFid = c.OFid INNER JOIN doqs_person AS d ON c.Pid = d.Pid INNER JOIN doqs_department AS f ON c.Did = f.Did INNER JOIN doqs_hospital AS g ON f.Hid = g.Hid  WHERE a.Pid = %s  ORDER BY b.start DESC",
            [request.session['user_id']])
        historyses = historyes.fetchall()
        dateshowlist = []
        for historyseses in historyses:
            dateshow = historyseses[1]
            dateshowlist.append(dateshow)
        dbqueue = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="doqs"
        )
        queue = dbqueue.cursor()
        queue.execute(
            "SELECT a.event,a.verify,a.status,b.start,b.timestart,b.timeend,d.Pname,f.Dname,g.Hname,a.id,a.reed,b.number,a.callqueue,a.Pid FROM doqs_bookingperson AS a INNER JOIN doqs_schedule AS b ON a.schedule_id = b.id INNER JOIN doqs_officer AS c ON b.OFid = c.OFid INNER JOIN doqs_person AS d ON c.Pid = d.Pid INNER JOIN doqs_department AS f ON c.Did = f.Did INNER JOIN doqs_hospital AS g ON f.Hid = g.Hid WHERE b.start = %s ORDER BY a.id ASC",
            [today])
        queues = queue.fetchall()
        queueslist = []
        countes = 0
        sumq = 0
        for queuesest in queues:
            listqu = []
            countes = countes + 1
            sumq = sumq + 1
            if queuesest[13] == request.session['user_id']:
                if queuesest[12] == None:
                    sumq = sumq - 1
                    listqu.append(countes)
                    listqu.append(str(queuesest[0]))
                    listqu.append(str(queuesest[1]))
                    listqu.append(int(queuesest[2]))
                    listqu.append(str(queuesest[3]))
                    listqu.append(str(queuesest[4]))
                    listqu.append(str(queuesest[5]))
                    listqu.append(str(queuesest[6]))
                    listqu.append(str(queuesest[7]))
                    listqu.append(str(queuesest[8]))
                    listqu.append(str(queuesest[9]))
                    listqu.append(str(queuesest[10]))
                    listqu.append(str(queuesest[11]))
                    listqu.append(str(queuesest[12]))
                    listqu.append(str(queuesest[13]))
                    listqu.append(int(sumq))
                    queueslist.append(listqu)
                    break
                else:
                    sumq = 0
                    listqu.append(countes)
                    listqu.append(str(queuesest[0]))
                    listqu.append(str(queuesest[1]))
                    listqu.append(int(queuesest[2]))
                    listqu.append(str(queuesest[3]))
                    listqu.append(str(queuesest[4]))
                    listqu.append(str(queuesest[5]))
                    listqu.append(str(queuesest[6]))
                    listqu.append(str(queuesest[7]))
                    listqu.append(str(queuesest[8]))
                    listqu.append(str(queuesest[9]))
                    listqu.append(str(queuesest[10]))
                    listqu.append(str(queuesest[11]))
                    listqu.append(str(queuesest[12]))
                    listqu.append(str(queuesest[13]))
                    listqu.append(int(sumq))
                    queueslist.append(listqu)
                    break
        y = 0
        checkactive = ''
        checkactivequeue = ''
        for queueslist in queueslist:
            if queueslist[2] == 'None':
                print("xxx")
            else:
                print("xxx")
                y = 1
                checkactivequeue = int(queueslist[10])
        if historyses:
            x = 0
        else:
            x = 1
        for historyseses in historyses:
            checkactive = historyseses[9]
            break
        return render(request, 'calendar.html',
                      {'bookingdetail': bookingdetail, 're_dep': re_dep, 'datads': datads, 'dataofs': dataofs,
                       'datapers': datapers, 're_sta': re_stas, 're_hos': re_hoss,
                       'datahospital': datahospital,
                       'historys': historys,
                       'dateshowlist': dateshowlist,
                       'historyses': historyses,
                       'queueslist': queueslist,
                       'checkactivequeue': checkactivequeue,
                       'y': y,
                       'x': x,
                       'checkactive': checkactive,
                       'today': today,
                       'sum': sum,
                       'dataHN': dataHN})
    else:
        return redirect('login')


def filterbooking(request):
    if request.session._session:
        test_list_ids = request.POST['test_list_ids']
        test_list_ids = json.loads(test_list_ids)
        OFid = request.POST['OFid']
        dataOFF = Officer.objects.filter(OFid=OFid).first()
        Dids = str(dataOFF.Did)
        OFids = dataOFF.OFid
        count = 0
        sum = 0
        checktest = 'show'
        scheduleshow = schedule.objects.filter(start=test_list_ids, OFid=OFid, status=0)
        dataOFFchk = Officer.objects.filter(Did=Dids)
        for dataOFFchk in dataOFFchk:
            SC = schedule.objects.filter(OFid=dataOFFchk.OFid, start=test_list_ids)
            for SC in SC:
                check = bookingperson.objects.filter(schedule_id=SC.id, Pid=request.session['user_id'])
                if check:
                    for checks in check:
                        if checks.schedule_id == SC.id:
                            checktest = 'disable'
        x = ''
        event = ''
        date = ''
        color = ''
        bookingshow = []
        for scheduleshowes in scheduleshow:
            check = bookingperson.objects.filter(schedule_id=scheduleshowes.id, Pid=request.session['user_id'])
            if check:
                for checks in check:
                    if checks.schedule_id == scheduleshowes.id:
                        date = 'check'
        for scheduleshow in scheduleshow:
            count = 0
            bookinglist = []
            check = bookingperson.objects.filter(schedule_id=scheduleshow.id, Pid=request.session['user_id'])
            if check:
                for checks in check:
                    event = str(checks.event)
            else:
                event = ''
            countbooking = bookingperson.objects.filter(schedule_id=scheduleshow.id)
            for countbookings in countbooking:
                count = count + 1
            sum = (count / scheduleshow.number) * 100
            if sum > 80:
                color = 'danger'
            elif sum > 50:
                color = 'warning'
            elif sum > 0:
                color = 'success'
            bookinglist.append(str(scheduleshow.id))
            bookinglist.append(str(scheduleshow.start))
            bookinglist.append(str(scheduleshow.timestart))
            bookinglist.append(str(scheduleshow.timeend))
            bookinglist.append(int(scheduleshow.number))
            bookinglist.append(date)
            bookinglist.append(event)
            bookinglist.append(int(count))
            bookinglist.append(int(sum))
            bookinglist.append(str(color))
            bookingshow.append(bookinglist)
        counttoday = schedule.objects.filter(start=test_list_ids, OFid=OFid)
        dataOFFDPM = Officer.objects.filter(Did=Dids)
        number = 0
        numbertoday = 0
        numberDPM = 0
        numberDPMtoday = 0
        text = ''
        for dataOFFDPMs in dataOFFDPM:
            countDPM = schedule.objects.filter(OFid=dataOFFDPMs.OFid, start=test_list_ids, status=0)
            for countDPMsa in countDPM:
                numberDPMtoday = countDPMsa.number + numberDPMtoday
        for counttodays in counttoday:
            if counttodays.OFid == counttodays.OFid:
                numbertoday = counttodays.number + numbertoday
        data = json.dumps({
            'bookingshow': bookingshow,
            'numbertoday': numbertoday,
            'numberDPMtoday': numberDPMtoday,
            'checktest': checktest,
        })
        return HttpResponse(data, content_type="application/json")
    else:
        return redirect('login')


def filterdashboard(request):
    test_list_ids = request.POST['dateList']
    dataOFF = Officer.objects.filter(Pid=request.session['user_id']).first()
    dataOFFALL = Officer.objects.filter(Did=dataOFF.Did)
    listbooking = []
    listinsertbook = []
    listtime = []
    number = 0
    count = 0
    for dataOFFALL in dataOFFALL:
        mydbdashboard = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="doqs"
        )
        dashboards = mydbdashboard.cursor()
        dashboards.execute(
            "SELECT SUM(number),start,timestart,timeend,OFid FROM `doqs_schedule` WHERE start = %s GROUP BY timestart",
            [test_list_ids])
        dashboardses = dashboards.fetchall()
        for dashboardses in dashboardses:
            if dashboardses[4] == dataOFFALL.OFid:
                listshow = []
                listshow.append(str(dashboardses[0]))
                listshow.append(str(dashboardses[1]))
                listshow.append(str(dashboardses[2]))
                listshow.append(str(dashboardses[3]))
                listtime.append(listshow)
    data = json.dumps({
        'test_list_ids': test_list_ids,
        'listtime': listtime,
    })
    return HttpResponse(data, content_type="application/json")


def calendar(request):
    if request.session._session:
        if request.session['Hid'] != '':
            request.session['datess'] = ''
            request.session['stfssss'] = ''
            request.session['dpmss'] = ''
            request.session['checkdelete'] = ''
            request.session['event'] = ''
            dataHNese = HN.objects.filter(HNpid=request.session['user_id'])
            schedulex = schedule.objects.all()
            if dataHNese:
                dataHos = Hospital.objects.filter(Hid=int(request.session['Hid'])).first()
                dataDPMse = Department.objects.filter(Hid=dataHos.Hid)
                now = datetime.now()
                today = date.today()
                dateshow = ''
                datahospital = Hospital.objects.all()
                dataHN = HN.objects.filter(HNpid=request.session['user_id'])
                mydbhistory = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="doqs"
                )
                history = mydbhistory.cursor()
                history.execute(
                    "SELECT a.event,b.start,b.timestart,b.timeend,d.Dname,e.Pname,a.status FROM doqs_bookingperson AS a INNER JOIN doqs_schedule AS b ON a.schedule_id = b.id INNER JOIN doqs_officer AS c ON b.OFid = c.OFid INNER JOIN doqs_department AS d ON d.Did = c.Did INNER JOIN doqs_person AS e ON e.Pid = c.Pid WHERE a.Pid = %s",
                    [request.session['user_id']])
                historys = history.fetchall()
                mydbhistoryes = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="doqs"
                )
                historyes = mydbhistoryes.cursor()
                historyes.execute(
                    "SELECT a.event,a.verify,a.status,b.start,b.timestart,b.timeend,d.Pname,f.Dname,g.Hname,a.id,a.reed FROM doqs_bookingperson AS a INNER JOIN doqs_schedule AS b ON a.schedule_id = b.id INNER JOIN doqs_officer AS c ON b.OFid = c.OFid INNER JOIN doqs_person AS d ON c.Pid = d.Pid INNER JOIN doqs_department AS f ON c.Did = f.Did INNER JOIN doqs_hospital AS g ON f.Hid = g.Hid  WHERE a.Pid = %s  ORDER BY b.start DESC",
                    [request.session['user_id']])
                historyses = historyes.fetchall()
                dateshowlist = []
                for historyseses in historyses:
                    dateshow = historyseses[1]
                    dateshowlist.append(dateshow)
                dbqueue = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="doqs"
                )
                queue = dbqueue.cursor()
                queue.execute(
                    "SELECT a.event,a.verify,a.status,b.start,b.timestart,b.timeend,d.Pname,f.Dname,g.Hname,a.id,a.reed,b.number,a.callqueue,a.Pid FROM doqs_bookingperson AS a INNER JOIN doqs_schedule AS b ON a.schedule_id = b.id INNER JOIN doqs_officer AS c ON b.OFid = c.OFid INNER JOIN doqs_person AS d ON c.Pid = d.Pid INNER JOIN doqs_department AS f ON c.Did = f.Did INNER JOIN doqs_hospital AS g ON f.Hid = g.Hid WHERE b.start = %s AND a.status = 1 ORDER BY a.id ASC",
                    [today])
                queues = queue.fetchall()
                queueslist = []
                countes = 0
                sumq = 0
                for queuesest in queues:
                    listqu = []
                    countes = countes + 1
                    sumq = sumq + 1
                    if queuesest[13] == request.session['user_id']:
                        if queuesest[12] == None:
                            sumq = sumq - 1
                            listqu.append(countes)
                            listqu.append(str(queuesest[0]))
                            listqu.append(str(queuesest[1]))
                            listqu.append(int(queuesest[2]))
                            listqu.append(str(queuesest[3]))
                            listqu.append(str(queuesest[4]))
                            listqu.append(str(queuesest[5]))
                            listqu.append(str(queuesest[6]))
                            listqu.append(str(queuesest[7]))
                            listqu.append(str(queuesest[8]))
                            listqu.append(str(queuesest[9]))
                            listqu.append(str(queuesest[10]))
                            listqu.append(str(queuesest[11]))
                            listqu.append(str(queuesest[12]))
                            listqu.append(str(queuesest[13]))
                            listqu.append(int(sumq))
                            queueslist.append(listqu)
                            break
                        else:
                            sumq = 0
                            listqu.append(countes)
                            listqu.append(str(queuesest[0]))
                            listqu.append(str(queuesest[1]))
                            listqu.append(int(queuesest[2]))
                            listqu.append(str(queuesest[3]))
                            listqu.append(str(queuesest[4]))
                            listqu.append(str(queuesest[5]))
                            listqu.append(str(queuesest[6]))
                            listqu.append(str(queuesest[7]))
                            listqu.append(str(queuesest[8]))
                            listqu.append(str(queuesest[9]))
                            listqu.append(str(queuesest[10]))
                            listqu.append(str(queuesest[11]))
                            listqu.append(str(queuesest[12]))
                            listqu.append(str(queuesest[13]))
                            listqu.append(int(sumq))
                            queueslist.append(listqu)
                            break
                y = 0
                checkactive = ''
                checkactivequeue = ''
                for queueslist in queueslist:
                    if queueslist[2] == 'None':
                        print("xxx")
                    else:
                        print("xxx")
                        y = 1
                        checkactivequeue = int(queueslist[10])
                if historyses:
                    x = 0
                else:
                    x = 1
                for historyseses in historyses:
                    checkactive = historyseses[9]
                    break
                return render(request, 'calendar.html',
                              {'datahospital': datahospital, 'historyses': historyses, 'historys': historys,
                               'dataHN': dataHN,
                               'now': now,
                               'checkactive': checkactive,
                               'x': x,
                               'y': y,
                               'schedulex': schedulex,
                               'dataDPMse': dataDPMse,
                               'checkactivequeue': checkactivequeue,
                               'dateshow': dateshow, 'queueslist': queueslist, 'today': today,
                               'dateshowlist': dateshowlist, })
            else:
                return redirect('person')
        else:
            return redirect('person')
    else:
        return redirect('login')


def bookingevent(request):
    if request.session._session:
        sids = schedule.objects.all()
        re_sta = request.POST['re_sta']
        re_hos = request.POST['re_hos']
        re_dep = request.POST['re_dep']
        checkdelete = request.POST['checkdelete']
        if checkdelete == '2':
            for sid in sids:
                id = sid.id
                ids = str(id)
                check = str('event' + ids)
                idss = str('id' + ids)

                if check in request.POST:
                    che = request.POST[check]
                    id = request.POST[idss]

                    if che != "":
                        insertbk = bookingperson(schedule_id=id, event=che, Pid=request.session['user_id'], status=0)
                        insertbk.save()
        if checkdelete == '1':
            for sid in sids:
                id = sid.id
                ids = str(id)
                check = str('event' + ids)
                idss = str('id' + ids)
                if check in request.POST:
                    che = request.POST[check]
                    id = request.POST[idss]
                    if id != "":
                        checkbooking = bookingperson.objects.filter(schedule_id=id, event=che,
                                                                    Pid=request.session['user_id'])
                        for checkbookings in checkbooking:
                            idbooking = checkbookings.id
                            bookingdelete = bookingperson.objects.get(pk=idbooking)
                            bookingdelete.delete()

        return redirect(reverse(getdatebooking2, kwargs={'re_dep': re_dep, 're_sta': re_sta, 're_hos': re_hos}))
    else:
        return redirect('login')


def filterstaffmoniter(request):
    if request.session._session:
        test_list_ids = request.POST['test_list_ids']
        test_list_ids = json.loads(test_list_ids)
        OFid = request.POST['OFid']
        timesst = request.POST['timesst']
        timesse = request.POST['timesse']
        timestart = str(timesst)
        timeend = str(timesse)
        bookingper = []
        numberDPMtoday = 0
        numbertoday = 0
        timese = ''
        dates = ''
        if OFid == '':
            Offxs = Officer.objects.filter(Pid=request.session['user_id']).first()
            dataOFFall = Officer.objects.filter(Did=Offxs.Did)
            for dataOFFall in dataOFFall:
                scheduilx = schedule.objects.filter(OFid=dataOFFall.OFid, start=test_list_ids, timestart=timestart,
                                                    timeend=timeend)
                dataHN = HN.objects.all()
                datastaff = Staff.objects.filter(Pid=request.session['user_id'])
                for datastaffs in datastaff:
                    Hid = datastaffs.Hid
                for scheduilx in scheduilx:
                    personbook = bookingperson.objects.filter(schedule_id=scheduilx.id)
                    datees = schedule.objects.filter(id=scheduilx.id).first()
                    persons = Person.objects.all()
                    dataOFF = Officer.objects.filter(OFid=dataOFFall.OFid)
                    for dataOFFs in dataOFF:
                        for personses in persons:
                            if dataOFFs.Pid == personses.Pid:
                                namestaff = personses.Pname
                    dataOFF = Officer.objects.filter(OFid=dataOFFall.OFid).first()
                    Dids = str(dataOFF.Did)
                    counttoday = schedule.objects.filter(start=datees.start, OFid=dataOFFall.OFid)
                    dataOFFDPM = Officer.objects.filter(Did=Dids)
                    number = 0
                    numbertoday = 0
                    numberDPM = 0
                    numberDPMtoday = 0
                    text = ''
                    for dataOFFDPMs in dataOFFDPM:
                        countDPM = schedule.objects.filter(OFid=dataOFFDPMs.OFid, start=datees.start, status=0)
                        for countDPMsa in countDPM:
                            numberDPMtoday = countDPMsa.number + numberDPMtoday
                    for counttodays in counttoday:
                        if counttodays.OFid == counttodays.OFid:
                            numbertoday = counttodays.number + numbertoday
                            timese = str(counttodays.timestart) + '-' + str(counttodays.timeend)
                            dates = str(counttodays.start)
                    for personbooks in personbook:
                        for personses in persons:
                            if personbooks.Pid == personses.Pid:
                                name = personses.Pname
                        for dataHNs in dataHN:
                            if personbooks.Pid == dataHNs.HNpid and dataHNs.HNhid == Hid:
                                HNs = dataHNs.HN
                        if personbooks.OFid != dataOFFall.OFid:
                            namestaff = '-'
                        bookinglist = []
                        bookinglist.append(int(personbooks.id))
                        bookinglist.append(str(personbooks.event))
                        bookinglist.append(str(name))
                        bookinglist.append(str(HNs))
                        bookinglist.append(str(namestaff))
                        bookinglist.append(str(personbooks.status))
                        bookingper.append(bookinglist)
        else:
            dataOFFall = Officer.objects.filter(OFid=OFid)
            for dataOFFall in dataOFFall:
                scheduilx = schedule.objects.filter(OFid=dataOFFall.OFid, start=test_list_ids, timestart=timestart,
                                                    timeend=timeend)
                dataHN = HN.objects.all()
                datastaff = Staff.objects.filter(Pid=request.session['user_id'])
                for datastaffs in datastaff:
                    Hid = datastaffs.Hid
                for scheduilx in scheduilx:
                    personbook = bookingperson.objects.filter(schedule_id=scheduilx.id, OFid=dataOFFall.OFid)
                    datees = schedule.objects.filter(id=scheduilx.id).first()
                    persons = Person.objects.all()
                    dataOFF = Officer.objects.filter(OFid=dataOFFall.OFid)
                    for dataOFFs in dataOFF:
                        for personses in persons:
                            if dataOFFs.Pid == personses.Pid:
                                namestaff = personses.Pname
                    dataOFF = Officer.objects.filter(OFid=dataOFFall.OFid).first()
                    Dids = str(dataOFF.Did)
                    counttoday = schedule.objects.filter(start=datees.start, OFid=dataOFFall.OFid)
                    dataOFFDPM = Officer.objects.filter(Did=Dids)
                    number = 0
                    numbertoday = 0
                    numberDPM = 0
                    numberDPMtoday = 0
                    text = ''
                    for dataOFFDPMs in dataOFFDPM:
                        countDPM = schedule.objects.filter(OFid=dataOFFDPMs.OFid, start=datees.start, status=0)
                        for countDPMsa in countDPM:
                            numberDPMtoday = countDPMsa.number + numberDPMtoday
                    for counttodays in counttoday:
                        if counttodays.OFid == counttodays.OFid:
                            numbertoday = counttodays.number + numbertoday
                            timese = str(counttodays.timestart) + '-' + str(counttodays.timeend)
                            dates = str(counttodays.start)
                    for personbooks in personbook:
                        for personses in persons:
                            if personbooks.Pid == personses.Pid:
                                name = personses.Pname
                        for dataHNs in dataHN:
                            if personbooks.Pid == dataHNs.HNpid and dataHNs.HNhid == Hid:
                                HNs = dataHNs.HN
                        if personbooks.OFid != dataOFFall.OFid:
                            namestaff = '-'
                        bookinglist = []
                        bookinglist.append(int(personbooks.id))
                        bookinglist.append(str(personbooks.event))
                        bookinglist.append(str(name))
                        bookinglist.append(str(HNs))
                        bookinglist.append(str(namestaff))
                        bookinglist.append(str(personbooks.status))
                        bookingper.append(bookinglist)
        data = json.dumps({
            'bookingper': bookingper,
            'numbertoday': numbertoday,
            'numberDPMtoday': numberDPMtoday,
            'timese': timese,
            'dates': dates,
        })
        return HttpResponse(data, content_type="application/json")
    else:
        return redirect('login')


def verifybooking(request):
    if request.session._session:
        now = datetime.now()
        selected_tests = request.POST['checklist']
        selected_tests = json.loads(selected_tests)
        for test in selected_tests:
            if test != '':
                y = test.strip("")
                bookingperson.objects.filter(id=y).update(status=1, verify=now)
                queuechk = bookingperson.objects.filter(id=y, status=1)
                for queuechk in queuechk:
                    if queuechk.status == 1:
                        schedulexs = schedule.objects.filter(id=queuechk.schedule_id)
                        for schedulexs in schedulexs:
                            counts = 0
                            bookingpersonx = bookingperson.objects.filter(schedule_id=schedulexs.id, status=1)
                            for bookingpersonx in bookingpersonx:
                                counts = counts + 1
                                print(counts)
                            bookingperson.objects.filter(id=y).update(queuenum=counts)
        test_list_ids = request.POST['test_list_ids']
        test_list_ids = json.loads(test_list_ids)
        OFid = request.POST['OFid']
        timesse = request.POST['timesse']
        timesst = request.POST['timesst']
        print(OFid)
        bookingper = []
        numberDPMtoday = 0
        numbertoday = 0
        timese = ''
        dates = ''
        if OFid == '':
            Offxs = Officer.objects.filter(Pid=request.session['user_id']).first()
            dataOFFall = Officer.objects.filter(Did=Offxs.Did)
            for dataOFFall in dataOFFall:
                scheduilx = schedule.objects.filter(OFid=dataOFFall.OFid, start=test_list_ids, timestart=timesst,
                                                    timeend=timesse)
                dataHN = HN.objects.all()
                datastaff = Staff.objects.filter(Pid=request.session['user_id'])
                for datastaffs in datastaff:
                    Hid = datastaffs.Hid
                for scheduilx in scheduilx:
                    personbook = bookingperson.objects.filter(schedule_id=scheduilx.id)
                    datees = schedule.objects.filter(id=scheduilx.id).first()
                    persons = Person.objects.all()
                    dataOFF = Officer.objects.filter(OFid=dataOFFall.OFid)
                    for dataOFFs in dataOFF:
                        for personses in persons:
                            if dataOFFs.Pid == personses.Pid:
                                namestaff = personses.Pname
                    dataOFF = Officer.objects.filter(OFid=dataOFFall.OFid).first()
                    Dids = str(dataOFF.Did)
                    counttoday = schedule.objects.filter(start=datees.start, OFid=dataOFFall.OFid)
                    dataOFFDPM = Officer.objects.filter(Did=Dids)
                    number = 0
                    numbertoday = 0
                    numberDPM = 0
                    numberDPMtoday = 0
                    text = ''
                    for dataOFFDPMs in dataOFFDPM:
                        countDPM = schedule.objects.filter(OFid=dataOFFDPMs.OFid, start=datees.start, status=0)
                        for countDPMsa in countDPM:
                            numberDPMtoday = countDPMsa.number + numberDPMtoday
                    for counttodays in counttoday:
                        if counttodays.OFid == counttodays.OFid:
                            numbertoday = counttodays.number + numbertoday
                            timese = str(counttodays.timestart) + '-' + str(counttodays.timeend)
                            dates = str(counttodays.start)
                    for personbooks in personbook:
                        for personses in persons:
                            if personbooks.Pid == personses.Pid:
                                name = personses.Pname
                        for dataHNs in dataHN:
                            if personbooks.Pid == dataHNs.HNpid and dataHNs.HNhid == Hid:
                                HNs = dataHNs.HN
                        if personbooks.OFid != dataOFFall.OFid:
                            namestaff = '-'
                        bookinglist = []
                        bookinglist.append(int(personbooks.id))
                        bookinglist.append(str(personbooks.event))
                        bookinglist.append(str(name))
                        bookinglist.append(str(HNs))
                        bookinglist.append(str(namestaff))
                        bookinglist.append(str(personbooks.status))
                        bookingper.append(bookinglist)
        else:
            dataOFFall = Officer.objects.filter(OFid=OFid)
            for dataOFFall in dataOFFall:
                scheduilx = schedule.objects.filter(OFid=dataOFFall.OFid, start=test_list_ids)
                dataHN = HN.objects.all()
                datastaff = Staff.objects.filter(Pid=request.session['user_id'])
                for datastaffs in datastaff:
                    Hid = datastaffs.Hid
                for scheduilx in scheduilx:
                    personbook = bookingperson.objects.filter(schedule_id=scheduilx.id, OFid=dataOFFall.OFid)
                    datees = schedule.objects.filter(id=scheduilx.id).first()
                    persons = Person.objects.all()
                    dataOFF = Officer.objects.filter(OFid=dataOFFall.OFid)
                    for dataOFFs in dataOFF:
                        for personses in persons:
                            if dataOFFs.Pid == personses.Pid:
                                namestaff = personses.Pname
                    dataOFF = Officer.objects.filter(OFid=dataOFFall.OFid).first()
                    Dids = str(dataOFF.Did)
                    counttoday = schedule.objects.filter(start=datees.start, OFid=dataOFFall.OFid)
                    dataOFFDPM = Officer.objects.filter(Did=Dids)
                    number = 0
                    numbertoday = 0
                    numberDPM = 0
                    numberDPMtoday = 0
                    text = ''
                    for dataOFFDPMs in dataOFFDPM:
                        countDPM = schedule.objects.filter(OFid=dataOFFDPMs.OFid, start=datees.start, status=0)
                        for countDPMsa in countDPM:
                            numberDPMtoday = countDPMsa.number + numberDPMtoday
                    for counttodays in counttoday:
                        if counttodays.OFid == counttodays.OFid:
                            numbertoday = counttodays.number + numbertoday
                            timese = str(counttodays.timestart) + '-' + str(counttodays.timeend)
                            dates = str(counttodays.start)
                    for personbooks in personbook:
                        for personses in persons:
                            if personbooks.Pid == personses.Pid:
                                name = personses.Pname
                        for dataHNs in dataHN:
                            if personbooks.Pid == dataHNs.HNpid and dataHNs.HNhid == Hid:
                                HNs = dataHNs.HN
                        if personbooks.OFid != dataOFFall.OFid:
                            namestaff = '-'
                        bookinglist = []
                        bookinglist.append(int(personbooks.id))
                        bookinglist.append(str(personbooks.event))
                        bookinglist.append(str(name))
                        bookinglist.append(str(HNs))
                        bookinglist.append(str(namestaff))
                        bookinglist.append(str(personbooks.status))
                        bookingper.append(bookinglist)
        data = json.dumps({
            'bookingper': bookingper,
            'numbertoday': numbertoday,
            'numberDPMtoday': numberDPMtoday,
            'timese': timese,
            'dates': dates,
        })
        return HttpResponse(data, content_type="application/json")
    else:
        return redirect('login')


def verifydontbooking(request):
    if request.session._session:
        now = datetime.now()
        selected_tests = request.POST['checklist']
        selected_tests = json.loads(selected_tests)
        for test in selected_tests:
            if test != '':
                bookingperson.objects.filter(id__in=selected_tests).update(status='2', verify=now)
        test_list_ids = request.POST['test_list_ids']
        test_list_ids = json.loads(test_list_ids)
        OFid = request.POST['OFid']
        timesse = request.POST['timesse']
        timesst = request.POST['timesst']
        print(OFid)
        bookingper = []
        numberDPMtoday = 0
        numbertoday = 0
        timese = ''
        dates = ''
        if OFid == '':
            Offxs = Officer.objects.filter(Pid=request.session['user_id']).first()
            dataOFFall = Officer.objects.filter(Did=Offxs.Did)
            for dataOFFall in dataOFFall:
                scheduilx = schedule.objects.filter(OFid=dataOFFall.OFid, start=test_list_ids, timestart=timesst,
                                                    timeend=timesse)
                dataHN = HN.objects.all()
                datastaff = Staff.objects.filter(Pid=request.session['user_id'])
                for datastaffs in datastaff:
                    Hid = datastaffs.Hid
                for scheduilx in scheduilx:
                    personbook = bookingperson.objects.filter(schedule_id=scheduilx.id)
                    datees = schedule.objects.filter(id=scheduilx.id).first()
                    persons = Person.objects.all()
                    dataOFF = Officer.objects.filter(OFid=dataOFFall.OFid)
                    for dataOFFs in dataOFF:
                        for personses in persons:
                            if dataOFFs.Pid == personses.Pid:
                                namestaff = personses.Pname
                    dataOFF = Officer.objects.filter(OFid=dataOFFall.OFid).first()
                    Dids = str(dataOFF.Did)
                    counttoday = schedule.objects.filter(start=datees.start, OFid=dataOFFall.OFid)
                    dataOFFDPM = Officer.objects.filter(Did=Dids)
                    number = 0
                    numbertoday = 0
                    numberDPM = 0
                    numberDPMtoday = 0
                    text = ''
                    for dataOFFDPMs in dataOFFDPM:
                        countDPM = schedule.objects.filter(OFid=dataOFFDPMs.OFid, start=datees.start, status=0)
                        for countDPMsa in countDPM:
                            numberDPMtoday = countDPMsa.number + numberDPMtoday
                    for counttodays in counttoday:
                        if counttodays.OFid == counttodays.OFid:
                            numbertoday = counttodays.number + numbertoday
                            timese = str(counttodays.timestart) + '-' + str(counttodays.timeend)
                            dates = str(counttodays.start)
                    for personbooks in personbook:
                        for personses in persons:
                            if personbooks.Pid == personses.Pid:
                                name = personses.Pname
                        for dataHNs in dataHN:
                            if personbooks.Pid == dataHNs.HNpid and dataHNs.HNhid == Hid:
                                HNs = dataHNs.HN
                        if personbooks.OFid != dataOFFall.OFid:
                            namestaff = '-'
                        bookinglist = []
                        bookinglist.append(int(personbooks.id))
                        bookinglist.append(str(personbooks.event))
                        bookinglist.append(str(name))
                        bookinglist.append(str(HNs))
                        bookinglist.append(str(namestaff))
                        bookinglist.append(str(personbooks.status))
                        bookingper.append(bookinglist)
        else:
            dataOFFall = Officer.objects.filter(OFid=OFid)
            for dataOFFall in dataOFFall:
                scheduilx = schedule.objects.filter(OFid=dataOFFall.OFid, start=test_list_ids)
                dataHN = HN.objects.all()
                datastaff = Staff.objects.filter(Pid=request.session['user_id'])
                for datastaffs in datastaff:
                    Hid = datastaffs.Hid
                for scheduilx in scheduilx:
                    personbook = bookingperson.objects.filter(schedule_id=scheduilx.id, OFid=dataOFFall.OFid)
                    datees = schedule.objects.filter(id=scheduilx.id).first()
                    persons = Person.objects.all()
                    dataOFF = Officer.objects.filter(OFid=dataOFFall.OFid)
                    for dataOFFs in dataOFF:
                        for personses in persons:
                            if dataOFFs.Pid == personses.Pid:
                                namestaff = personses.Pname
                    dataOFF = Officer.objects.filter(OFid=dataOFFall.OFid).first()
                    Dids = str(dataOFF.Did)
                    counttoday = schedule.objects.filter(start=datees.start, OFid=dataOFFall.OFid)
                    dataOFFDPM = Officer.objects.filter(Did=Dids)
                    number = 0
                    numbertoday = 0
                    numberDPM = 0
                    numberDPMtoday = 0
                    text = ''
                    for dataOFFDPMs in dataOFFDPM:
                        countDPM = schedule.objects.filter(OFid=dataOFFDPMs.OFid, start=datees.start, status=0)
                        for countDPMsa in countDPM:
                            numberDPMtoday = countDPMsa.number + numberDPMtoday
                    for counttodays in counttoday:
                        if counttodays.OFid == counttodays.OFid:
                            numbertoday = counttodays.number + numbertoday
                            timese = str(counttodays.timestart) + '-' + str(counttodays.timeend)
                            dates = str(counttodays.start)
                    for personbooks in personbook:
                        for personses in persons:
                            if personbooks.Pid == personses.Pid:
                                name = personses.Pname
                        for dataHNs in dataHN:
                            if personbooks.Pid == dataHNs.HNpid and dataHNs.HNhid == Hid:
                                HNs = dataHNs.HN
                        if personbooks.OFid != dataOFFall.OFid:
                            namestaff = '-'
                        bookinglist = []
                        bookinglist.append(int(personbooks.id))
                        bookinglist.append(str(personbooks.event))
                        bookinglist.append(str(name))
                        bookinglist.append(str(HNs))
                        bookinglist.append(str(namestaff))
                        bookinglist.append(str(personbooks.status))
                        bookingper.append(bookinglist)
        data = json.dumps({
            'bookingper': bookingper,
            'numbertoday': numbertoday,
            'numberDPMtoday': numberDPMtoday,
            'timese': timese,
            'dates': dates,
        })
        return HttpResponse(data, content_type="application/json")
    else:
        return redirect('login')


def sentmailnoti(request):
    if request.session._session:
        now = datetime.now()
        selected_tests = request.POST['checklist']
        selected_tests = json.loads(selected_tests)
        # for test in selected_tests:
        #     if test != '':
        #         x = test.strip("")
        #         emails = bookingperson.objects.filter(id__in=selected_tests).first()
        #         Persx = Person.objects.filter(Pid=emails.Pid)
        #         dbqueue = mysql.connector.connect(
        #             host="db",
        #             user="ableplant",
        #             password="abp1234",
        #             database="webapp"
        #         )
        #         queue = dbqueue.cursor()
        #         queue.execute(
        #             "SELECT a.event,a.verify,a.status,b.start,b.timestart,b.timeend,d.Pname,f.Dname,g.Hname,a.id,a.reed,b.number,a.callqueue,a.Pid FROM doqs_bookingperson AS a INNER JOIN doqs_schedule AS b ON a.schedule_id = b.id INNER JOIN doqs_officer AS c ON b.OFid = c.OFid INNER JOIN doqs_person AS d ON c.Pid = d.Pid INNER JOIN doqs_department AS f ON c.Did = f.Did INNER JOIN doqs_hospital AS g ON f.Hid = g.Hid WHERE a.id = %s ORDER BY a.id ASC",
        #             [x])
        #         queues = queue.fetchall()
        #         for queues in queues:
        #             dpm = queues[7]
        #             event = queues[0]
        #             hname = queues[8]
        #             staffname = queues[6]
        #         for Persx in Persx:
        #             emailx = Persx.Pemail
        #         sender_email = "DooQService@gmail.com"
        #         receiver_email = emailx
        #         password = "dooqservice"
        #
        #         message = MIMEMultipart("alternative")
        #         message["Subject"] = "doo-q"
        #         message["From"] = sender_email
        #         message["To"] = receiver_email
        #         print(datetime.now())
        #         # Create the plain-text and HTML version of your message
        #         text = """\
        #                     Hi,
        #                     How are you?
        #                     Real Python has many great tutorials:
        #                     www.realpython.com"""
        #         html = """\
        #                     <html>
        #                       <body>
        #                         <p>กิจกรรม : """ + event + """<br>
        #                          <p>โรงพยาบาล : """ + hname + """<br>
        #                           <p>แผนก : """ + dpm + """<br>
        #                            <p>หมอ/เจ้าหน้าที่ : """ + staffname + """<br>
        #                            ปฏิเสธการจองคิว<br>
        #                            <br>
        #                         </p>
        #                       </body>
        #                     </html>
        #                     """
        #
        #         # Turn these into plain/html MIMEText objects
        #         part1 = MIMEText(text, "plain")
        #         part2 = MIMEText(html, "html")
        #
        #         # Add HTML/plain-text parts to MIMEMultipart message
        #         # The email client will try to render the last part first
        #         message.attach(part1)
        #         message.attach(part2)
        #
        #         # Create secure connection with server and send email
        #         context = ssl.create_default_context()
        #         with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        #             server.login(sender_email, password)
        #             server.sendmail(
        #                 sender_email, receiver_email, message.as_string()
        #             )
        #             print(datetime.now())
        return HttpResponse("xxx")
    else:
        return redirect('login')


def sentmailverti(request):
    if request.session._session:
        now = datetime.now()
        selected_tests = request.POST['checklist']
        selected_tests = json.loads(selected_tests)
        # for test in selected_tests:
        #     if test != '':
        #         x = test.strip("")
        #         emails = bookingperson.objects.filter(id__in=selected_tests).first()
        #         Persx = Person.objects.filter(Pid=emails.Pid)
        #         dbqueue = mysql.connector.connect(
        #             host="db",
        #             user="ableplant",
        #             password="abp1234",
        #             database="webapp"
        #         )
        #         queue = dbqueue.cursor()
        #         queue.execute(
        #             "SELECT a.event,a.verify,a.status,b.start,b.timestart,b.timeend,d.Pname,f.Dname,g.Hname,a.id,a.reed,b.number,a.callqueue,a.Pid FROM doqs_bookingperson AS a INNER JOIN doqs_schedule AS b ON a.schedule_id = b.id INNER JOIN doqs_officer AS c ON b.OFid = c.OFid INNER JOIN doqs_person AS d ON c.Pid = d.Pid INNER JOIN doqs_department AS f ON c.Did = f.Did INNER JOIN doqs_hospital AS g ON f.Hid = g.Hid WHERE a.id = %s ORDER BY a.id ASC",
        #             [x])
        #         queues = queue.fetchall()
        #         for queues in queues:
        #             dpm = queues[7]
        #             event = queues[0]
        #             hname = queues[8]
        #             staffname = queues[6]
        #         for Persx in Persx:
        #             emailx = Persx.Pemail
        #         sender_email = "DooQService@gmail.com"
        #         receiver_email = emailx
        #         password = "dooqservice"
        #
        #         message = MIMEMultipart("alternative")
        #         message["Subject"] = "doo-q"
        #         message["From"] = sender_email
        #         message["To"] = receiver_email
        #
        #         # Create the plain-text and HTML version of your message
        #         text = """\
        #                     Hi,
        #                     How are you?
        #                     Real Python has many great tutorials:
        #                     www.realpython.com"""
        #         html = """\
        #                     <html>
        #                       <body>
        #                         <p>กิจกรรม : """ + event + """<br>
        #                          <p>โรงพยาบาล : """ + hname + """<br>
        #                           <p>แผนก : """ + dpm + """<br>
        #                            <p>หมอ/เจ้าหน้าที่ : """ + staffname + """<br>
        #                            รับนัด<br>
        #                            <br>
        #                         </p>
        #                       </body>
        #                     </html>
        #                     """
        #
        #         # Turn these into plain/html MIMEText objects
        #         part1 = MIMEText(text, "plain")
        #         part2 = MIMEText(html, "html")
        #
        #         # Add HTML/plain-text parts to MIMEMultipart message
        #         # The email client will try to render the last part first
        #         message.attach(part1)
        #         message.attach(part2)
        #
        #         # Create secure connection with server and send email
        #         context = ssl.create_default_context()
        #         with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        #             server.login(sender_email, password)
        #             server.sendmail(
        #                 sender_email, receiver_email, message.as_string()
        #             )
        return HttpResponse("xxx")
    else:
        return redirect('login')


def stmcheck(request):
    if request.session._session:
        modalbk = bookingperson.objects.all()
        OFid = request.POST['re_sta']
        if OFid == '':
            request.session['OFid'] = ''
        if OFid != '':
            request.session['OFid'] = OFid
        return redirect('vtfbooking2')


def callqueue(request):
    if request.session._session:
        checkstaff = Staff.objects.filter(Pid=request.session['user_id']).first()
        if checkstaff.status == 1:
            dataOFFax = Officer.objects.filter(Pid=request.session['user_id'])
            if dataOFFax:
                dataST = Staff.objects.get(Pid=request.session['user_id'])
                for dataOFFs in dataOFFax:
                    OFid = dataOFFs.OFid
                    datatime = hospitaltime.objects.filter(Did=dataOFFs.Did).order_by('timestart')
                dataDPM = Department.objects.filter(Hid=dataST.Hid)
                datahospital = Hospital.objects.all()
                dataPerson = Person.objects.all()
                dataST = Staff.objects.get(Pid=request.session['user_id'])
                dataOFF = Officer.objects.filter(Pid=request.session['user_id']).first()
                Dids = dataOFF.Did
                dataOFFall = Officer.objects.filter(Did=Dids)
                dataOFF = Officer.objects.filter(Pid=request.session['user_id']).first()
                schedules = schedule.objects.filter(OFid=dataOFF.OFid)
                error = ''
                count = 0
                color = ''
                bookingshow = []
                for scheduleses in schedules:
                    count = 0
                    personbooking = bookingperson.objects.filter(schedule_id=scheduleses.id, status=1)
                    for personbookings in personbooking:
                        count = count + 1

                    bookinglist = []
                    bookinglist.append(str(scheduleses.id))
                    bookinglist.append(str(scheduleses.start))
                    bookinglist.append(str(scheduleses.timestart))
                    bookinglist.append(str(scheduleses.timeend))
                    bookinglist.append(str(scheduleses.number))
                    bookinglist.append(count)
                    bookinglist.append(color)
                    bookingshow.append(bookinglist)
                return render(request, 'callqueue.html',
                              {'dataST': dataST, 'datahospital': datahospital,
                               'Dids': Dids,
                               'OFid': OFid,
                               'dataOFFax': dataOFFax,
                               'bookingshow': bookingshow,
                               'dataDPM': dataDPM,
                               'error': error,
                               'dataPerson': dataPerson,
                               'schedules': schedules,
                               'dataOFFall': dataOFFall})
            else:
                return redirect('staffinfo')
        else:
            return redirect('staffcheck')
    else:
        return redirect('login')


def filtercallqueue(request):
    if request.session._session:
        test_list_ids = request.POST['test_list_ids']
        test_list_ids = json.loads(test_list_ids)
        OFid = request.POST['OFid']
        timesst = request.POST['timesst']
        timesse = request.POST['timesse']
        timestart = str(timesst)
        timeend = str(timesse)
        if OFid == '':
            bookingper = []
            cout = 0
            dataOFFX = Officer.objects.filter(Pid=request.session['user_id']).first()
            Hosx = hospitaltime.objects.filter(Did=dataOFFX.Did)
            dataOFFALL = Officer.objects.filter(Did=dataOFFX.Did)
            for dataOFFALL in dataOFFALL:
                namestaff = ''
                schedulero = schedule.objects.filter(OFid=dataOFFALL.OFid, start=test_list_ids, timestart=timestart,
                                                     timeend=timeend)
                for schedulero in schedulero:
                    dataHN = HN.objects.all()
                    datastaff = Staff.objects.filter(Pid=dataOFFALL.Pid)
                    for datastaffs in datastaff:
                        Hid = datastaffs.Hid
                    personbook = bookingperson.objects.filter(schedule_id=schedulero.id)
                    datees = schedule.objects.filter(id=schedulero.id).first()
                    persons = Person.objects.all()
                    dataOFFx = Officer.objects.filter(OFid=dataOFFALL.OFid)
                    for personbookst in personbook:
                        if personbookst.OFid == dataOFFALL.OFid:
                            for dataOFFs in dataOFFx:
                                for personses in persons:
                                    if dataOFFs.Pid == personses.Pid:
                                        namestaff = personses.Pname
                        if personbookst.OFid != dataOFFALL.OFid:
                            namestaff = '-'
                    dataOFF = Officer.objects.filter(OFid=dataOFFALL.OFid).first()
                    Dids = str(dataOFF.Did)
                    counttoday = schedule.objects.filter(start=datees.start, OFid=dataOFFALL.OFid)
                    dataOFFDPM = Officer.objects.filter(Did=Dids)
                    number = 0
                    numbertoday = 0
                    numberDPM = 0
                    numberDPMtoday = 0
                    text = ''
                    call = ''
                    for dataOFFDPMs in dataOFFDPM:
                        countDPM = schedule.objects.filter(OFid=dataOFFDPMs.OFid, start=datees.start)
                        for countDPMsa in countDPM:
                            numberDPMtoday = countDPMsa.number + numberDPMtoday
                    for counttodays in counttoday:
                        if counttodays.OFid == counttodays.OFid:
                            numbertoday = counttodays.number + numbertoday
                    for personbooks in personbook:
                        for personses in persons:
                            if personbooks.Pid == personses.Pid:
                                name = personses.Pname
                        for dataHNs in dataHN:
                            if personbooks.Pid == dataHNs.HNpid and dataHNs.HNhid == Hid:
                                HNs = dataHNs.HN
                        cout = cout + 1
                        if personbooks.callqueue:
                            call = 1
                        else:
                            call = 0
                        if personbooks.OFid:
                            for dataOFFs in dataOFFx:
                                for personses in persons:
                                    if dataOFFs.Pid == personses.Pid:
                                        namestaff = personses.Pname
                        else:
                            namestaff = '-'
                        print(namestaff)
                        bookinglist = []
                        bookinglist.append(int(personbooks.id))
                        bookinglist.append(str(personbooks.event))
                        bookinglist.append(str(name))
                        bookinglist.append(str(HNs))
                        bookinglist.append(str(namestaff))
                        bookinglist.append(str(personbooks.status))
                        bookinglist.append(str(personbooks.queuenum))
                        bookinglist.append(str(call))
                        bookinglist.append(str(personbooks.schedule_id))
                        bookinglist.append(str(personbooks.callqueue))
                        bookingper.append(bookinglist)
        else:
            dataHN = HN.objects.all()
            bookingper = []
            datastaff = Staff.objects.filter(Pid=request.session['user_id'])
            cout = 0
            for datastaffs in datastaff:
                Hid = datastaffs.Hid
            dataOFFALL = Officer.objects.filter(OFid=OFid)
            for dataOFFALL in dataOFFALL:
                schedulero = schedule.objects.filter(OFid=OFid, start=test_list_ids, timestart=timestart,
                                                     timeend=timeend)
                for schedulero in schedulero:
                    dataHN = HN.objects.all()
                    datastaff = Staff.objects.filter(Pid=dataOFFALL.Pid)
                    for datastaffs in datastaff:
                        Hid = datastaffs.Hid
                    personbook = bookingperson.objects.filter(schedule_id=schedulero.id, OFid=OFid).order_by('queuenum')
                    datees = schedule.objects.filter(id=schedulero.id).first()
                    persons = Person.objects.all()
                    dataOFF = Officer.objects.filter(OFid=dataOFFALL.OFid)
                    for personbookst in personbook:
                        if personbookst.OFid == dataOFFALL.OFid:
                            for dataOFFs in dataOFF:
                                for personses in persons:
                                    if dataOFFs.Pid == personses.Pid:
                                        namestaff = personses.Pname
                        else:
                            namestaff = '-'
                    dataOFF = Officer.objects.filter(OFid=dataOFFALL.OFid).first()
                    Dids = str(dataOFF.Did)
                    counttoday = schedule.objects.filter(start=datees.start, OFid=dataOFFALL.OFid)
                    dataOFFDPM = Officer.objects.filter(Did=Dids)
                    number = 0
                    numbertoday = 0
                    numberDPM = 0
                    numberDPMtoday = 0
                    text = ''
                    call = ''
                    for personbooks in personbook:
                        for personses in persons:
                            if personbooks.Pid == personses.Pid:
                                name = personses.Pname
                        for dataHNs in dataHN:
                            if personbooks.Pid == dataHNs.HNpid and dataHNs.HNhid == Hid:
                                HNs = dataHNs.HN
                        cout = cout + 1
                        if personbooks.callqueue:
                            call = 1
                        else:
                            call = 0
                        bookinglist = []
                        bookinglist.append(int(personbooks.id))
                        bookinglist.append(str(personbooks.event))
                        bookinglist.append(str(name))
                        bookinglist.append(str(HNs))
                        bookinglist.append(str(namestaff))
                        bookinglist.append(str(personbooks.status))
                        bookinglist.append(str(personbooks.queuenum))
                        bookinglist.append(str(call))
                        bookinglist.append(str(personbooks.schedule_id))
                        bookinglist.append(str(personbooks.callqueue))
                        bookingper.append(bookinglist)
        data = json.dumps({
            'bookingper': bookingper,
        })
        return HttpResponse(data, content_type="application/json")
    else:
        return redirect('login')


def callqueueup(request):
    if request.session._session:
        bkid = request.POST['id']
        nowx = datetime.now()
        bookingperson.objects.filter(pk=bkid).update(callqueue=nowx)
        test_list_ids = request.POST['test_list_ids']
        test_list_ids = json.loads(test_list_ids)
        OFid = request.POST['OFid']
        timesst = request.POST['timesst']
        timesse = request.POST['timesse']
        timestart = str(timesst)
        timeend = str(timesse)
        if OFid == '':
            bookingper = []
            cout = 0
            dataOFFX = Officer.objects.filter(Pid=request.session['user_id']).first()
            Hosx = hospitaltime.objects.filter(Did=dataOFFX.Did)
            dataOFFALL = Officer.objects.filter(Did=dataOFFX.Did)
            for dataOFFALL in dataOFFALL:
                schedulero = schedule.objects.filter(OFid=dataOFFALL.OFid, start=test_list_ids, timestart=timestart,
                                                     timeend=timeend)
                for schedulero in schedulero:
                    dataHN = HN.objects.all()
                    datastaff = Staff.objects.filter(Pid=dataOFFALL.Pid)
                    for datastaffs in datastaff:
                        Hid = datastaffs.Hid
                    personbook = bookingperson.objects.filter(schedule_id=schedulero.id).order_by('queuenum')
                    datees = schedule.objects.filter(id=schedulero.id).first()
                    persons = Person.objects.all()
                    dataOFF = Officer.objects.filter(OFid=dataOFFALL.OFid)
                    for personbookst in personbook:
                        if personbookst.OFid == dataOFFALL.OFid:
                            for dataOFFs in dataOFF:
                                for personses in persons:
                                    if dataOFFs.Pid == personses.Pid:
                                        namestaff = personses.Pname
                        else:
                            namestaff = '-'
                    dataOFF = Officer.objects.filter(OFid=dataOFFALL.OFid).first()
                    Dids = str(dataOFF.Did)
                    counttoday = schedule.objects.filter(start=datees.start, OFid=dataOFFALL.OFid)
                    dataOFFDPM = Officer.objects.filter(Did=Dids)
                    number = 0
                    numbertoday = 0
                    numberDPM = 0
                    numberDPMtoday = 0
                    text = ''
                    call = ''
                    for dataOFFDPMs in dataOFFDPM:
                        countDPM = schedule.objects.filter(OFid=dataOFFDPMs.OFid, start=datees.start)
                        for countDPMsa in countDPM:
                            numberDPMtoday = countDPMsa.number + numberDPMtoday
                    for counttodays in counttoday:
                        if counttodays.OFid == counttodays.OFid:
                            numbertoday = counttodays.number + numbertoday
                    for personbooks in personbook:
                        for personses in persons:
                            if personbooks.Pid == personses.Pid:
                                name = personses.Pname
                        for dataHNs in dataHN:
                            if personbooks.Pid == dataHNs.HNpid and dataHNs.HNhid == Hid:
                                HNs = dataHNs.HN
                        cout = cout + 1
                        if personbooks.callqueue:
                            call = 1
                        else:
                            call = 0
                        bookinglist = []
                        bookinglist.append(int(personbooks.id))
                        bookinglist.append(str(personbooks.event))
                        bookinglist.append(str(name))
                        bookinglist.append(str(HNs))
                        bookinglist.append(str(namestaff))
                        bookinglist.append(str(personbooks.status))
                        bookinglist.append(str(personbooks.queuenum))
                        bookinglist.append(str(call))
                        bookinglist.append(str(personbooks.schedule_id))
                        bookinglist.append(str(personbooks.callqueue))
                        bookingper.append(bookinglist)
        else:
            dataHN = HN.objects.all()
            datastaff = Staff.objects.filter(Pid=request.session['user_id'])
            for datastaffs in datastaff:
                Hid = datastaffs.Hid
            personbook = bookingperson.objects.filter(schedule_id=test_list_ids).order_by('id')
            datees = schedule.objects.filter(id=test_list_ids).first()
            persons = Person.objects.all()
            dataOFF = Officer.objects.filter(OFid=OFid)
            for dataOFFs in dataOFF:
                for personses in persons:
                    if dataOFFs.Pid == personses.Pid:
                        namestaff = personses.Pname
            dataOFF = Officer.objects.filter(OFid=OFid).first()
            Dids = str(dataOFF.Did)
            counttoday = schedule.objects.filter(start=datees.start, OFid=OFid)
            dataOFFDPM = Officer.objects.filter(Did=Dids)
            number = 0
            numbertoday = 0
            numberDPM = 0
            numberDPMtoday = 0
            text = ''
            cout = 0
            call = ''
            for dataOFFDPMs in dataOFFDPM:
                countDPM = schedule.objects.filter(OFid=dataOFFDPMs.OFid, start=datees.start)
                for countDPMsa in countDPM:
                    numberDPMtoday = countDPMsa.number + numberDPMtoday
            for counttodays in counttoday:
                if counttodays.OFid == counttodays.OFid:
                    numbertoday = counttodays.number + numbertoday
            bookingper = []
            for personbooks in personbook:
                for personses in persons:
                    if personbooks.Pid == personses.Pid:
                        name = personses.Pname
                for dataHNs in dataHN:
                    if personbooks.Pid == dataHNs.HNpid and dataHNs.HNhid == Hid:
                        HNs = dataHNs.HN
                cout = cout + 1
                if personbooks.callqueue:
                    call = 1
                else:
                    call = 0
                bookinglist = []
                bookinglist.append(int(personbooks.id))
                bookinglist.append(str(personbooks.event))
                bookinglist.append(str(name))
                bookinglist.append(str(HNs))
                bookinglist.append(str(namestaff))
                bookinglist.append(str(personbooks.status))
                bookinglist.append(str(cout))
                bookinglist.append(str(call))
                bookinglist.append(str(personbooks.schedule_id))
                bookinglist.append(str(personbooks.callqueue))
                bookingper.append(bookinglist)
            print(bookingper)
        data = json.dumps({
            'bookingper': bookingper,
            'numbertoday': numbertoday,
            'numberDPMtoday': numberDPMtoday,
        })
        return HttpResponse(data, content_type="application/json")
    else:
        return redirect('login')


def callqueuemail(request):
    if request.session._session:
        bkid = request.POST['id']
        return redirect(reverse(callqueuemail2, kwargs={'bkid': bkid}))


def callqueuemail2(request, bkid):
    x = int(bkid)
    # emails = bookingperson.objects.filter(pk=x).first()
    # Persx = Person.objects.filter(Pid=emails.Pid)
    # dbqueue = mysql.connector.connect(
    #     host="db",
    #     user="ableplant",
    #     password="abp1234",
    #     database="webapp"
    # )
    # queue = dbqueue.cursor()
    # queue.execute(
    #     "SELECT a.event,a.verify,a.status,b.start,b.timestart,b.timeend,d.Pname,f.Dname,g.Hname,a.id,a.reed,b.number,a.callqueue,a.Pid FROM doqs_bookingperson AS a INNER JOIN doqs_schedule AS b ON a.schedule_id = b.id INNER JOIN doqs_officer AS c ON b.OFid = c.OFid INNER JOIN doqs_person AS d ON c.Pid = d.Pid INNER JOIN doqs_department AS f ON c.Did = f.Did INNER JOIN doqs_hospital AS g ON f.Hid = g.Hid WHERE a.id = %s ORDER BY a.id ASC",
    #     [x])
    # queues = queue.fetchall()
    # for queues in queues:
    #     dpm = queues[7]
    #     event = queues[0]
    #     hname = queues[8]
    #     staffname = queues[6]
    # for Persx in Persx:
    #     emailx = Persx.Pemail
    # sender_email = "DooQService@gmail.com"
    # receiver_email = emailx
    # password = "dooqservice"
    #
    # message = MIMEMultipart("alternative")
    # message["Subject"] = "doo-q"
    # message["From"] = sender_email
    # message["To"] = receiver_email
    #
    # # Create the plain-text and HTML version of your message
    # text = """\
    #            Hi,
    #            How are you?
    #            Real Python has many great tutorials:
    #            www.realpython.com"""
    # html = """\
    #            <html>
    #              <body>
    #                <p>กิจกรรม : """ + event + """<br>
    #                 <p>โรงพยาบาล : """ + hname + """<br>
    #                  <p>แผนก : """ + dpm + """<br>
    #                   <p>หมอ/เจ้าหน้าที่ : """ + staffname + """<br>
    #                   เชิญที่ห้องตรวจ<br>
    #                   <br>
    #                   <a href="https://www.doo-q.com/calendar">กดลิ้งเพื่อตรวจดูข้อมูลการจองคิวของคุณ</a>
    #                </p>
    #              </body>
    #            </html>
    #            """
    #
    # # Turn these into plain/html MIMEText objects
    # part1 = MIMEText(text, "plain")
    # part2 = MIMEText(html, "html")
    #
    # # Add HTML/plain-text parts to MIMEMultipart message
    # # The email client will try to render the last part first
    # message.attach(part1)
    # message.attach(part2)
    #
    # # Create secure connection with server and send email
    # context = ssl.create_default_context()
    # with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    #     server.login(sender_email, password)
    #     server.sendmail(
    #         sender_email, receiver_email, message.as_string()
    #     )
    return HttpResponse("เสร็จ")


def callqueueck(request):
    if request.session._session:
        OFid = request.POST['re_sta']
        if OFid != '':
            OFix = int(OFid)
        else:
            OFix = OFid
        check = 1
        bklistxs = []
        sumnumber = 0
        sumcount = 0
        dataOFFax = Officer.objects.filter(Pid=request.session['user_id'])
        today = date.today()
        if dataOFFax:
            dataST = Staff.objects.get(Pid=request.session['user_id'])
            for dataOFFs in dataOFFax:
                OFid = dataOFFs.OFid
                datatime = hospitaltime.objects.filter(Did=dataOFFs.Did).order_by('timestart')
            dataDPM = Department.objects.filter(Hid=dataST.Hid)
            datahospital = Hospital.objects.all()
            dataPerson = Person.objects.all()
            dataST = Staff.objects.get(Pid=request.session['user_id'])
            dataOFF = Officer.objects.filter(Pid=request.session['user_id']).first()
            Dids = dataOFF.Did
            dataOFFall = Officer.objects.filter(Did=Dids)
            if OFix != '':
                dataOFFallx = Officer.objects.filter(OFid=OFix)
            dataOFF = Officer.objects.filter(Did=Dids)
            dataHospitalx = hospitaltime.objects.filter(Did=Dids, start=today).order_by('timestart')
            bookingshow = []
            error = ''
            for dataHospitalx in dataHospitalx:
                bookinglist = []
                bookinglist.append(str(dataHospitalx.start))
                bookinglist.append(str(dataHospitalx.timestart))
                bookinglist.append(str(dataHospitalx.timeend))
                bookingshow.append(bookinglist)
            if OFix != '':
                for dataOFFallx in dataOFFallx:
                    scheduleys = schedule.objects.filter(OFid=dataOFFallx.OFid, start=today).order_by('timestart')
                    for scheduleys in scheduleys:
                        counts = 0
                        dataOFFxs = Officer.objects.filter(OFid=scheduleys.OFid).first()
                        sperson = Person.objects.filter(Pid=dataOFFxs.Pid).first()
                        personbking = bookingperson.objects.filter(OFid=dataOFFxs.OFid, schedule_id=scheduleys.id)
                        for personbking in personbking:
                            counts = counts + 1
                        sumnumber = scheduleys.number + sumnumber
                        sumcount = counts + sumcount
                        bklistx = []
                        bklistx.append(str(scheduleys.id))
                        bklistx.append(str(scheduleys.timestart))
                        bklistx.append(str(scheduleys.timeend))
                        bklistx.append(scheduleys.number)
                        bklistx.append(counts)
                        bklistx.append(str(sperson.Pname))
                        bklistxs.append(bklistx)
            if OFix == '':
                for dataOFFallx in dataOFFall:
                    scheduleys = schedule.objects.filter(OFid=dataOFFallx.OFid, start=today).order_by('timestart')
                    for scheduleys in scheduleys:
                        counts = 0
                        dataOFFxs = Officer.objects.filter(OFid=scheduleys.OFid).first()
                        sperson = Person.objects.filter(Pid=dataOFFxs.Pid).first()
                        personbking = bookingperson.objects.filter(OFid=dataOFFxs.OFid, schedule_id=scheduleys.id)
                        for personbking in personbking:
                            counts = counts + 1
                        sumnumber = scheduleys.number + sumnumber
                        sumcount = counts + sumcount
                        bklistx = []
                        bklistx.append(str(scheduleys.id))
                        bklistx.append(str(scheduleys.timestart))
                        bklistx.append(str(scheduleys.timeend))
                        bklistx.append(scheduleys.number)
                        bklistx.append(counts)
                        bklistx.append(str(sperson.Pname))
                        bklistxs.append(bklistx)
            return render(request, 'callqueue2.html',
                          {'dataST': dataST, 'datahospital': datahospital,
                           'Dids': Dids,
                           'OFid': OFix,
                           'dataOFFax': dataOFFax,
                           'bookingshow': bookingshow,
                           'dataDPM': dataDPM,
                           'error': error,
                           'check': check,
                           'sumcount': sumcount,
                           'sumnumber': sumnumber,
                           'bklistxs': bklistxs,
                           'dataPerson': dataPerson,
                           'dataOFFall': dataOFFall})
        else:
            return redirect('staffinfo')
    else:
        return redirect('login')


def reed(request):
    bkid = request.POST['id']
    bookingperson.objects.filter(pk=bkid).update(reed='1')
    return redirect('calendar')


def dashboard(request):
    if request.session._session:
        today = date.today()
        checkstaff = Staff.objects.filter(Pid=request.session['user_id']).first()
        if checkstaff.status == 1:
            dataOFFax = Officer.objects.filter(Pid=request.session['user_id'])
            if dataOFFax:
                shows = '0'
                dataST = Staff.objects.get(Pid=request.session['user_id'])
                for dataOFFs in dataOFFax:
                    OFid = dataOFFs.OFid
                    datatime = hospitaltime.objects.filter(Did=dataOFFs.Did).order_by('timestart')
                dataDPM = Department.objects.filter(Hid=dataST.Hid)
                datahospital = Hospital.objects.all()
                dataPerson = Person.objects.all()
                dataST = Staff.objects.get(Pid=request.session['user_id'])
                dataOFF = Officer.objects.filter(Pid=request.session['user_id']).first()
                Dids = dataOFF.Did
                dataOFF = Officer.objects.filter(Pid=request.session['user_id']).first()
                dataOFFALL = Officer.objects.filter(Pid=request.session['user_id'])
                listbooking = []
                listinsertbook = []
                listtime = []
                number = 0
                for dataOFFALL in dataOFFALL:
                    mydbdashboard = mysql.connector.connect(
                        host="localhost",
                        user="root",
                        password="",
                        database="doqs"
                    )
                    dashboards = mydbdashboard.cursor()
                    dashboards.execute(
                        "SELECT SUM(a.number),a.start,a.timestart,a.timeend,a.OFid,a.id  FROM `doqs_schedule` AS a WHERE a.start = %s GROUP BY a.timestart ORDER BY a.timestart DESC",
                        [today])
                    dashboardses = dashboards.fetchall()
                    mydbdashboardesy = mysql.connector.connect(
                        host="localhost",
                        user="root",
                        password="",
                        database="doqs"
                    )
                    dashboardsesy = mydbdashboardesy.cursor()
                    dashboardsesy.execute(
                        "SELECT sum(a.number),a.start,a.timestart,a.timeend,a.OFid,a.id, COUNT(b.id) FROM `doqs_schedule` AS a LEFT JOIN doqs_bookingperson AS b ON a.id = b.schedule_id WHERE a.start = %s GROUP BY a.timestart  ORDER BY timestart DESC",
                        [today])
                    dashboardsesst = dashboardsesy.fetchall()
                    for dashboardsesst in dashboardsesst:
                        if dashboardsesst[4] == dataOFFALL.OFid:
                            listbk = []
                            listbk.append(str(dashboardsesst[6]))
                            listbooking.append(listbk)
                    for dashboardses in dashboardses:
                        count = 0
                        if dashboardses[4] == dataOFFALL.OFid:
                            databk = bookingperson.objects.filter(schedule_id=dashboardses[5])
                            for databk in databk:
                                count = count + 1
                            listshow = []
                            listshow.append(str(dashboardses[0]))
                            listshow.append(str(dashboardses[1]))
                            listshow.append(str(dashboardses[2]))
                            listshow.append(str(dashboardses[3]))
                            listshow.append(str(dashboardses[5]))
                            listtime.append(listshow)
                if listbooking:
                    z = 1
                else:
                    z = 2
                todays = str(today)
                return render(request, 'dashboard.html',
                              {'dataST': dataST, 'datahospital': datahospital,
                               'Dids': Dids,
                               'todays': todays,
                               'listtime': listtime,
                               'listbooking': listbooking,
                               'OFid': OFid,
                               'z': z,
                               'shows': shows,
                               'dataOFFax': dataOFFax,
                               'dataDPM': dataDPM,
                               })
            else:
                return redirect('staffinfo')
        else:
            return redirect('staffcheck')
    else:
        return redirect('login')


def indexan(request):
    if request.session._session:
        now = datetime.now()
        today = date.today()
        dateshow = ''
        datahospital = Hospital.objects.all()
        dataHN = HN.objects.filter(HNpid=request.session['user_id'])
        mydbhistory = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="doqs"
        )
        history = mydbhistory.cursor()
        history.execute(
            "SELECT a.event,b.start,b.timestart,b.timeend,d.Dname,e.Pname,a.status FROM doqs_bookingperson AS a INNER JOIN doqs_schedule AS b ON a.schedule_id = b.id INNER JOIN doqs_officer AS c ON b.OFid = c.OFid INNER JOIN doqs_department AS d ON d.Did = c.Did INNER JOIN doqs_person AS e ON e.Pid = c.Pid WHERE a.Pid = %s",
            [request.session['user_id']])
        historys = history.fetchall()
        mydbhistoryes = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="doqs"
        )
        historyes = mydbhistoryes.cursor()
        historyes.execute(
            "SELECT a.event,a.verify,a.status,b.start,b.timestart,b.timeend,d.Pname,f.Dname,g.Hname,a.id,a.reed,a.callqueue FROM doqs_bookingperson AS a INNER JOIN doqs_schedule AS b ON a.schedule_id = b.id INNER JOIN doqs_officer AS c ON b.OFid = c.OFid INNER JOIN doqs_person AS d ON c.Pid = d.Pid INNER JOIN doqs_department AS f ON c.Did = f.Did INNER JOIN doqs_hospital AS g ON f.Hid = g.Hid  WHERE a.Pid = %s ORDER BY b.start DESC",
            [request.session['user_id']])
        historyses = historyes.fetchall()
        dateshowlist = []
        for historyseses in historyses:
            dateshow = historyseses[1]
            dateshowlist.append(dateshow)
        dbqueue = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="doqs"
        )
        queue = dbqueue.cursor()
        queue.execute(
            "SELECT a.event,a.verify,a.status,b.start,b.timestart,b.timeend,d.Pname,f.Dname,g.Hname,a.id,a.reed,b.number,a.callqueue,a.Pid FROM doqs_bookingperson AS a INNER JOIN doqs_schedule AS b ON a.schedule_id = b.id INNER JOIN doqs_officer AS c ON b.OFid = c.OFid INNER JOIN doqs_person AS d ON c.Pid = d.Pid INNER JOIN doqs_department AS f ON c.Did = f.Did INNER JOIN doqs_hospital AS g ON f.Hid = g.Hid WHERE b.start = %s AND a.status = 1 ORDER BY a.id ASC",
            [today])
        queues = queue.fetchall()
        queueslist = []
        countes = 0
        sumq = 0
        for queuesest in queues:
            listqu = []
            countes = countes + 1
            sumq = sumq + 1
            if queuesest[13] == request.session['user_id']:
                if queuesest[12] == None:
                    sumq = sumq - 1
                    listqu.append(countes)
                    listqu.append(str(queuesest[0]))
                    listqu.append(str(queuesest[1]))
                    listqu.append(int(queuesest[2]))
                    listqu.append(str(queuesest[3]))
                    listqu.append(str(queuesest[4]))
                    listqu.append(str(queuesest[5]))
                    listqu.append(str(queuesest[6]))
                    listqu.append(str(queuesest[7]))
                    listqu.append(str(queuesest[8]))
                    listqu.append(str(queuesest[9]))
                    listqu.append(str(queuesest[10]))
                    listqu.append(str(queuesest[11]))
                    listqu.append(str(queuesest[12]))
                    listqu.append(str(queuesest[13]))
                    listqu.append(int(sumq))
                    queueslist.append(listqu)
                    break
                else:
                    sumq = 0
                    listqu.append(countes)
                    listqu.append(str(queuesest[0]))
                    listqu.append(str(queuesest[1]))
                    listqu.append(int(queuesest[2]))
                    listqu.append(str(queuesest[3]))
                    listqu.append(str(queuesest[4]))
                    listqu.append(str(queuesest[5]))
                    listqu.append(str(queuesest[6]))
                    listqu.append(str(queuesest[7]))
                    listqu.append(str(queuesest[8]))
                    listqu.append(str(queuesest[9]))
                    listqu.append(str(queuesest[10]))
                    listqu.append(str(queuesest[11]))
                    listqu.append(str(queuesest[12]))
                    listqu.append(str(queuesest[13]))
                    listqu.append(int(sumq))
                    queueslist.append(listqu)
                    break
        y = 0
        checkactive = ''
        checkactivequeue = ''
        for queueslist in queueslist:
            if queueslist[2] == 'None':
                print("xxx")
            else:
                y = 1
                checkactivequeue = int(queueslist[10])
        if historyses:
            x = 0
        else:
            x = 1
        for historyseses in historyses:
            checkactive = historyseses[9]
            break
        return render(request, 'androidindex.html',
                      {'datahospital': datahospital, 'historyses': historyses, 'historys': historys, 'dataHN': dataHN,
                       'now': now,
                       'y': y,
                       'x': x,
                       'checkactive': checkactive,
                       'checkactivequeue': checkactivequeue,
                       'dateshow': dateshow, 'queueslist': queueslist, 'today': today, 'dateshowlist': dateshowlist, })
    else:
        return redirect('loginan')


def infoan(request):
    if request.session._session:
        dataPerson = Person.objects.filter(Pid=request.session['user_id'])
        if request.session['error2'] == 1:
            request.session['error'] = ''
        if request.session['error']:
            request.session['error2'] = request.session['error']
        return render(request, 'androidinfo.html', {'dataPerson': dataPerson})
    else:
        return redirect('login')


def historyan(request):
    if request.session._session:
        mydbhistoryes = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="doqs"
        )
        historyes = mydbhistoryes.cursor()
        historyes.execute(
            "SELECT a.event,a.verify,a.status,b.start,b.timestart,b.timeend,d.Pname,f.Dname,g.Hname,a.id,a.reed FROM doqs_bookingperson AS a INNER JOIN doqs_schedule AS b ON a.schedule_id = b.id INNER JOIN doqs_officer AS c ON b.OFid = c.OFid INNER JOIN doqs_person AS d ON c.Pid = d.Pid INNER JOIN doqs_department AS f ON c.Did = f.Did INNER JOIN doqs_hospital AS g ON f.Hid = g.Hid  WHERE a.Pid = %s  ORDER BY b.start DESC",
            [request.session['user_id']])
        historyses = historyes.fetchall()
        return render(request, 'androidhistory.html',
                      {'historyses': historyses})
    else:
        return redirect('loginan')


def hnan(request):
    if request.session._session:
        dataHN = HN.objects.filter(HNpid=request.session['user_id'])
        datahospital = Hospital.objects.all()
        hospitalcheck = []
        hncheck = []
        hospitaledit = []
        hospitalshow = []
        hnlist = []
        for dataHNs in dataHN:
            hnlist.append(dataHN)
        for d in datahospital:
            hospitalcheck.append(int(d.Hid))
        for dataHNs in dataHN:
            hncheck.append(int(dataHNs.HNhid))
        for hncheck in hncheck:
            hospitalcheck.remove(int(hncheck))
            dtHos = Hospital.objects.filter(Hid=int(hncheck))
            for dtHoses in dtHos:
                dataHNcheck = HN.objects.filter(HNpid=request.session['user_id'], HNhid=dtHoses.Hid)
                for dataHNs in dataHNcheck:
                    listex = []
                    listex.append(int(dtHoses.Hid))
                    listex.append(str(dtHoses.Hname))
                    listex.append(str(dataHNs.HN))
                    listex.append(str(dataHNs.id))
                    hospitalshow.append(listex)
        for datahospitals in datahospital:
            for hospitalcheckes in hospitalcheck:
                if datahospitals.Hid == hospitalcheckes:
                    listshow = []
                    listshow.append(int(datahospitals.Hid))
                    listshow.append(str(datahospitals.Hname))
                    hospitaledit.append(listshow)
        return render(request, 'androidhn.html',
                      {'hospital': datahospital, 'HN': dataHN, 'datahospital': datahospital,
                       'hospitaledit': hospitaledit,
                       'hospitalshow': hospitalshow})
    else:
        return redirect('loginan')


def bkan(request):
    if request.session._session:
        if request.session['Hid'] != '':
            request.session['error'] = ''
            request.session['checkdelete'] = ''
            dataHos = Hospital.objects.filter(Hid=int(request.session['Hid'])).first()
            dataDPM = Department.objects.filter(Hid=dataHos.Hid)
            return render(request, 'androidhnbooking.html', {'dataDPM': dataDPM})

        else:
            return redirect('hnan')
    else:
        return redirect('loginan')


def scbkan(request):
    if request.session._session:
        return render(request, 'androidbksucces.html')
    else:
        return redirect('loginan')


def fiterbookan(request):
    if request.session._session:
        dateList = request.POST['dateList']
        schedules = schedule.objects.filter(start=dateList)
        shows = ''
        for schedules in schedules:
            checkbooking = bookingperson.objects.filter(Pid=request.session['user_id'], schedule_id=schedules.id)
            for checkbooking in checkbooking:
                shows = 1
        dataHos = Hospital.objects.filter(Hid=int(request.session['Hid'])).first()
        dataDPM = Department.objects.filter(Hid=dataHos.Hid)
        count = 0
        number = 0
        sum = 0
        color = 'mediumseagreen'
        color2 = 'seagreen'
        for dataDPMs in dataDPM:
            dataOFF = Officer.objects.filter(Did=dataDPMs.Did)
            for dataOFFs in dataOFF:
                datacalendar = schedule.objects.filter(OFid=dataOFFs.OFid, start=dateList)
                for datacalendars in datacalendar:
                    count = datacalendars.number + count
                    dataperson = bookingperson.objects.filter(schedule_id=datacalendars.id)
                    for datapersons in dataperson:
                        number = number + 1
        if number > 0:
            sum = (number / count) * 100
            if sum > 80:
                color = '#f22b16'
                color2 = '#e42110'
            elif sum > 50:
                color = '#ff9a03'
                color2 = '#fe8906'
            elif sum >= 0:
                color = 'mediumseagreen'
                color2 = 'seagreen'
        data = json.dumps({
            'count': count,
            'number': number,
            'color': color,
            'color2': color2,
            'shows': shows,
        })
        return HttpResponse(data, content_type="application/json")
    else:
        return redirect('loginan')


def filtermodal(request):
    if request.session._session:
        idcheck = request.POST['idcheck']
        statuses = ''
        show = bookingperson.objects.filter(id=idcheck)
        for shows in show:
            Pid = shows.Pid
        modal = bookingperson.objects.filter(Pid=Pid)
        modallist = []
        color = 'black'
        for modals in modal:
            print('x')
            schedules = schedule.objects.filter(id=modals.schedule_id)
            for scheduleses in schedules:
                dataOFF = Officer.objects.filter(OFid=scheduleses.OFid)
                for dataOFFs in dataOFF:
                    OFPID = dataOFFs.Pid
                    OFDID = dataOFFs.Did
                dataper = Person.objects.filter(Pid=OFPID)
                per = Person.objects.filter(Pid=Pid)
                for pers in per:
                    bkname = pers.Pname
                dataDPM = Department.objects.filter(Did=OFDID)
                for datapers in dataper:
                    name = datapers.Pname
                for dataDPMs in dataDPM:
                    dpmname = dataDPMs.Dname
                if modals.status == 1 or modals.status == 3:
                    statuses = 'รับนัด'
                if modals.status == 2 or modals.status == 4:
                    statuses = 'ปฏิเสธ'
                    color = 'red'
                list = []
                list.append(modals.id)
                list.append(modals.event)
                list.append(str(scheduleses.start))
                list.append(str(scheduleses.timestart))
                list.append(str(scheduleses.timeend))
                list.append(str(name))
                list.append(str(dpmname))
                list.append(str(statuses))
                list.append(str(bkname))
                list.append(str(color))
                modallist.append(list)
        data = json.dumps({
            'modallist': modallist,
        })
        return HttpResponse(data, content_type="application/json")
    else:
        return redirect('loginan')


def addhumanan(request):
    HMid = request.POST['userid']
    HMname = request.POST['usename']
    HMpassword = request.POST['password']
    passwordcomfrim = request.POST['comfirm']
    HMemail = request.POST['mail']
    dataperson = Person.objects.filter(Pid=HMid)
    if dataperson:
        error = 2
        return render(request, 'registeran.html', {'data': error})
    else:
        inserthuman = Person(Pid=HMid, Pname=HMname, Ppassword=HMpassword, Pemail=HMemail)
        inserthuman.save()
        error = 1
        if request.POST['check'] != '2':
            Patients = Patient(Pid=HMid)
            Patients.save()
            error = 1
            dataPerson = Person.objects.get(Pid=HMid)
            if dataPerson.Pid == HMid and dataPerson.Ppassword == HMpassword:
                dataStaff = Staff.objects.all()
            for dataStaffs in dataStaff:
                if dataStaffs.Pid == HMid:
                    x = 1
                    break
                else:
                    x = 2
            request.session['permission'] = x
            request.session['user_id'] = HMid
            request.session['name'] = HMname
            user_id = request.session['user_id']
            name = request.session['name']
            request.session['hospital'] = ''
            request.session['hn'] = ''
            request.session['Hid'] = ''
            request.session['error'] = ''
            request.session['error2'] = ''
            response = redirect('indexan')
            return response
        else:
            Staffs = Staff(Pid=HMid, status=0)
            Staffs.save()
            error = 1
            dataPerson = Person.objects.get(Pid=HMid)
            if dataPerson.Pid == HMid and dataPerson.Ppassword == HMpassword:
                dataStaff = Staff.objects.all()
            for dataStaffs in dataStaff:
                if dataStaffs.Pid == HMid:
                    x = 1
                    break
                else:
                    x = 2
            request.session['permission'] = x
            request.session['user_id'] = HMid
            request.session['name'] = HMname
            user_id = request.session['user_id']
            name = request.session['name']
            response = redirect('staffmoniter')
            return response


def cloginan(request):
    Pid = request.POST['Pid']
    Ppassword = request.POST['Ppassword']
    dataPerson = Person.objects.filter(Pid=Pid).first()
    if dataPerson:
        if dataPerson.Pid == Pid and dataPerson.Ppassword == Ppassword:
            dataStaff = Staff.objects.all()
            for dataStaffs in dataStaff:
                if dataStaffs.Pid == Pid:
                    x = 1
                    break
                else:
                    x = 2
        else:
            data = 1
            return render(request, 'login.html',
                          {'data': data, })
        dataHNs = HN.objects.filter(HNpid=dataPerson.Pid, hncheck=1)
        datahos = Hospital.objects.all()
        if dataHNs:
            for dataHNs in dataHNs:
                if dataHNs.hncheck == 1:
                    for datahos in datahos:
                        if datahos.Hid == dataHNs.HNhid:
                            request.session['hospital'] = datahos.Hname
                            request.session['hn'] = dataHNs.HN
                            request.session['Hid'] = datahos.Hid
        else:
            request.session['hospital'] = ''
            request.session['hn'] = ''
            request.session['Hid'] = ''
        request.session['error'] = ''
        request.session['error2'] = ''
        request.session['permission'] = x
        request.session['user_id'] = dataPerson.Pid
        request.session['name'] = dataPerson.Pname
        user_id = request.session['user_id']
        name = request.session['name']
        permission = request.session['permission']
        if x == 1:
            request.session['hospital'] = ''
            request.session['hn'] = ''
            request.session['Hid'] = ''
            response = redirect('dashboard')
            return response
        else:
            response = redirect('indexan')
            return response
    else:
        data = 1
        return render(request, 'login.html',
                      {'data': data, })


def editpersonan(request):
    if request.session._session:
        HMid = request.POST['userid']
        HMname = request.POST['usename']
        HMpassword = request.POST['password']
        HMemail = request.POST['mail']
        user_edit = Person.objects.get(pk=HMid)
        user_edit.Pname = HMname
        user_edit.Pemail = HMemail
        user_edit.Ppassword = HMpassword
        user_edit.save()
        request.session['error'] = 1
        response = redirect('infoan')
        return response
    else:
        return redirect('loginan')


def addhnan(request):
    if request.session._session:
        hospitals = Hospital.objects.all()
        for hospitals in hospitals:
            idcheck = hospitals.Hid
            ids = str(idcheck)
            check = str('HN' + ids)
            idsss = str('HNid' + ids)
            check2 = str('HNnew' + ids)
            if check in request.POST:
                chek = request.POST[check]
                idck = request.POST[idsss]
                if chek != "":
                    HN.objects.filter(pk=idck).update(HN=chek)
            if check2 in request.POST:
                che = request.POST[check2]
                if che != "":
                    HNpid = request.session['user_id']
                    inserthn = HN(HNpid=HNpid, HNhid=hospitals.Hid, HN=che)
                    inserthn.save()
        response = redirect('hnan')
        return response
    else:
        return redirect('login')


def settinghns(request):
    if request.session._session:
        hnid = request.POST['hnid']
        dataHN = HN.objects.filter(id=int(hnid))
        request.session['hospital'] = ''
        request.session['hn'] = ''
        del request.session['hn']
        del request.session['hospital']
        for dataHNs in dataHN:
            datahos = Hospital.objects.filter(Hid=int(dataHNs.HNhid))
            for datahoss in datahos:
                print(datahoss.Hname)
                request.session['hospital'] = datahoss.Hname
                request.session['hn'] = dataHNs.HN
                request.session['Hid'] = datahoss.Hid
        dataHNst = HN.objects.filter(id=int(hnid), HNpid=request.session['user_id']).update(hncheck='1')
        dataHNsts = HN.objects.filter(HNpid=request.session['user_id'])
        for dataHNsts in dataHNsts:
            if dataHNsts.id != int(hnid) and dataHNsts.HNpid == request.session['user_id']:
                a = HN.objects.get(pk=dataHNsts.id)
                a.hncheck = '0'
                a.save()
        response = redirect('indexan')
        return response
    else:
        return redirect('loginan')


def checkad(request):
    if request.session._session:
        bookingshow = []
        bookingshow2 = []
        x = ''
        event = ''
        date = ''
        color = ''
        count = 0
        sum = 0
        x = ''
        y = ''
        checkx = ''
        f1 = request.POST['function']
        test_list_ids = request.POST['dateshow']
        select = []
        listtime = []
        if f1 == 'department':
            shownumber = 0
            shownumber2 = 0
            Did = request.POST['id']
            dataofs = Officer.objects.filter(Did=Did)

            datapers = Person.objects.all()

            for dataof in dataofs:
                for dataper in datapers:
                    if dataper.Pid == dataof.Pid:
                        test = []
                        test.append(str(dataof.OFid))
                        test.append(dataper.Pname)
                        select.append(test)
            dataOFFes = Officer.objects.filter(Did=Did)
            hospitaltimexx = hospitaltime.objects.filter(Did=Did, start=test_list_ids).order_by('timestart')
            for hospitaltimexx in hospitaltimexx:
                listday = []
                listday.append(str(hospitaltimexx.timestart))
                listday.append(str(hospitaltimexx.timeend))
                listday.append(str(hospitaltimexx.start))
                listtime.append(listday)
            for dataOFFS in dataOFFes:
                shownumber2 = 0
                timestart = ''
                timeend = ''
                OFid = dataOFFS.OFid
                ShowOFF = Officer.objects.filter(OFid=OFid).first()
                Dids = str(ShowOFF.Did)
                OFids = ShowOFF.OFid
                dataOFFSx = Officer.objects.filter(Did=Dids)
                for dataOFFSx in dataOFFSx:
                    schedulex = schedule.objects.filter(OFid=dataOFFSx.OFid, start=test_list_ids)
                    thebest = schedule.objects.filter(start=test_list_ids)
                    for schedulex in schedulex:
                        shownumber2 = schedulex.number + shownumber2
                scheduleshow = schedule.objects.filter(start=test_list_ids, OFid=OFid, status=0)
                for scheduleshowes in scheduleshow:
                    shownumber = scheduleshowes.number + shownumber
                for thebest in thebest:
                    check = bookingperson.objects.filter(schedule_id=thebest.id, Pid=request.session['user_id'])
                    if check:
                        for checks in check:
                            if checks.schedule_id == thebest.id:
                                date = 'check'
                for scheduleshow in scheduleshow:
                    dataOFFcheck = Officer.objects.filter(OFid=scheduleshow.OFid)
                    for dataOFFcheck in dataOFFcheck:
                        dataper = Person.objects.filter(Pid=dataOFFcheck.Pid)
                        for dataper in dataper:
                            name = dataper.Pname
                    count = 0
                    bookinglist = []
                    check = bookingperson.objects.filter(schedule_id=scheduleshow.id, Pid=request.session['user_id'])
                    if check:
                        for checks in check:
                            event = str(checks.event)
                    else:
                        event = ''
                    countbooking = bookingperson.objects.filter(schedule_id=scheduleshow.id)
                    for countbookings in countbooking:
                        count = count + 1
                    sum = (count / scheduleshow.number) * 100
                    if sum > 80:
                        color = 'danger'
                    elif sum > 50:
                        color = 'warning'
                    elif sum > 0:
                        color = 'success'
                    bookinglist.append(str(scheduleshow.id))
                    bookinglist.append(str(scheduleshow.start))
                    bookinglist.append(str(scheduleshow.timestart))
                    bookinglist.append(str(scheduleshow.timeend))
                    bookinglist.append(int(scheduleshow.number))
                    bookinglist.append(date)
                    bookinglist.append(event)
                    bookinglist.append(int(count))
                    bookinglist.append(int(sum))
                    bookinglist.append(str(color))
                    bookinglist.append(str(name))
                    bookingshow.append(bookinglist)
        if f1 == 'staff':
            OFid = request.POST['id']
            shownumber = 0
            shownumber2 = 0
            dataOFFes = Officer.objects.filter(OFid=OFid)
            for dataOFFS in dataOFFes:
                OFid = dataOFFS.OFid
                ShowOFF = Officer.objects.filter(OFid=OFid).first()
                Dids = str(ShowOFF.Did)
                OFids = ShowOFF.OFid
                scheduleshow = schedule.objects.filter(start=test_list_ids, OFid=OFid, status=0)
                schedulecheck = schedule.objects.filter(start=test_list_ids, status=0)
                dataOFFSx = Officer.objects.filter(Did=Dids)
                for dataOFFSx in dataOFFSx:
                    schedulex = schedule.objects.filter(OFid=dataOFFSx.OFid, start=test_list_ids)
                    for schedulex in schedulex:
                        shownumber2 = schedulex.number + shownumber2
                for scheduleshow in scheduleshow:
                    dataOFFcheck = Officer.objects.filter(OFid=scheduleshow.OFid)
                    for dataOFFcheck in dataOFFcheck:
                        dataper = Person.objects.filter(Pid=dataOFFcheck.Pid)
                        for dataper in dataper:
                            name = dataper.Pname
                    shownumber = scheduleshow.number + shownumber
                    count = 0
                    bookinglist = []
                    check = bookingperson.objects.filter(schedule_id=scheduleshow.id, Pid=request.session['user_id'])
                    if check:
                        for checks in check:
                            event = str(checks.event)
                    else:
                        event = ''
                    countbooking = bookingperson.objects.filter(schedule_id=scheduleshow.id)
                    for scheduleshowes in schedulecheck:
                        check = bookingperson.objects.filter(schedule_id=scheduleshowes.id,
                                                             Pid=request.session['user_id'])
                        if check:
                            for checks in check:
                                if checks.schedule_id == scheduleshowes.id and checks.OFid == scheduleshowes.OFid:
                                    date = 'check'
                                elif checks.schedule_id == scheduleshowes.id:
                                    date = 'check'
                                    event = ''
                    for countbookings in countbooking:
                        count = count + 1
                    sum = (count / scheduleshow.number) * 100
                    if sum > 80:
                        color = 'danger'
                    elif sum > 50:
                        color = 'warning'
                    elif sum > 0:
                        color = 'success'
                    bookinglist.append(str(scheduleshow.id))
                    bookinglist.append(str(scheduleshow.start))
                    bookinglist.append(str(scheduleshow.timestart))
                    bookinglist.append(str(scheduleshow.timeend))
                    bookinglist.append(int(scheduleshow.number))
                    bookinglist.append(date)
                    bookinglist.append(event)
                    bookinglist.append(int(count))
                    bookinglist.append(int(sum))
                    bookinglist.append(str(color))
                    bookinglist.append(str(name))
                    bookingshow.append(bookinglist)
            print(bookingshow)
        data = json.dumps({
            'bookingshow': bookingshow,
            'selectOFif': select,
            'listtime': listtime,
            'shownumber': shownumber,
            'shownumber2': shownumber2,
        })
        return HttpResponse(data, content_type="application/json")
    else:
        return redirect('login')


def bookingeventan(request):
    if request.session._session:
        today = date.today()
        sids = schedule.objects.all()
        event = request.POST['eventes']
        checkdelete = request.POST['checkdelete']
        request.session['checkdelete'] = checkdelete
        Dids = ''
        OFidx = ''
        if checkdelete == '2':
            for sid in sids:
                idtest = sid.id
                ids = str(idtest)
                check = str('even' + ids)
                idss = str('id' + ids)
                if check in request.POST:
                    che = request.POST[check]
                    id = request.POST[idss]
                    schedulexy = schedule.objects.filter(id=id)
                    for schedulexy in schedulexy:
                        dataOFFxs = Officer.objects.filter(OFid=schedulexy.OFid)
                        for dataOFFxs in dataOFFxs:
                            Dids = dataOFFxs.Did
                            OFidx = dataOFFxs.OFid
                    if event == '':
                        event = 'ตรวจทั่วไป'
                    if che != "":
                        insertbk = bookingperson(schedule_id=id, event=event, Pid=request.session['user_id'],
                                                 status=0, OFid=OFidx, Did=Dids)
                        insertbk.save()
            mydbhistoryes = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="doqs"
            )
            historyes = mydbhistoryes.cursor()
            historyes.execute(
                "SELECT a.event,a.verify,a.status,b.start,b.timestart,b.timeend,d.Pname,f.Dname,g.Hname,a.id,a.reed,a.callqueue FROM doqs_bookingperson AS a INNER JOIN doqs_schedule AS b ON a.schedule_id = b.id INNER JOIN doqs_officer AS c ON b.OFid = c.OFid INNER JOIN doqs_person AS d ON c.Pid = d.Pid INNER JOIN doqs_department AS f ON c.Did = f.Did INNER JOIN doqs_hospital AS g ON f.Hid = g.Hid  WHERE a.Pid = %s ORDER BY a.id DESC ",
                [request.session['user_id']])
            if event == '':
                event = 'ตรวจทั่วไป'
            dataevent = event
            return render(request, 'androidbksucces.html',
                          {'dataevent': dataevent, 'historyes': historyes, 'checkdelete': checkdelete, 'today': today})
        if checkdelete == '1':
            checkbk = bookingperson.objects.all()
            for sid in checkbk:
                idtest = sid.schedule_id
                ids = str(idtest)
                check = str('even' + ids)
                idss = str('id' + ids)
                if idss in request.POST:
                    id = request.POST[idss]
                    checkbooking = bookingperson.objects.filter(schedule_id=id,
                                                                Pid=request.session['user_id'])

                    for checkbookings in checkbooking:
                        eventcancel = checkbookings.event
                        bookingperson.objects.get(pk=checkbookings.id).delete()
        return render(request, 'androidbksucces.html',
                      {'eventcancel': eventcancel, 'checkdelete': checkdelete, })

    else:
        return redirect('login')


def logout(request):
    request.session.clear()
    response = redirect('loginan')
    return response


def staffcheck(request):
    if request.session._session:
        checkstaff = Staff.objects.filter(Pid=request.session['user_id']).first()
        if checkstaff.status == 1:
            return redirect('staffinfo')
        else:
            return render(request, 'staffcheck.html')
    else:
        return redirect('login')


def staffpermiss(request):
    mydbhistoryes = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="doqs"
    )
    staffshow = mydbhistoryes.cursor()
    staffshow.execute(
        "SELECT * FROM `doqs_person` AS a INNER JOIN doqs_staff AS b ON a.Pid = b.Pid ORDER BY b.status ASC")
    return render(request, 'staffpermission.html',
                  {'staffshow': staffshow})


def permission(request, Pid):
    Staff.objects.filter(id__in=Pid).update(status='1')
    return redirect('staffpermiss')


def canpermission(request, Pid):
    Staff.objects.filter(id__in=Pid).update(status='0')
    return redirect('staffpermiss')


def getdatedb(request):
    if request.session._session:
        checkdate = request.POST['checkdate']
        datechecks = request.POST['datechecks']
        checkstaff = Staff.objects.filter(Pid=request.session['user_id']).first()
        dateshow = ''
        if checkstaff.status == 1:
            dataOFFax = Officer.objects.filter(Pid=request.session['user_id'])
            if dataOFFax:
                shows = 0
                dataST = Staff.objects.get(Pid=request.session['user_id'])
                for dataOFFs in dataOFFax:
                    OFid = dataOFFs.OFid
                    datatime = hospitaltime.objects.filter(Did=dataOFFs.Did).order_by('timestart')
                dataDPM = Department.objects.filter(Hid=dataST.Hid)
                datahospital = Hospital.objects.all()
                dataPerson = Person.objects.all()
                dataST = Staff.objects.get(Pid=request.session['user_id'])
                dataOFF = Officer.objects.filter(Pid=request.session['user_id']).first()
                Dids = dataOFF.Did
                dataOFF = Officer.objects.filter(Pid=request.session['user_id']).first()
                dataOFFALL = Officer.objects.filter(Pid=request.session['user_id'])
                listbooking = []
                listinsertbook = []
                listtime = []
                listtimex = []
                number = 0
                today = date.today()
                if checkdate == '0':
                    dateshow = '%' + datechecks[0:13] + '%'
                    shows = checkdate
                    for dataOFFALL in dataOFFALL:
                        mydbdashboard = mysql.connector.connect(
                            host="localhost",
                            user="root",
                            password="",
                            database="doqs"
                        )
                        dashboards = mydbdashboard.cursor()
                        dashboards.execute(
                            "SELECT SUM(number),start,timestart,timeend,OFid,id FROM `doqs_schedule` WHERE start LIKE %s AND OFid = %s GROUP BY timestart ORDER BY timestart DESC",
                            [dateshow, dataOFFALL.OFid])
                        dashboardses = dashboards.fetchall()
                        mydbdashboardesy = mysql.connector.connect(
                            host="localhost",
                            user="root",
                            password="",
                            database="doqs"
                        )
                        dashboardsesy = mydbdashboardesy.cursor()
                        dashboardsesy.execute(
                            "SELECT sum(a.number),a.start,a.timestart,a.timeend,a.OFid,a.id, COUNT(b.id) FROM `doqs_schedule` AS a LEFT JOIN doqs_bookingperson AS b ON a.id = b.schedule_id WHERE a.start LIKE %s AND a.OFid = %s GROUP BY a.timestart  ORDER BY timestart DESC",
                            [dateshow, dataOFFALL.OFid])
                        dashboardsesst = dashboardsesy.fetchall()
                        for dashboardsesst in dashboardsesst:
                            listbk = []
                            listbk.append(str(dashboardsesst[6]))
                            listbooking.append(listbk)
                        for dashboardses in dashboardses:
                            count = 0
                            databk = bookingperson.objects.filter(schedule_id=dashboardses[5])
                            for databk in databk:
                                count = count + 1
                            listshow = []
                            listshow.append(str(dashboardses[0]))
                            listshow.append(str(dashboardses[1]))
                            listshow.append(str(dashboardses[2]))
                            listshow.append(str(dashboardses[3]))
                            listshow.append(str(dashboardses[5]))
                            listtime.append(listshow)
                if checkdate == '1':
                    monthshow = '%' + datechecks[0:8] + '%'
                    shows = checkdate
                    for dataOFFALL in dataOFFALL:
                        mydbdashboard = mysql.connector.connect(
                            host="localhost",
                            user="root",
                            password="",
                            database="doqs"
                        )
                        dashboards = mydbdashboard.cursor()
                        dashboards.execute(
                            "SELECT SUM(number),start,timestart,timeend,OFid,id FROM `doqs_schedule` WHERE start LIKE %s AND OFid = %s GROUP BY start ORDER BY start ASC",
                            [monthshow, dataOFFALL.OFid])
                        dashboardses = dashboards.fetchall()
                        mydbdashboardesy = mysql.connector.connect(
                            host="localhost",
                            user="root",
                            password="",
                            database="doqs"
                        )
                        dashboardsesy = mydbdashboardesy.cursor()
                        dashboardsesy.execute(
                            "SELECT sum(a.number),a.start,a.timestart,a.timeend,a.OFid,a.id, COUNT(b.id) FROM `doqs_schedule` AS a LEFT JOIN doqs_bookingperson AS b ON a.id = b.schedule_id WHERE a.start LIKE %s AND a.OFid = %s GROUP BY a.start  ORDER BY a.start ASC",
                            [monthshow, dataOFFALL.OFid])
                        dashboardsesst = dashboardsesy.fetchall()
                        for dashboardsesst in dashboardsesst:
                            listbk = []
                            listbk.append(str(dashboardsesst[6]))
                            listbooking.append(listbk)
                        for dashboardses in dashboardses:
                            count = 0
                            databk = bookingperson.objects.filter(schedule_id=dashboardses[5])
                            for databk in databk:
                                count = count + 1
                            listshow = []
                            day = str(dashboardses[1])
                            listshow.append(str(dashboardses[0]))
                            listshow.append('วันที่' + day[8:12])
                            listshow.append(str(dashboardses[2]))
                            listshow.append(str(dashboardses[3]))
                            listshow.append(str(dashboardses[5]))
                            listtime.append(listshow)
                    print(listtime)
                if checkdate == '2':
                    shows = checkdate
                    yearshow = '%' + datechecks[0:4] + '%'
                    print(yearshow)
                    for dataOFFALL in dataOFFALL:
                        mydbdashboard = mysql.connector.connect(
                            host="localhost",
                            user="root",
                            password="",
                            database="doqs"
                        )
                        dashboards = mydbdashboard.cursor()
                        dashboards.execute(
                            "SELECT SUM(number),start,timestart,timeend,OFid,id FROM `doqs_schedule` WHERE start LIKE %s AND OFid = %s GROUP BY MONTH(start) ORDER BY START DESC",
                            [yearshow, dataOFFALL.OFid])
                        dashboardses = dashboards.fetchall()
                        mydbdashboardesy = mysql.connector.connect(
                            host="localhost",
                            user="root",
                            password="",
                            database="doqs"
                        )
                        dashboardsesy = mydbdashboardesy.cursor()
                        dashboardsesy.execute(
                            "SELECT sum(a.number),a.start,a.timestart,a.timeend,a.OFid,a.id, COUNT(b.id) FROM `doqs_schedule` AS a LEFT JOIN doqs_bookingperson AS b ON a.id = b.schedule_id WHERE a.start LIKE %s  AND a.OFid = %s GROUP BY MONTH(a.START)  ORDER BY START DESC",
                            [yearshow, dataOFFALL.OFid])
                        dashboardsesst = dashboardsesy.fetchall()
                        for dashboardsesst in dashboardsesst:
                            listbk = []
                            listbk.append(str(dashboardsesst[6]))
                            listbooking.append(listbk)
                        for dashboardses in dashboardses:
                            count = 0
                            databk = bookingperson.objects.filter(schedule_id=dashboardses[5])
                            for databk in databk:
                                count = count + 1
                            months = str(dashboardses[1])
                            if months[5:7] == '01':
                                M = "มกราคม"
                            elif months[5:7] == '02':
                                M = "กุมภาพันธ์"
                            elif months[5:7] == '03':
                                months[5:7] = "มีนาคม"
                            elif months[5:7] == '04':
                                M = "เมษายน"
                            elif months[5:7] == '05':
                                M = "พฤษภาคม"
                            elif months[5:7] == '06':
                                M = "มิถุนายน"
                            elif months[5:7] == '07':
                                M = "กรกฎาคม"
                            elif months[5:7] == '08':
                                months[5:7] = "สิงหาคม"
                            elif months[5:7] == '09':
                                M = "กันยายน"
                            elif months[5:7] == '10':
                                M = "ตุลาคม"
                            elif months[5:7] == '11':
                                M = "พฤศจิกายน"
                            elif months[5:7] == '12':
                                M = "ธันวาคม"
                            listshow = []
                            listshow.append(str(dashboardses[0]))
                            listshow.append(M)
                            listshow.append(str(dashboardses[2]))
                            listshow.append(str(dashboardses[3]))
                            listshow.append(str(dashboardses[5]))
                            listtime.append(listshow)
                if listbooking:
                    z = 1
                else:
                    z = 2
                return render(request, 'dashboard.html',
                              {'dataST': dataST, 'datahospital': datahospital,
                               'Dids': Dids,
                               'listtime': listtime,
                               'listbooking': listbooking,
                               'OFid': OFid,
                               'z': z,
                               'shows': shows,
                               'dataOFFax': dataOFFax,
                               'dataDPM': dataDPM,
                               'checkdate': checkdate,
                               'datechecks': datechecks,
                               'dataPerson': dataPerson,
                               })
            else:
                return redirect('staffinfo')
        else:
            return redirect('staffcheck')
    else:
        return redirect('login')


def hnud(request):
    hospitals = Hospital.objects.all()
    for hospitals in hospitals:
        idcheck = hospitals.Hid
        ids = str(idcheck)
        check = str('HN' + ids)
        idsss = str('HNid' + ids)
        check2 = str('HNnew' + ids)
        if check in request.POST:
            chek = request.POST[check]
            idck = request.POST[idsss]
            if chek != "":
                HN.objects.filter(pk=idck).update(HN=chek)
        if check2 in request.POST:
            che = request.POST[check2]
            if che != "":
                HNpid = request.session['user_id']
                inserthn = HN(HNpid=HNpid, HNhid=hospitals.Hid, HN=che)
                inserthn.save()
    response = redirect('person')
    return response


def checkqueue(request):
    if request.session._session:
        now = datetime.now()
        today = date.today()
        dateshow = ''
        datahospital = Hospital.objects.all()
        dataHN = HN.objects.filter(HNpid=request.session['user_id'])
        mydbhistory = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="doqs"
        )
        history = mydbhistory.cursor()
        history.execute(
            "SELECT a.event,b.start,b.timestart,b.timeend,d.Dname,e.Pname,a.status FROM doqs_bookingperson AS a INNER JOIN doqs_schedule AS b ON a.schedule_id = b.id INNER JOIN doqs_officer AS c ON b.OFid = c.OFid INNER JOIN doqs_department AS d ON d.Did = c.Did INNER JOIN doqs_person AS e ON e.Pid = c.Pid WHERE a.Pid = %s",
            [request.session['user_id']])
        historys = history.fetchall()
        mydbhistoryes = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="doqs"
        )
        historyes = mydbhistoryes.cursor()
        historyes.execute(
            "SELECT a.event,a.verify,a.status,b.start,b.timestart,b.timeend,d.Pname,f.Dname,g.Hname,a.id,a.reed,a.callqueue FROM doqs_bookingperson AS a INNER JOIN doqs_schedule AS b ON a.schedule_id = b.id INNER JOIN doqs_officer AS c ON b.OFid = c.OFid INNER JOIN doqs_person AS d ON c.Pid = d.Pid INNER JOIN doqs_department AS f ON c.Did = f.Did INNER JOIN doqs_hospital AS g ON f.Hid = g.Hid  WHERE a.Pid = %s ORDER BY b.start DESC",
            [request.session['user_id']])
        historyses = historyes.fetchall()
        dateshowlist = []
        for historyseses in historyses:
            dateshow = historyseses[1]
            dateshowlist.append(dateshow)
        dbqueue = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="doqs"
        )
        queue = dbqueue.cursor()
        queue.execute(
            "SELECT a.event,a.verify,a.status,b.start,b.timestart,b.timeend,d.Pname,f.Dname,g.Hname,a.id,a.reed,b.number,a.callqueue,a.Pid FROM doqs_bookingperson AS a INNER JOIN doqs_schedule AS b ON a.schedule_id = b.id INNER JOIN doqs_officer AS c ON b.OFid = c.OFid INNER JOIN doqs_person AS d ON c.Pid = d.Pid INNER JOIN doqs_department AS f ON c.Did = f.Did INNER JOIN doqs_hospital AS g ON f.Hid = g.Hid WHERE b.start = %s  AND a.status = 1 ORDER BY a.id ASC",
            [today])
        queues = queue.fetchall()
        queueslist = []
        countes = 0
        sumq = 0
        for queuesest in queues:
            listqu = []
            countes = countes + 1
            sumq = sumq + 1
            if queuesest[13] == request.session['user_id']:
                if queuesest[12] == None:
                    sumq = sumq - 1
                    listqu.append(countes)
                    listqu.append(str(queuesest[0]))
                    listqu.append(str(queuesest[1]))
                    listqu.append(int(queuesest[2]))
                    listqu.append(str(queuesest[3]))
                    listqu.append(str(queuesest[4]))
                    listqu.append(str(queuesest[5]))
                    listqu.append(str(queuesest[6]))
                    listqu.append(str(queuesest[7]))
                    listqu.append(str(queuesest[8]))
                    listqu.append(str(queuesest[9]))
                    listqu.append(str(queuesest[10]))
                    listqu.append(str(queuesest[11]))
                    listqu.append(str(queuesest[12]))
                    listqu.append(str(queuesest[13]))
                    listqu.append(int(sumq))
                    queueslist.append(listqu)
                    break
                else:
                    sumq = 0
                    listqu.append(countes)
                    listqu.append(str(queuesest[0]))
                    listqu.append(str(queuesest[1]))
                    listqu.append(int(queuesest[2]))
                    listqu.append(str(queuesest[3]))
                    listqu.append(str(queuesest[4]))
                    listqu.append(str(queuesest[5]))
                    listqu.append(str(queuesest[6]))
                    listqu.append(str(queuesest[7]))
                    listqu.append(str(queuesest[8]))
                    listqu.append(str(queuesest[9]))
                    listqu.append(str(queuesest[10]))
                    listqu.append(str(queuesest[11]))
                    listqu.append(str(queuesest[12]))
                    listqu.append(str(queuesest[13]))
                    listqu.append(int(sumq))
                    queueslist.append(listqu)
                    break
        y = 0
        checkactive = ''
        checkactivequeue = ''
        for queueslist in queueslist:
            if queueslist[2] == 'None':
                print("xxx")
            else:
                y = 1
                checkactivequeue = int(queueslist[10])
        if historyses:
            x = 0
        else:
            x = 1
        for historyseses in historyses:
            checkactive = historyseses[9]
            break
        if queueslist:
            z = 2
        else:
            z = 1
        return render(request, 'CheckQueue.html',
                      {'datahospital': datahospital, 'historyses': historyses, 'historys': historys, 'dataHN': dataHN,
                       'now': now,
                       'y': y,
                       'x': x,
                       'z': z,
                       'checkactive': checkactive,
                       'checkactivequeue': checkactivequeue,
                       'dateshow': dateshow, 'queueslist': queueslist, 'today': today, 'dateshowlist': dateshowlist, })
    else:
        return redirect('loginan')


def bookingeventan2(request):
    if request.session._session:
        dpmss = request.POST['dpms']
        stfssss = request.POST['stfs']
        datess = request.POST['dates']
        request.session['datess'] = datess
        request.session['stfssss'] = stfssss
        request.session['dpmss'] = dpmss
        today = date.today()
        sids = schedule.objects.all()
        checkdelete = request.POST['checkdelete']
        request.session['checkdelete'] = checkdelete
        checksql = ''
        counts = 0
        dataOFFXXX = Officer.objects.filter(Did=dpmss)
        for dataOFFXXX in dataOFFXXX:
            datasce = schedule.objects.filter(OFid=dataOFFXXX.OFid, start=datess)
            for datasce in datasce:
                bkper = bookingperson.objects.filter(schedule_id=datasce.id)
                for bkper in bkper:
                    counts = counts + 1
        if checkdelete == '2':
            if stfssss == '':
                for sid in sids:
                    idtest = sid.id
                    ids = str(idtest)
                    check = str('eventes' + ids)
                    idss = str('id' + ids)
                    even = str('even' + ids)
                    if even in request.POST:
                        che = request.POST[check]
                        evens = request.POST[even]
                        checksql = che
                        id = request.POST[idss]
                        schedulest = schedule.objects.filter(id=id)
                        for schedulest in schedulest:
                            count = 0
                            bkps = bookingperson.objects.filter(schedule_id=schedulest.id)
                            for bkps in bkps:
                                count = count + 1
                            if count == schedulest.number:
                                dataOFF = Officer.objects.filter(OFid=schedulest.OFid).first()
                                Dids = dataOFF.Did
                                dataOFFall = Officer.objects.filter(Did=Dids)
                                for dataOFFall in dataOFFall:
                                    schedulestsc = schedule.objects.filter(OFid=dataOFFall.OFid,
                                                                           timestart=schedulest.timestart,
                                                                           timeend=schedulest.timeend,
                                                                           start=schedulest.start)
                                    for schedulestsc in schedulestsc:
                                        if count < schedulestsc.number:
                                            if evens == '1':
                                                if che == '':
                                                    che = 'ตรวจทั่วไป'
                                                checksql = che
                                                insertbk = bookingperson(schedule_id=schedulestsc.id, event=che,
                                                                         Pid=request.session['user_id'], Did=dpmss,
                                                                         status=0,
                                                                         OFid=schedulestsc.OFid)
                                                request.session['event'] = che
                                                return redirect('calendarridirec')
                        if evens == '1':
                            schedulestxt = schedule.objects.filter(id=id)
                            for schedulest in schedulestxt:
                                if che == '':
                                    che = 'ตรวจทั่วไป'
                                checksql = che
                                insertbk = bookingperson(schedule_id=id, event=che, Pid=request.session['user_id'],
                                                         status=0, Did=dpmss, OFid=schedulest.OFid)
                                insertbk.save()
                                request.session['event'] = che
                                return redirect('calendarridirec')
                if checksql == '':
                    dataevent = checksql
                    request.session['event'] = dataevent
                    return redirect('calendarridirec')
            else:
                for sid in sids:
                    idtest = sid.id
                    ids = str(idtest)
                    check = str('eventes' + ids)
                    idss = str('id' + ids)
                    even = str('even' + ids)
                    if even in request.POST:
                        che = request.POST[check]
                        evens = request.POST[even]
                        checksql = che
                        id = request.POST[idss]
                        schedulest = schedule.objects.filter(id=id)
                        for schedulest in schedulest:
                            count = 0
                            bkps = bookingperson.objects.filter(schedule_id=schedulest.id)
                            for bkps in bkps:
                                count = count + 1
                            if count == schedulest.number:
                                dataOFF = Officer.objects.filter(OFid=schedulest.OFid).first()
                                Dids = dataOFF.Did
                                dataOFFall = Officer.objects.filter(Did=Dids)
                                for dataOFFall in dataOFFall:
                                    schedulestsc = schedule.objects.filter(OFid=dataOFFall.OFid,
                                                                           timestart=schedulest.timestart,
                                                                           timeend=schedulest.timeend,
                                                                           start=schedulest.start)
                                    for schedulestsc in schedulestsc:
                                        if count < schedulestsc.number:
                                            if evens == '1':
                                                if che == '':
                                                    che = 'ตรวจทั่วไป'
                                                checksql = che
                                                insertbk = bookingperson(schedule_id=schedulestsc.id, event=che,
                                                                         Pid=request.session['user_id'], Did=dpmss,
                                                                         status=0, OFid=stfssss, queuenum=counts + 1)
                                                request.session['event'] = che
                                                return redirect('calendarridirec')
                        if evens == '1':
                            if che == '':
                                che = 'ตรวจทั่วไป'
                            checksql = che
                            insertbk = bookingperson(schedule_id=id, event=che, Pid=request.session['user_id'],
                                                     status=0, Did=dpmss, OFid=stfssss, queuenum=counts + 1)
                            insertbk.save()
                            request.session['event'] = che
                            return redirect('calendarridirec')
                if checksql == '':
                    dataevent = checksql
                    request.session['event'] = dataevent
                    return redirect('calendarridirec')
        if checkdelete == '1':
            checkbk = schedule.objects.all()
            for sid in checkbk:
                idtest = sid.id
                ids = str(idtest)
                check = str('eventes' + ids)
                idss = str('id' + ids)
                if idss in request.POST:
                    id = request.POST[idss]
                    checkbooking = bookingperson.objects.filter(schedule_id=id,
                                                                Pid=request.session['user_id'])
                    if checkbooking:
                        for checkbookings in checkbooking:
                            eventcancel = checkbookings.event
                            bookingperson.objects.get(pk=checkbookings.id).delete()
                    else:
                        scedulesxm = schedule.objects.filter(id=id)
                        for scedulesxm in scedulesxm:
                            dataOFFALLX = Officer.objects.filter(OFid=scedulesxm.OFid).first()
                            Didsx = dataOFFALLX.Did
                            dataOFFALLS = Officer.objects.filter(Did=Didsx)
                            for dataOFFALLS in dataOFFALLS:
                                scedulesllx = schedule.objects.filter(start=scedulesxm.start,
                                                                      timestart=scedulesxm.timestart,
                                                                      timeend=scedulesxm.timeend, OFid=dataOFFALLS.OFid)
                                for scedulesllx in scedulesllx:
                                    bkpsx = bookingperson.objects.filter(schedule_id=scedulesllx.id,
                                                                         Pid=request.session['user_id'])
                                    if bkpsx:
                                        for bkpsx in bkpsx:
                                            eventcancel = bkpsx.event
                                            bookingperson.objects.get(pk=bkpsx.id).delete()
            request.session['event'] = eventcancel
            return redirect('calendarridirec')
            # return render(request, 'bksucces.html',
            #               {'eventcancel': eventcancel, 'checkdelete': checkdelete, })
    else:
        return redirect('login')


def settingHNweb(request, Hnid):
    if request.session._session:
        dataHN = HN.objects.filter(id=int(Hnid), HNpid=request.session['user_id'])
        request.session['hospital'] = ''
        request.session['hn'] = ''
        del request.session['hn']
        del request.session['hospital']
        for dataHNs in dataHN:
            datahos = Hospital.objects.filter(Hid=int(dataHNs.HNhid))
            for datahoss in datahos:
                print(datahoss.Hname)
                request.session['hospital'] = datahoss.Hname
                request.session['hn'] = dataHNs.HN
                request.session['Hid'] = datahoss.Hid
        dataHNst = HN.objects.filter(id=int(Hnid), HNpid=request.session['user_id']).update(hncheck='1')
        dataHNsts = HN.objects.filter(HNpid=request.session['user_id'])
        for dataHNsts in dataHNsts:
            if dataHNsts.id != int(Hnid) and dataHNsts.HNpid == request.session['user_id']:
                a = HN.objects.get(pk=dataHNsts.id)
                a.hncheck = '0'
                a.save()
        response = redirect('person')
        return response
    else:
        return redirect('login')


def checkad2(request):
    print("xxx")
    bookingshow = []
    x = ''
    event = ''
    date = ''
    color = ''
    count = 0
    sum = 0
    f1 = request.POST['function']
    select = []
    listdays = []
    if f1 == 'department':
        shownumber = 0
        shownumber2 = 0
        Did = request.POST['id']
        dataofs = Officer.objects.filter(Did=Did)
        datapers = Person.objects.all()
        for dataof in dataofs:
            for dataper in datapers:
                if dataper.Pid == dataof.Pid:
                    test = []
                    test.append(str(dataof.OFid))
                    test.append(dataper.Pname)
                    select.append(test)
        dataOFFes = Officer.objects.filter(Did=Did)
        for dataOFFS in dataOFFes:
            OFid = dataOFFS.OFid
            ShowOFF = Officer.objects.filter(OFid=OFid).first()
            Dids = str(ShowOFF.Did)
            OFids = ShowOFF.OFid
            mydbdashboardesy = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="doqs"
            )
            dashboardsesy = mydbdashboardesy.cursor()
            dashboardsesy.execute(
                "SELECT START FROM `doqs_schedule` WHERE OFid = %s GROUP BY start ",
                [OFid])
            dashboardsesst = dashboardsesy.fetchall()
            for dashboardsesst in dashboardsesst:
                listday = []
                listday.append(str(dashboardsesst[0]))
                listdays.append(listday)
            scheduleshow = schedule.objects.filter(OFid=OFid, status=0).order_by('start')
            for scheduleshow in scheduleshow:
                count = 0
                countbooking = bookingperson.objects.filter(schedule_id=scheduleshow.id)
                for countbookings in countbooking:
                    count = count + 1
                sum = (count / scheduleshow.number) * 100
                if sum > 80:
                    color = '#f22b16'
                elif sum > 50:
                    color = '#ff9a03'
                elif sum >= 0:
                    color = 'mediumseagreen'
                bookinglist = []
                bookinglist.append(str(scheduleshow.start))
                bookinglist.append(int(scheduleshow.number))
                bookinglist.append(int(count))
                bookinglist.append(str(color))
                bookingshow.append(bookinglist)
    if f1 == 'staff':
        OFid = request.POST['id']
        shownumber = 0
        shownumber2 = 0
        dataOFFes = Officer.objects.filter(OFid=OFid)
        for dataOFFS in dataOFFes:
            OFid = dataOFFS.OFid
            ShowOFF = Officer.objects.filter(OFid=OFid).first()
            Dids = str(ShowOFF.Did)
            OFids = ShowOFF.OFid
            mydbdashboardesy = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="doqs"
            )
            dashboardsesy = mydbdashboardesy.cursor()
            dashboardsesy.execute(
                "SELECT START FROM `doqs_schedule` WHERE OFid = %s GROUP BY start ",
                [OFid])
            dashboardsesst = dashboardsesy.fetchall()
            for dashboardsesst in dashboardsesst:
                listday = []
                listday.append(str(dashboardsesst[0]))
                listdays.append(listday)
            scheduleshow = schedule.objects.filter(OFid=OFid, status=0).order_by('start')
            for scheduleshow in scheduleshow:
                count = 0
                bookinglist = []
                countbooking = bookingperson.objects.filter(schedule_id=scheduleshow.id)
                for countbookings in countbooking:
                    count = count + 1
                sum = (count / scheduleshow.number) * 100
                if sum > 80:
                    color = '#f22b16'
                elif sum > 50:
                    color = '#ff9a03'
                elif sum >= 0:
                    color = 'mediumseagreen'
                bookinglist.append(str(scheduleshow.start))
                bookinglist.append(int(scheduleshow.number))
                bookinglist.append(int(count))
                bookinglist.append(str(color))
                bookingshow.append(bookinglist)
    data = json.dumps({
        'bookingshow': bookingshow,
        'selectOFif': select,
        'listday': listdays,
        'shownumber': shownumber,
        'shownumber2': shownumber2,
    })
    return HttpResponse(data, content_type="application/json")


def calendarridirec(request):
    if request.session._session:
        if request.session['Hid'] != '':
            dataHNese = HN.objects.filter(HNpid=request.session['user_id'])
            schedulex = schedule.objects.all()
            if dataHNese:
                dataHos = Hospital.objects.filter(Hid=int(request.session['Hid'])).first()
                dataDPMse = Department.objects.filter(Hid=dataHos.Hid)
                now = datetime.now()
                today = date.today()
                dateshow = ''
                datahospital = Hospital.objects.all()
                dataHN = HN.objects.filter(HNpid=request.session['user_id'])
                mydbhistory = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="doqs"
                )
                history = mydbhistory.cursor()
                history.execute(
                    "SELECT a.event,b.start,b.timestart,b.timeend,d.Dname,e.Pname,a.status FROM doqs_bookingperson AS a INNER JOIN doqs_schedule AS b ON a.schedule_id = b.id INNER JOIN doqs_officer AS c ON b.OFid = c.OFid INNER JOIN doqs_department AS d ON d.Did = c.Did INNER JOIN doqs_person AS e ON e.Pid = c.Pid WHERE a.Pid = %s",
                    [request.session['user_id']])
                historys = history.fetchall()
                mydbhistoryes = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="doqs"
                )
                historyes = mydbhistoryes.cursor()
                historyes.execute(
                    "SELECT a.event,a.verify,a.status,b.start,b.timestart,b.timeend,d.Pname,f.Dname,g.Hname,a.id,a.reed FROM doqs_bookingperson AS a INNER JOIN doqs_schedule AS b ON a.schedule_id = b.id INNER JOIN doqs_officer AS c ON b.OFid = c.OFid INNER JOIN doqs_person AS d ON c.Pid = d.Pid INNER JOIN doqs_department AS f ON c.Did = f.Did INNER JOIN doqs_hospital AS g ON f.Hid = g.Hid  WHERE a.Pid = %s  ORDER BY b.start DESC",
                    [request.session['user_id']])
                historyses = historyes.fetchall()
                dateshowlist = []
                for historyseses in historyses:
                    dateshow = historyseses[1]
                    dateshowlist.append(dateshow)
                dbqueue = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="doqs"
                )
                queue = dbqueue.cursor()
                queue.execute(
                    "SELECT a.event,a.verify,a.status,b.start,b.timestart,b.timeend,d.Pname,f.Dname,g.Hname,a.id,a.reed,b.number,a.callqueue,a.Pid FROM doqs_bookingperson AS a INNER JOIN doqs_schedule AS b ON a.schedule_id = b.id INNER JOIN doqs_officer AS c ON b.OFid = c.OFid INNER JOIN doqs_person AS d ON c.Pid = d.Pid INNER JOIN doqs_department AS f ON c.Did = f.Did INNER JOIN doqs_hospital AS g ON f.Hid = g.Hid WHERE b.start = %s ORDER BY a.id ASC",
                    [today])
                queues = queue.fetchall()
                queueslist = []
                countes = 0
                sumq = 0
                for queuesest in queues:
                    listqu = []
                    countes = countes + 1
                    sumq = sumq + 1
                    if queuesest[13] == request.session['user_id']:
                        if queuesest[12] == None:
                            sumq = sumq - 1
                            listqu.append(countes)
                            listqu.append(str(queuesest[0]))
                            listqu.append(str(queuesest[1]))
                            listqu.append(int(queuesest[2]))
                            listqu.append(str(queuesest[3]))
                            listqu.append(str(queuesest[4]))
                            listqu.append(str(queuesest[5]))
                            listqu.append(str(queuesest[6]))
                            listqu.append(str(queuesest[7]))
                            listqu.append(str(queuesest[8]))
                            listqu.append(str(queuesest[9]))
                            listqu.append(str(queuesest[10]))
                            listqu.append(str(queuesest[11]))
                            listqu.append(str(queuesest[12]))
                            listqu.append(str(queuesest[13]))
                            listqu.append(int(sumq))
                            queueslist.append(listqu)
                            break
                        else:
                            sumq = 0
                            listqu.append(countes)
                            listqu.append(str(queuesest[0]))
                            listqu.append(str(queuesest[1]))
                            listqu.append(int(queuesest[2]))
                            listqu.append(str(queuesest[3]))
                            listqu.append(str(queuesest[4]))
                            listqu.append(str(queuesest[5]))
                            listqu.append(str(queuesest[6]))
                            listqu.append(str(queuesest[7]))
                            listqu.append(str(queuesest[8]))
                            listqu.append(str(queuesest[9]))
                            listqu.append(str(queuesest[10]))
                            listqu.append(str(queuesest[11]))
                            listqu.append(str(queuesest[12]))
                            listqu.append(str(queuesest[13]))
                            listqu.append(int(sumq))
                            queueslist.append(listqu)
                            break
                y = 0
                checkactive = ''
                checkactivequeue = ''
                for queueslist in queueslist:
                    if queueslist[2] == 'None':
                        print("xxx")
                    else:
                        print("xxx")
                        y = 1
                        checkactivequeue = int(queueslist[10])
                if historyses:
                    x = 0
                else:
                    x = 1
                for historyseses in historyses:
                    checkactive = historyseses[9]
                    break
                datess = request.session['datess']
                stfssss = request.session['stfssss']
                dpmss = request.session['dpmss']
                OFFx = Officer.objects.filter(Did=dpmss)
                Perx = Officer.objects.all()
                return render(request, 'calendar.html',
                              {'datahospital': datahospital, 'historyses': historyses, 'historys': historys,
                               'dataHN': dataHN,
                               'now': now,
                               'checkactive': checkactive,
                               'x': x,
                               'y': y,
                               'datess': datess,
                               'stfssss': stfssss,
                               'dpmss': dpmss,
                               'OFFx': OFFx,
                               'Perx': Perx,
                               'schedulex': schedulex,
                               'dataDPMse': dataDPMse,
                               'checkactivequeue': checkactivequeue,
                               'dateshow': dateshow, 'queueslist': queueslist, 'today': today,
                               'dateshowlist': dateshowlist, })
            else:
                return redirect('person')
        else:
            return redirect('person')
    else:
        return redirect('login')


def callqueue2(request):
    if request.session._session:
        checkstaff = Staff.objects.filter(Pid=request.session['user_id']).first()
        if checkstaff.status == 1:
            dataOFFax = Officer.objects.filter(Pid=request.session['user_id'])
            today = date.today()
            counts = 0
            sumnumber = 0
            sumcount = 0
            bklistxs = []
            if dataOFFax:
                dataST = Staff.objects.get(Pid=request.session['user_id'])
                for dataOFFs in dataOFFax:
                    OFid = dataOFFs.OFid
                    datatime = hospitaltime.objects.filter(Did=dataOFFs.Did).order_by('timestart')
                dataDPM = Department.objects.filter(Hid=dataST.Hid)
                datahospital = Hospital.objects.all()
                dataPerson = Person.objects.all()
                dataST = Staff.objects.get(Pid=request.session['user_id'])
                dataOFF = Officer.objects.filter(Pid=request.session['user_id']).first()
                Dids = dataOFF.Did
                dataOFFall = Officer.objects.filter(Did=Dids)
                dataOFFallx = Officer.objects.filter(Did=Dids)
                dataOFF = Officer.objects.filter(Did=Dids)
                dataHospitalx = hospitaltime.objects.filter(Did=Dids, start=today).order_by('timestart')
                bookingshow = []
                error = ''
                OFidx = ''
                for dataHospitalx in dataHospitalx:
                    bookinglist = []
                    bookinglist.append(str(dataHospitalx.start))
                    bookinglist.append(str(dataHospitalx.timestart))
                    bookinglist.append(str(dataHospitalx.timeend))
                    bookingshow.append(bookinglist)
                for dataOFFallx in dataOFFallx:
                    scheduleys = schedule.objects.filter(OFid=dataOFFallx.OFid, start=today).order_by('timestart')
                    for scheduleys in scheduleys:
                        counts = 0
                        dataOFFxs = Officer.objects.filter(OFid=scheduleys.OFid).first()
                        sperson = Person.objects.filter(Pid=dataOFFxs.Pid).first()
                        personbking = bookingperson.objects.filter(OFid=dataOFFxs.OFid, schedule_id=scheduleys.id)
                        for personbking in personbking:
                            counts = counts + 1
                        sumnumber = scheduleys.number + sumnumber
                        sumcount = counts + sumcount
                        bklistx = []
                        bklistx.append(str(scheduleys.id))
                        bklistx.append(str(scheduleys.timestart))
                        bklistx.append(str(scheduleys.timeend))
                        bklistx.append(scheduleys.number)
                        bklistx.append(counts)
                        bklistx.append(str(sperson.Pname))
                        bklistxs.append(bklistx)
                return render(request, 'callqueue2.html',
                              {'dataST': dataST, 'datahospital': datahospital,
                               'Dids': Dids,
                               'OFid': OFidx,
                               'sumnumber': sumnumber,
                               'sumcount': sumcount,
                               'dataOFFax': dataOFFax,
                               'bookingshow': bookingshow,
                               'dataDPM': dataDPM,
                               'error': error,
                               'today': today,
                               'bklistxs': bklistxs,
                               'dataPerson': dataPerson,
                               'dataOFFall': dataOFFall})
            else:
                return redirect('staffinfo')
        else:
            return redirect('staffcheck')
    else:
        return redirect('login')


def vtfbooking(request):
    if request.session._session:
        checkstaff = Staff.objects.filter(Pid=request.session['user_id']).first()
        if checkstaff.status == 1:
            request.session['OFid'] = ''
            dataOFFax = Officer.objects.filter(Pid=request.session['user_id'])
            modalbk = bookingperson.objects.all()
            dataOFFax = Officer.objects.filter(Pid=request.session['user_id'])
            today = date.today()
            bklistxs = []
            sumnumber = 0
            sumcount = 0
            now = datetime.now()
            dataOFFallx = Officer.objects.all()
            for dataOFFallx in dataOFFallx:
                schedulenovef = schedule.objects.filter(OFid=dataOFFallx.OFid)
                for schedulenovef in schedulenovef:
                    if schedulenovef.start < today:
                        bookingperson.objects.filter(schedule_id=schedulenovef.id, status=0).update(status='2',
                                                                                                    verify=now)
            if dataOFFax:
                dataST = Staff.objects.get(Pid=request.session['user_id'])
                for dataOFFs in dataOFFax:
                    OFid = dataOFFs.OFid
                    datatime = hospitaltime.objects.filter(Did=dataOFFs.Did).order_by('timestart')
                dataDPM = Department.objects.filter(Hid=dataST.Hid)
                datahospital = Hospital.objects.all()
                dataPerson = Person.objects.all()
                dataST = Staff.objects.get(Pid=request.session['user_id'])
                dataOFF = Officer.objects.filter(Pid=request.session['user_id']).first()
                Dids = dataOFF.Did
                dataOFFall = Officer.objects.filter(Did=Dids)
                dataOFF = Officer.objects.filter(Did=Dids)
                dataHospitalx = hospitaltime.objects.filter(Did=Dids).order_by('timestart')
                bookingshow = []
                error = ''
                OFidx = ''
                for dataHospitalx in dataHospitalx:
                    bookinglist = []
                    bookinglist.append(str(dataHospitalx.start))
                    bookinglist.append(str(dataHospitalx.timestart))
                    bookinglist.append(str(dataHospitalx.timeend))
                    bookingshow.append(bookinglist)
                for dataOFFallx in dataOFFall:
                    scheduleys = schedule.objects.filter(OFid=dataOFFallx.OFid, start=today).order_by('timestart')
                    for scheduleys in scheduleys:
                        counts = 0
                        dataOFFxs = Officer.objects.filter(OFid=scheduleys.OFid).first()
                        sperson = Person.objects.filter(Pid=dataOFFxs.Pid).first()
                        personbking = bookingperson.objects.filter(OFid=dataOFFxs.OFid, schedule_id=scheduleys.id)
                        for personbking in personbking:
                            counts = counts + 1
                        sumnumber = scheduleys.number + sumnumber
                        sumcount = counts + sumcount
                        bklistx = []
                        bklistx.append(str(scheduleys.id))
                        bklistx.append(str(scheduleys.timestart))
                        bklistx.append(str(scheduleys.timeend))
                        bklistx.append(scheduleys.number)
                        bklistx.append(counts)
                        bklistx.append(str(sperson.Pname))
                        bklistxs.append(bklistx)
                return render(request, 'vertiflybooking.html',
                              {'dataST': dataST, 'datahospital': datahospital,
                               'Dids': Dids,
                               'OFid': OFidx,
                               'dataOFFax': dataOFFax,
                               'bookingshow': bookingshow,
                               'dataDPM': dataDPM,
                               'sumcount': sumcount,
                               'sumnumber': sumnumber,
                               'modalbk': modalbk,
                               'error': error,
                               'bklistxs': bklistxs,
                               'dataPerson': dataPerson,
                               'dataOFFall': dataOFFall})
            else:
                return redirect('staffinfo')
        else:
            return redirect('staffcheck')
    else:
        return redirect('login')


def vtfbooking2(request):
    if request.session._session:
        checkstaff = Staff.objects.filter(Pid=request.session['user_id']).first()
        if checkstaff.status == 1:
            dataOFFax = Officer.objects.filter(Pid=request.session['user_id'])
            modalbk = bookingperson.objects.all()
            dataOFFax = Officer.objects.filter(Pid=request.session['user_id'])
            today = date.today()
            bklistxs = []
            sumnumber = 0
            sumcount = 0
            check = 1
            if dataOFFax:
                dataST = Staff.objects.get(Pid=request.session['user_id'])
                for dataOFFs in dataOFFax:
                    OFid = dataOFFs.OFid
                    datatime = hospitaltime.objects.filter(Did=dataOFFs.Did).order_by('timestart')
                dataDPM = Department.objects.filter(Hid=dataST.Hid)
                datahospital = Hospital.objects.all()
                dataPerson = Person.objects.all()
                dataST = Staff.objects.get(Pid=request.session['user_id'])
                dataOFF = Officer.objects.filter(Pid=request.session['user_id']).first()
                Dids = dataOFF.Did
                dataOFFallsz = Officer.objects.filter(Did=Dids)
                if request.session['OFid'] != '':
                    dataOFFall = Officer.objects.filter(OFid=request.session['OFid'])
                    OFidx = int(request.session['OFid'])
                else:
                    dataOFFall = Officer.objects.filter(Did=Dids)
                    OFidx = request.session['OFid']
                dataOFF = Officer.objects.filter(Did=Dids)
                dataHospitalx = hospitaltime.objects.filter(Did=Dids).order_by('timestart')
                bookingshow = []
                error = ''
                for dataHospitalx in dataHospitalx:
                    bookinglist = []
                    bookinglist.append(str(dataHospitalx.start))
                    bookinglist.append(str(dataHospitalx.timestart))
                    bookinglist.append(str(dataHospitalx.timeend))
                    bookingshow.append(bookinglist)
                for dataOFFallx in dataOFFall:
                    scheduleys = schedule.objects.filter(OFid=dataOFFallx.OFid, start=today).order_by('timestart')
                    for scheduleys in scheduleys:
                        counts = 0
                        dataOFFxs = Officer.objects.filter(OFid=scheduleys.OFid).first()
                        sperson = Person.objects.filter(Pid=dataOFFxs.Pid).first()
                        personbking = bookingperson.objects.filter(OFid=dataOFFxs.OFid, schedule_id=scheduleys.id)
                        for personbking in personbking:
                            counts = counts + 1
                        sumnumber = scheduleys.number + sumnumber
                        sumcount = counts + sumcount
                        bklistx = []
                        bklistx.append(str(scheduleys.id))
                        bklistx.append(str(scheduleys.timestart))
                        bklistx.append(str(scheduleys.timeend))
                        bklistx.append(scheduleys.number)
                        bklistx.append(counts)
                        bklistx.append(str(sperson.Pname))
                        bklistxs.append(bklistx)
                return render(request, 'vertiflybooking.html',
                              {'dataST': dataST, 'datahospital': datahospital,
                               'Dids': Dids,
                               'OFid': OFidx,
                               'dataOFFax': dataOFFax,
                               'bookingshow': bookingshow,
                               'dataDPM': dataDPM,
                               'sumcount': sumcount,
                               'sumnumber': sumnumber,
                               'modalbk': modalbk,
                               'error': error,
                               'check': check,
                               'bklistxs': bklistxs,
                               'dataPerson': dataPerson,
                               'dataOFFall': dataOFFallsz})
            else:
                return redirect('staffinfo')
        else:
            return redirect('staffcheck')
    else:
        return redirect('login')


def historybooks(request):
    today = date.today()
    bklistxs = []
    sumnumber = 0
    sumcount = 0
    OFidx = ''
    test_list_ids = request.POST['test_list_ids']
    test_list_ids = json.loads(test_list_ids)
    dataOFF = Officer.objects.filter(Pid=request.session['user_id']).first()
    Dids = dataOFF.Did
    if request.session['OFid'] != '':
        dataOFFall = Officer.objects.filter(OFid=request.session['OFid'])
        OFidx = int(request.session['OFid'])
    else:
        dataOFFall = Officer.objects.filter(Did=Dids)
        OFidx = request.session['OFid']
    for dataOFFallx in dataOFFall:
        scheduleys = schedule.objects.filter(OFid=dataOFFallx.OFid, start=test_list_ids).order_by('timestart')
        for scheduleys in scheduleys:
            counts = 0
            dataOFFxs = Officer.objects.filter(OFid=scheduleys.OFid).first()
            sperson = Person.objects.filter(Pid=dataOFFxs.Pid).first()
            personbking = bookingperson.objects.filter(OFid=dataOFFxs.OFid, schedule_id=scheduleys.id)
            for personbking in personbking:
                counts = counts + 1
            sumnumber = scheduleys.number + sumnumber
            sumcount = counts + sumcount
            bklistx = []
            bklistx.append(str(scheduleys.id))
            bklistx.append(str(scheduleys.timestart))
            bklistx.append(str(scheduleys.timeend))
            bklistx.append(scheduleys.number)
            bklistx.append(counts)
            bklistx.append(str(sperson.Pname))
            bklistxs.append(bklistx)
    print(bklistxs)
    data = json.dumps({
        'bklistxs': bklistxs,
        'sumcount': sumcount,
        'sumnumber': sumnumber,
    })
    return HttpResponse(data, content_type="application/json")


def settinghnx(request, Hnid):
    if request.session._session:
        dataHN = HN.objects.filter(id=int(Hnid), HNpid=request.session['user_id'])
        request.session['hospital'] = ''
        request.session['hn'] = ''
        del request.session['hn']
        del request.session['hospital']
        for dataHNs in dataHN:
            datahos = Hospital.objects.filter(Hid=int(dataHNs.HNhid))
            for datahoss in datahos:
                print(datahoss.Hname)
                request.session['hospital'] = datahoss.Hname
                request.session['hn'] = dataHNs.HN
                request.session['Hid'] = datahoss.Hid
        dataHNst = HN.objects.filter(id=int(Hnid), HNpid=request.session['user_id']).update(hncheck='1')
        dataHNsts = HN.objects.filter(HNpid=request.session['user_id'])
        for dataHNsts in dataHNsts:
            if dataHNsts.id != int(Hnid) and dataHNsts.HNpid == request.session['user_id']:
                a = HN.objects.get(pk=dataHNsts.id)
                a.hncheck = '0'
                a.save()
        response = redirect('calendar')
        return response
    else:
        return redirect('login')


def settingHNwebx(request, Hnid):
    if request.session._session:
        dataHN = HN.objects.filter(id=int(Hnid), HNpid=request.session['user_id'])
        request.session['hospital'] = ''
        request.session['hn'] = ''
        del request.session['hn']
        del request.session['hospital']
        for dataHNs in dataHN:
            datahos = Hospital.objects.filter(Hid=int(dataHNs.HNhid))
            for datahoss in datahos:
                print(datahoss.Hname)
                request.session['hospital'] = datahoss.Hname
                request.session['hn'] = dataHNs.HN
                request.session['Hid'] = datahoss.Hid
        dataHNst = HN.objects.filter(id=int(Hnid), HNpid=request.session['user_id']).update(hncheck='1')
        dataHNsts = HN.objects.filter(HNpid=request.session['user_id'])
        for dataHNsts in dataHNsts:
            if dataHNsts.id != int(Hnid) and dataHNsts.HNpid == request.session['user_id']:
                a = HN.objects.get(pk=dataHNsts.id)
                a.hncheck = '0'
                a.save()
        response = redirect('hnan')
        return response
    else:
        return redirect('login')


def testline(request):
    num = 10
    Person.objects.filter(pk='test').update(linetoken=num + 1)
    return render(request, 'testline.html')


def infouser(request):
    return render(request, 'infouser.html')


def tagdpm(request):
    Didx = ''
    dataOFFxs = Officer.objects.filter(Pid=request.session['user_id'])
    for dataOFFxs in dataOFFxs:
        Didx = dataOFFxs.Did
    datatag = tagdepartment.objects.filter(Did=Didx)
    return render(request, 'tagsdpm.html', {'datatag': datatag})


def addtags(request):
    tagsx = request.POST['tagsx']
    tagsinput = tagsx.split(',')
    tagsinputx = []
    Didx = ''
    dataOFFxs = Officer.objects.filter(Pid=request.session['user_id'])
    for dataOFFxs in dataOFFxs:
        Didx = dataOFFxs.Did
    for i in tagsinput:
        if i not in tagsinputx:
            tagsinputx.append(i)
    for tag in tagsinputx:
        taginsert = tagdepartment(tags=tag, Did=Didx)
        taginsert.save()
    return redirect('tagdpm')


def edittags(request):
    tagsx = request.POST['tagsxx']
    tagid = request.POST['tagid']
    tagdepartment.objects.filter(pk=tagid).update(tags=tagsx)
    return redirect('tagdpm')


def deletetags(request):
    if request.session._session:
        selected_tests = request.POST['test_list_ids']
        selected_tests = json.loads(selected_tests)
        for test in selected_tests:
            if test != '':
                tagdepartment.objects.filter(id__in=selected_tests).delete()
        response = redirect('tagsdpm')
        return response
    else:
        return redirect('login')


def showtags(request):
    dataOFFxs = Officer.objects.filter(Pid=request.session['user_id'])
    for dataOFFxs in dataOFFxs:
        Didx = dataOFFxs.Did
    idpm = request.POST['id']
    datatags = []
    tagsx = tagdepartment.objects.filter(Did=idpm)
    for tagsx in tagsx:
        datatag = []
        datatag.append(tagsx.id)
        datatag.append(tagsx.tags)
        datatags.append(datatag)
    data = json.dumps({
        'datatags': datatags,
    })
    return HttpResponse(data, content_type="application/json")


def tagssearch(request):
    idpm = request.POST['id']
    dInput = request.POST['dInput']
    print(dInput)
    datatags = []
    tagsx = tagdepartment.objects.filter(Did=idpm)
    for tagsx in tagsx:
        if dInput in tagsx.tags:
            datatag = []
            datatag.append(tagsx.id)
            datatag.append(tagsx.tags)
            datatags.append(datatag)
    data = json.dumps({
        'datatags': datatags,
    })
    return HttpResponse(data, content_type="application/json")


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def replazex(request):
    start = request.POST['start']
    end = request.POST['end']
    dataOFFxs = Officer.objects.filter(Pid=request.session['user_id'])
    for dataOFFxs in dataOFFxs:
        Didx = dataOFFxs.Did
    datecustome = request.POST['datecustome']
    date1 = 'จันทร์'
    date2 = 'อังคาร'
    date3 = 'พุธ'
    date4 = 'พฤหัส'
    date5 = 'ศุกร์'
    date6 = 'เสาร์'
    date7 = 'อาทิตย์'
    if 'date1' in request.POST:
        date1 = request.POST['date1']
    if 'date2' in request.POST:
        date2 = request.POST['date2']
    if 'date3' in request.POST:
        date3 = request.POST['date3']
    if 'date4' in request.POST:
        date4 = request.POST['date4']
    if 'date5' in request.POST:
        date5 = request.POST['date5']
    if 'date6' in request.POST:
        date6 = request.POST['date6']
    if 'date7' in request.POST:
        date7 = request.POST['date7']
    yearstart = int(start[0:4])
    mountstart = int(start[5:7])
    daystart = int(start[8:10])
    yearend = int(end[0:4])
    mountend = int(end[5:7])
    dayend = int(end[8:10])
    datecheck = ''
    dateday = ''
    hostimex = hospitaltime.objects.filter(Did=Didx, start=datecustome)
    start_date = date(yearstart, mountend, daystart)
    end_date = date(yearend, mountend, dayend)
    time_range = DateTimeRange(start, end)
    if hostimex:
        for value in time_range.range(timedelta(days=1)):
            datecheck = value.strftime("%Y-%m-%d")
            yearck = int(datecheck[0:4])
            mountck = int(datecheck[5:7])
            dayck = int(datecheck[8:10])
            x = date(yearck, mountck, dayck)
            dateday = x.ctime()
            print(dateday)
            if date1 in dateday:
                for hostime in hostimex:
                    insertime = hospitaltime(timestart=hostime.timestart, timeend=hostime.timeend, start=datecheck,
                                             Did=Didx, Hid=hostime.Hid)
                    insertime.save()
            if date2 in dateday:
                for hostime in hostimex:
                    insertime = hospitaltime(timestart=hostime.timestart, timeend=hostime.timeend, start=datecheck,
                                             Did=Didx, Hid=hostime.Hid)
                    insertime.save()
            if date3 in dateday:
                for hostime in hostimex:
                    insertime = hospitaltime(timestart=hostime.timestart, timeend=hostime.timeend, start=datecheck,
                                             Did=Didx, Hid=hostime.Hid)
                    insertime.save()
            if date4 in dateday:
                for hostime in hostimex:
                    insertime = hospitaltime(timestart=hostime.timestart, timeend=hostime.timeend, start=datecheck,
                                             Did=Didx, Hid=hostime.Hid)
                    insertime.save()
            if date5 in dateday:
                for hostime in hostimex:
                    insertime = hospitaltime(timestart=hostime.timestart, timeend=hostime.timeend, start=datecheck,
                                             Did=Didx, Hid=hostime.Hid)
                    insertime.save()
            if date6 in dateday:
                for hostime in hostimex:
                    insertime = hospitaltime(timestart=hostime.timestart, timeend=hostime.timeend, start=datecheck,
                                             Did=Didx, Hid=hostime.Hid)
                    insertime.save()
            if date7 in dateday:
                for hostime in hostimex:
                    insertime = hospitaltime(timestart=hostime.timestart, timeend=hostime.timeend, start=datecheck,
                                             Did=Didx, Hid=hostime.Hid)
                    insertime.save()
    return redirect('mnbook')


def replazecount(request):
    start = request.POST['start']
    end = request.POST['end']
    OFidx = request.POST['OFidx']
    dataOFFxs = Officer.objects.filter(Pid=request.session['user_id'])
    for dataOFFxs in dataOFFxs:
        Didx = dataOFFxs.Did
    datecustome = request.POST['datecustome']
    date1 = 'จันทร์'
    date2 = 'อังคาร'
    date3 = 'พุธ'
    date4 = 'พฤหัส'
    date5 = 'ศุกร์'
    date6 = 'เสาร์'
    date7 = 'อาทิตย์'
    if 'date1' in request.POST:
        date1 = request.POST['date1']
    if 'date2' in request.POST:
        date2 = request.POST['date2']
    if 'date3' in request.POST:
        date3 = request.POST['date3']
    if 'date4' in request.POST:
        date4 = request.POST['date4']
    if 'date5' in request.POST:
        date5 = request.POST['date5']
    if 'date6' in request.POST:
        date6 = request.POST['date6']
    if 'date7' in request.POST:
        date7 = request.POST['date7']
    yearstart = int(start[0:4])
    mountstart = int(start[5:7])
    daystart = int(start[8:10])
    yearend = int(end[0:4])
    mountend = int(end[5:7])
    dayend = int(end[8:10])
    datecheck = ''
    dateday = ''
    hostimex = schedule.objects.filter(OFid=OFidx, start=datecustome)
    hostimexy = hospitaltime.objects.filter(Did=Didx, start=datecustome)
    start_date = date(yearstart, mountend, daystart)
    end_date = date(yearend, mountend, dayend)
    time_range = DateTimeRange(start, end)
    if hostimex:
        for value in time_range.range(timedelta(days=1)):
            datecheck = value.strftime("%w")
            yearck = int(datecheck[0:4])
            mountck = int(datecheck[5:7])
            dayck = int(datecheck[8:10])
            x = date(yearck, mountck, dayck)
            dateday = x.ctime()
            if date1 in dateday:
                for hostime in hostimex:
                    insertime = schedule(timestart=hostime.timestart, timeend=hostime.timeend, start=datecheck,
                                         OFid=OFidx, status=hostime.status, number=hostime.number)
                    insertime.save()
                for hoscks in hostimexy:
                    insertimex = hospitaltime(timestart=hoscks.timestart, timeend=hoscks.timeend, start=datecheck,
                                              Did=Didx, Hid=hoscks.Hid)
                    insertimex.save()
            if date2 in dateday:
                for hostime in hostimex:
                    insertime = schedule(timestart=hostime.timestart, timeend=hostime.timeend, start=datecheck,
                                         OFid=OFidx, status=hostime.status, number=hostime.number)
                    insertime.save()
                for hoscks in hostimexy:
                    insertimex = hospitaltime(timestart=hoscks.timestart, timeend=hoscks.timeend, start=datecheck,
                                              Did=Didx, Hid=hoscks.Hid)
                    insertimex.save()
            if date3 in dateday:
                for hostime in hostimex:
                    insertime = hospitaltime(timestart=hostime.timestart, timeend=hostime.timeend, start=datecheck,
                                             Did=Didx, Hid=hostime.Hid)
                    insertime.save()
                for hoscks in hostimexy:
                    insertimex = hospitaltime(timestart=hoscks.timestart, timeend=hoscks.timeend, start=datecheck,
                                              Did=Didx, Hid=hoscks.Hid)
                    insertimex.save()
            if date4 in dateday:
                for hostime in hostimex:
                    insertime = schedule(timestart=hostime.timestart, timeend=hostime.timeend, start=datecheck,
                                         OFid=OFidx, status=hostime.status, number=hostime.number)
                    insertime.save()
                for hoscks in hostimexy:
                    insertimex = hospitaltime(timestart=hoscks.timestart, timeend=hoscks.timeend, start=datecheck,
                                              Did=Didx, Hid=hoscks.Hid)
                    insertimex.save()
            if date5 in dateday:
                for hostime in hostimex:
                    insertime = schedule(timestart=hostime.timestart, timeend=hostime.timeend, start=datecheck,
                                         OFid=OFidx, status=hostime.status, number=hostime.number)
                    insertime.save()
                for hoscks in hostimexy:
                    insertimex = hospitaltime(timestart=hoscks.timestart, timeend=hoscks.timeend, start=datecheck,
                                              Did=Didx, Hid=hoscks.Hid)
                    insertimex.save()
            if date6 in dateday:
                for hostime in hostimex:
                    insertime = schedule(timestart=hostime.timestart, timeend=hostime.timeend, start=datecheck,
                                         OFid=OFidx, status=hostime.status, number=hostime.number)
                    insertime.save()
                for hoscks in hostimexy:
                    insertimex = hospitaltime(timestart=hoscks.timestart, timeend=hoscks.timeend, start=datecheck,
                                              Did=Didx, Hid=hoscks.Hid)
                    insertimex.save()
            if date7 in dateday:
                for hostime in hostimex:
                    insertime = schedule(timestart=hostime.timestart, timeend=hostime.timeend, start=datecheck,
                                         OFid=OFidx, status=hostime.status, number=hostime.number)
                    insertime.save()
                for hoscks in hostimexy:
                    insertimex = hospitaltime(timestart=hoscks.timestart, timeend=hoscks.timeend, start=datecheck,
                                              Did=Didx, Hid=hoscks.Hid)
                    insertimex.save()

    return redirect('doctor')
