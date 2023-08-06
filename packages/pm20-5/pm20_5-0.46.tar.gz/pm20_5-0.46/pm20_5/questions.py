from importlib.resources import contents, path
from PIL import ImageGrab
from IPython.display import display, Image
import os

def q1(qn=0):
    if not qn:
        with path(
                'pm20_5.qu1',
                'q1_task1.png'
                ) as pt:
            img = Image(filename=pt)
            display(img)
        with path(
                'pm20_5.qu1',
                'q1_task2.png'
                ) as pt:
            img = Image(filename=pt)
            display(img)
    else:
        qn = str(qn)
        files = sorted(contents('pm20_5.qu1'))
        to_disp = []
        for elem in files:
            if 'q1' + '_' + qn + '_' in elem:
                to_disp.append(elem)
        if not to_disp:
            to_disp.append('q1_' + qn + '.png')
        to_disp.sort()
        for elem in to_disp:
            with path(
                'pm20_5.qu1',
                elem
                ) as pt:
                img = Image(filename=pt)
                display(img)


def q2(qn=0):
    if not qn:
        with path(
                'pm20_5.qu2',
                'q2_task1.png'
                ) as pt:
            img = Image(filename=pt)
            display(img)
        with path(
                'pm20_5.qu2',
                'q2_task2.png'
                ) as pt:
            img = Image(filename=pt)
            display(img)
        with path(
                'pm20_5.qu2',
                'q2_task3.png'
                ) as pt:
            img = Image(filename=pt)
            display(img)
    else:
        qn = str(qn)
        files = sorted(contents('pm20_5.qu2'))
        to_disp = []
        for elem in files:
            if 'q2' + '_' + qn + '_' in elem:
                to_disp.append(elem)
        if not to_disp:
            to_disp.append('q2_' + qn + '.png')
        to_disp.sort()
        for elem in to_disp:
            with path(
                'pm20_5.qu2',
                elem
                ) as pt:
                img = Image(filename=pt)
                display(img)



def q3(qn=0):
    if not qn:
        with path(
                'pm20_5.qu3',
                'q3_task1.png'
                ) as pt:
            img = Image(filename=pt)
            display(img)
        with path(
                'pm20_5.qu3',
                'q3_task2.png'
                ) as pt:
            img = Image(filename=pt)
            display(img)
    else:
        qn = str(qn)
        files = sorted(contents('pm20_5.qu3'))
        to_disp = []
        for elem in files:
            if 'q3' + '_' + qn + '_' in elem:
                to_disp.append(elem)
        if not to_disp:
            to_disp.append('q3_' + qn + '.png')
        to_disp.sort()
        for elem in to_disp:
            with path(
                'pm20_5.qu3',
                elem
                ) as pt:
                img = Image(filename=pt)
                display(img)
