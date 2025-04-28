from django.shortcuts import render, redirect
from django.utils.html import escape
from django.contrib import messages
from django.http import JsonResponse
from ..forms import RequestConfigForm
from django.db import transaction
from django.template.loader import render_to_string
from ..models import RequestConfig, Notification
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import json
from datetime import datetime, timedelta
from django.views.decorators.http import require_POST, require_http_methods
from ..utils import send_request_email
from django.contrib.auth.models import User
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage
from django.utils.timezone import now
from django.shortcuts import get_object_or_404

def apply_filters(request, base_queryset):
    user = request.GET.get('user', None)
    priority = request.GET.get('priority', 'all')
    date = request.GET.get('date', 'all')
    completion = request.GET.get('completion', 'all')

    filters = Q()

    if user and user != 'all':
        filters &= Q(creator__username=user)

    if priority != 'all':
        filters &= Q(priority_status=priority)

    if completion != 'all':
        is_completed = completion.lower() == 'true'
        filters &= Q(completion_status=is_completed)

    if date != 'all':
        now = datetime.now()
        if date == 'today':
            filters &= Q(schedule_time__date=now.date())
        elif date == 'last7days':
            now = datetime.now()
            filters &= Q(schedule_time__gte=now - timedelta(days=7))
        elif date == 'thismonth':
            filters &= Q(schedule_time__year=now.year, schedule_time__month=now.month)
    
    filtered_queryset = base_queryset.filter(filters)

    return base_queryset.filter(filters)

def filter_requests(request):
    base_queryset = RequestConfig.objects.all()
    filtered_queryset = apply_filters(request, base_queryset)
  
    paginator = Paginator(filtered_queryset, 10)
    page_number = request.GET.get('page', 1)
    
    try:
        page_obj = paginator.get_page(page_number)
    except EmptyPage:
        return JsonResponse({'error': 'Invalid page number'}, status=400)

    data = {
        'requests': [
            {
                'id': req.id,
                'date_submitted': req.date_submitted.strftime('%Y-%m-%d %H:%M:%S'),
                'priority_status': req.priority_status,
                'schedule_time': req.schedule_time.strftime('%Y-%m-%d %H:%M:%S'),
                'creator': req.creator.username,
                'email_content': req.email_content,
                'completion_status': 'Completed' if req.completion_status else 'Pending',
            }
            for req in page_obj
        ],
        'users': list(User.objects.values_list('username', flat=True)) if request.user.is_superuser else [],
        'total_results': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
    }
    return JsonResponse(data)

