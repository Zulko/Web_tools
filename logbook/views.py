from django.shortcuts import render, get_object_or_404, redirect

from db.models import Machine
from .models import LogBook
from .forms import LogBookForm


def logbook_view(request):
    user = request.user
    machines = Machine.objects.all()

    context = {
        'all_machines': machines,
        'user': user,
    }
    return render(request, 'logbook/index.html', context)


def book_view(request, machine_id):
    user = request.user
    machines = Machine.objects.all()
    machine = get_object_or_404(Machine, id=machine_id)
    all_logbook = LogBook.objects.filter(machine_id=machine.id)
    formLogBookAdd = LogBookForm(initial={'name': machine.name, 'machine': machine.id})

    if request.method == 'POST':
        formLogBookAdd = LogBookForm(request.POST, initial={'name': machine.name, 'machine': machine.id})
        print(formLogBookAdd)
        if formLogBookAdd.is_valid():
            new_entry = formLogBookAdd.save()
            return redirect('logbook:book', machine.id)
        else:
            print('form with error')

    context = {
        'all_machines': machines,
        'all_logbook': all_logbook,
        'user': user,
        'machine': machine,
        'formLogBookAdd': formLogBookAdd,
    }
    return render(request, 'logbook/book.html', context)


def book_add(request, machine_id):
    user = request.user
    machines = Machine.objects.all()
    machine = get_object_or_404(Machine, id=machine_id)
    all_logbook = LogBook.objects.filter(machine_id=machine.id)
    formLogBookAdd = LogBookForm(initial={'machine': machine.id})

    if request.method == 'POST':
        formLogBookAdd = LogBookForm(request.POST, initial={'machine': machine.id})
        if formLogBookAdd.is_valid():
            new_entry = formLogBookAdd.save()
            return redirect('logbook:book', new_entry.id)
    else:
        formLogBookAdd = LogBookForm(initial={'machine': machine.id})

    context = {
        'all_machines': machines,
        'all_logbook': all_logbook,
        'user': user,
        'machine': machine,
        'formLogBookAdd': formLogBookAdd
    }

    return render(request, 'db/samples_list.html', context)