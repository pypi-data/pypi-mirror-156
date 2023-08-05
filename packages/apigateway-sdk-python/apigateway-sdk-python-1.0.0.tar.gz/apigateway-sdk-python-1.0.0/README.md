# API Gateway SDK для подписи запросов на Python

Для вызова API опубликованных c режимом аутентификации APP, запрос должен быть подписан при помощи APP_KEY и SECRET_KEY.
Для подписи запросов используются API Gateay SDK на одном из поддерживаемых языков программирования.

## Пререквизиты

* Python 3.8 и выше;
* pip 19.3.x и выше;
* requests 2.6 и выше.

## Подключение SDK к проекту

1. Установите SDK:
    ```python
    pip install apigateway-sdk-python
    ```

2. Импортируйте в проект библиотеку signer из apigateway-sdk-python и библиотеку requests.
    ```python
    from apigateway_sdk_python import signer
    import requests
    ```

## Пример использования SDK

1. В проекте с подключенным SDK создайте новый signer и передайте в него `APP_KEY` и `SECRET_KEY`.
     ```python
    sig = signer.Signer()
    sig.Key = "key"
    sig.Secret = "secret"
    ```

2. Создайте запрос, в котором укажите метод, URI, заголовки и тело запроса.
     ```python
    r = signer.HttpRequest("POST",
                           "https://my-domain.example.com/v1/test",
                           {"x-stage": "RELEASE"},
                           "body")
    ```

3. Вызовите функцию для подписывания запроса. Функция автоматически добавит заголовки `X-Sdk-Date` и `Authorization`.
    ```python
    sig.Sign(r)
    ```

4. Обратитесь к API и просмотрите ответ.
    ```python
    resp = requests.request(r.method, r.scheme + "://" + r.host + r.uri, headers=r.headers, data=r.body)
    print(resp.status_code, resp.reason)
    print(resp.content)
    ```
