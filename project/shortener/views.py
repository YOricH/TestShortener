# project/shortener/views.py
# Views of shortener app.

from django.shortcuts import render, get_object_or_404, HttpResponse
from  shortener.models import Direction, UserDirection
from django.http import HttpResponsePermanentRedirect
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.core.cache import cache
from .forms import DirectionForm
from django.conf import settings
from uuid import UUID
import logging


logger = logging.getLogger(__name__)


def index(request):
    """The main view of the app.

    Keywords arguments:
    request -- HttpRequest

    Return value:
    HttpResponse

    """
    direction_form = DirectionForm(request.POST or None)

    context = {
        "form": direction_form,
    }

    if request.method == "POST":

        if direction_form.is_valid():
            target = request.POST.get("target")
            subpart = request.POST.get("subpart")

            direction, err_str = Direction.get_or_create_direction(subpart, target)

            if request.session.test_cookie_worked():
                logger.debug(f'Cookie works.')
                request.session.delete_test_cookie()

                if err_str is None:
                    user_uuid = request.session.get('user_uuid', False)

                    user_direction = UserDirection()
                    user_direction.direction = direction

                    if user_uuid:
                        user_direction.user_uuid = UUID(user_uuid)

                    user_direction.save()

                    logger.debug(f'Save new UserDirection: {user_direction}')

                    if not user_uuid:
                        str_user_id = str(user_direction.user_uuid)
                        request.session['user_uuid'] = str_user_id

                        logger.debug(f'Save new user_id in session: {str_user_id}')
                else:
                    direction_form.add_error('subpart', ValidationError(err_str, code='Already use'))

    request.session.set_test_cookie()

    logger.debug(f'Trying to set cookie.')
    user_uuid = request.session.get('user_uuid', False)

    if user_uuid:
        user_uuid = UUID(user_uuid)
        direction_list = UserDirection.objects.select_related().filter(user_uuid=user_uuid). \
            values('direction__subpart', 'direction__target')

        paginator = Paginator(direction_list, settings.LINES_ON_PAGE)
        page = request.GET.get('page')
        directions = paginator.get_page(page)

        context['directions'] = directions

    return render(request, "index.html", context)


def redirect(request, subpart=None):
    """Redirects from subpart to the appropriate link.

    Keywords arguments:
    request -- HttpRequest
    subpart -- short link, str

    Return value:
    HttpResponsePermanentRedirect - redirect to the target link.

    """
    if subpart is None:
        return index(request)

    target = None

    if settings.USE_CACHE:
        try:
            target = cache.get(subpart)
        except Exception as e:
            logger.exception(f'Error getting direction from cache: {type(e)} - {str(e)}')

    if target is None:
        direction = get_object_or_404(Direction, subpart=subpart)
        target = direction.target
        rest_of_life = direction.get_rest_of_life()

        if rest_of_life > 0 and settings.USE_CACHE:

            try:
                cache.set(subpart, target, rest_of_life)
                logger.debug(f'Save direction "{direction}" is cache.')
            except Exception as e:
                logger.exception(f'Error saving direction in cache: {type(e)} - {str(e)}')

    return HttpResponsePermanentRedirect(target)
