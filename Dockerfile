FROM python:3.9-slim

EXPOSE 8550

WORKDIR /app

ADD requirements.txt .
ADD external_mods.csv .
ADD dataEditor.py .
ADD dataViewer.py .
ADD frontend.py .
ADD lcms_db.py .
ADD mzdatapy.py .
ADD mz_oligo_identify.py .
ADD test2_dash_file.py .
ADD oligo_lcms_0.db .

RUN pip3 install -r requirements.txt
RUN mkdir -p data/temp

# VOLUME "/app/data/temp"

ENTRYPOINT ["python"]
CMD ["test2_dash_file.py"]

