FROM public.ecr.aws/lambda/python:3.9

WORKDIR ${LAMBDA_TASK_ROOT}
COPY . .
RUN pip install .

CMD [ "kmws_accounting.adapters.awslambda.handler" ]
