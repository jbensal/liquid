from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.core.paginator import Paginator
from utils.group_decorator import group_admin_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from intranet.caffeine_manager.soda.models import Soda
from intranet.caffeine_manager.soda.forms import SodaForm
from intranet.caffeine_manager.views import fromLocations

def allSodas(request):
    sodas=Soda.objects.all().order_by('-total_sold', 'name')
    for s in sodas:
        s.votedFor=(s.votes.filter(username=request.user.username).count() == 1)

    request.session['from'] = fromLocations.ALL_SODAS

    is_caffeine_admin=request.user.is_group_admin('Caffeine')

    # Get paginator and page
    page=1
    paginator=Paginator(sodas, 10)
    page_arg=request.GET.get('page')
    if page_arg and page_arg.isdigit():
        page=int(page_arg)
        page=max(1, min(paginator.num_pages, page))
    sodasPage=paginator.page(page)

    return render_to_response(
     'intranet/caffeine_manager/soda/allsodas.html',
     {
       'section':'intranet',
       'page':'caffeine',
       'sub_page':'sodas',
       'sodasPage':sodasPage,
       'request':request,
       'is_caffeine_admin':is_caffeine_admin
     }, context_instance=RequestContext(request))


@group_admin_required(['Caffeine'])
def add(request):
    soda_form=None;
    from_arg=request.session.get('from', fromLocations.ALL_SODAS)
    if request.method == 'POST':
        soda_form=SodaForm(request.POST)
        if soda_form.is_valid():
            soda_form.save()
            return redirect(reverse('cm_soda_all_sodas'))
    else:
        soda_form=SodaForm()

    return render_to_response(
       'intranet/caffeine_manager/soda/edit_soda.html',
       {
         'section':'intranet',
         'page':'caffeine',
         'form':soda_form,
         'from_arg':from_arg
       },
       context_instance=RequestContext(request))

@group_admin_required(['Caffeine'])
def edit(request, sodaId):
    soda=get_object_or_404(Soda, pk=sodaId)
    soda_form=None;
    from_arg=request.session.get('from', fromLocations.ALL_SODAS)

    if request.method == 'POST':
        soda_form=SodaForm(request.POST, instance=soda)
        if soda_form.is_valid():
            soda_form.save()
            if from_arg == fromLocations.TRAYS:
                return redirect(reverse('cm_trays_view'))
            else:
                return redirect(reverse('cm_soda_allsodas'))
    else:
        soda_form=SodaForm(instance=soda)

    return render_to_response(
       'intranet/caffeine_manager/soda/edit_soda.html',
       {
         'section':'intranet',
         'page':'caffeine',
         'form':soda_form,
         'id':sodaId,
         'from_arg':from_arg
       }, context_instance=RequestContext(request))

@group_admin_required(['Caffeine'])
def delete(request, sodaId):
    get_object_or_404(Soda, pk=sodaId).delete()

    if request.session.get('from', fromLocations.ALL_SODAS) == fromLocations.TRAYS:
        return redirect(reverse('cm_trays_view'))
    return redirect(reverse('cm_soda_allsodas'))

def toggleVote(request, sodaId):
    votes=get_object_or_404(Soda, pk=sodaId).votes
    has_voted=votes.filter(username=request.user.username).count()
    if has_voted:
        votes.remove(request.user)
        messages.add_message(request, messages.INFO, 'Your vote has been removed!')
    else:
        votes.add(request.user)
        messages.add_message(request, messages.SUCCESS, 'Your vote has been recorded!')

    return redirect(reverse('cm_soda_allsodas'))

@group_admin_required(['Caffeine'])
def clearVotes(request, sodaId):
    get_object_or_404(Soda, pk=sodaId).votes.clear()
    messages.add_message(request, messages.INFO, 'Votes cleared.')
    return redirect(reverse('cm_soda_allsodas'))
