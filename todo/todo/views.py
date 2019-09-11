import datetime
import json
import jwt
import re

from onemsdk.schema import v1 as onem

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
        response = onem.Response(menu_or_form)
        return HttpResponse(
            response.json(),
            content_type='application/json'
        )


class HomeView(View):
    http_method_names = ['get']

    def get(self, request):
        user = self.get_user()

        done_count = user.task_set.filter(done=True).count()
        todo = user.task_set.filter(done=False)
        todo_count = todo.count()

        body = [
            onem.MenuItem('New todo', path=reverse('task_create')),
            onem.MenuItem('Done({done})'.format(done=done_count),
                          path=reverse('task_list_done')),
            onem.MenuItem('Todo({todo})'.format(todo=todo_count))
        ]

        for item in todo:
            body.append(
                onem.MenuItem('{descr} {due}'.format(
                    descr=item.descr,
                    due=item.due_date,
                ), path=item.get_absolute_url()))

        return self.to_response(onem.Menu(body, header='menu'))


class TaskCreateView(View):
    http_method_names = ['get', 'post']

    def get(self, request):
        body = [
            onem.FormItemContent(
                onem.FormItemContentType.string,
                'descr',
                description='Please provide a description for the task',
                header='description',
            ),
            onem.FormItemContent(
                onem.FormItemContentType.date,
                'due_date',
                description='Provide a due date',
                header='due date',
            ),

        ]
        return self.to_response(
            onem.Form(body, reverse('task_create'), method='POST')
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


class TaskCreateValidateView(View):
    http_method_names = ['get']

    def get(self, request):
        descr = request.GET.get('descr')
        if descr:
            if re.findall('[^\w]+', descr):
                valid = False
                message = 'You are not allowed to use special chars'
            else:
                valid = True
                message = None
        else:
            valid = True
            message = None

        return HttpResponse(
            json.dumps({'valid': valid, 'message': message}),
            content_type='application/json'
        )


class TaskDetailView(View):
    http_method_names = ['get', 'put', 'delete']

    def get(self, request, id):
        task = get_object_or_404(Task, id=id)

        mark_as_label = 'Mark as todo' if task.done else 'Mark as done'

        body = [
            onem.MenuItem('Task: {descr}'.format(descr=task.descr)),
            onem.MenuItem('Due: {date}'.format(date=str(task.due_date))),
            onem.MenuItem(mark_as_label, path=task.get_absolute_url(),
                          method='PUT'),
            onem.MenuItem('Delete', path=task.get_absolute_url(),
                          method='DELETE'),
        ]
        return self.to_response(onem.Menu(body, header='view'))

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
                onem.MenuItem('{descr} {due}'.format(
                    descr=item.descr,
                    due=item.due_date,
                ), path=item.get_absolute_url()))

        return self.to_response(onem.Menu(body, header='done'))
