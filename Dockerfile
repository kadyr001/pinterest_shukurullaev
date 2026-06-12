FROM python:3.12

ENV PYTHONUNBUFFERED=1

WORKDIR /online_png

COPY req.txt .


RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY nginx/nginx.conf /etc/nginx/conf.d/

COPY . /online_shop/

#CMD ["uvicorn", "main:shop_app", "--host", "0.0.0.0", "--port", "8000"]