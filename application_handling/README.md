# Описание очередей микросервиса application_handling

## Эндпоинт `/create_application`
![image](https://github.com/user-attachments/assets/356ecabf-96bd-4f14-ad10-effc23e79e25)

- Тело запроса
  
  ``` json
  {
    "token": "valid_token",
    "event_id": "b2d6b4a5-dc28-4a7d-902d-3f67b84c123c",
    "creator_id": "b8b8774b-0b3c-4b5a-bbc6-130586c5e5ee",
    "application_type": "open",
    "result": {"score": 100}
  }
  
  ```
- Ответ (идёт в очередь `approved-events-queue`)

  ``` json
  {
      "status": "success",
      "application_id": "9e1fb57f-cbc3-4c55-8c1b-510d558a7163"
  }
  ```
## Эндпоинт `/process_application`


- Тело запроса

  ``` json
  {
    "token": "valid_token",
    "application_id": "9e1fb57f-cbc3-4c55-8c1b-510d558a7163",
    "approved": false
  }
  
  
  ```
- Ответ (идёт в очередь `finished-events-queue`)

  ``` json
  {
      "status": "success",
      "application_id": "9e1fb57f-cbc3-4c55-8c1b-510d558a7163",
      "approved": false
  }
  ```
