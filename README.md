1. Create a Virtual Environment

```
    python3 -m venv env
    source env/bin/activate  # On Windows: env\Scripts\activate
```

2. Install Dependencies
```
    pip3 install -r requirements.txt
```

3. Start Project
run three terminal parellel

    #1:
    ```
        uvicorn main:app --reload --host=0.0.0.0 --port=8000
    ```

    #2:
    ```
        celery -A celery_app worker --loglevel=info
    ```

    #3:
    ```
        celery -A celery_app beat --loglevel=info
    ```

4. please user default user password to generate jwt

    email: admin@gmail.com
    password: password123

