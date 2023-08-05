import pkg_resources


def q1(qn=0):
    from PIL import ImageGrab
    from IPython.display import display, Image
    import os
    if not qn:
        resource_package = __name__
        resource_path = '/'.join(('q1', 'q1_task1.png'))
        template = pkg_resources.resource_string(resource_package, resource_path)
        
        img = Image(filename=template)
        display(img)
        img = Image(filename='q1/q1_task2.png')
        display(img)
    else:
        qn = str(qn)
        files = [f for f in os.listdir('q1')]
        to_disp = []
        for elem in files:
            if 'q1' + '_' + qn + '_' in elem:
                to_disp.append(elem)
        if not to_disp:
            to_disp.append('q1_' + qn + '.png')
        to_disp.sort()
        for elem in to_disp:
            img = Image(filename='q1/' + elem)
            display(img)


def q2(qn=0):
    from PIL import ImageGrab
    from IPython.display import display, Image
    import os
    if not qn:
        img = Image(filename='q2/q2_task1.png')
        display(img)
        img = Image(filename='q2/q2_task2.png')
        display(img)
        img = Image(filename='q2/q2_task3.png')
        display(img)
    else:
        qn = str(qn)
        files = [f for f in os.listdir('q2')]
        to_disp = []
        for elem in files:
            if 'q2' + '_' + qn + '_' in elem:
                to_disp.append(elem)
        if not to_disp:
            to_disp.append('q2_' + qn + '.png')
        to_disp.sort()
        for elem in to_disp:
            img = Image(filename='q2/' + elem)
            display(img)



def q3(qn=0):
    from PIL import ImageGrab
    from IPython.display import display, Image
    import os
    if not qn:
        img = Image(filename='q3/q3_task1.png')
        display(img)
        img = Image(filename='q3/q3_task2.png')
        display(img)
    else:
        qn = str(qn)
        files = [f for f in os.listdir('q3')]
        to_disp = []
        for elem in files:
            if 'q3' + '_' + qn + '_' in elem:
                to_disp.append(elem)
        if not to_disp:
            to_disp.append('q3_' + qn + '.png')
        to_disp.sort()
        for elem in to_disp:
            img = Image(filename='q3/' + elem)
            display(img)
