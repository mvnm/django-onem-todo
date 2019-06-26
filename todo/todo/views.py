import onem
import datetime
import jwt

from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.views.generic import View as _View
from django.shortcuts import get_object_or_404

from .models import Task


class View(_View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *a, **kw):
        return super(View, self).dispatch(*a, **kw)

    def get_user(self):
        # return User.objects.filter()[0]
        token = self.request.headers.get('Authorization')
        if token is None:
            raise PermissionDenied

        data = jwt.decode(token.replace('Bearer ', ''), key='87654321')
        user, created = User.objects.get_or_create(id=data['sub'],
                                                   username=str(data['sub']))
        return user

    def to_response(self, menu_or_form):
        return HttpResponse(menu_or_form.as_json(),
                            content_type='application/json')


class HomeView(View):
    http_method_names = ['get']

    def get(self, request):
        user = self.get_user()

        done_count = user.task_set.filter(done=True).count()
        todo = user.task_set.filter(done=False)
        todo_count = todo.count()

        body = [
            onem.menus.MenuItem('New todo', url=reverse('task_create')),
            onem.menus.MenuItem('Done({done})'.format(done=done_count),
                                url=reverse('task_list_done')),
            onem.menus.MenuItem('Todo({todo})'.format(todo=todo_count),
                                is_option=False),
        ]

        for item in todo:
            body.append(
                onem.menus.MenuItem('{descr} {due}'.format(
                    descr=item.descr,
                    due=item.due_date,
                ), url=item.get_absolute_url()))

        return self.to_response(onem.menus.Menu(body, header='menu'))


class TaskCreateView(View):
    http_method_names = ['get', 'post']

    def get(self, request):
        body = [
            onem.forms.FormItem('Please provide a description for the task',
                                'descr',
                                onem.forms.FormItemType.STRING,
                                header='description'),
            onem.forms.FormItem('Provide a due date',
                                'due_date',
                                onem.forms.FormItemType.DATE,
                                header='due date')

        ]
        return self.to_response(
            onem.forms.Form(body, reverse('task_create'), method='POST')
        )

    def post(self, request):
        descr = request.POST['descr']

        due_date = request.POST['due_date']

        Task.objects.create(
            user=self.get_user(),
            descr=descr,
            due_date=datetime.datetime.strptime(due_date, '%Y-%m-%d').date()
        )
        return HttpResponseRedirect(reverse('home'))


class TaskDetailView(View):
    http_method_names = ['get', 'put', 'delete']

    def get(self, request, id):
        task = get_object_or_404(Task, id=id)

        mark_as_label = 'Mark as todo' if task.done else 'Mark as done'

        body = [
            onem.menus.MenuItem('Task: {descr}'.format(descr=task.descr),
                                is_option=False),
            onem.menus.MenuItem('Due: {date}'.format(date=str(task.due_date)),
                                is_option=False),
            onem.menus.MenuItem(mark_as_label, url=task.get_absolute_url(),
                                method='PUT'),
            onem.menus.MenuItem('Delete', url=task.get_absolute_url(),
                                method='DELETE'),
        ]
        return self.to_response(onem.menus.Menu(body, header='view'))

    def put(self, request, id):
        task = get_object_or_404(Task, id=id)
        task.done = not task.done
        task.save()
        return HttpResponseRedirect(reverse('home'))

    def delete(self, request, id):
        task = get_object_or_404(Task, id=id)
        task.delete()
        return HttpResponseRedirect(reverse('home'))


class TaskListDoneView(View):
    http_method_names = ['get']

    def get(self, request):
        user = self.get_user()

        done = user.task_set.filter(done=True)
        body = []

        for item in done:
            body.append(
                onem.menus.MenuItem('{descr} {due}'.format(
                    descr=item.descr,
                    due=item.due_date,
                ), url=item.get_absolute_url()))

        return self.to_response(onem.menus.Menu(body, header='done'))
