from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    # Call DRF's default exception handler first to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        data = response.data
        status_code = response.status_code
        
        custom_data = {
            "status_code": status_code,
            "error": "Ошибка",
            "possible_reason": "Неизвестная ошибка сервера.",
            "suggested_fix": "Обратитесь в поддержку или проверьте технические детали.",
            "technical_details": data
        }

        if status_code == status.HTTP_401_UNAUTHORIZED:
            custom_data.update({
                "error": "Аутентификация не выполнена",
                "possible_reason": "Токен отсутствует, просрочен или невалиден.",
                "suggested_fix": "Выполните вход через /api/users/login/ и передайте токен в заголовке Authorization: Bearer <token>."
            })
        elif status_code == status.HTTP_403_FORBIDDEN:
            custom_data.update({
                "error": "Доступ запрещен",
                "possible_reason": "У вас недостаточно прав для этого действия (требуются права администратора или владение объектом).",
                "suggested_fix": "Проверьте, авторизованы ли вы под нужным аккаунтом."
            })
        elif status_code == status.HTTP_404_NOT_FOUND:
            custom_data.update({
                "error": "Ресурс не найден",
                "possible_reason": "Запрашиваемый объект не существует или ID в URL указан неверно.",
                "suggested_fix": "Проверьте правильность ID и убедитесь, что ресурс не был удален."
            })
        elif status_code == status.HTTP_400_BAD_REQUEST:
            custom_data.update({
                "error": "Некорректный запрос",
                "possible_reason": "Ошибка в формате данных или отсутствуют обязательные поля.",
                "suggested_fix": "Проверьте JSON-тело запроса на соответствие документации в Swagger."
            })
        elif status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            custom_data.update({
                "error": "Слишком много запросов",
                "possible_reason": "Вы превысили лимит запросов для вашего аккаунта или IP.",
                "suggested_fix": "Подождите некоторое время (обычно от 1 минуты) прежде чем пробовать снова."
            })

        response.data = custom_data

    return response
