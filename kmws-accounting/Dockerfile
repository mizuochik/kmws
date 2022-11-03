FROM public.ecr.aws/lambda/python:3.9 AS stage

RUN python -m venv /.venv
ENV PATH="/.venv/bin:$PATH"

COPY . .
RUN pip install .

FROM public.ecr.aws/lambda/python:3.9

COPY --from=stage /.venv /.venv
ENV PATH="/.venv/bin:$PATH"
ENV PYTHONPATH=/.venv/lib/python3.9/site-packages

CMD [ "kmws_accounting.adapters.awslambda.handler" ]
