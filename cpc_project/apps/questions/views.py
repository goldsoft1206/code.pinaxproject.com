from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response

from questions.forms import AskQuestionForm
from questions.models import Question


def question_list(request, group_slug=None, bridge=None):
    
    if bridge:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404()
    else:
        group = None
    
    questions = Question.objects.all()
    
    if group:
        questions = group.content_objects(questions)
    
    return render_to_response("questions/question_list.html", {
        "group": group,
        "questions": questions,
    }, context_instance=RequestContext(request))


def question_create(request, group_slug=None, bridge=None):
    
    if bridge:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404()
    else:
        group = None
    
    if request.method == "POST":
        form = AskQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.user = request.user
            question.save()
            return HttpResponseRedirect(question.get_absolute_url())
    else:
        form = AskQuestionForm()
    
    return render_to_response("questions/question_create.html", {
        "group": group,
        "form": form,
    }, context_instance=RequestContext(request))


def question_detail(request, question_id, group_slug=None, bridge=None):
    
    if bridge:
        try:
            group = bridge.get_group(group_slug)
        except ObjectDoesNotExist:
            raise Http404()
    else:
        group = None
    
    questions = Question.objects.all()
    
    if group:
        questions = group.content_objects(questions)
    
    question = get_object_or_404(questions, pk=question_id)
    responses = question.responses.all() # @@@ ordering
    
    if question.user == request.user:
        is_me = True
    else:
        is_me = False
    
    if "accept" in request.GET:
        response_id = int(request.GET["accept"])
        
        if is_me:
            response = responses.get(pk=response_id)
            response.accept()
        else:
            return HttpResponse("cannot perform action")
        
        return HttpResponse("good")
    
    return render_to_response("questions/question_detail.html", {
        "group": group,
        "is_me": is_me,
        "question": question,
        "responses": responses,
    }, context_instance=RequestContext(request))
