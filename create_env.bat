call conda env create -f environment.yml
call conda activate place-extraction
call python -m ipykernel install --user --name place-extraction --display-name "place-extraction"
call python -m spacy download en
call python -m spacy download nl
pause