def get_prior_requests_context(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            base_queryset = RequestConfig.objects.all().order_by('-date_submitted')
        else:
            base_queryset = RequestConfig.objects.filter(creator=request.user).order_by('-date_submitted')
    else:
        base_queryset = RequestConfig.objects.none()

    filtered_queryset = apply_filters(request, base_queryset)

    paginator = Paginator(filtered_queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'total_pages': paginator.num_pages,
        'total_results': paginator.count,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('emailscraper_app/request_list.html', {'page_obj': page_obj}, request=request)
        return JsonResponse({
            'html': html.strip(),
            'total_results': paginator.count,
            'total_pages': paginator.num_pages,
            'current_page': page_obj.number
        })

    return context

def paginate_requests(request, queryset, per_page=10):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return {
        'page_obj': page_obj,
        'total_pages': paginator.num_pages,
        'total_results': paginator.count,
        'current_page': page_obj.number,
    }

@transaction.atomic
def create_request_config(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            base_queryset = RequestConfig.objects.all().order_by('-date_submitted')
        else:
            base_queryset = RequestConfig.objects.filter(creator=request.user).order_by('-date_submitted')
    else:
        base_queryset = RequestConfig.objects.none()

    filtered_queryset = apply_filters(request, base_queryset)

    pagination_context = paginate_requests(request, filtered_queryset)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('emailscraper_app/request_list.html', {'page_obj': pagination_context['page_obj']}, request=request)
        return JsonResponse({
            'html': html.strip(),
            'total_results': pagination_context['total_results'],
            'total_pages': pagination_context['total_pages'],
            'current_page': pagination_context['current_page'],
        })

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = RequestConfigForm(request.POST)
            if form.is_valid():
                request_config = form.save(commit=False)

                user_id = request.POST.get('user_id')
                if request.user.is_superuser and user_id:
                    try:
                        user = User.objects.get(id=user_id)
                        request_config.creator = user
                    except User.DoesNotExist:
                        context = {
                            'form': form,
                            'error_message': escape("Selected user does not exist."),
                        }
                        return render(request, 'emailscraper_app/submit_request.html', context)
                else:
                    request_config.creator = request.user

                request_config.save()

                send_request_email(request_config, request_config.creator)

                base_queryset = RequestConfig.objects.filter(creator=request.user).order_by('-date_submitted') if not request.user.is_superuser else RequestConfig.objects.all().order_by('-date_submitted')
                filtered_queryset = apply_filters(request, base_queryset)
                pagination_context = paginate_requests(request, filtered_queryset)
                
                context = {
                    'form': RequestConfigForm(),
                    'success_message': 'Request Submitted Successfully',
                    'page_obj': pagination_context['page_obj'],
                    'total_pages': pagination_context['total_pages'],
                    'total_results': pagination_context['total_results'],
                }
                return render(request, 'emailscraper_app/submit_request.html', context)

            else:
                context = {
                    'form': form,
                    'error_message': escape("Please correct the errors below."),
                }
                return render(request, 'emailscraper_app/submit_request.html', context)

        else:
            context = {
                'error_message': escape("You must be logged in to submit a request."),
            }
            return render(request, 'emailscraper_app/submit_request.html', context)

    context = {
        'form': RequestConfigForm(),
        'page_obj': pagination_context['page_obj'],
        'total_pages': pagination_context['total_pages'],
        'total_results': pagination_context['total_results'],
    }
    if request.user.is_superuser:
        context['users'] = User.objects.all()

    return render(request, 'emailscraper_app/submit_request.html', context)

@csrf_exempt
def update_email_content(request, request_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            email_content = data.get('email_content', '').strip()
            selected_user_username = data.get('userFilter')

            request_config = RequestConfig.objects.get(id=request_id)
            request_config.email_content = email_content
            request_config.save()

            return JsonResponse({'success': True})
        except RequestConfig.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Request not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

@csrf_exempt
def delete_request(request, config_id):
    try:
        config = RequestConfig.objects.get(id=config_id)
        config.delete()

        Notification.objects.create(
            user=request.user,
            message=f"Request '{config_id}' has been deleted."
        )

        return JsonResponse({'success': True})
    except RequestConfig.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Request not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
def update_completion_status(request, config_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            completion_status = data.get('completion_status', False)

            config = RequestConfig.objects.get(id=config_id)
            config.completion_status = completion_status
            config.save()

            Notification.objects.create(
                user=request.user,
                message=f"Request '{config_id}' has been {'completed' if completion_status else 'marked as pending'}."
            )

            return JsonResponse({'success': True})
        except RequestConfig.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Request not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

def create_notifications(logged_in_user, selected_user_username, request_id, user_message):
    Notification.objects.create(
        user=logged_in_user,
        message=user_message,
    )

    if logged_in_user.is_superuser and selected_user_username and selected_user_username != logged_in_user.username:
        try:
            selected_user = User.objects.get(username=selected_user_username)
            Notification.objects.create(
                user=selected_user,
                message=user_message,
            )
        except User.DoesNotExist:
            pass

@login_required
def historical_requests(request):
    keyword = request.GET.get('keyword', '')
    request_id = request.GET.get('id')

    if request.user.is_superuser:
        base_queryset = RequestConfig.objects.all()
    else:
        base_queryset = RequestConfig.objects.filter(creator=request.user)

    if keyword:
        base_queryset = base_queryset.filter(email_content__icontains=keyword)

    if request_id:
        request_obj = get_object_or_404(base_queryset, id=request_id)
    else:
        request_obj = base_queryset.order_by('id').first()

    all_request_ids = base_queryset.values_list('id', flat=True).order_by('id')

    return render(request, 'emailscraper_app/historical_requests.html', {
        'request_obj': request_obj,
        'all_request_ids': all_request_ids,
        'keyword': keyword
    })

@login_required
def get_next_request_id(request):
    current_id = request.GET.get('id')

    try:
        if not current_id:
            return JsonResponse({'error': 'Missing "id" parameter'}, status=400)
        try:
            current_id = int(current_id)
        except ValueError:
            return JsonResponse({'error': '"id" parameter must be an integer'}, status=400)

        user = request.user

        next_request = RequestConfig.objects.filter(id__gt=current_id, creator=user).order_by('id').first()
        if next_request:
            return JsonResponse({'next_request_id': next_request.id})
        else:
            first_request = RequestConfig.objects.filter(creator=user).order_by('id').first()
            if first_request:
                return JsonResponse({'next_request_id': first_request.id})
            else:
                return JsonResponse({'next_request_id': None})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)