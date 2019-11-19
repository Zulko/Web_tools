from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from db.models import Machine
from .models import LogBook
from .forms import LogBookForm, LogBookUpdateForm


def logbook_view(request):
    user = request.user
    machines = Machine.objects.all().order_by('-id').reverse()

    context = {
        'all_machines': machines,
        'user': user,
    }
    return render(request, 'logbook/index.html', context)


def book_view(request, machine_id):
    user = request.user
    machines = Machine.objects.all().order_by('-id').reverse()
    machine = get_object_or_404(Machine, id=machine_id)
    all_logbook = LogBook.objects.filter(machine_id=machine.id)
    formLogBookAdd = LogBookForm(initial={'name': machine.name, 'machine': machine.id})

    if request.method == 'POST':
        formLogBookAdd = LogBookForm(request.POST, initial={'name': machine.name, 'machine': machine.id})
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
    return render(request, 'logbook/index.html', context)


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

    return render(request, 'logbook/index.html', context)


def book_entry_view(request, machine_id, entry_id):
    user = request.user
    machines = Machine.objects.all().order_by('-id').reverse()
    machine = get_object_or_404(Machine, id=machine_id)
    entry = get_object_or_404(LogBook, machine=machine.id, id=entry_id)
    all_logbook = LogBook.objects.filter(machine_id=machine.id)
    formLogBookAdd = LogBookForm(initial={'machine': machine.id})
    if request.user.is_authenticated:
        formLogBookUpdate = LogBookForm(instance=entry)
    else:
        formLogBookUpdate = LogBookUpdateForm(instance=entry)

    if 'submit_add_entry' in request.POST:
        formLogBookAdd = LogBookForm(initial={'machine': machine.id})
        if formLogBookAdd.is_valid():
            formLogBookAdd.save()
            return redirect('logbook:book', machine.id)
        else:
            print('form with error')

    elif 'submit_update_entry' in request.POST:
        if request.user.is_authenticated:
            formLogBookUpdate = LogBookForm(request.POST, instance=entry)
        else:
            formLogBookUpdate = LogBookUpdateForm(request.POST, instance=entry)

        if formLogBookUpdate.is_valid():
            formLogBookUpdate.save()
            return redirect('logbook:book', machine.id)
        else:
            print('form with error')

    context = {
        'all_machines': machines,
        'all_logbook': all_logbook,
        'user': user,
        'machine': machine,
        'formLogBookAdd': formLogBookAdd,
        'formLogBookUpdate': formLogBookUpdate,
        'entry': entry,
    }
    return render(request, 'logbook/index.html', context)


def book_entry_update(request, machine_id, entry_id):
    machine = Machine.objects.get(id=machine_id)
    entry = get_object_or_404(LogBook, machine=machine.id, id=entry_id)

    if request.user.is_authenticated:
        if 'submit_update_entry' in request.POST:
            formLogBookUpdate = LogBookForm(request.POST, instance=entry)
            if formLogBookUpdate.is_valid():
                formLogBookUpdate.save()
                return redirect('logbook:book', machine.id)
            else:
                print('form with error')
        else:
            formLogBookUpdate = LogBookForm(instance=machine)

    else:
        if 'submit_update_entry' in request.POST:
            formLogBookUpdate = LogBookUpdateForm(request.POST, instance=entry)
            if formLogBookUpdate.is_valid():
                formLogBookUpdate.save()
                return redirect('logbook:book', machine.id)
            else:
                print('form with error')
        else:
            formLogBookUpdate = LogBookUpdateForm(instance=machine)

    context = {
        'formLogBookUpdate': formLogBookUpdate,
    }

    return render(request, 'logbook/index.html', context)


@login_required()
def book_entry_delete(request, machine_id, entry_id):
    machine = Machine.objects.get(id=machine_id)
    entry = get_object_or_404(LogBook, machine=machine.id, id=entry_id)
    if request.method == 'POST':
        entry.delete()

    return redirect('logbook:book', machine.id)

